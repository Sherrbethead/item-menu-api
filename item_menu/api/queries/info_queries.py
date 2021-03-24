"""
Информационные запросы
"""
from graphene import ObjectType, String
from graphql import ResolveInfo

from item_menu.api.logging import query_log


class ServiceQuery(ObjectType):
    """
    Сервисный запрос
    """
    item_menu_version = String(description='Версия сервиса пунктов меню')

    @staticmethod
    @query_log
    async def resolve_item_menu_version(_, info: ResolveInfo) -> str:
        return info.context['config'].VERSION
