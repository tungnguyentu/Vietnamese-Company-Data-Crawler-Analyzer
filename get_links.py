import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from urllib.parse import unquote
from pymongo import InsertOne

client = MongoClient('mongodb://localhost:27017/')
db = client['companies']
link_col = db['links']

def get_soup(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')

def get_google_search_links(query, page):
    url = f"https://www.google.com/search?q={query}&start={(page)*10}"
    try:
        soup = get_soup(url)
        urls = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('/url?'):
                start_index = href.find('url=') + 4
                end_index = href.find('&', start_index)
                url = unquote(href[start_index:end_index])
            else:
                url = href
            if url.startswith('https://hosocongty.vn'):
                urls.append(url)
        return urls
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def get_next_page_url(query, page=1):
    return f"https://www.google.com/search?q={query}&start={(page)*10}"

def save_links_to_mongodb(links):
    if links:
        bulk_operations = []
        for link in links:
            existing_doc = link_col.find_one({"link": link})
            if not existing_doc:
                bulk_operations.append(InsertOne({'link': link}))
        if bulk_operations:
            link_col.bulk_write(bulk_operations, ordered=False)
            print("New links saved to MongoDB.")
        else:
            print("No new links to save.")
    else:
        print("No links to save.")

query = 'site:hosocongty.vn+"gmail.com"'
page = 1

while True:
    links = get_google_search_links(query, page)
    if links:
        save_links_to_mongodb(links)
        page += 1
    else:
        print("No more search results.")
        break
