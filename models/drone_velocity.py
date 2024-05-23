from dataclasses import dataclass
from sqlalchemy import TypeDecorator, String

from serialization.serialization import Serializer


@dataclass
class Velocity(Serializer):
    velocity_x: float
    velocity_y: float
    velocity_z: float

    def serialize(self):
        velocity_serialized = Serializer.serialize_base(self)
        return velocity_serialized


class VelocityType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            # Convert your Position object to a database-friendly form
            return f"{value.velocity_x},{value.velocity_y},{value.velocity_z}"
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            # Convert the database value back to a Position object
            velocity_x, velocity_y, velocity_z = map(float, value.split(','))
            return Velocity(velocity_x, velocity_y, velocity_z)
        return value
