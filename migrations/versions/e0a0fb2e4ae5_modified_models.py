"""Modified models

Revision ID: e0a0fb2e4ae5
Revises: a0a5f2c3a345
Create Date: 2022-06-14 14:59:28.309787

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0a0fb2e4ae5'
down_revision = 'a0a5f2c3a345'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('file_name', sa.String(), nullable=True))
    op.drop_column('posts', 'file_path')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('file_path', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('posts', 'file_name')
    # ### end Alembic commands ###
