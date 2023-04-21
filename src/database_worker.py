# Database worker file
from sqlalchemy import Integer, String, Column, Text, DateTime, BigInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class User(Base):
    '''
    Модель данных для пользователя
    '''
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    username = Column(String(100))
    telegram_id = Column(Integer, nullable=True)
    creation_date = Column(DateTime)
    rating = Column(BigInteger, default=0)


class Message(Base):
    '''
    Модель данных для сообщения
    Сообщения из диалога между двумя пользователей во время чатинга(кроме комманд)
    '''
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer)
    receiver_id = Column(Integer)
    message_text = Column(Text)
    creation_date = Column(DateTime)

class Admin(Base):
    '''
    Модель данных для админов
    Список админов
    '''
    __tablename__ = 'admins'

    telegram_id = Column(Integer, primary_key=True)
    admin_mode = Column(Boolean)
