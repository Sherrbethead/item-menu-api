"""Create tables

Revision ID: a97adcfa1f14
Revises:

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Sequence
from sqlalchemy.sql.ddl import CreateSequence, DropSequence

revision = 'a97adcfa1f14'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute(CreateSequence(Sequence('exec_type_id_seq')))
    op.execute(CreateSequence(Sequence('item_id_seq')))

    op.create_table('exec_type',
                    sa.Column('id', sa.BigInteger(), server_default=sa.text("nextval('exec_type_id_seq')"),
                              nullable=False, comment='Уникальный идентификатор запускаемого типа'),
                    sa.Column('name', sa.Text(), nullable=False, comment='Наименование запускаемого типа'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name'),
                    schema='public',
                    comment='Запускаемые типы'
                    )
    op.create_table('root',
                    sa.Column('item_id', sa.BigInteger(), nullable=False,
                              comment='Идентификатор корневой пункта для построения дерева'),
                    sa.PrimaryKeyConstraint('item_id'),
                    schema='public',
                    comment='Корень либо маркер для построения дерева меню'
                    )
    op.create_table('item',
                    sa.Column('id', sa.BigInteger(), server_default=sa.text("nextval('item_id_seq')"), nullable=False,
                              comment='Уникальный идентификатор пункта'),
                    sa.Column('parent_id', sa.BigInteger(), nullable=True,
                              comment='Идентификатор родительского пункта'),
                    sa.Column('sorted_id', sa.BigInteger(), nullable=False,
                              comment='Порядок сортировки на одном уровне'),
                    sa.Column('name', sa.Text(), nullable=False, comment='Наименование пункта'),
                    sa.Column('full_name', sa.Text(), nullable=False, comment='Полное наименование пункта'),
                    sa.Column('key', sa.Text(), nullable=True, comment='Ключ запускаемого типа'),
                    sa.Column('exec_type_id', sa.BigInteger(), nullable=True,
                              comment='Идентификатор запускаемого типа'),
                    sa.Column('visible', sa.Boolean(), server_default=sa.text('false'), nullable=False,
                              comment='Видимость пункта в меню'),
                    sa.ForeignKeyConstraint(['exec_type_id'], ['public.exec_type.id'], onupdate='CASCADE'),
                    sa.ForeignKeyConstraint(['parent_id'], ['public.item.id'], onupdate='CASCADE', ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    schema='public',
                    comment='Пункты меню'
                    )


def downgrade():
    op.drop_table('item', schema='public')
    op.drop_table('root', schema='public')
    op.drop_table('exec_type', schema='public')

    op.execute(DropSequence(Sequence('item_id_seq')))
    op.execute(DropSequence(Sequence('exec_type_id_seq')))
