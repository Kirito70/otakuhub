---
name: db-migrations
description: Create, review, and test an Alembic migration for OtakuHub. Covers new tables, column additions, index changes, and enum types.
---

# Database Migration Skill

## Before Writing Any Migration
1. Read `docs/database-schema.md` — understand the current state
2. Run `alembic heads` — confirm there is only one head revision
3. Identify exactly what change is needed: new table, add column, new index, new enum

## Migration Authoring Steps

### For a New Table
```bash
# 1. Write the SQLAlchemy model in backend/models/
# 2. Import it in backend/models/__init__.py so Alembic sees it
# 3. Generate
alembic revision --autogenerate -m "add_watch_parties_table"
# 4. Review the generated file — fix these common autogenerate gaps:
#    - server_default for uuid_generate_v7() not added → add manually
#    - PostgreSQL ENUM type not created before table → add op.execute("CREATE TYPE...")
#    - GIN indexes not generated → add manually
#    - updated_at onupdate not reflected → add trigger or note
```

### For Adding a Column
```python
def upgrade() -> None:
    op.add_column(
        "user_list_entries",
        sa.Column(
            "repeat_count",
            sa.SmallInteger(),
            nullable=False,
            server_default="0",   # required for existing rows
        ),
    )
    # Add index if this column will be filtered/sorted
    op.create_index("idx_list_entries_repeat", "user_list_entries", ["repeat_count"])

def downgrade() -> None:
    op.drop_index("idx_list_entries_repeat")
    op.drop_column("user_list_entries", "repeat_count")
```

### For a New PostgreSQL ENUM
```python
def upgrade() -> None:
    # Create type BEFORE the table that uses it
    op.execute(
        "CREATE TYPE rsvp_status_enum AS ENUM "
        "('pending', 'attending', 'declined')"
    )
    op.add_column(
        "watch_party_rsvps",
        sa.Column(
            "status",
            postgresql.ENUM(name="rsvp_status_enum", create_type=False),
            nullable=False,
            server_default="pending",
        ),
    )

def downgrade() -> None:
    op.drop_column("watch_party_rsvps", "status")
    op.execute("DROP TYPE IF EXISTS rsvp_status_enum")
```

### For a GIN Full-Text Search Index
```python
def upgrade() -> None:
    # Add tsvector column
    op.add_column(
        "media_entries",
        sa.Column("title_search", postgresql.TSVECTOR(), nullable=True),
    )
    # Add GIN index on it
    op.create_index(
        "idx_media_entries_title_search",
        "media_entries",
        ["title_search"],
        postgresql_using="gin",
    )
    # Populate existing rows
    op.execute("""
        UPDATE media_entries SET title_search =
            setweight(to_tsvector('simple', unaccent(coalesce(title_english, ''))), 'A') ||
            setweight(to_tsvector('simple', unaccent(coalesce(title_romaji, ''))), 'B') ||
            setweight(to_tsvector('simple', unaccent(coalesce(title_native, ''))), 'C')
    """)

def downgrade() -> None:
    op.drop_index("idx_media_entries_title_search")
    op.drop_column("media_entries", "title_search")
```

## Mandatory Round-Trip Test
```bash
alembic upgrade head      # apply
alembic downgrade -1      # revert — must not error
alembic upgrade head      # re-apply — must not error
```
If downgrade errors: fix the `downgrade()` function. Never ship a migration without a working downgrade.

## After Migration
Update `docs/database-schema.md` to reflect the change.
State the new column/table/index in a comment at the top of the migration file.
