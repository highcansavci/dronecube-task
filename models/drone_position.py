from dataclasses import dataclass
from sqlalchemy import TypeDecorator, String

from serialization.serialization import Serializer


@dataclass
class Position(Serializer):
    latitude: float
    longitude: float
    altitude: float

    def serialize(self):
        position_serialized = Serializer.serialize_base(self)
        return position_serialized


class PositionType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            return f"{value.latitude},{value.longitude},{value.altitude}"
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            latitude, longitude, altitude = map(float, value.split(','))
            return Position(latitude, longitude, altitude)
        return value

