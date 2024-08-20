import json
from dataclasses import dataclass, asdict


@dataclass
class Stats:
    sent: int = 0
    failed: int = 0
    total_time: float = 0.0

    @classmethod
    def from_redis(cls, redis_data: str) -> "Stats":
        """Create a Stats instance from a Redis JSON string."""
        if redis_data:
            data = json.loads(redis_data)
            return cls(
                sent=data.get('sent', 0),
                failed=data.get('failed', 0),
                total_time=data.get('total_time', 0.0)
            )
        return cls()

    def to_json(self) -> str:
        """Convert Stats instance to a JSON string."""
        return json.dumps(asdict(self))

    def update(self, sent: int = 0, failed: int = 0, time_spent: float = 0.0) -> None:
        """Update the stats with new values."""
        self.sent += sent
        self.failed += failed
        self.total_time += time_spent

    @property
    def avg_time(self) -> float:
        """Calculate the average time per message."""
        return self.total_time / self.sent if self.sent > 0 else 0.0
