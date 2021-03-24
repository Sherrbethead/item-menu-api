"""
Запросы для получения данных из базы данных
"""
import typing
from graphene import ObjectType, List, Argument, NonNull, Int
from graphene_sqlalchemy import SQLAlchemyConnectionField
from graphql import ResolveInfo
from sqlalchemy.orm import Session

from item_menu.api.filters import ItemFilter
from item_menu.api.logging import query_log
from item_menu.api.orders import ItemSort
from item_menu.api.utils import get_user_items
from item_menu.auth_service import AuthService
from item_menu.database.models import ItemModel, RootModel, ExecutionTypeModel
from item_menu.api.schemas import ItemNode, ExecutionType
from item_menu.database.sortings import get_paragraph_order, sort_by
from item_menu.database.utils import db_session_query


ROOT_ID = 0  # корневой ID всех пунктов


class ItemQuery(ObjectType):
    """
    Запросы пунктов меню
    """
    user_items = SQLAlchemyConnectionField(
        ItemNode,
        filters=Argument(ItemFilter, description='Фильтры пунктов'),
        description='Перечень всех доступных пользователю пунктов'
    )
    all_items = List(
        NonNull(ItemNode),
        sort=List(NonNull(ItemSort), description='Сортировка пунктов'),
        filters=Argument(ItemFilter, description='Фильтры пунктов'),
        description='Список всех пунктов'
    )

    @staticmethod
    @query_log
    @db_session_query()
    async def resolve_user_items(info: ResolveInfo, session: Session, **kwargs) -> ItemNode:
        auth_service = info.context['auth']  # type: AuthService
        user_permissions = await auth_service.user_perms(info)

        # фильтр по родительскому корневому ID и сортировка по цифровому префиксу имени пункта первого уровня
        items_query = session.query(ItemModel).filter_by(
            parent_id=ROOT_ID
        ).order_by(
            await get_paragraph_order(ItemModel)
        )

        # добавляет фильтр по полученным о сервиса авторизации наименования пунктов,
        # если пользователь ограничен в правах
        if user_permissions:
            info.context['permission_filter'] = await get_user_items(session, user_permissions, ROOT_ID)
            items_query = items_query.filter(ItemModel.id.in_(info.context['permission_filter']))

        items = items_query.all()

        filters = kwargs.get('filters', {})
        # добавляет фильтр по префиксу имени пункта первого уровня, если ID корневого пункта не равно 0
        current_tree_item = session.query(RootModel).first()
        filter_item_id = current_tree_item.item_id
        if filter_item_id:
            filters.update(paragraph=filter_item_id)
        # фильтр пунктов первого уровня
        if filters:
            item_filter = ItemFilter(items, filters)
            items = await item_filter.filter_items()

        return items

    @staticmethod
    @query_log
    @db_session_query()
    async def resolve_all_items(_info, session: Session, **kwargs) -> typing.List[ItemModel]:
        items_query = session.query(ItemModel)

        # сортировка пунктов
        sort = kwargs.get('sort')
        if sort:
            items_query = await sort_by(items_query, sort)

        items = items_query.all()

        # фильтр пунктов
        filters = kwargs.get('filters', {})
        if filters:
            item_filter = ItemFilter(items, filters)
            items = await item_filter.filter_items()

        return items


class RootQuery(ObjectType):
    """
    Запрос ID корневого пункта
    """
    root_item = Int(description='ID корневого пункта')

    @staticmethod
    @query_log
    @db_session_query()
    async def resolve_current_tree_item(_info, session: Session) -> int:
        current_tree_item = session.query(RootModel).first()
        return current_tree_item.item_id


class ExecutionTypeQuery(ObjectType):
    """
    Запрос запускаемых типов
    """
    execution_types = List(NonNull(ExecutionType), description='Перечень запускаемых типов')

    @staticmethod
    @query_log
    @db_session_query()
    async def resolve_execution_types(_info, session: Session) -> typing.List[ExecutionTypeModel]:
        return session.query(ExecutionTypeModel).all()
