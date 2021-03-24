"""
Модели ORM для связи с базой данных
"""
from sqlalchemy import BigInteger, Column, ForeignKey, Text, Sequence, Boolean, text
from sqlalchemy.orm import relationship, backref

from item_menu.database.models import BaseModel


class ItemModel(BaseModel):
    __tablename__ = 'item'
    __table_args__ = {
        'schema': 'public',
        'comment': 'Пункты меню'
    }

    item_id_seq = Sequence('item_id_seq', metadata=BaseModel.metadata)
    id = Column(
        BigInteger,
        primary_key=True,
        server_default=item_id_seq.next_value(),
        doc='Уникальный идентификатор пункта',
        comment='Уникальный идентификатор пункта'
    )
    parent_id = Column(
        ForeignKey('public.item.id', ondelete='CASCADE', onupdate='CASCADE'),
        doc='Идентификатор родительского пункта',
        comment='Идентификатор родительского пункта'
    )
    sorted_id = Column(
        BigInteger,
        nullable=False,
        doc='Порядок сортировки на одном уровне',
        comment='Порядок сортировки на одном уровне'
    )
    name = Column(
        Text,
        nullable=False,
        doc='Наименование пункта',
        comment='Наименование пункта'
    )
    full_name = Column(
        Text,
        nullable=False,
        doc='Полное наименование пункта',
        comment='Полное наименование пункта'
    )
    key = Column(
        Text,
        doc='Ключ запускаемого типа',
        comment='Ключ запускаемого типа'
    )
    exec_type_id = Column(
        ForeignKey('public.exec_type.id', onupdate='CASCADE'),
        doc='Идентификатор запускаемого типа',
        comment='Идентификатор запускаемого типа'
    )
    visible = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        doc='Видимость пункта в меню',
        comment='Видимость пункта в меню'
    )

    children = relationship(
        'ItemModel',
        backref=backref('parent', remote_side=[id]),
        uselist=True,
        lazy='bulk'
    )
    exec_type = relationship('ExecutionTypeModel', lazy='bulk')


class RootModel(BaseModel):
    __tablename__ = 'root'
    __table_args__ = {
        'schema': 'public',
        'comment': 'Корень либо маркер для построения дерева меню'
    }

    item_id = Column(
        BigInteger,
        primary_key=True,
        doc='Идентификатор корневой пункта для построения дерева',
        comment='Идентификатор корневой пункта для построения дерева'
    )


class ExecutionTypeModel(BaseModel):
    __tablename__ = 'exec_type'
    __table_args__ = {
        'schema': 'public',
        'comment': 'Запускаемые типы'
    }

    exec_type_id_seq = Sequence('exec_type_id_seq', metadata=BaseModel.metadata)
    id = Column(
        BigInteger,
        primary_key=True,
        server_default=exec_type_id_seq.next_value(),
        doc='Уникальный идентификатор запускаемого типа',
        comment='Уникальный идентификатор запускаемого типа'
    )
    name = Column(
        Text,
        unique=True,
        nullable=False,
        doc='Наименование запускаемого типа',
        comment='Наименование запускаемого типа'
    )
