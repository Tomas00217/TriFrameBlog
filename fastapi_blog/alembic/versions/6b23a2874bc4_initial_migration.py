"""Initial migration

Revision ID: 6b23a2874bc4
Revises: 
Create Date: 2025-03-11 18:23:10.233238

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '6b23a2874bc4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('email_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
    sa.Column('slug', sqlmodel.sql.sqltypes.AutoString(length=60), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('slug')
    )
    op.create_table('blog_post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('content', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('image', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['email_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('blogpost_tag',
    sa.Column('blogpost_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['blogpost_id'], ['blog_post.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.PrimaryKeyConstraint('blogpost_id', 'tag_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('blogpost_tag')
    op.drop_table('blog_post')
    op.drop_table('tag')
    op.drop_table('email_user')
    # ### end Alembic commands ###
