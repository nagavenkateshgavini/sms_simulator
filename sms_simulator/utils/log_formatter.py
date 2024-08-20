import json
import logging


class JsonFormatter(logging.Formatter):
    """Custom logging formatter to output log messages in JSON format."""
    def format(self, record):
        log_message = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'message': record.getMessage()
        }
        return json.dumps(log_message)
