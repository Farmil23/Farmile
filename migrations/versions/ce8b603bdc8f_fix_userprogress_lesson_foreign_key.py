"""Fix UserProgress lesson foreign key

Revision ID: ce8b603bdc8f
Revises: ec4b60358701
Create Date: 2025-09-02 14:13:08.824377

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce8b603bdc8f'
down_revision = 'ec4b60358701'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user_progress', schema=None) as batch_op:
        batch_op.add_column(sa.Column('lesson_id', sa.Integer(), nullable=False))
        # Beri nama constraint secara eksplisit
        batch_op.create_foreign_key(
            'fk_userprogress_lesson',  # <- nama unik constraint
            'lesson', 
            ['lesson_id'], 
            ['id']
        )

def downgrade():
    with op.batch_alter_table('user_progress', schema=None) as batch_op:
        # Gunakan nama constraint yang sama saat drop
        batch_op.drop_constraint('fk_userprogress_lesson', type_='foreignkey')
        batch_op.drop_column('lesson_id')

