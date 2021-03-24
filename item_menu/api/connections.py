"""
Connection-классы для схем запросов
"""
from graphene import Connection, Int


class ItemConnection(Connection):
    """
    Connection-класс для запросов пунктов меню
    """
    total_count = Int(description='Количество доступных пунктов меню первого уровня')

    class Meta:
        abstract = True

    @staticmethod
    async def resolve_total_count(root, _info) -> int:
        return len(root.iterable)
