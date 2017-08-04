"""create jenkins_job_groups table

Revision ID: 73c55823bd16
Revises: 987bb2a53069
Create Date: 2017-08-04 14:25:17.525066

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73c55823bd16'
down_revision = '987bb2a53069'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table( 'jenkins_groups',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('jobs_base_path', sa.String(512), nullable=False)
    )
    op.create_index('jenkins_groups_unq_index', 'jenkins_groups', ['name'], unique=True)

    op.create_table( 'jenkins_jobs',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('jenkins_group_id', sa.Integer, nullable=False),
        sa.Column('jenkins_job_perent_id', sa.Integer, nullable=True),
        sa.Column('gitlab_project_id', sa.Integer, nullable=False)
    )
    op.create_index('jenkins_jobs_unq_index', 'jenkins_jobs', ['name', 'jenkins_group_id'], unique=True)

def downgrade():
    op.drop_table('jenkins_jobs')
    op.drop_table('jenkins_groups')
