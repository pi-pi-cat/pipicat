from tortoise import Tortoise, run_async
from model import TestSession, CaseModel

# fake 数据
from faker import Faker


async def init_db():
    await Tortoise.init(
        db_url="sqlite://cases.db?mode=rwc", modules={"models": ["model"]}
    )
    await Tortoise.generate_schemas()


async def fake_data():
    fake = Faker()
    for _ in range(10):
        session_name = fake.name()
        description = fake.text()
        start_time = fake.date_time_this_year()
        visible = fake.boolean()
        session = await TestSession.create(
            session_name=session_name,
            description=description,
            start_time=start_time,
            visible=visible,
        )

        for __ in range(100):
            status = fake.random_element(elements=("Success", "Failure"))
            queue_level = fake.random_int(min=1, max=3)
            predicted_runtime = fake.random_int(min=1, max=100)
            start_time = fake.date_time_this_month()
            actual_runtime = fake.random_int(min=1, max=100)
            # end_time 比 start_time 大，也有可以为 None
            end_time = fake.date_time_between_dates(
                datetime_start=start_time, datetime_end="+1d"
            )
            # 10% 的概率为 None
            if fake.random_int(min=1, max=10) == 1:
                end_time = None
                status = "RUNNING"
            result_dir = fake.file_path()
            case = await CaseModel.create(
                status=status,
                queue_level=queue_level,
                predicted_runtime=predicted_runtime,
                start_time=start_time,
                actual_runtime=actual_runtime,
                end_time=end_time,
                result_dir=result_dir,
                session=session,
            )


async def main():
    await init_db()
    await fake_data()


if __name__ == "__main__":
    run_async(main())
