import pika
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import pandas as pd
import mysql.connector
import threading
import uuid

def get_keywords_from_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Replace with your MySQL username
            password='82461937Cr7@',  # Replace with your MySQL password
            database='web_crawler'
        )
        cursor = connection.cursor()
        cursor.execute("SELECT keyword FROM keywords")
        keywords = [item[0] for item in cursor.fetchall()]
        cursor.close()
        connection.close()
        return keywords
    except mysql.connector.Error as err:
        print("Error connecting to MySQL:", err)
        return []

def crawl(url, depth, keywords, hits, visited_urls, lock):
    if depth == 0 or url in visited_urls:
        return

    with lock:
        if url in visited_urls:
            return
        visited_urls.add(url)

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text().lower()

        for keyword in keywords:
            lower_keyword = keyword.lower()
            count = text.count(lower_keyword)
            if count > 0:
                with lock:
                    print(f"Keyword '{keyword}' found {count} times at {url}")
                    hits.append({'Keyword': keyword, 'URL': url, 'Count': count})

        for link in soup.find_all('a'):
            href = link.get('href')
            if href and not href.startswith('#'):
                absolute_url = urljoin(url, href)
                if absolute_url not in visited_urls:
                    threading.Thread(target=crawl, args=(absolute_url, depth - 1, keywords, hits, visited_urls, lock)).start()

    except requests.RequestException as e:
        with lock:
            print(f"Failed to crawl {url}: {str(e)}")

def on_request(ch, method, properties, body):
    data = json.loads(body)
    crawl_id = str(uuid.uuid4())

    print(f" [x] Received crawl request (ID: {crawl_id}) for", data['url'])

    keywords = get_keywords_from_db()
    hits = []
    visited_urls = set()
    lock = threading.Lock()

    crawl(data['url'], data['depth'], keywords, hits, visited_urls, lock)

    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
            continue
        t.join()

    if hits:
        excel_file_name = f'keyword_hits_{crawl_id}.xlsx'
        df = pd.DataFrame(hits)
        df.to_excel(excel_file_name, index=False)

    print(f"Crawling completed for request (ID: {crawl_id}):", data['url'])
    ch.basic_ack(delivery_tag=method.delivery_tag)

    # Mark completion for this batch
    mark_consumer_done()

def mark_consumer_done():
    with open('consumer_done.txt', 'w') as f:
        f.write('done')

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='crawl_requests', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='crawl_requests', on_message_callback=on_request)

    print(' [*] Waiting for crawl requests. To exit, press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    main()
