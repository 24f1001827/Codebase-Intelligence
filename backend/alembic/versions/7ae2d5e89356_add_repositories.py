"""add repositories

Revision ID: 7ae2d5e89356
Revises: f3784f4a7b7e
Create Date: 2026-09-18 01:14:12.356081

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7ae2d5e89356"
down_revision: Union[str, Sequence[str], None] = "f3784f4a7b7e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create repositories table.
    op.create_table(
        "repositories",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("source_type", sa.String(), nullable=False),
        sa.Column("source_url", sa.String(), nullable=True),
        sa.Column("local_path", sa.String(), nullable=False),
        sa.Column("current_commit", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_repositories_name",
        "repositories",
        ["name"],
        unique=False,
    )

    op.create_index(
        "ix_repositories_source_type",
        "repositories",
        ["source_type"],
        unique=False,
    )

    # 2. Add repository_id temporarily as nullable.
    op.add_column(
        "code_units",
        sa.Column(
            "repository_id",
            sa.String(),
            nullable=True,
        ),
    )

    # 3. Copy existing repositories into the new table.
    #
    # Existing code_units.repository contains the local repository path.
    # Each distinct path becomes one RepositoryRecord.
    connection = op.get_bind()

    repositories = connection.execute(
        sa.text(
            """
            SELECT DISTINCT repository
            FROM code_units
            WHERE repository IS NOT NULL
            """
        )
    ).fetchall()

    for (repository_path,) in repositories:
        repository_id = f"local:{repository_path}"

        repository_name = repository_path.replace("\\", "/").rstrip("/").split("/")[-1]

        connection.execute(
            sa.text(
                """
                INSERT INTO repositories (
                    id,
                    name,
                    source_type,
                    source_url,
                    local_path,
                    current_commit,
                    created_at,
                    updated_at
                )
                VALUES (
                    :id,
                    :name,
                    :source_type,
                    :source_url,
                    :local_path,
                    :current_commit,
                    NOW(),
                    NOW()
                )
                """
            ),
            {
                "id": repository_id,
                "name": repository_name,
                "source_type": "local",
                "source_url": None,
                "local_path": repository_path,
                "current_commit": None,
            },
        )

    # 4. Connect every existing CodeUnit to its Repository.
    connection.execute(
        sa.text(
            """
            UPDATE code_units
            SET repository_id = 'local:' || repository
            """
        )
    )

    # 5. repository_id can now safely become NOT NULL.
    op.alter_column(
        "code_units",
        "repository_id",
        existing_type=sa.String(),
        nullable=False,
    )

    # 6. Replace the old repository index.
    op.drop_index(
        "ix_code_units_repository",
        table_name="code_units",
    )

    op.create_index(
        "ix_code_units_repository_id",
        "code_units",
        ["repository_id"],
        unique=False,
    )

    # 7. Add the foreign key now that all rows have valid IDs.
    op.create_foreign_key(
        "fk_code_units_repository_id",
        "code_units",
        "repositories",
        ["repository_id"],
        ["id"],
    )

    # 8. The old path-based repository column is no longer needed.
    op.drop_column(
        "code_units",
        "repository",
    )


def downgrade() -> None:
    # Re-create the old repository column.
    op.add_column(
        "code_units",
        sa.Column(
            "repository",
            sa.String(),
            nullable=True,
        ),
    )

    # Restore repository paths from the Repository table.
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            UPDATE code_units cu
            SET repository = r.local_path
            FROM repositories r
            WHERE cu.repository_id = r.id
            """
        )
    )

    op.alter_column(
        "code_units",
        "repository",
        existing_type=sa.String(),
        nullable=False,
    )

    op.drop_constraint(
        "fk_code_units_repository_id",
        "code_units",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_code_units_repository_id",
        table_name="code_units",
    )

    op.create_index(
        "ix_code_units_repository",
        "code_units",
        ["repository"],
        unique=False,
    )

    op.drop_column(
        "code_units",
        "repository_id",
    )

    op.drop_index(
        "ix_repositories_source_type",
        table_name="repositories",
    )

    op.drop_index(
        "ix_repositories_name",
        table_name="repositories",
    )

    op.drop_table("repositories")