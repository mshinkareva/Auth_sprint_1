import asyncio
from typing import Optional

import asyncpg
from tests.functional.settings import test_settings
from tests.functional.utils.backoff import backoff


@backoff()
async def connect_postgres() -> Optional[bool]:
    connection = f"postgresql://{test_settings.postgres_user}:{test_settings.postgres_password}@{test_settings.postgres_host}:{test_settings.postgres_port}/{test_settings.postgres_db}"
    conn = await asyncpg.connect(dsn=connection)
    try:
        await conn.fetch("SELECT 1 FROM permission LIMIT 1;")
        print("Successfully connected to the 'permissions' table.")
        return True
    except asyncpg.UndefinedTableError as ex:
        print(f"😀The table 'permissions' does not exist! {ex}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        await conn.close()


if __name__ == '__main__':
    asyncio.run(connect_postgres())
