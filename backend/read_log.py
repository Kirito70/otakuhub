import asyncio
import json
import asyncpg

async def read_log():
    conn = await asyncpg.connect('postgresql://postgres:admin@localhost:5432/otakuhub')
    row = await conn.fetchrow(
        "SELECT error_log FROM syncjob ORDER BY created_at DESC LIMIT 1"
    )
    if row and row[0]:
        err = json.loads(row[0])
        if isinstance(err, dict):
            print(json.dumps(err, indent=2)[:2000])
        elif isinstance(err, list):
            print(f"Total errors: {len(err)}")
            for e in err[:3]:
                print(json.dumps(e, indent=2)[:400])
    else:
        print("No error log found")
    await conn.close()

asyncio.run(read_log())
