import argparse
import pika
import json
import random
import string

from config.producer_config import producer_config


class Producer:
    def __init__(self, rabbitmq_host: str, queue_name: str) -> None:
        self.rabbitmq_host = rabbitmq_host
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.connect()
        self.declare_queue()

    def connect(self) -> None:
        """Connect to RabbitMQ and handle connection errors."""
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_host))
            self.channel = self.connection.channel()
            print(f"Connected to RabbitMQ at {self.rabbitmq_host}")
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Failed to connect to RabbitMQ: {e}")
            raise SystemExit(1)  # Exit the script if connection fails

    def declare_queue(self) -> None:
        """Declare the RabbitMQ queue."""
        try:
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            print(f"Queue '{self.queue_name}' declared.")
        except pika.exceptions.AMQPError as e:
            print(f"Failed to declare queue: {e}")
            raise SystemExit(1)

    def produce_messages(self, num_messages: int) -> None:
        """Produce a given number of messages and handle errors."""
        try:
            for i in range(1, num_messages + 1):
                phone_number = f"+{random.randint(1000000000, 9999999999)}"
                message = ''.join(random.choices(string.ascii_letters + string.digits, k=100))
                message_body = json.dumps({"phone_number": phone_number, "message": message})

                # Publish message to the queue with default exchange mechanism
                self.channel.basic_publish(
                    exchange='',
                    routing_key=self.queue_name,
                    body=message_body,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Make the message persistent
                    ))

                if i % 100 == 0:
                    print(f"Produced {i} messages.")

            print(f"Successfully produced {num_messages} messages.")
        except (pika.exceptions.AMQPError, json.JSONDecodeError) as e:
            print(f"Error while producing messages: {e}")
        finally:
            if self.connection:
                self.connection.close()
                print("Connection to RabbitMQ closed.")


def main() -> None:
    """Main function to parse command-line arguments and produce messages."""
    parser = argparse.ArgumentParser(description="Produce SMS messages")
    parser.add_argument('--num-messages', type=int, default=1000,
                        help="Number of messages to produce (default: 1000)")
    args = parser.parse_args()

    rabbitmq_host = producer_config.rabbitmq_host
    queue_name = producer_config.queue_name

    producer = Producer(rabbitmq_host=rabbitmq_host, queue_name=queue_name)
    producer.produce_messages(args.num_messages)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
