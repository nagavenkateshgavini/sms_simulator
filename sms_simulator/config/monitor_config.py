from .base import Config


class MonitorConfig(Config):

    @property
    def redis_host(self):
        return self.get_property("REDIS_HOST")

    @property
    def monitor_update_interval(self):
        return int(self.get_property("MONITOR_UPDATE_INTERVAL"))


monitor_config = MonitorConfig()
