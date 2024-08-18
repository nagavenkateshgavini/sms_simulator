# producer.py
import pika
import json
import random
import string
import sys

RABBITMQ_HOST = 'localhost'  # Use 'localhost' to connect from outside Docker
QUEUE_NAME = 'sms_queue'


def produce_messages(num_messages):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    # Declare the queue
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    for _ in range(num_messages):
        phone_number = f"+{random.randint(1000000000, 9999999999)}"
        message = ''.join(random.choices(string.ascii_letters + string.digits, k=100))
        message_body = json.dumps({"phone_number": phone_number, "message": message})

        # Publish message to the queue
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=message_body,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make the message persistent
            ))
        print(f"Produced message to {phone_number}")

    connection.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python producer.py <num_messages>")
        sys.exit(1)

    num_messages = int(sys.argv[1])
    produce_messages(num_messages)
