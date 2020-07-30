from .worksheet_config import common_words, BS4Headers
# from CNN import test_article_contents # Change this later
import bs4, requests, re, random, time
from pprint import pprint
from PyDictionary import PyDictionary
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
dictionary = PyDictionary()
lem = WordNetLemmatizer()


# paragraph_divided = test_article_contents


def getAllUniqueWords(listOfParagraphs):

    '''
    Takes a list containing paragraphs of content, and returns a filtered list of all the unique words.
    '''
    exclude_list = ("you'", "hasn", "we'" , "cnn")
    words = (' ').join(listOfParagraphs) #Turn the paragraph into list of words.

    onlyWordCharacters = ''.join([i.lower() for i in words if i.isalpha() or i in (' ', "'", '-', '(', ')')])

    wordList = set(onlyWordCharacters.split(' '))
    remove_apostrophe_S_words_etc = []
    for word in wordList:

        #Ditch complicated hyphenated words (they almost never show up in the dictionary)
        if '-' in word:

            continue

        
        # If the word is in brackets, remove them
        if word.startswith('('):
            word = word[1:]

        if word.endswith(')'):
            word = word[:-1]

        # Screw it, if there is still a bracket in there, that word sucks anyway
        if '(' in word or ')' in word:
            continue
        
        #Remove 's from possessive words
        if word.endswith("'s"):
            word = word[:-2]
        
 

        #Most people know most short words, discard them
        if len(word) < 4:
            continue

        #Finally, check against exclude list
        skip = False
        for ex in exclude_list:
            if ex in word:
                skip = True
                break
        if skip == True:
            continue
        
        remove_apostrophe_S_words_etc.append(lem.lemmatize(word, 'v'))


               
    wordList = set(remove_apostrophe_S_words_etc) #Use set to remove duplicates.

    significantWordList = [word for word in wordList if word not in common_words]
    significantWordList.sort()

    return significantWordList

def getRandomWordsFromParagraph(listOfParagraphs, sample=6):
    '''
    Takes a list of paragrahps of content, and returns a random sample of unique words from those paragraphs.
    '''
    source = getUniqueWords(listOfParagraphs)
    if len(source) < sample:
        print('Low quantity of words found')
        sample = len(source)
    return random.sample(source, sample)


def getDefinitionFromDictSite(word):

    try:
        found_definitions_dict = dictionary.meaning(word)

         # Search for example
        print(f'Searching for example for {word}')
        try:
            example_sentence = getExampleForWord(word)
        except:
            print('An error occurred getting the example')
            example_sentence = []

        found_definitions_dict['examples'] = example_sentence

        return found_definitions_dict
    
    
    except:
        print(f'Word {word} was missing from the dictionary')

def getDefinitionForRandomWords(listOfWords, sample=6):

    defined_words = {}
    collecting = True
    word_index = 0
    added_words = 0

    # Prevent going out of range
    if len(listOfWords) < sample:
        print('List of words is smaller than the sample.')
        sample = len(listOfWords)

    # Choose a sample of words to work from
    random.shuffle(listOfWords)

    # Collect word definition
    while collecting: #Use while loop to cover searching for a word
        word = listOfWords[word_index]
        print(f'Working on: {word}')
        try:
            result = getDefinitionFromDictSite(word)
            defined_words[word.capitalize()] = result
            added_words += 1
        except:
            print(f'Could not find this word: {word}')
        
        word_index += 1

        if added_words >= sample:
            collecting = False


    # defined_words_with_examples = addExampleToWordDict(defined_words)

    return defined_words


        


    # actual_definitions = top_definitions_section[1:]

    # IPA_pron = pronunciation_chunk.select('.pron-spell-ipa-containera')
    # print(IPA_pron)

def getDefinitionsForUserChosenWords(wordList):
    '''
    Given a list of words, searches for most common uses of each word. Returns a dict, key is word, item is definitions.

    Parameters:
    wordList: List of string words.

    '''


    defined_words = {}
    for word in wordList:
        print(f'Working on: {word}')
        try:
            result = getDefinitionFromDictSite(word)
            if result:
                defined_words[word.capitalize()] = result
            else:
                print(f'Dictionary returned None, {word} excluded.')
        except:
            print(f'Could not find this word: {word}')
    
    # defined_words_with_examples = addExampleToWordDict(defined_words)
    return defined_words

def getExampleForWord(word):
    '''
    Given a word, search web for the example and scrape it.
    Return a cloze-ified sentence if example was found, else returns empty list.
    '''
    example_site_url = 'https://sentence.yourdictionary.com/'


    res = requests.get(f'{example_site_url}{word.lower()}', headers=BS4Headers)
    res.raise_for_status()

    soup = bs4.BeautifulSoup(res.text, features='html.parser')

    # print(soup)
    # word_heading_section = soup.select("#top-definitions-section")
    example = soup.find('div', class_='sentence component')


    if example:
        ex_text = example.text
        split_for_cloze_example = ex_text.split()

        for i in range(len(split_for_cloze_example)):
            
            cell = split_for_cloze_example[i]
            if word in cell:
                split_for_cloze_example[i] = '__________________'

        return ' '.join(split_for_cloze_example)

    else:

        return []


# print(getMultipleDefinitions(getRandomUniqueWords(test_article_contents)))

# print(getDefinitionFromDictSite('conditions'))