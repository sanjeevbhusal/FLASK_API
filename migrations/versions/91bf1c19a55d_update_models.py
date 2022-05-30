"""Update Models

Revision ID: 91bf1c19a55d
Revises: d6a143871eff
Create Date: 2022-05-30 20:54:28.882617

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91bf1c19a55d'
down_revision = 'd6a143871eff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_verified')
    # ### end Alembic commands ###
