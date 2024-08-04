import requests
from bs4 import BeautifulSoup
import mysql.connector
import pika

# MySQL setup for crawl_requests database
crawl_db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="keshav",
    database="web_crawler"
)
crawl_db_cursor = crawl_db_connection.cursor()

# MySQL setup for bad_hits database
bad_hits_db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="keshav",
    database="badword"
)
bad_hits_db_cursor = bad_hits_db_connection.cursor()

# RabbitMQ setup
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare a queue named 'crawl_requests'
channel.queue_declare(queue='crawl_requests', durable=True)

def create_crawl_request(url, depth, keywords):
    # Create a new crawl request in the crawl_requests database
    crawl_db_cursor.execute("""
        INSERT INTO crawl_requests (start_url, crawl_depth, keywords, start_date, progress)
        VALUES (%s, %s, %s, NOW(), 0)
    """, (url, depth, ','.join(keywords)))

    crawl_db_connection.commit()

    # Retrieve the ID of the newly created crawl request
    crawl_db_cursor.execute("SELECT LAST_INSERT_ID()")
    crawl_request_id = crawl_db_cursor.fetchone()[0]

    # Create a new crawl request message
    request_data = {
        "crawl_request_id": crawl_request_id,
        "start_url": url,
        "crawl_depth": depth,
        "keywords": keywords,
    }

    # Send the crawl request to the 'crawl_requests' queue
    channel.basic_publish(
        exchange='',
        routing_key='crawl_requests',
        body=str(request_data),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make the message persistent
        )
    )

    return crawl_request_id

def update_crawl_progress(crawl_request_id, progress):
    # Update the progress of a crawl request
    crawl_db_cursor.execute("""
        UPDATE crawl_requests
        SET progress = %s
        WHERE id = %s
    """, (progress, crawl_request_id))

    crawl_db_connection.commit()

def get_crawl_progress(crawl_request_id):
    # Retrieve the progress of a crawl request
    crawl_db_cursor.execute("""
        SELECT progress FROM crawl_requests WHERE id = %s
    """, (crawl_request_id,))

    result = crawl_db_cursor.fetchone()

    return result[0] if result else 0

def complete_crawl(crawl_request_id):
    # Mark a crawl request as completed
    crawl_db_cursor.execute("""
        UPDATE crawl_requests
        SET end_date = NOW()
        WHERE id = %s
    """, (crawl_request_id,))

    crawl_db_connection.commit()

def check_bad_hits(phrase):
    # Check if a phrase is in the new_table in the bad_hits database
    bad_hits_db_cursor.execute("""
        SELECT COUNT(*) FROM new_table WHERE word = %s
    """, (phrase,))

    result = bad_hits_db_cursor.fetchone()

    return result[0] > 0

def crawl_website(url, depth, keywords):
    # Create a new crawl request
    crawl_request_id = create_crawl_request(url, depth, keywords)

    # Perform initial crawl
    crawl_page(url, depth, keywords, set(), crawl_request_id)

    # Mark crawl as completed
    complete_crawl(crawl_request_id)

def crawl_page(url, depth, keywords, visited, crawl_request_id):
    if depth == 0 or url in visited:
        return

    # Update the progress of the crawl request
    current_progress = get_crawl_progress(crawl_request_id)
    update_crawl_progress(crawl_request_id, current_progress + 1)

    print(f"Crawling: {url}")

    # Send a request to the URL
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Process the page content
    process_page(url, soup, keywords, crawl_request_id)

    # Extract links from the page
    links = soup.find_all('a', href=True)
    for link in links:
        next_url = link['href']
        crawl_page(next_url, depth - 1, keywords, visited.union({url}), crawl_request_id)

def process_page(url, soup, keywords, crawl_request_id):
    # Extract and process text content from the page
    page_text = soup.get_text()

    # Check for keyword hits
    for keyword in keywords:
        if keyword.lower() in page_text.lower():
            # Check if it's a bad hit
            if not check_bad_hits(keyword):
                print(f"Good Keyword '{keyword}' found on {url}")
            else:
                print(f"Bad Keyword '{keyword}' found on {url}")

# Close the RabbitMQ connection
connection.close()

# Close the database connections after the script completes
crawl_db_cursor.close()
crawl_db_connection.close()

bad_hits_db_cursor.close()
bad_hits_db_connection.close()