"""
Утилиты для работы с базой данных
"""
from functools import wraps
from typing import Any, Callable

from graphql import ResolveInfo
from sqlalchemy.orm import Session


def db_session_query(method: str = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Обработчик-декоратор для манипуляций с данными в базе данных с помощью сессии
    @param method: тип оборачиваемого запроса (добавление данных либо всё остальное)
    @return: ответ обернутого запроса
    """
    if method and method != 'add':
        raise ValueError('Unexpected argument for DB session query decorator')

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(_, info: ResolveInfo, *args, **kwargs) -> Any:
            session = info.context['session']  # type: Session
            output = await func(info, session, *args, **kwargs)

            # если запрос на добавление данных, то добавляем к сессии выходные данных запроса
            if method == 'add':
                session.add(output)
                session.commit()
                output = session.query(output.__class__).filter_by(id=output.id).first()

            return output
        return wrapper
    return decorator
