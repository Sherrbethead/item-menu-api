"""
Утилиты для запросов
"""
from typing import List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from item_menu.database.models import ItemModel


async def get_user_items(session: Session, user_permissions, root_id: int) -> List[int]:
    """
    Получение имен всех пунктов от конечного уровня дерева к корневому
    @param session: сессия базы данных
    @param user_permissions: список наименований конечных пунктов, к которым нужно предоставить доступ
    @param root_id: корневой ID всех пунктов
    @return: список ID всех пунктов, к которым предоставлен доступ
    """
    # все доступные конечные пункты
    leaf_user_items = session.query(ItemModel).filter(or_(*[
        ItemModel.name.contains(name) for name in user_permissions
    ])).all()

    allowed_items = []
    for item in leaf_user_items:
        allowed_items.append(item.id)
        item_parent = item.parent
        # проход по дереву снизу вверх
        # обрываем цикл, если дошли до корневого ID либо если имя пункта уже находится в списке
        while item_parent.id != root_id and item_parent.id not in allowed_items:
            allowed_items.append(item_parent.id)
            item_parent = item_parent.parent
    return allowed_items
