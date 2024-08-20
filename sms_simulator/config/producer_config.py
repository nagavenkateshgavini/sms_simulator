from .base import Config


class ProducerConfig(Config):

    @property
    def rabbitmq_host(self):
        return self.get_property("RABBITMQ_HOST")

    @property
    def queue_name(self):
        return self.get_property("QUEUE_NAME")


producer_config = ProducerConfig()
