from .worksheet_config import common_words, BS4Headers
# from CNN import test_article_contents # Change this later
import bs4, requests, re, random, time
from pprint import pprint




# paragraph_divided = test_article_contents

def getAllUniqueWords(listOfParagraphs):

    '''
    Takes a list containing paragraphs of content, and returns a filtered list of all the unique words.
    '''

    words = (' ').join(listOfParagraphs) #Turn the paragraph into list of words.

    onlyWordCharacters = ''.join([i.lower() for i in words if i.isalpha() or i==' ' or i=="'" or i=='-'])

    wordList = set(onlyWordCharacters.split(' '))
    remove_apostrophe_S_words_etc = []
    for word in wordList:


        if len(word) < 4: # Skip short words

            continue

        if word.endswith("'s"):
            word =word[:-2]
        elif word.startswith('cnn'):
 
            continue #Ditch the first word that contains CNN.
        if "you'" in word or "hasn'" in word or "we'" in word: #Throw away these common words

            continue
        if word[0].isalpha() == False: #Discard weird hyphen-first words
 
            continue


        if len(word) < 4:
            continue
        else:
            remove_apostrophe_S_words_etc.append(word)

                
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
    '''
    Given a single word, searches for definition on web and returns most uses for that word.  Returns a dict.

    Parameters:
    word: Single word as string.

    '''

    
    dictionary_url = 'https://www.dictionary.com/browse/'


    res = requests.get(f'{dictionary_url}{word}', headers=BS4Headers)
    res.raise_for_status()

    soup = bs4.BeautifulSoup(res.text, features='html.parser')

    # word_heading_section = soup.select("#top-definitions-section")
    heading = soup.select('.css-1jzk4d9')
    if heading:
        print(f'Found word {heading[0].text}')
    top_definitions_section = soup.select('.css-1urpfgu.e16867sm0')[0] # Dict site uses this class to contain definitions chunk. We just want the top.
    
    # Get IPA for the word
    IPA_pron = top_definitions_section.select('.pron-ipa-content.css-z3mf2.evh0tcl2')[0].text

    definitions = top_definitions_section.select('.css-pnw38j.e1hk9ate0') #This contains each definition. Iterate over this

    found_definitions_dict = {}
    for c in definitions:

        part_of_speech = c.select('.luna-pos')[0].text.capitalize() #Noun, Verb, etc
        all_defs = c.select('.e1hk9ate4')

        definition_text = [] # List of all text-only definitions
        

        for definition_paragraph in all_defs: #For each chunk of definitions given for the part of speech...

            default_content = definition_paragraph.select('.default-content') #Check if there is the expandable cell
            if default_content:

                for definition_text_span in default_content: #For each actual entry inside this
                    for content in definition_text_span.select('.e1q3nk1v3'): #Get the text content from it.

                        definition_text_span = content.text

                        for luna_example in content.select('.luna-example'): # Find the example sentences
                            example_sentence = luna_example.text

                            # The definition text comes with the example sentence. Remove the example sentence from the definition.
                            definition_text_span = definition_text_span.replace(example_sentence, '')

                        
                        
                        if definition_text_span.endswith(': '):
                            definition_text_span = definition_text_span[:-2]
                        definition_text.append(definition_text_span)

            else: #No expandable content in cell

                for content in definition_paragraph.select('.e1q3nk1v3'): #Grab all content.

                    definition_text_span = content.text
                    
                    
                    if definition_text_span.endswith(': '):
                        definition_text_span = definition_text_span[:-2]

                    definition_text.append(definition_text_span)
                    
                    # definition_text.append(content.text)

        found_definitions_dict[part_of_speech] = definition_text


    # Search for example
    print(f'Searching for example for {word}')
    try:
        example_sentence = getExampleForWord(word)
    except:
        print('An error occurred getting the example')
        example_sentence = []

    found_definitions_dict['examples'] = example_sentence



    return found_definitions_dict  


      
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
            defined_words[word.capitalize()] = result
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