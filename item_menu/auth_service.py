import logging
from asyncio import get_event_loop
from typing import Any, Optional, Dict, List

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from dynaconf.utils.boxing import DynaBox
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from graphql import ResolveInfo
from graphql.language.ast import Document


class AuthService:
    """
    Класс для работы с сервисом авторизации
    """
    def __init__(self, config: DynaBox):
        """
        Инициализация класса сервиса авторизации
        @param config: данные конфигурации сервиса
        """
        self._config = config
        self.enabled = self._config.enabled
        self._client = None

    @property
    def url(self) -> str:
        """
        URL сервиса
        @return: строка URL сервиса
        """
        params = {
            'host': self._config.host,
            'port': self._config.port,
            'endpoint': self._config.endpoint
        }
        return 'http://{host}:{port}/{endpoint}'.format(**params)

    @staticmethod
    def _get_ping_query() -> Document:
        """
        Базовый запрос для получения прав
        @return: запрос версии сервиса
        """
        query = gql(
            '''
                query {
                  authVersion
                }
            '''
        )
        return query

    async def initialize(self):
        """
        Информация об интеграционном состоянии сервиса
        """
        auth_status = {
            True: 'enabled',
            False: 'disabled'
        }
        logging.info('Auth service integration is {}'.format(auth_status.get(self.enabled)))
        if self.enabled:
            await self._execute(for_init=True)

    async def _execute(self, header: str = None,
                       query: Document = None,
                       for_init: bool = False) -> Optional[Dict[str, str]]:
        """
        Асинхронный обработчик запроса к сервису
        @param header: заголовок
        @param query: запрос
        @param for_init: флаг цели запроса (для инициализации связи или нет)
        @return: ответ сервиса (опционально)
        """
        self._client = Client(transport=RequestsHTTPTransport(self.url, headers={'Authorization': header}))
        try:
            # в случае отсутствия запроса использует запрос по дефолту
            query = query if query else self._get_ping_query
            result = await get_event_loop().run_in_executor(None, self._client.execute, query)
            if not for_init:
                query_name = query.definitions[0].name.value or \
                             query.definitions[0].selection_set.selections[0].name.value
                logging.debug('Successfully resolved auth service query: {}'.format(query_name))
        except IOError as ioe:
            if for_init and ioe.response.status_code in (200, 401):
                logging.info('Successfully connected to auth service')
                return None
            logging.error('Connection to auth service is failed: {}'.format(ioe))
            raise ioe

        return result

    async def user_perms(self, info: ResolveInfo) -> List[str]:
        """
        Запрос прав к сервису
        @param info: данные запроса
        @return: список пунктов, к которым открыт доступ
        """
        user_permissions = []
        if self.enabled:
            # получение bearer-токена для заголовка
            header = info.context['request'].bearer_token
            query = gql(
                '''
                    query {
                      allUserPerms(filters: {isAllow: true}) {
                        permission {
                          name
                        }
                      }
                    }
                '''
            )
            result = await self._execute(header, query)
            user_permissions = [
                perm_dict.get('permission', {}).get('name') for perm_dict in result.get('allUserPerms', [])
            ]
        return user_permissions

    @web.middleware
    async def login_required(self, request: Request, handler: Any) -> Response:
        """
        Запрос токена при необходимости авторизации
        @param request: данные запроса
        @param handler: данные обработчика
        @return: ответ после прохождения авторизации
        """
        if self.enabled:
            # получение аккаунта из заголовка
            header = request.headers.get('Authorization')

            result = await self._execute(header)
            # в случае успеха присвоение bearer-токена
            request.bearer_token = 'Bearer {}'.format(result.get('access_token'))

        response = await handler(request)
        return response
