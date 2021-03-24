"""
Определение связующих схемы GraphQL и создание точки входа отображения API
"""
from typing import Dict, Any

from aiohttp_graphql import GraphQLView
from graphene import Schema
from graphql.execution.executors.asyncio import AsyncioExecutor

from item_menu.api.queries import Query
from item_menu.api.mutations import Mutation


schema = Schema(query=Query, mutation=Mutation)


def get_view(context: Dict[str, Any], graphiql: bool) -> GraphQLView:
    """
    Получение GraphQl-view
    @param context: контекстный словарь вэб-сессии
    @param graphiql: флаг подключения GraphiQL-клиента
    @return: объект GraphQL-view
    """
    view = GraphQLView(
        schema=schema,
        context=context,
        executor=AsyncioExecutor(),
        graphiql=graphiql,
        enable_async=True
    )

    return view
