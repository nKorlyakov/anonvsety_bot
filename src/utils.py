# Файл для утилитарных функций
from datetime import datetime
from database_worker import User, Admin


def register_user(session, logger, user_info) -> None:
    '''
    Функция регистриурет нового пользователя если такого нет в базе данных
    session - экземпляр бд сессии
    logger - экземпляр класса CustomLogger для логирования
    user_info - message.from_user из aiogram
    '''
    if session.query(User).filter_by(telegram_id=user_info.id).one_or_none() is None:
        user = User(first_name=user_info.first_name, \
                    last_name=user_info.last_name, \
                    username=user_info.username, \
                    telegram_id=user_info.id,
                    creation_date=datetime.now()
                    )
        session.add(user)
        session.commit()
        logger.send_to_file(f'New user - {user_info.id}', 'INFO')


def is_admin_mode(session, telegram_id: int) -> bool:
    '''
    Функция возвращает является ли пользователь админом
    '''
    if session.query(Admin).filter_by(telegram_id=telegram_id).one_or_none():
        return True
    return False
        