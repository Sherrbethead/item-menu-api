"""Init functions

Revision ID: 377bed6b7ee5
Revises: a97adcfa1f14

"""
from alembic import op

revision = '377bed6b7ee5'
down_revision = 'a97adcfa1f14'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        create or replace function public.full_name_add()
         returns trigger
         language plpgsql
        as $function$
        begin	
            if new.full_name is null then
                new.full_name := new.name;
                return new;
            end if;
            return new;
        end;
        $function$;
    """)
    op.execute("""
        create or replace function public.sorted_id_increment()
         returns trigger
         language plpgsql
        as $function$
        declare 
            max_id int8;
            parent int8;
        begin
            if new.sorted_id is null then
                select into parent
                    parent_id
                from public.item
                where id = new.parent_id;
                
                if new.parent_id is not null and parent is not null then
                    select into max_id
                        max(sorted_id)
                    from public.item
                    where parent_id = new.parent_id;
                end if;	
                
                if max_id is null then
                    new.sorted_id := 0;
                else
                    new.sorted_id := max_id + 1;
                end if;
            end if;
            return new;
        end;
        $function$;
    """)


def downgrade():
    op.execute('drop function if exists public.sorted_id_increment()')
    op.execute('drop function if exists public.full_name_add()')
