from .base import Config


class SenderConfig(Config):

    @property
    def rabbitmq_host(self):
        return self.get_property("RABBITMQ_HOST")

    @property
    def redis_host(self):
        return self.get_property("REDIS_HOST")

    @property
    def queue_name(self):
        return self.get_property("QUEUE_NAME")

    @property
    def mean_processing_time(self):
        return int(self.get_property("MEAN_PROCESSING_TIME"))

    @property
    def failure_rate(self):
        return float(self.get_property("FAILURE_RATE"))


sender_config = SenderConfig()
