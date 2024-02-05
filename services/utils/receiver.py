import json
import os
import random
import time

import pika
import sys


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    channel.queue_declare(queue='videos', durable=True)
    print(' [*] Waiting for videos. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        data = json.loads(body.decode())
        time.sleep(random.randint(10, 30))
        print("[DONE] ", data["title"])
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='videos', on_message_callback=callback)

    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)