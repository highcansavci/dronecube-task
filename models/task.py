from sqlalchemy.orm import Mapped

from config.config import Config
from dataclasses import dataclass

from models.image import Image
from serialization.serialization import Serializer
from datetime import datetime, timezone, timedelta


@dataclass
class Task(Config.db.Model, Serializer):
    id: int
    title: str
    date: datetime
    completed: bool
    drone_id: int
    images: Mapped[list["Image"]]

    id = Config.db.Column(Config.db.Integer(), primary_key=True)
    title = Config.db.Column(Config.db.String(50), nullable=False)
    date = Config.db.Column(Config.db.DateTime(timezone=True), default=datetime.now(tz=timezone(timedelta(hours=Config.UTC))), nullable=False)
    completed = Config.db.Column(Config.db.Boolean(), default=False, nullable=False)
    drone_id = Config.db.Column(Config.db.Integer(), Config.db.ForeignKey('drones.id', ondelete="CASCADE"),
                                nullable=False)
    images = Config.db.relationship("Image", backref="task", lazy="dynamic", cascade="all, delete")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"< Task id: {self.id} - {self.title}>"

    def serialize(self):
        task_serialized = Serializer.serialize(self)
        del task_serialized["images"]
        return task_serialized
