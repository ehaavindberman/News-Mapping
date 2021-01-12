import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import datetime
os.chdir('C:\\Developer\\News Mapping')


# TODO: primary vs secondary connections



def checkLocations(p):
  return [w for w in countries.name if re.search(r'\b{}\b'.format(re.escape(w)), p)]

def getArticleContent(base_url, article_url):
  res = requests.get(base_url + article_url)
  soup = BeautifulSoup(res.text, 'html.parser')
  
  header = soup.find(class_='article-header') 
  title = header.h1.text
  subhead = header.find(class_='article__subhead').text
  
  body = soup.find(class_='wysiwyg wysiwyg--all-content')
  places = []
  for p in body.find_all('p'):
    new_places = checkLocations(p.text)
    for pl in new_places:
      if pl not in places:
        places.extend([pl])

  content = {'title': title, 
             'subhead': subhead, 
             'places': places
             }
  
  return content

def categorizeLinks(url, links, all_articles = [], article_urls = [], tag = ''):
  types = ['/news/','/economy/','/features/']
  
  for link in links:
    d = link.split('/')
    try:
      article_date = datetime.date(int(d[2]), int(d[3]), int(d[4]))
    except:
      continue
    
    if len(link) > 11 and article_date == datetime.date.today():
      
      for a_type in types:
        if link[:len(a_type)] == a_type and link not in article_urls:
          print(link)
          try: 
            content = getArticleContent(url, link)
          except:
            print('(skipping)')
            break
          
          content['date'] = article_date
          content['type'] = a_type
          content['url'] = url[:-1] + link
          content['tag'] = tag
            
          all_articles.append(content)
          article_urls.append(link)

  return all_articles, article_urls


def getLinks(url):
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')

  links = []
  for link in soup.findAll('a'):
      links.append(link.get('href'))
  
  print('found all links for ' + url + '\n')
  return links


def exportLongFormat(all_articles):
  long_table = []
  j = 1
  for at in all_articles:
    i = 1
    for cntry in at['places']:
      lt_entry = {'url': at['url'],
                  'type': at['type'],
                  'tag': at['tag'],
                  'title': at['title'], 
                  'subhead': at['subhead'], 
                  'country': cntry, 
                  'date': at['date'],
                  'authors':'',
                  'source': 'Al Jazeera'
                  }
      i = i + 1
      long_table.append(lt_entry)
    j = j + 1
  
  article_data = pd.DataFrame.from_dict(long_table)
  countries.rename(columns = {'country':'code','name':'country'}, inplace = True) 
  df= pd.merge(article_data, countries, on='country', how='left')
      
  with open('news_data.csv', 'a') as f:
    df.to_csv(f, header=False, index = False)
    
  print('\nExported to news_data.csv')


def main():
  base_url = 'https://www.aljazeera.com'
  urls = [
          {'url':'/investigations/', 'tag':''},
          {'url':'/tag/climate/', 'tag':'Climate'},
          {'url':'/tag/science-and-technology/', 'tag':'Science'},
          {'url':'/sports/', 'tag':'Sports'},
          {'url':'/', 'tag':''},
          {'url':'/investigations/', 'tag':''},
          {'url':'/middle-east/', 'tag':''},
          {'url':'/africa/', 'tag':''},
          {'url':'/asia/', 'tag':''},
          {'url':'/us-canada/', 'tag':''},
          {'url':'/latin-america/', 'tag':''},
          {'url':'/europe/', 'tag':''},
          {'url':'/asia-pacific/', 'tag':''}
          ]
  all_articles = []
  article_urls = []
  for url in urls:
    print('\nStarting scrape for ' + base_url + url['url'])
    
    links = getLinks(base_url + url['url'])
  
    all_articles, article_urls = categorizeLinks(base_url + url['url'], 
                                                 links, 
                                                 all_articles, 
                                                 article_urls, 
                                                 url['tag'])
  
  exportLongFormat(all_articles)
  
  

if __name__ == '__main__':
  
  countries = pd.read_csv('countries.csv', header=0, engine='python')
  
  all_articles = main()

