"""empty message

Revision ID: 345700da477e
Revises: ef241588f170
Create Date: 2025-06-05 22:12:17.112774

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '345700da477e'
down_revision = 'ef241588f170'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sleep_schedule', schema=None) as batch_op:
        batch_op.add_column(sa.Column('enabled', sa.Boolean(), nullable=True))
        
    op.execute("UPDATE sleep_schedule SET enabled = true")
    op.alter_column('sleep_schedule', 'enabled', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sleep_schedule', schema=None) as batch_op:
        batch_op.drop_column('enabled')

    # ### end Alembic commands ###
