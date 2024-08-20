import os

from dotenv import load_dotenv

load_dotenv()

config = {
    "RABBITMQ_HOST": "",
    "REDIS_HOST": "",
    "QUEUE_NAME": "",
    "MONITOR_UPDATE_INTERVAL": "",
    "MEAN_PROCESSING_TIME": "",
    "FAILURE_RATE": ""
}

# Use the config properties if it is defined in env variables
config = {key: os.environ[key] if key in os.environ.keys() else val for key, val in config.items()}


class Config(object):
    def __init__(self):
        self._config = config

    def get_property(self, key):
        return self._config.get(key)
