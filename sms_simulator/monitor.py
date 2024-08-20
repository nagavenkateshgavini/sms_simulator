import time
import logging
import os
import redis
import argparse
from stats import Stats
from config.monitor_config import monitor_config
from utils.log_formatter import JsonFormatter


class Monitor:
    def __init__(self, redis_host: str, update_interval: int) -> None:
        self.redis_client = redis.Redis(host=redis_host, port=6379, db=0)
        self.update_interval = update_interval

        # Configure logging
        self.logger = logging.getLogger('Monitor')
        self.logger.setLevel(logging.INFO)

        # Stream handler for console output
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(JsonFormatter())
        # TODO: add file handler
        self.logger.addHandler(stream_handler)

    def get_stats(self) -> Stats:
        try:
            current_stats_data = self.redis_client.get('sms_simulator_stats')
            return Stats.from_redis(current_stats_data)
        except redis.ConnectionError as e:
            self.logger.error(f"Error connecting to Redis: {e}")
            return Stats()

    def run(self) -> None:
        while True:
            stats = self.get_stats()
            if stats:
                self.logger.info(f"Messages sent: {stats.sent}, Messages failed: {stats.failed}, "
                                 f"Avg. time per message: {stats.avg_time:.2f} sec")
            time.sleep(self.update_interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor the SMS sender stats from Redis.")
    parser.add_argument('--update-interval', type=int, default=int(os.getenv('MONITOR_UPDATE_INTERVAL', 5)),
                        help="Interval (in seconds) for updating stats (default: 5 seconds)")
    args = parser.parse_args()

    monitor = Monitor(redis_host=monitor_config.redis_host, update_interval=monitor_config.monitor_update_interval)
    monitor.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Monitor process interrupted by user.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
