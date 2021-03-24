import logging.config
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import cpu_count

from aiohttp import web
from aiohttp.web_urldispatcher import Resource
from aiohttp_cors import ResourceOptions, setup
from dynaconf.utils.boxing import DynaBox
from dynaconf.utils.files import read_file

from item_menu.api import get_view
from item_menu.auth_service import AuthService
from item_menu.database import Database


class Application:
    """
    Класс работы с приложением
    """
    def __init__(self, config: DynaBox):
        """
        Инициализация класса приложения
        @param config: данные конфигурации приложения
        """
        self._config = config
        self._config.VERSION = read_file(config.VERSION_PATH)
        self._db = Database(self._config.POSTGRES)
        self._auth = AuthService(self._config.SERVICES.auth)
        self._app = web.Application(middlewares=[self._auth.login_required, self._db.db_session])

    async def _init_pool_thread(self, app: web.Application):
        """
        Добавление в приложение данных по многопоточным воркерам и событийному циклу
        @param app: приложение
        """
        self._app['pool_thread'] = ThreadPoolExecutor(max_workers=cpu_count())
        self._app['loop'] = app._loop

    async def _init_logging(self, _app):
        """
        Инициализация логирования
        """
        logging.getLogger(__name__)
        logging.config.dictConfig(self._config.LOGGING)
        logging.info('Starting service v.{}'.format(self._config.VERSION))

    async def _init_db(self, _app):
        """
        Инициализация связи с базой данных
        """
        await self._db.initialize()

    async def _init_auth(self, _app):
        """
        Инициализация связи с сервисом авторизации
        """
        await self._auth.initialize()

    async def _setup_cors(self, resource: Resource):
        """
        Настройка CORS
        @param resource: сущность в таблице роута
        """
        cors = setup(self._app, defaults={
            '*': ResourceOptions(
                allow_credentials=True,
                expose_headers='*',
                allow_headers='*',
                allow_methods='*'
            )
        })
        cors.add(resource)

    async def _init_views(self, app: web.Application):
        """
        Инициализация роутов, CORS-прав и доступных CRUD-методов
        @param app: приложение
        """
        # добавление контекста данных для view
        app.context = {
            'config': self._config,
            'db': self._db,
            'auth': self._auth
        }
        # инициализация GraphQL-view
        gqil_view = get_view(context=app.context, graphiql=True)
        gql_view = get_view(context=app.context, graphiql=False)

        # добавление graphiql-endpoint
        app.router.add_route('*', '/graphiql', gqil_view, name='graphiql')
        resource = self._app.router.add_resource('/graphql')
        # добавление CORS-прав
        await self._setup_cors(resource)
        # добавление всех доступных методов
        resource.add_route('*', gql_view)

    async def _close_db(self, _app):
        """
        Закрытие связи с базой данных
        """
        await self._db.close()

    def init_app(self) -> web.Application:
        """
        Инициализация расширений приложения
        @return: приложение
        """
        self._app.on_startup.extend([
            self._init_pool_thread,
            self._init_logging,
            self._init_db,
            self._init_auth,
            self._init_views
        ])
        self._app.on_cleanup.append(self._close_db)
        return self._app
