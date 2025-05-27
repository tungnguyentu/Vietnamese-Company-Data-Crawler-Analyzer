from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver
import threading

client = MongoClient('mongodb://localhost:27017/')
db = client['companies']
data_col = db['info']

def extract_emails_from_page(url):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        driver = webdriver.Chrome(options=options)

        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        company_info = {"url": url}

        for ultag in soup.find_all('ul', {'class': 'hsct'}):
            for litag in ultag.find_all('li'):
                company_name = litag.find('h1')
                if company_name:
                    company_info["Tên công ty"] = company_name.text.strip()

                content = litag.text.strip().split(":", 1)
                if len(content) > 1:
                    title = content[0]
                    value = content[1].strip()
                    if title in ["Mã số thuế", "Email", "Điện thoại", "Website"]:
                        company_info[title] = value

        if company_info:
            data_col.update_one({"url": url}, {"$set": company_info}, upsert=True)
            driver.quit()
            return 1
        else:
            driver.quit()
            return 0
    except Exception as e:
        print(f"An error occurred while accessing {url}: {e}")
        return None

def process_links(links):
    for link in links:
        print(f"Processing link: {link}")
        extract_emails_from_page(link)


def main():
    links = db['links'].distinct('link')
    num_threads = 5
    chunk_size = len(links) // num_threads
    threads = []

    for i in range(num_threads):
        start_index = i * chunk_size
        end_index = (i + 1) * chunk_size if i < num_threads - 1 else len(links)
        thread = threading.Thread(target=process_links, args=(links[start_index:end_index],))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("All threads finished.")

if __name__ == "__main__":
    main()
