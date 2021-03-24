"""Init triggers

Revision ID: 364d9ba8bacd
Revises: 377bed6b7ee5

"""
from alembic import op

revision = '364d9ba8bacd'
down_revision = '377bed6b7ee5'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        create trigger auto_add_full_name before
        insert
            on
            public.item for each row execute function full_name_add()
    """)
    op.execute("""
        create trigger auto_increment_sorted_id before
        insert
            on
            public.item for each row execute function sorted_id_increment()
    """)


def downgrade():
    op.execute('drop trigger if exists auto_increment_sorted_id on public.item')
    op.execute('drop trigger if exists auto_add_full_name on public.item')
