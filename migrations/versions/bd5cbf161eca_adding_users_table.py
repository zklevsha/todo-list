"""Adding Users table

Revision ID: bd5cbf161eca
Revises: 30383fbd4ed1
Create Date: 2024-08-19 14:10:05.131263

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session
from models import User
from settings import admin_username, admin_email, admin_password, admin_hashed_password
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'bd5cbf161eca'
down_revision = '30383fbd4ed1'
branch_labels = None
depends_on = None

user_role_enum = sa.Enum('ADMIN', 'USER', name='userrole'
    ).with_variant(postgresql.ENUM(
        'ADMIN',
        'USER',
        name='userrole',
        create_type=True,
        ), "postgresql",
    )

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=30), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('creation_date', sa.Integer(), nullable=False),
    sa.Column('timezone', sa.String(length=30), nullable=False),
    sa.Column('role', user_role_enum, nullable=False),
    sa.Column('daily_reminder', sa.Boolean, nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('todos', 'title',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('todos', 'description',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('todos', 'is_finished',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.create_unique_constraint(None, 'users', ['username'])
    op.create_unique_constraint(None, 'users', ['email'])
    # ### end Alembic commands ###
    bind = op.get_bind()
    session = Session(bind=bind)

    # Creating the default admin user
    admin_user = User(
        username=admin_username,
        email=admin_email,
        password=admin_hashed_password, 
        role='ADMIN',
        timezone='UTC',
        creation_date=(int(datetime.now().timestamp()))
    )

    session.add(admin_user)
    session.commit()
    print(f"\nAdmin password is: {admin_password}\n")

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('todos', 'is_finished',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('todos', 'description',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('todos', 'title',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_table('users')
    user_role_enum.drop(op.get_bind(), checkfirst=True)
    # ### end Alembic commands ###
