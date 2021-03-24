import logging
from typing import Awaitable, Any, Coroutine

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from async_generator import yield_, async_generator, asynccontextmanager
from dynaconf.utils.boxing import DynaBox
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, Session


class Database:
    """
    Класс для работы с базой данных
    """
    def __init__(self, config: DynaBox):
        """
        Инициализация класса базы данных
        @param config: данные конфигурации базы данных
        """
        self._config = config
        self._engine = None
        self._session = None

    @property
    def url(self) -> str:
        """
        URL сервиса
        @return: строка URL сервиса
        """
        params = {
            'user': self._config.user,
            'password': self._config.password,
            'host': self._config.host,
            'port': self._config.port,
            'name': self._config.database
        }
        return 'postgresql://{user}:{password}@{host}:{port}/{name}'.format(**params)

    async def initialize(self):
        """
        Инициализация связи с базой данных
        """
        logging.info('Connecting to DB {}'.format(self.url))
        self._engine = create_engine(self.url)
        self._session = sessionmaker(bind=self._engine)

        # проверка на наличие базы данных пинг-запросом
        async with self.asessioncontext() as session:
            session.execute('SELECT 1;')
            logging.info('Successfully connected to DB')

    async def _asessioncontext(self):
        """
        Реализация контекстного менеджера сессии базы данных
        """
        session = self._session(expire_on_commit=False)
        try:
            await yield_(session)
            session.commit()
        except OperationalError as oe:
            session.rollback()
            logging.error('DB session error: {}'.format(oe))
            raise oe
        except Exception as e:
            session.rollback()
            logging.error('DB session error: {}'.format(e))
            raise e
        finally:
            session.close()

    @asynccontextmanager
    @async_generator
    async def asessioncontext(self) -> Coroutine[Awaitable[Session], Any, Any]:
        """
        Интерфейс для работы с асинхронным контекстным менеджером сессии базы данных
        @return: контекстный менеджер сессии
        """
        return await self._asessioncontext()

    @web.middleware
    async def db_session(self, request: Request, handler: Any) -> Response:
        """
        Инициализация сессии базы данных перед каждым запросом
        @param request: данные запроса
        @param handler: данные обработчика
        @return: ответ после оборачивания сессией
        """
        async with self.asessioncontext() as request.app.context['session']:
            logging.debug('Session is initialized: {}'.format(request.app.context['session']))
            response = await handler(request)
        return response

    async def close(self):
        """
        Закрытие связи с базой данных
        """
        self._engine.dispose()
        logging.info('DB connection is closed')
