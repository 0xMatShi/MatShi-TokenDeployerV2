import asyncio
from database.engine import engine, BaseSQLAlchemyModel
from database import models  # ⚡ важно импортировать модели, иначе таблицы не увидит

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(BaseSQLAlchemyModel.metadata.create_all)
    await engine.dispose()  # закрыть соединение после работы

if __name__ == "__main__":
    asyncio.run(create_db())