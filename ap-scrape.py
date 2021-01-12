import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
from datetime import datetime
os.chdir('C:\\Developer\\News Mapping')


# TODO: primary vs secondary connections
# TODO: add authors somehow

def checkLocations(p):
  # return [w for w in countries.name if re.search(r'\b{}\b'.format(re.escape(w)), p)]
  p = [w for w in countries.name if p.find(w) > -1]
  if 'U.S.' in p:
    p[p.index('U.S.')] = 'United States'
  return list(set(p))

def getArticleContent(base_url, article_url):
    
  res = requests.get(base_url + article_url)
  soup = BeautifulSoup(res.text, 'html.parser')
  
  article_date = soup.find(class_=re.compile('Component-timestamp*')).text
  article_date = datetime.strptime(article_date[:-4], "%B %d, %Y").date()
  if article_date == datetime.date.today():
    raise ValueError('Was not from today')
  
  header = soup.find(class_=re.compile('Component-headline*')) 
  title = header.h1.text
  
  authors = soup.find(class_=re.compile('Component-signature*')).span.text
  authors = authors.replace('and ','').replace('By ','').split(', ')
  

  
  body = soup.find(class_='Article')
  places = []
  for p in body.find_all('p'):
    new_places = checkLocations(p.text)
    for pl in new_places:
      if pl not in places:
        places.extend([pl])
        
  
    
  content = {'title': title, 
             'subhead': '', 
             'places': places,
             'authors': authors,
             'date': article_date
             }
  
  return content

def categorizeLinks(url, links, all_articles = [], article_urls = [], tag = ''):
  
  for link in links:
    if link not in article_urls:
      print(link)
      try: 
        content = getArticleContent(url, link)
      except:
        print('(skipping)')
        continue

      content['url'] = url + link
      content['tag'] = tag
          
      all_articles.append(content)
      article_urls.append(link)

  return all_articles, article_urls


def getLinks(url):
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')

  links = []
  for link in soup.findAll('a'):
    l = link.get('href')
    if (l is not None and l[:9] == '/article/'):
      links.append(l)
  
  print('found all links for ' + url + '\n')
  return links


def exportLongFormat(all_articles):
  long_table = []
  for at in all_articles:
    for cntry in at['places']:
      lt_entry = {'url': at['url'],
                  'authors': at['authors'],
                  'tag': at['tag'],
                  'title': at['title'], 
                  'type': '',
                  'subhead': at['subhead'], 
                  'country': cntry, 
                  'date': at['date'],
                  'source': 'AP News'
                  }
      long_table.append(lt_entry)
  
  article_data = pd.DataFrame.from_dict(long_table)
  countries.rename(columns = {'country':'code','name':'country'}, inplace = True) 
  df= pd.merge(article_data, countries, on='country', how='left')
      
  with open('news_data.csv', 'a') as f:
    df.to_csv(f, header = False, index = False)
    
  print('\nExported to news_data.csv')


def main():
  base_url = 'https://www.apnews.com'
  urls = [
          {'url':'/', 'tag':''},
          {'url':'/hub/sports', 'tag':'Sports'},
          {'url':'/hub/entertainment', 'tag':'Entertainment'},
          {'url':'/hub/travel', 'tag':'Travel'},
          {'url':'/hub/technology', 'tag':'Science'},
          {'url':'/hub/business', 'tag':'Economy'},
          {'url':'/hub/health', 'tag':'Science'},
          {'url':'/hub/science', 'tag':'Science'},
          {'url':'/hub/international-news', 'tag':''},
          {'url':'/hub/religion', 'tag':''}
          ]
  all_articles = []
  article_urls = []
  for url in urls:
    print('\nStarting scrape for ' + base_url + url['url'])
    
    links = getLinks(base_url + url['url'])
  
    all_articles, article_urls = categorizeLinks(base_url, 
                                                 links, 
                                                 all_articles, 
                                                 article_urls, 
                                                 url['tag'])
  
  exportLongFormat(all_articles)
  
  

if __name__ == '__main__':
  
  countries = pd.read_csv('countries.csv', header=0, engine='python')
  
  all_articles = main()

