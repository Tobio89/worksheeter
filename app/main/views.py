from datetime import datetime
import os
from flask import Flask, render_template, session, redirect, url_for, request, flash, send_file, send_from_directory
from .. import db
# from ..models import # Add the DB models here
# from ..email import send_email
from . import main
# If you need custom functions and stuff they go in the same folder as email and models, and are imported here

# from ..tasks import recurringTask, oneTimeTask, getTimelessDate

from ..CNN import getNewsArticles, getArticleContent
from ..vocab import getRandomUniqueWords, getMultipleDefinitions
from ..docx_maker import writeDocx


# Constant Variables




# FLASK ROUTES / SITE PAGES

@main.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        if 'user_search_terms' in request.form:
            user_search_terms = request.form.get('user_search_terms')
            session['search_terms'] = user_search_terms

            return redirect(url_for('main.maker'))

    return render_template('index.html')



@main.route('/maker', methods=['GET', 'POST'])
def maker():

    if request.method == 'POST': # Handle the selection of the article

        if 'user_selected_article' in request.form:        
            form_response = request.form.get('user_selected_article')

            form_response_split = form_response.split('%')
            session['article-url'] = form_response_split[0]
            session['article-title'] =  form_response_split[1]
        else:
            flash('No article selected', 'warning')

        print(form_response_split)
        print('Pretend the sheet is being made now lol')

        session['search_terms'] = None

        return redirect(url_for('main.sheet'))

    else: # Handle the gathering of articles to choose from
        terms = session['search_terms']
        if terms:
            CNN_articles = getNewsArticles(terms)
        else:
            terms = None
            CNN_articles = None
    
    

    return render_template('maker.html', chosen_terms=terms, articles=CNN_articles)


@main.route('/sheet', methods=['GET', 'POST'])
def sheet():

    user_article_title = session['article-title']
    user_article_url = session['article-url']

    article_paragraphs = getArticleContent(user_article_url)
    user_word_list = getRandomUniqueWords(article_paragraphs)
    # user_word_definitions = getMultipleDefinitions(user_word_list)
    
    download_file = writeDocx(article_paragraphs, user_word_list, user_article_title)

    return render_template('sheet.html', downLink=download_file)
    
      
@main.route('/download/<filename>')
def download_file(filename):

    return send_from_directory(directory='./static/download', filename=filename, as_attachment=True)
    