"""Check for column drift between models and the actual DB schema."""
import asyncio
import asyncpg
from sqlmodel import SQLModel

# Import all models so they register with SQLModel.metadata
import src.app.models  # noqa: F401


async def main():
    conn = await asyncpg.connect(
        "postgresql://postgres:admin@localhost:5432/otakuhub"
    )
    rows = await conn.fetch(
        "SELECT table_name, column_name, data_type, is_nullable, column_default "
        "FROM information_schema.columns "
        "WHERE table_schema = 'public' "
        "ORDER BY table_name, ordinal_position"
    )
    db_schema: dict[str, set[str]] = {}
    for r in rows:
        t = r["table_name"]
        if t not in db_schema:
            db_schema[t] = set()
        db_schema[t].add(r["column_name"])

    for table_name, table in sorted(SQLModel.metadata.tables.items()):
        if table_name not in db_schema:
            print(f"TABLE NOT IN DB: {table_name}")
            continue

        model_cols = set(table.columns.keys())
        db_cols = db_schema[table_name]

        missing_in_db = model_cols - db_cols
        extra_in_db = db_cols - model_cols

        if missing_in_db:
            print(f"\n{table_name}: MISSING IN DB ({len(missing_in_db)}):")
            for col in sorted(missing_in_db):
                col_type = table.columns[col].type
                print(f"  - {col}: {col_type}")

        if extra_in_db:
            print(f"\n{table_name}: EXTRA IN DB ({len(extra_in_db)}):")
            for col in sorted(extra_in_db):
                print(f"  - {col}")

    print("\nDone checking drift.")
    await conn.close()


asyncio.run(main())
