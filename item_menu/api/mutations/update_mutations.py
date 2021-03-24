"""
Мутации на удаление данных
"""
from typing import Union

import graphene
from graphene import Mutation, Int, String, Boolean, ID
from sqlalchemy.orm import Session

from item_menu.api.logging import query_log
from item_menu.api.schemas import ItemNode, Root, ExecutionType
from item_menu.api.validators import (
    validate_sorted_id, validate_existed_execution_type, validate_empty_name,
    validate_update_item, validate_not_existed_execution_type, validate_existed_paragraph
)
from item_menu.database.models import RootModel, ItemModel, ExecutionTypeModel
from item_menu.database.utils import db_session_query


class UpdateRoot(Mutation):
    """
    Обновление ID корневого пункта
    """
    class Arguments:
        item_id = Int(
            required=True,
            description='''
                Для отображения всех пунктов: id = 0 \n
                Для отображения определенных пунктов №.хх.хх: № префикса пункта
            '''
        )

    Output = Root

    @staticmethod
    @query_log
    @db_session_query()
    async def mutate(_info, session: Session, item_id: Union[int, str]) -> RootModel:
        # валидация наличия пунктов с необходимым префиксом
        if item_id:
            items = session.query(ItemModel).all()
            await validate_existed_paragraph(items, item_id)

        root_item = session.query(RootModel).first()
        root_item.item_id = item_id

        return root_item


class UpdateItem(Mutation):
    """
    Обновление пункта
    """
    class Arguments:
        id = ID(required=True, description='ID пункта')
        sorted_id = Int(description='ID для сортировки на одном уровне')
        name = String(description='Наименование пункта')
        full_name = String(description='Полное наименование пункта')
        key = String(description='Ключ запускаемого типа')
        exec_type = String(description='Запускаемый тип')
        visible = Boolean(description='Видимость пункта в меню')

    Output = ItemNode

    @staticmethod
    @query_log
    @db_session_query()
    async def mutate(_info, session: Session, id: Union[int, str], **kwargs) -> ItemModel:
        item_query = session.query(ItemModel).filter_by(id=id)
        item = item_query.first()

        # валидация наличия пункта и прав на изменения пункта
        name, full_name = kwargs.get('name'), kwargs.get('full_name')
        sorted_id = kwargs.get('sorted_id')
        await validate_update_item(item, name, full_name, sorted_id)
        # валидация отсутствия имени
        await validate_empty_name(name, full_name)

        # валидация порядка сортировки
        sorted_id = kwargs.get('sorted_id')
        if sorted_id is not None:
            # получение пунктов одного уровня
            one_level_items_query = session.query(ItemModel).filter_by(parent_id=item.parent_id)
            one_level_items = one_level_items_query.all()

            await validate_sorted_id(len(one_level_items) - 1, sorted_id)

            # сдвиг вперед и назад порядка сортировки для пунктов одного уровня
            for one_level_item in one_level_items:
                if sorted_id <= one_level_item.sorted_id < item.sorted_id:
                    one_level_item.sorted_id += 1
                elif sorted_id >= one_level_item.sorted_id > item.sorted_id:
                    one_level_item.sorted_id -= 1

        # валидация запускаемого типа
        if kwargs.get('exec_type') is not None:
            exec_type = kwargs.pop('exec_type')
            execution_type_query = session.query(ExecutionTypeModel).filter_by(name=exec_type)
            # присвоение ID по имени типа
            kwargs['exec_type_id'] = await validate_existed_execution_type(execution_type_query.first())

        item_query.update(kwargs)

        return item


class UpdateExecutionType(graphene.Mutation):
    """
    Обновление запускаемого типа
    """
    class Arguments:
        id = ID(required=True, description='ID запускаемого типа')
        name = String(required=True, description='Наименование запускаемого типа')

    Output = ExecutionType

    @staticmethod
    @query_log
    @db_session_query()
    async def mutate(_info, session: Session, id: Union[int, str], **kwargs) -> ExecutionTypeModel:
        # валидация наличия запускаемого типа
        execution_type_query = session.query(ExecutionTypeModel).filter_by(id=id)
        execution_type = execution_type_query.first()
        await validate_existed_execution_type(execution_type, for_item=False)

        # валидация отсутствия имени
        name = kwargs.get('name')
        await validate_empty_name(name, for_item=False)

        # валидация имени
        execution_type_query = session.query(ExecutionTypeModel).filter_by(name=name)
        await validate_not_existed_execution_type(execution_type_query.first())

        execution_type_query.update(kwargs)
        return execution_type
