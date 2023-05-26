"""Modify column data type

Revision ID: 86d21ece297a
Revises: 
Create Date: 2023-05-24 13:58:22.800541

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86d21ece297a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('trips', schema=None) as batch_op:
        batch_op.alter_column('stops',
               existing_type=sa.VARCHAR(length=140),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('budget',
               existing_type=sa.VARCHAR(length=140),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('timestamp',
               existing_type=sa.DATETIME(),
               type_=sa.String(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('trips', schema=None) as batch_op:
        batch_op.alter_column('timestamp',
               existing_type=sa.String(),
               type_=sa.DATETIME(),
               existing_nullable=True)
        batch_op.alter_column('budget',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(length=140),
               existing_nullable=True)
        batch_op.alter_column('stops',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(length=140),
               existing_nullable=True)

    # ### end Alembic commands ###
