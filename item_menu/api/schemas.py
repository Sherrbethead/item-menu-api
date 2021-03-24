"""
Схемы для запросов
"""
import typing
from graphene import Node, NonNull, List, Argument, ID
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql import ResolveInfo

from item_menu.api.connections import ItemConnection
from item_menu.api.filters import ItemFilter
from item_menu.database.models import ItemModel, RootModel, ExecutionTypeModel


class ItemNode(SQLAlchemyObjectType):
    """
    Схема запросов пунктов
    """
    id = ID(required=True, description='Уникальный идентификатор пункта')
    children = List(
        lambda: NonNull(ItemNode),
        filters=Argument(ItemFilter, description='Фильтры пунктов'),
        description='Пункты меню, начиная со второго уровня'
    )

    class Meta:
        model = ItemModel
        description = 'Пункты меню первого уровня'
        interfaces = (Node,)
        connection_class = ItemConnection

    async def resolve_children(self, info: ResolveInfo, **kwargs) -> typing.List[ItemModel]:
        approved_children = self.children

        # фильтр пунктов, начиная со второго уровня
        filters = kwargs.get('filters', {})
        # фильтр по пунктам, к которым предоставлены права доступа
        if 'permission_filter' in info.context:
            filters.update(permission=info.context['permission_filter'])
        if filters:
            item_filter = ItemFilter(approved_children, filters)
            approved_children = await item_filter.filter_items()

        return sorted(approved_children, key=lambda x: x.sorted_id)  # сортировка по порядковому ID


class Root(SQLAlchemyObjectType):
    """
   Схема запроса ID корневого пункта
   """
    class Meta:
        model = RootModel
        description = 'Корневой пункт'


class ExecutionType(SQLAlchemyObjectType):
    """
   Схема запроса запускаемых типов
   """
    class Meta:
        model = ExecutionTypeModel
        description = 'Запускаемый тип'
