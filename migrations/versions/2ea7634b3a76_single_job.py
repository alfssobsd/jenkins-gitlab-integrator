"""single job

Revision ID: 2ea7634b3a76
Revises: 73c55823bd16
Create Date: 2017-08-21 13:24:35.422636

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ea7634b3a76'
down_revision = '73c55823bd16'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column( 'jenkins_groups',
        sa.Column('is_pipeline', sa.Boolean(), nullable=False, server_default=sa.schema.DefaultClause("1")),
    )

def downgrade():
    op.drop_column('jenkins_groups', 'is_pipeline')
