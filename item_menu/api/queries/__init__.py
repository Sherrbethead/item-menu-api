from .database_queries import ItemQuery, RootQuery, ExecutionTypeQuery
from .info_queries import ServiceQuery


class Query(
    ServiceQuery,
    ExecutionTypeQuery,
    RootQuery,
    ItemQuery
):
    """
    Запросы к сервису
    """
