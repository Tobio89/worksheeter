import bs4, requests, random
from .worksheet_config import BS4Headers
from os import path
from os import environ
from newsapi import NewsApiClient



API_KEY=environ.get['NEWS_API_KEY'] #add to env later!
exclusions = ('videos', 'live-news', 'gallery', 'travel', 'underscored') 

newsapi = NewsApiClient(API_KEY)


def getNewsArticles(search_term):
    print(f'Received request for article search {search_term}')

    response = newsapi.get_everything(q=search_term, domains='cnn.com')

    articles_list = []

    if response:
        status = response['status']
        if status == 'ok':
            articles = response['articles']
            article_objects = []
            for raw_art in articles:
                exclude_flag = False
                for x in exclusions:
                    if x in raw_art['url']:
                        print(raw_art['url'])
                        exclude_flag = True
                
                if exclude_flag:
                    continue
                else:

                    a = {
                        'title' : raw_art['title'], 
                        'source' : raw_art['source']['name'], 
                        'url' : raw_art['url'],
                    }
                    articles_list.append(a)
            if articles_list:
                return articles_list
            else:
                print('Error searching: There were no suitable articles')
                return None
        else:
            print('Error with API: response status not OK')
            return None
    else:
        print('Error with API: no response')
        return None

def getArticleContent(article_URL):

    res = requests.get(article_URL, headers=BS4Headers)
    res.raise_for_status()

    soup = bs4.BeautifulSoup(res.text, features='html.parser')

    paragraphs = soup.select('.zn-body__paragraph')
    
    output_text = [chunk.text for chunk in paragraphs]


    return output_text