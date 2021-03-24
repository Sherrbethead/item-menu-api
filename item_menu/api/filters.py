"""
Фильтры для запросов
"""
from typing import Callable, Union, List, Dict

from graphene import Boolean, String, Int, InputObjectType

from item_menu.database.models import ItemModel


class ItemFilter(InputObjectType):
    """
    Фильтр пунктов
    """
    id = Int(description='ID пункта')
    visible = Boolean(description='Видимость пункта')
    name_like = String(descriprion='Частичное совпадение в имени пункта')
    paragraph = Int(descriprion='Номер пункта (только для первого уровня)')

    def __init__(self, items: List[ItemModel], filters: Dict[str, Union[int, str, bool]]):
        """
        Инициализация класса фильтра пунктов меню
        @param items: список всех пунктов
        @param filters: словарь вида поле для фильтрации - значение для фильтрации
        """
        super().__init__()
        self.items = items
        self.filters = filters

    @staticmethod
    def _resolve_filter(field: str, value: Union[int, str, bool]) -> Callable[[int, str, bool], bool]:
        """
        Получение lambda-функции, содержащей условия для выполнения фильтрации
        @param field: поле, по которому производится фильтрация
        @param value: введенное значение для поля фильтрации
        @return: функция с условием для фильтрации
        """
        fields_filter_dict = {
            'id': lambda x: x.id == value,
            'visible': lambda x: x.visible == value,
            'name_like': lambda x: (value.strip().lower() in x.name.lower()) or
                                   (value.strip().lower() in x.full_name.lower()),
            'paragraph': lambda x: x.name.startswith('{}.'.format(value)),
            'permission': lambda x: x.id in value
        }
        return fields_filter_dict.get(field)

    async def filter_items(self) -> List[ItemModel]:
        """
        Фильтрация пунктов по всем признакам, описанным в введенных в фильтрах данных
        @return: список отфильтрованных пунктов
        """
        items = self.items
        for filter_name, value in self.filters.items():
            items = filter(self._resolve_filter(filter_name, value), items)
        return list(items)
