"""
Migration script to add the user_favorite_extension table.
"""

import logging

from sqlalchemy import Column, ForeignKey, Integer, MetaData, Table, Text

log = logging.getLogger(__name__)
metadata = MetaData()

UserFavoriteExtension_table = Table(
    "user_favorite_extension", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("galaxy_user.id"), index=True),
    Column("value", Text, index=True, unique=True)
)


def upgrade(migrate_engine):
    metadata.bind = migrate_engine
    print(__doc__)
    metadata.reflect()
    try:
        UserFavoriteExtension_table.create()
    except Exception:
        log.exception("Creating user_favorite_extension table failed.")


def downgrade(migrate_engine):
    metadata.bind = migrate_engine
    # Load existing tables
    metadata.reflect()
    try:
        UserFavoriteExtension_table.drop()
    except Exception:
        log.exception("Dropping user_favorite_extension table failed.")