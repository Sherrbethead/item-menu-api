"""
Мутации на удаление данных
"""
from typing import Union

from graphene import Mutation, String, ID
from sqlalchemy.orm import Session

from item_menu.api.logging import query_log
from item_menu.api.validators import validate_delete_item, validate_existed_execution_type
from item_menu.database.models import ItemModel, ExecutionTypeModel
from item_menu.database.utils import db_session_query


class DeleteItem(Mutation):
    """
    Удаление пункта
    """
    class Arguments:
        id = ID(required=True, description='ID пункта')

    message = String(required=True)

    @staticmethod
    @query_log
    @db_session_query()
    async def mutate(_info, session: Session, id: Union[int, str]) -> Mutation:
        # валидация наличия пункта
        item_query = session.query(ItemModel).filter_by(id=id)
        item = item_query.first()
        await validate_delete_item(item)

        # сдвиг назад порядка сортировки для пунктов одного уровня
        one_level_items = session.query(ItemModel).filter_by(parent_id=item.parent_id)
        for one_level_item in one_level_items.all():
            if item.sorted_id < one_level_item.sorted_id:
                one_level_item.sorted_id -= 1

        item_name = item.name
        item_query.delete()

        return DeleteItem(
            message='Пункт с ID {item_id} и наименованием «{item_name}» удален'.format(
                item_id=id, item_name=item_name
            )
        )


class DeleteExecutionType(Mutation):
    """
    Удаление запускаемого типа
    """
    class Arguments:
        id = ID(required=True, description='ID запускаемого типа')

    message = String(required=True)

    @staticmethod
    @query_log
    @db_session_query()
    async def mutate(_info, session: Session, id: Union[int, str]) -> Mutation:
        # валидация наличия запускаемого типа
        execution_type_query = session.query(ExecutionTypeModel).filter_by(id=id)
        execution_type = execution_type_query.first()
        await validate_existed_execution_type(execution_type, for_item=False)

        execution_type_name = execution_type.name
        execution_type_query.delete()

        return DeleteExecutionType(
            message='Запускаемый тип с ID {execution_type_id} и наименованием «{execution_type_name}» удалён'.format(
                execution_type_id=id, execution_type_name=execution_type_name
            )
        )
