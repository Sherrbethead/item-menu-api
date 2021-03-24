from graphene import ObjectType

from .update_mutations import UpdateRoot, UpdateItem, UpdateExecutionType
from .create_mutations import CreateItem, CreateExecutionType
from .delete_mutations import DeleteItem, DeleteExecutionType


class Mutation(ObjectType):
    """
    Мутации для изменения данных в базе данных
    """

    update_root_item = UpdateRoot.Field(
        description='Обновить корневой пункт'
    )
    update_item = UpdateItem.Field(
        description='Обновить пункт'
    )
    update_execution_type = UpdateExecutionType.Field(
        description='Обновить запускаемый тип'
    )
    create_item = CreateItem.Field(
        description='Добавить пункт'
    )
    create_execution_type = CreateExecutionType.Field(
        description='Добавить запускаемый тип'
    )
    delete_item = DeleteItem.Field(
        description='Удалить пункт'
    )
    delete_execution_type = DeleteExecutionType.Field(
        description='Удалить запускаемый тип'
    )
