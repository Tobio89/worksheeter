from datetime import datetime
import os, random
from flask import Flask, render_template, session, redirect, url_for, request, flash, send_file, send_from_directory
from .. import db
from ..models import Worksheets
# from ..email import send_email
from . import main
# If you need custom functions and stuff they go in the same folder as email and models, and are imported here

# from ..tasks import recurringTask, oneTimeTask, getTimelessDate

from ..CNN import getNewsArticles, getArticleContent
from ..vocab import getAllUniqueWords, getDefinitionsForUserChosenWords, getDefinitionForRandomWords
from ..docx_maker import writeDocx
from ..maintenance import clearOldFiles, timeless


# Constant Variables




# FLASK ROUTES / SITE PAGES
@main.route('/about')
def about():
    return render_template('about.html')



@main.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        if 'user_search_terms' in request.form:
            user_search_terms = request.form.get('user_search_terms')
            session['search_terms'] = user_search_terms

            return redirect(url_for('main.articles'))

    return render_template('index.html')



@main.route('/articles', methods=['GET', 'POST'])
def articles():

    # If the user submits the form, save the title and url to DB for further use.
    if request.method == 'POST': 

        # The form was submitted correctly
        if 'user_selected_article' in request.form:

            #Load title/url data from form        
            form_response = request.form.get('user_selected_article')

            #Split into separate variables
            form_response_split = form_response.split('%')
            user_selected_article_title = form_response_split[1]
            user_selected_article_URL = form_response_split[0]
            print('User selected the following article:')
            print(user_selected_article_title)

            # Add these to DB
            print('Added title and URL to DB.')
            session_worksheet = Worksheets(title=user_selected_article_title, url=user_selected_article_URL, timestamp=timeless(datetime.now()))
            db.session.add(session_worksheet)
            
            #Flush to generate row id - 
            # save this to session to allow working on same data across multiple pages.
            db.session.flush()
            user_sheet_id = session_worksheet.id
            session['user-sheet-id'] = user_sheet_id
            print(user_sheet_id)

            db.session.commit()


        #Error message for if the form was submitted with nothing selected 
        else:
            flash('No article selected', 'warning')

        # Clear terms to prevent clashes
        session['search_terms'] = None

        return redirect(url_for('main.words'))

    else: # Initial loading of page - load articles from CNN and show them to the user
        terms = session['search_terms']
        if terms:
            # Uncomment this to view error message related to selenium.
            # CNN_articles = getNewsArticles(terms)
            try:
                CNN_articles = getNewsArticles(terms)
            except:
                flash(f'Failed to find articles for {terms}!', 'danger')
                print('WARNING: If this failed, probably the chrome driver has a version issue.')
                print('Try commenting the try block out and un-commenting the CNN_articles line above to see.')
                CNN_articles = None
                return redirect(url_for('main.index'))
        else:
            terms = None
            CNN_articles = None
    
    

    return render_template('articles.html', chosen_terms=terms, articles=CNN_articles)


@main.route('/words', methods=['GET', "POST"])
def words():

    try:
        # Load sheet data via id in session
        user_sheet_id = session['user-sheet-id']
        DB_sheet_data = Worksheets.query.filter_by(id=user_sheet_id).first()

        print('Successfully loaded session sheet data for sheet:')
        print(DB_sheet_data.title)

        user_article_title = DB_sheet_data.title
        user_article_url = DB_sheet_data.url
    except:
        # User will reach here if they try to go back to a page after the download was performed.
        flash("Your worksheet session has expired! Try making the sheet again.", 'danger')
        return redirect(url_for('main.index'))

    # If the form has been submitted: (The user is already on the page)
    if request.method == 'POST':

        # Get words from the form
        form_words = request.form.get('submitted_words')
        
        #Cover weird situation where JS selects random words but they're not loaded here.
        if not form_words:
            print('No selected words found. Randomly choosing 6.')
            user_selected_words = random.sample(unique_words_in_paragraph, 6)

            #Join words into DB-compatible string using #
            form_words = '#'.join(user_selected_words) 

        #Save the words as one string with separator #
        DB_sheet_data.words = form_words 
        db.session.commit()


        return(redirect(url_for('main.sheet')))

    # Initial loading of page
    else:
         
        print(f'Getting words for {user_article_title}')

        try:
            #Get the paragraphs from the actual article
            article_paragraphs = getArticleContent(user_article_url)
            
            # Join paras into DB-compatible string, save to DB
            joined_paras = '#%#'.join(article_paragraphs)
            print('Saving paragraphs to DB...')
            DB_sheet_data.paragraphs = joined_paras
            db.session.commit()

        except:
            # This tends to happen if the article doesn't have the right CSS tags
            print('Failed to extract paragraph data')
            flash('Failed to extract paragraph data! Sorry :(', 'danger')

        # Parse words from paras so user can select them
        try:
            unique_words_in_paragraph = getAllUniqueWords(article_paragraphs)


        except:
            print('Failed to gather words')
            flash('Failed to gather words! Sorry :(', 'danger')
            return(redirect(url_for('main.index')))

    

    return render_template('words.html', words=unique_words_in_paragraph)



@main.route('/sheet', methods=['GET', 'POST'])
def sheet():

    try:
        # Load sheet data via id in session
        user_sheet_id = session['user-sheet-id']
        DB_sheet_data = Worksheets.query.filter_by(id=user_sheet_id).first()

        print('Successfully loaded session sheet data for sheet:')
        print(DB_sheet_data.title)

        user_article_title = DB_sheet_data.title
        user_article_url = DB_sheet_data.url
        users_words = DB_sheet_data.words.split('#')
        article_paragraphs = DB_sheet_data.paragraphs.split('#%#')
    except:
        # User will reach here if they try to go back to a page after the download was performed.
        flash("Your worksheet session has expired! Try making the sheet again.", 'danger')
        return redirect(url_for('main.index'))


    # Collect definitions for chosen words
    if users_words:
        user_word_definitions = getDefinitionsForUserChosenWords(users_words)
    
    # Cover (very unlikely) event where words are missing or not loaded
    else:
        print('User forgot to select words. Going random.')
        user_word_definitions = getDefinitionForRandomWords(article_paragraphs)
        flash('No words were selected, so six random words were picked.', 'info')

    # Generate file
    download_file = writeDocx(article_paragraphs, user_word_definitions, user_article_title)

    return render_template('sheet.html', downLink=download_file)
    
      
@main.route('/download/<filename>')
def download_file(filename):
    print('Pre-download clean-up...')
    # clearOldFiles()

    # #Clear old data from DB:
    # #Load data
    # user_sheet_id = session['user-sheet-id']
    # DB_sheet_data = Worksheets.query.filter_by(id=user_sheet_id).first()
    # db.session.delete(DB_sheet_data)
    # db.session.commit()
    # print('Cleared old data from sheet')




    return send_from_directory(directory='./static/download', filename=filename, as_attachment=True)
    