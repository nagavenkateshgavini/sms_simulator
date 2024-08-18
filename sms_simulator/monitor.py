import time
import requests
import logging
import os

# Get environment variables for RabbitMQ Management API
RABBITMQ_API_URL = os.getenv('RABBITMQ_API_URL', 'http://localhost:15672/api/queues/%2f/sms_queue')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', '/app/logs/monitor.log')
MONITOR_UPDATE_INTERVAL = 5  # Update every 5 seconds

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    handlers=[logging.FileHandler(LOG_FILE_PATH), logging.StreamHandler()])


def get_queue_stats():
    try:
        response = requests.get(RABBITMQ_API_URL, auth=(RABBITMQ_USER, RABBITMQ_PASSWORD))
        if response.status_code == 200:
            data = response.json()
            messages_ready = data.get('messages_ready', 0)
            messages_unacknowledged = data.get('messages_unacknowledged', 0)
            total_messages = data.get('messages', 0)
            consumers = data.get('consumers', 0)
            return total_messages, messages_ready, messages_unacknowledged, consumers
        else:
            logging.error(f"Failed to fetch RabbitMQ stats: {response.status_code}")
            return None, None, None, None
    except Exception as e:
        logging.error(f"Error fetching RabbitMQ stats: {str(e)}")
        return None, None, None, None


class ProgressMonitor:
    def run(self):
        while True:
            total_messages, messages_ready, messages_unacknowledged, consumers = get_queue_stats()
            if total_messages is not None:
                logging.info(
                    f"Total messages: {total_messages}, Ready: {messages_ready}, Unacknowledged: {messages_unacknowledged}, Consumers: {consumers}")
            else:
                logging.info("Unable to fetch RabbitMQ stats.")

            time.sleep(MONITOR_UPDATE_INTERVAL)


if __name__ == "__main__":
    monitor = ProgressMonitor()
    monitor.run()
