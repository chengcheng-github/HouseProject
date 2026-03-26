"""initial migration

Revision ID: 0001
Revises: 
Create Date: 2026-03-25 17:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建用户表
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('nickname', sa.String(length=100), nullable=True),
        sa.Column('avatar', sa.String(length=500), nullable=True),
        sa.Column('role', sa.Enum('ADMIN', 'USER', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    
    # 创建房屋表
    op.create_table('houses',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('area', sa.Float(), nullable=False),
        sa.Column('rooms', sa.Integer(), nullable=False),
        sa.Column('address', sa.String(length=500), nullable=False),
        sa.Column('district', sa.String(length=100), nullable=True),
        sa.Column('max_visits_per_day', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('0', '1', '2', name='housestatus'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_houses_district'), 'houses', ['district'], unique=False)
    op.create_index(op.f('ix_houses_id'), 'houses', ['id'], unique=False)
    
    # 创建房屋图片表
    op.create_table('house_images',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('house_id', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['house_id'], ['houses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_house_images_id'), 'house_images', ['id'], unique=False)
    
    # 创建配置表
    op.create_table('configs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_index(op.f('ix_configs_id'), 'configs', ['id'], unique=False)
    
    # 创建统计表
    op.create_table('statistics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_registrations', sa.Integer(), nullable=False),
        sa.Column('house_publications', sa.Integer(), nullable=False),
        sa.Column('page_views', sa.Integer(), nullable=False),
        sa.Column('unique_visitors', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('date')
    )
    op.create_index(op.f('ix_statistics_id'), 'statistics', ['id'], unique=False)
    
    # 创建房屋参观预约表
    op.create_table('house_visits',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('house_id', sa.Integer(), nullable=False),
        sa.Column('visitor_name', sa.String(length=100), nullable=False),
        sa.Column('visitor_phone', sa.String(length=20), nullable=False),
        sa.Column('visit_date', sa.Date(), nullable=False),
        sa.Column('visit_time_slot', sa.Enum('morning', 'afternoon', name='visittimeslot'), nullable=False),
        sa.Column('status', sa.Enum('0', '1', '2', name='visitstatus'), nullable=False),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['house_id'], ['houses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_house_visits_id'), 'house_visits', ['id'], unique=False)
    op.create_index(op.f('ix_house_visits_visit_date'), 'house_visits', ['visit_date'], unique=False)


def downgrade() -> None:
    # 删除表
    op.drop_index(op.f('ix_house_visits_visit_date'), table_name='house_visits')
    op.drop_index(op.f('ix_house_visits_id'), table_name='house_visits')
    op.drop_table('house_visits')
    
    op.drop_index(op.f('ix_statistics_id'), table_name='statistics')
    op.drop_table('statistics')
    
    op.drop_index(op.f('ix_configs_id'), table_name='configs')
    op.drop_table('configs')
    
    op.drop_index(op.f('ix_house_images_id'), table_name='house_images')
    op.drop_table('house_images')
    
    op.drop_index(op.f('ix_houses_id'), table_name='houses')
    op.drop_index(op.f('ix_houses_district'), table_name='houses')
    op.drop_table('houses')
    
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    
    # 删除枚举类型
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS housestatus")
    op.execute("DROP TYPE IF EXISTS visittimeslot")
    op.execute("DROP TYPE IF EXISTS visitstatus")