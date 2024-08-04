# DATASCRAPE-Web-Crawler-for-Data-Extraction-and-Storage

Web Crawler Application README

Overview

This repository contains two Python scripts: producer.py and consumer.py, which work together to create a simple web crawling application. The application allows users to input a URL and a crawl depth to search for specific keywords on web pages.

producer.py: This script is responsible for sending crawl requests to the RabbitMQ server, specifying the URL and crawl depth. It uses the pika library to communicate with the message queue.

consumer.py: This script listens for crawl requests on the RabbitMQ server, performs web crawling based on the received requests, and saves the results in an Excel file. It utilizes libraries such as requests, BeautifulSoup, pandas, and mysql.connector for web crawling, data processing, and database connectivity.

Prerequisites
Before running the web crawler application, ensure that you have the following prerequisites installed:

Python 3.x
RabbitMQ Server
Required Python packages (pika, requests, BeautifulSoup, pandas, mysql.connector)
You can install the Python packages using pip:

pip install pika requests beautifulsoup4 pandas mysql-connector-python


Usage
Start the RabbitMQ server and ensure it's running.

Run the consumer.py script to listen for crawl requests and perform web crawling:

python consumer.py
This script will continuously listen for crawl requests and execute crawls based on the received requests.

Run the producer.py script to send crawl requests:

python producer.py
You will be prompted to enter the URL and crawl depth for the web crawl. The script will send a crawl request to the consumer.py script via RabbitMQ.

Wait for the crawling to complete. The consumer.py script will print progress messages and save the results in an Excel file with a unique name based on the crawl request.

Configuration
producer.py assumes that the RabbitMQ server is running locally. You can modify the connection parameters in this script if the server is hosted elsewhere.

The database connection details (MySQL) in consumer.py are configured for a local MySQL server. Update the host, user, password, and database fields in the get_keywords_from_db() function to match your MySQL setup.

Notes
The web crawler in consumer.py is a basic example and may need additional customization to suit your specific requirements.

The application is designed for educational purposes and may require further enhancements for production use.
