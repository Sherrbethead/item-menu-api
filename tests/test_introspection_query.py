"""
Тест интроспекции
"""
from graphql import introspection_query

from item_menu.api import schema


def test_introspection_query():
    result = schema.execute(introspection_query)
    assert not result.errors
