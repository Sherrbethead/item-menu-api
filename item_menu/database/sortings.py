"""
Сортировки для запросов на уровне базы данных
"""
from typing import List

from sqlalchemy import cast, func, String, Integer, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Query
from sqlalchemy.sql.elements import Cast

from item_menu.api.orders import ItemSort
from item_menu.database.models import BaseModel


async def get_paragraph_order(model: BaseModel) -> Cast:
    """
    Сортировка запроса по числовому параграфовидному префиксу наименования
    @param model: модель ORM
    @return: выражение для сортировки по префиксу
    """
    paragraph_order = cast(
        func.string_to_array(
            func.string_to_array(
                model.name, ' ', type_=ARRAY(String)
            )[1], '.'
        ), ARRAY(Integer)
    )
    return paragraph_order


async def sort_by(query: Query, sort: List[ItemSort]) -> Query:
    """
    Сортировка запроса по введенным в правила данным
    @param query: запрос в базу данных
    @param sort: список правил сортировки
    @return: запрос, отсортированный по введенным правилам сортировки
    """
    order = []
    for s in sort:
        sort_fields_and_rules = text('{} {} nulls {}'.format(s.field, s.order, s.nulls))
        order.append(sort_fields_and_rules)
    return query.order_by(*order)
