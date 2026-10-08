"""allow anonymous client public keys

Revision ID: 4f3c2a1b0d9e
Revises: d0ed71e09119
Create Date: 2026-09-06
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "4f3c2a1b0d9e"
down_revision: Union[str, Sequence[str], None] = "d0ed71e09119"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "client_public_keys",
        "user_uid",
        existing_type=sa.Uuid(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "client_public_keys",
        "user_uid",
        existing_type=sa.Uuid(),
        nullable=False,
    )
