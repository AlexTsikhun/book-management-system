"""Make Str Enum

Revision ID: 35a1ba9b0db6
Revises: 13954310c1fd
Create Date: 2025-04-04 19:55:20.490668

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "35a1ba9b0db6"
down_revision: Union[str, None] = "13954310c1fd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute("ALTER TABLE books ALTER COLUMN genre DROP DEFAULT")
    op.execute("ALTER TABLE books ALTER COLUMN genre TYPE genre USING genre::text::genre")

    op.execute("ALTER TABLE books ALTER COLUMN genre SET DEFAULT 'Fiction'")
    op.execute("DROP TYPE IF EXISTS genreenum")


def downgrade() -> None:
    """Downgrade schema."""

    op.execute("ALTER TABLE books ALTER COLUMN genre DROP DEFAULT")
    op.execute("CREATE TYPE genreenum AS ENUM ('Fiction', 'Non-Fiction', 'Science', 'History')")

    op.execute("ALTER TABLE books ALTER COLUMN genre TYPE genreenum USING genre::text::genreenum")
    op.execute("ALTER TABLE books ALTER COLUMN genre SET DEFAULT 'Fiction'")
