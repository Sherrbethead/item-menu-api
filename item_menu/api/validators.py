"""
Валидаторы данных мутаций
"""
from typing import Union, List

from graphql import GraphQLError
from typing_extensions import NoReturn

from item_menu.api.filters import ItemFilter
from item_menu.database.models import ItemModel, ExecutionTypeModel


async def validate_create_item(parent_item: ItemModel):
    """
    Валидация при создании пункта
    @param parent_item: родительский пункт
    """
    if not parent_item:
        raise GraphQLError('Введен родительский ID несуществующей пункта')
    if not parent_item.id:
        raise GraphQLError('Нельзя создавать пункт первого уровня')


async def validate_empty_name(name: str, full_name: str = None, for_item: bool = True):
    """
    Валидация имени и полного имени сущности
    @param name: имя сущности
    @param full_name: полное имя сущности
    @param for_item: флаг цели валидации (для пункта или нет)
    """
    if for_item:
        if not name or full_name == '':
            raise GraphQLError('Наименование и полное наименование пункта не могут быть пустыми')
    else:
        if not name:
            raise ValueError('Наименование запускаемого типа не может быть пустым')


async def validate_sorted_id(one_level_items_count: int, sorted_id: int):
    """
    Валидация порядка сортировка
    @param one_level_items_count: количество пунктов на одном уровне
    @param sorted_id: ID порядка сортировки
    """
    if not one_level_items_count and sorted_id:
        raise GraphQLError('Для данного уровня пунктов допустимо только одно значение, равное 0')
    if sorted_id < 0 or sorted_id > one_level_items_count:
        raise GraphQLError(
            'Для данного уровня пунктов допустим порядок сортировки от 0 до {} включительно'.format(
                one_level_items_count
            )
        )


async def validate_existed_execution_type(execution_type: ExecutionTypeModel,
                                          for_item: bool = True) -> Union[int, NoReturn]:
    """
    Валидация наличия запускаемого типа и присвоение ID по имени типа для мутаций пунктов
    @param execution_type: запускаемый тип
    @param for_item: флаг цели валидации (для пункта или нет)
    @return: ID запускаемого типа (опционально)
    """
    if for_item:
        if not execution_type:
            raise GraphQLError('Введен несуществующий запускаемый тип')
        return execution_type.id
    else:
        raise GraphQLError('Введен ID несуществующего запускаемого типа')


async def validate_not_existed_execution_type(execution_type: ExecutionTypeModel):
    """
    Валидация отсутствия запускаемого типа с заданным именем
    @param execution_type: запускаемый тип
    """
    if execution_type:
        raise GraphQLError('Запускаемый тип с таким наименованием уже существует')


async def validate_update_item(item: ItemModel, name: str, full_name: str, sorted_id: int):
    """
    Валидация наличия пункта при ее изменении и наличия прав на ее изменение
    @param item: пункт
    @param name: имя пункта
    @param full_name: полное имя пункта
    @param sorted_id: ID порядка сортировки
    """
    if not item:
        raise GraphQLError('Введен ID несуществующей пункта')
    if not item.id:
        raise GraphQLError('Нельзя изменять данные корневой пункта')
    if (name is not None or full_name is not None) and not item.parent_id:
        raise GraphQLError('Нельзя изменять наименование и полное наименование пункта первого уровня')
    if sorted_id is not None and not item.parent_id:
        raise GraphQLError('Нельзя изменять порядок сортировки пункта первого уровня')


async def validate_delete_item(item: ItemModel):
    """
    Валидация наличия пункта при ее удалении и наличия прав на ее удаление
    @param item: пункт
    """
    if not item:
        raise GraphQLError('Введен ID несуществующей пункта')
    if not item.id:
        raise GraphQLError('Нельзя удалять корневой пункт')
    if not item.parent_id:
        raise GraphQLError('Нельзя удалять пункт первого уровня')


async def validate_existed_paragraph(items: List[ItemModel], paragraph_value: Union[int, str]):
    """
    Валидация наличия пункта с заданным в значении префиксе
    @param items: список пунктов
    @param paragraph_value: численное значение префикса пункта
    """
    item_filter = ItemFilter(items, {'paragraph': paragraph_value})
    items = await item_filter.filter_items()
    if not items:
        raise GraphQLError('Пунктов {}.xx.xx не существует'.format(paragraph_value))
