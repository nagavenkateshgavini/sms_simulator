import pika
import json
import random
import time
import redis
import logging
import string
from pika.spec import Basic, BasicProperties

from stats import Stats
from config.sender_config import sender_config
from utils.log_formatter import JsonFormatter


class Sender:
    def __init__(self, rabbitmq_host: str, queue_name: str,
                 redis_host: str, mean_time: float, failure_rate: float) -> None:
        self.rabbitmq_host = rabbitmq_host
        self.queue_name = queue_name
        self.mean_time = mean_time
        self.failure_rate = failure_rate
        self.sender_id = self.generate_sender_id()
        self.redis_key = "sms_simulator_stats"

        # Configure logging
        self.logger = logging.getLogger(self.sender_id)
        self.logger.setLevel(logging.INFO)

        # Stream handler for console output
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(JsonFormatter())
        # TODO: add file handler
        self.logger.addHandler(stream_handler)

        # Connect to Redis
        try:
            self.redis_client = redis.Redis(host=redis_host, port=6379, db=0)
            self.logger.info(f"Connected to Redis at {redis_host}")
        except redis.ConnectionError as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            raise SystemExit(1)

    @staticmethod
    def generate_sender_id() -> str:
        """Generate a random string to uniquely identify the sender."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    def update_stats(self, sent: int, failed: int, time_spent: float) -> None:
        try:
            current_stats_data = self.redis_client.get(self.redis_key)
            stats = Stats.from_redis(current_stats_data)

            stats.update(sent=sent, failed=failed, time_spent=time_spent)
            self.redis_client.set(self.redis_key, stats.to_json())

        except redis.ConnectionError as e:
            self.logger.error(f"Error updating stats in Redis: {e}")

    def send_message(self, ch: pika.adapters.blocking_connection.BlockingChannel,
                     method: Basic.Deliver, properties: BasicProperties, body: bytes) -> None:
        try:
            message_data = json.loads(body)
            phone_number = message_data.get('phone_number')
            message = message_data.get('message')

            start_time = time.time()
            time.sleep(random.expovariate(1 / self.mean_time))

            if random.random() < self.failure_rate:  # Configurable failure rate
                self.logger.warning(f"Failed to send message to {phone_number}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                self.update_stats(0, 1, 0)
            else:
                elapsed_time = time.time() - start_time
                self.logger.info(f"Successfully sent message to {phone_number} in {elapsed_time:.2f} seconds")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                self.update_stats(1, 0, elapsed_time)
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def start(self) -> None:
        """Start the sender using a blocking connection to RabbitMQ."""
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_host))
            channel = connection.channel()

            # Declare the queue
            channel.queue_declare(queue=self.queue_name, durable=True)

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=self.queue_name, on_message_callback=self.send_message)

            self.logger.info("Sender is waiting for messages...")
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as e:
            self.logger.error(f"Error connecting to RabbitMQ: {e}")
            raise SystemExit(1)
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise SystemExit(1)


def main() -> None:
    sender = Sender(
        rabbitmq_host=sender_config.rabbitmq_host,
        queue_name=sender_config.queue_name,
        redis_host=sender_config.redis_host,
        mean_time=sender_config.mean_processing_time,
        failure_rate=sender_config.failure_rate
    )
    sender.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Sender process interrupted by user.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
