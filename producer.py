import pika
import json
import os
import time

def check_consumer_done():
    return os.path.exists('consumer_done.txt')

def clear_consumer_done():
    if os.path.exists('consumer_done.txt'):
        os.remove('consumer_done.txt')

def send_crawl_request(channel, url, depth):
    message = json.dumps({'url': url, 'depth': depth})
    channel.basic_publish(
        exchange='',
        routing_key='crawl_requests',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
        )
    )
    print("[x] Sent %r" % message)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='crawl_requests', durable=True)

    while True:
        clear_consumer_done()
        url = input("Enter URL to crawl or 'exit' to quit: ")
        if url.lower() == 'exit':
            break
        depth = int(input("Enter depth of crawl: "))
        send_crawl_request(channel, url, depth)

        print("Waiting for the consumer to finish...")
        while not check_consumer_done():
            time.sleep(1)

    connection.close()

if __name__ == "__main__":
    main()
