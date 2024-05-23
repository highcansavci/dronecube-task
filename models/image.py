from sqlalchemy.orm import Mapped

from config.config import Config
from datetime import datetime
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

from serialization.serialization import Serializer


@dataclass
class Image(Config.db.Model, Serializer):
    id: int
    task_id: int
    date: datetime

    id = Config.db.Column(Config.db.Integer(), primary_key=True)
    date = Config.db.Column(Config.db.DateTime(timezone=True), default=datetime.now(tz=timezone(timedelta(hours=Config.UTC))), nullable=False)
    filename = Config.db.Column(Config.db.String(50), nullable=False)
    task_id = Config.db.Column(Config.db.Integer(), Config.db.ForeignKey('task.id', ondelete="CASCADE"), nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"< Image taken: {self.id} - {self.date}>"

    def serialize(self):
        image_serialized = Serializer.serialize(self)
        del image_serialized["task"]
        return image_serialized
