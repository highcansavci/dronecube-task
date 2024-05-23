import dataclasses

from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from dataclasses import dataclass

from models.drone_position import PositionType
from models.drone_velocity import VelocityType
from sqlalchemy.orm import Mapped
from config.config import Config
from models.task import Task
from serialization.serialization import Serializer


@dataclasses.dataclass
class Users(UserMixin, Config.db.Model):
    __tablename__ = 'users'
    id = Config.db.Column(Config.db.Integer, primary_key=True)
    username = Config.db.Column(Config.db.String(250), unique=True, nullable=False)
    email = Config.db.Column(Config.db.String(50), unique=True, nullable=False)
    password = Config.db.Column(Config.db.String(250), nullable=False)
    drones = Config.db.relationship('Drone', secondary="user_drones", lazy="dynamic", back_populates='users')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def generate_reset_password_token(self):
        serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
        return serializer.dumps(self.email, salt=self.password)

    @staticmethod
    def validate_reset_password_token(token: str, user_id: int):
        user = Config.db.session.get(Users, user_id)
        if user is None:
            print("none1")
            return None
        serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
        try:
            token_user_email = serializer.loads(
                token,
                max_age=Config.RESET_PASS_TOKEN_MAX_AGE,
                salt=user.password
            )
        except (BadSignature, SignatureExpired):
            print("none2")
            return None
        if token_user_email != user.email:
            print("none3")
            return None
        return user


@dataclass
class Drone(Config.db.Model, Serializer):
    id: int
    name: str
    connected: False
    tasks: Mapped[list["Task"]]

    __tablename__ = 'drones'

    id = Config.db.Column(Config.db.Integer(), primary_key=True)
    name = Config.db.Column(Config.db.String(50), nullable=False)
    global_position = Config.db.Column(PositionType, nullable=False)
    home_position = Config.db.Column(PositionType, nullable=False)
    velocity = Config.db.Column(VelocityType, nullable=False)
    connected = Config.db.Column(Config.db.Boolean(), default=False, nullable=False)
    tasks = Config.db.relationship("Task", backref="drone", lazy="dynamic", cascade="all, delete")
    users = Config.db.relationship('Users', secondary="user_drones", lazy="dynamic", back_populates='drones')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"< Drone info: {self.id} - {self.name}>"

    def serialize(self):
        drone_serialized = Serializer.serialize(self)
        del drone_serialized["tasks"]
        del drone_serialized["users"]
        return drone_serialized


user_drones = Config.db.Table(
    "user_drones",
    Config.db.Column("user_id", Config.db.Integer, Config.db.ForeignKey(Users.__tablename__ + ".id")),
    Config.db.Column("drone_id", Config.db.Integer, Config.db.ForeignKey(Drone.__tablename__ + ".id")),
)
