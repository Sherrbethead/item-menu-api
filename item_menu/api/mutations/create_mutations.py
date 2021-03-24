"""
Мутации на добавлении данных
"""

from graphene import Mutation, Int, String, Boolean
from sqlalchemy.orm import Session

from item_menu.api.logging import query_log
from item_menu.api.validators import (
    validate_create_item, validate_empty_name, validate_sorted_id,
    validate_existed_execution_type, validate_not_existed_execution_type
)
from item_menu.database.models import ItemModel, ExecutionTypeModel
from item_menu.api.schemas import ItemNode, ExecutionType
from item_menu.database.utils import db_session_query


class CreateItem(Mutation):
    """
    Добавление пункта
    """
    class Arguments:
        parent_id = Int(required=True, description='ID родительского пункта')
        sorted_id = Int(description='ID для сортировки на одном уровне')
        name = String(required=True, description='Наименование пункта')
        full_name = String(description='Полное наименование пункта')
        key = String(description='Ключ запускаемого типа')
        exec_type = String(description='Запускаемый тип')
        visible = Boolean(description='Видимость пункта в меню')

    Output = ItemNode

    @staticmethod
    @query_log
    @db_session_query('add')
    async def mutate(_info, session: Session, **kwargs) -> ItemModel:
        # валидация родительского пункта
        parent_id = kwargs.get('parent_id')
        parent_item_query = session.query(ItemModel).filter_by(id=parent_id)
        await validate_create_item(parent_item_query.first())

        # валидация отсутствия имени
        await validate_empty_name(kwargs.get('name'), kwargs.get('full_name'))

        # валидация порядка сортировки
        sorted_id = kwargs.get('sorted_id')
        if sorted_id is not None:
            # получение пунктов меню одного уровня
            one_level_items_query = session.query(ItemModel).filter_by(parent_id=parent_id)
            one_level_items = one_level_items_query.all()

            await validate_sorted_id(len(one_level_items), sorted_id)

            # сдвиг вперед порядка сортировки для пунктов меню одного уровня
            for one_level_item in one_level_items:
                if sorted_id <= one_level_item.sorted_id:
                    one_level_item.sorted_id += 1

        # валидация запускаемого типа
        if kwargs.get('exec_type') is not None:
            exec_type = kwargs.pop('exec_type')
            execution_type_query = session.query(ExecutionTypeModel).filter_by(name=exec_type)
            # присвоение ID по имени типа
            kwargs['exec_type_id'] = await validate_existed_execution_type(execution_type_query.first())

        return ItemModel(**kwargs)


class CreateExecutionType(Mutation):
    """
    Добавление запускаемого типа
    """
    class Arguments:
        name = String(required=True, description='Наименование запускаемого типа')

    Output = ExecutionType

    @staticmethod
    @query_log
    @db_session_query('add')
    async def mutate(_info, session: Session, name: str) -> ExecutionTypeModel:
        # валидация отсутствия имени
        await validate_empty_name(name, for_item=False)

        # валидация имени
        execution_type_query = session.query(ExecutionTypeModel).filter_by(name=name)
        await validate_not_existed_execution_type(execution_type_query.first())

        return ExecutionTypeModel(name=name)
