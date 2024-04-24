import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


# REST-сервисы обмениваются информацией в формате json. Научить объекты наших моделей превращаться в словарь, для чего
# надо добавить каждой из моделей метод to_dict. Чтобы не делать руками, воспользуемся модулем SQLAlchemy-serializer.
class Anceta(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'ankets'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')