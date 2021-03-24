"""
Сортировки и аргументы сортировок для запросов
"""
from graphene import Enum, InputObjectType, Argument


class SortOrderEnum(Enum):
    """
    Порядок сортировки
    """
    ASC = 'asc'
    DESC = 'desc'

    @property
    def description(self) -> str:
        if self == SortOrderEnum.ASC:
            return 'По возрастанию'
        if self == SortOrderEnum.DESC:
            return 'По убыванию'


class SortNullsEnum(Enum):
    """
    Порядок места для null-значений
    """
    LAST = 'last'
    FIRST = 'first'

    @property
    def description(self) -> str:
        if self == SortNullsEnum.LAST:
            return 'Нулевые значения в конце'
        if self == SortNullsEnum.FIRST:
            return 'Нулевые значения в начале'


class ItemSortFieldEnum(Enum):
    """
    Свойство пункта
    """
    ID = 'id'
    NAME = 'name'


class ItemSort(InputObjectType):
    """
    Сортировка пункта
    """
    field = ItemSortFieldEnum(
        required=True,
        description='Свойство пункта, используемое для сортировки'
    )
    order = Argument(
        SortOrderEnum,
        default_value=SortOrderEnum.ASC.value,
        description='Порядок сортировки (по умолчанию ASC)'
    )
    nulls = Argument(
        SortNullsEnum,
        default_value=SortNullsEnum.LAST.value,
        description='Порядок места для null-значений (по умолчанию LAST)'
    )
