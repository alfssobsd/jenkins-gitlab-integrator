"""create events table

Revision ID: 987bb2a53069
Revises:
Create Date: 2017-06-26 13:18:36.723933

"""
from alembic import op
import sqlalchemy as sa
import enum

# revision identifiers, used by Alembic.
revision = '987bb2a53069'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table( 'delayed_tasks',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('task_status', sa.String(32), nullable=False),
        sa.Column('task_type', sa.String(32), nullable=False),
        sa.Column('group', sa.String(32), nullable=False),
        sa.Column('job_name', sa.String(32), nullable=False),
        sa.Column('gitlab_project_id', sa.Integer, nullable=True),
        sa.Column('gitlab_merge_id', sa.Integer, nullable=True),
        sa.Column('gitlab_merge_comment_id', sa.Integer, nullable=True),
        sa.Column('repo_remote_url', sa.String(512), nullable=True),
        sa.Column('sha1', sa.String(40), nullable=False),
        sa.Column('branch', sa.String(256), nullable=False),
        sa.Column('counter_attempts', sa.Integer, nullable=False, default=0),
        sa.Column('uniq_md5sum', sa.String(32), nullable=False),
    )
    op.create_index('delayed_tasks_unq_index', 'delayed_tasks', ['uniq_md5sum'], unique=True)

def downgrade():
    op.drop_table('delayed_tasks')
