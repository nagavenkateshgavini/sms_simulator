# sender.py
import pika
import json
import random
import time
import os

# Get environment variables for RabbitMQ configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
QUEUE_NAME = os.getenv('RABBITMQ_QUEUE', 'sms_queue')


def send_message(ch, method, properties, body):
    message_data = json.loads(body)
    phone_number = message_data['phone_number']
    message = message_data['message']

    # Simulate sending time
    time.sleep(random.expovariate(1.0 / 2))  # Adjustable mean time

    if random.random() < 0.1:  # Adjustable failure rate
        print(f"Failed to send message to {phone_number}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    else:
        print(f"Successfully sent message to {phone_number}")
        ch.basic_ack(delivery_tag=method.delivery_tag)


def start_sender():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    # Declare the queue
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=send_message)

    print("Sender is waiting for messages...")
    channel.start_consuming()


if __name__ == "__main__":
    start_sender()
