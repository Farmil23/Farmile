"""Add lesson_id to user_progress and fix relations

Revision ID: 79849550c1be
Revises: ce8b603bdc8f
Create Date: 2025-09-02 14:32:21.851525

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79849550c1be'
down_revision = 'ce8b603bdc8f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user_progress', schema=None) as batch_op:
        batch_op.add_column(sa.Column('lesson_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            'fk_userprogress_lesson',
            'lesson',
            ['lesson_id'],
            ['id']
        )


def downgrade():
    pass
