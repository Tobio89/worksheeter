import bs4, requests, random
from .worksheet_config import BS4Headers

from selenium import webdriver
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC





CNN_URL = 'https://edition.cnn.com/search?size=100&q='

def getNewsArticles(searchTerms, quantity=20):

    searchURL = f'{CNN_URL}{searchTerms}'

    options = Options()
    options.add_argument("--headless") # This opens headless (windowless) Chrome/ium
    driver = webdriver.Chrome(options=options)
    driver.get(searchURL)
    print('Headless Chrome Initialised...')
    articles = driver.find_elements_by_css_selector("div.cnn-search__results-list div.cnn-search__result-contents")

    WebDriverWait(driver, 20).until( # Wait until it loads
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.cnn-search__result-contents")) #This table appears when loaded
        )

    article_headlines = driver.find_elements_by_css_selector("div.cnn-search__result-contents")  

    # Gather useable headlines and the links to their pages.
    output_list = []
    article_index = 0
    gathering = True
    while gathering: 
        headline = article_headlines[article_index]
        headline = headline.get_attribute('innerHTML')
        
        soup = bs4.BeautifulSoup(headline, features="html.parser")

        headline_complete_link = soup.find('a', href=True) #Gets entire link part

        headline_text = soup.find('a').get_text() #Get the headline text
        
        headline_links = [f"http:{a['href']}" for a in soup.find_all('a', href=True)] # This produces only the link. 
        
        # Discard video, live_news, and gallery-type articles
        if 'videos' in headline_links[0] or 'live-news' in headline_links[0] or 'gallery' in headline_links[0] or 'travel' in headline_links[0]:
            print(f'Skipping article {headline_text}')

        else:

            output_list.append({
                'atag': headline_complete_link,
                'head': headline_text,
                'href': headline_links[0]
            })
            
        article_index += 1
        if len(output_list) >= quantity:
            gathering = False

    print(f'Gathered {len(output_list)} articles.')
    return output_list



def getArticleContent(article_URL):

    res = requests.get(article_URL, headers=BS4Headers)
    res.raise_for_status()

    soup = bs4.BeautifulSoup(res.text, features='html.parser')

    paragraphs = soup.select('.zn-body__paragraph')
    
    output_text = [chunk.text for chunk in paragraphs]

    # print(output_text)
    return output_text

# print(getNewsArticles('manchester united'))