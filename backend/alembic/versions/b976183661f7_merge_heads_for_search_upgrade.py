"""merge heads for search upgrade

Revision ID: b976183661f7
Revises: 20260504_add_search, 9bc20af3782f, 0001_baseline_platform
Create Date: 2026-05-04 11:04:59.340782

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b976183661f7'
down_revision: Union[str, None] = ('20260504_add_search', '9bc20af3782f', '0001_baseline_platform')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
