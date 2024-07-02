from tortoise import Tortoise, run_async
from rich.console import Console
from rich.table import Table

console = Console()


async def init_db():
    await Tortoise.init(db_url="sqlite://cases.db", modules={"models": ["__main__"]})
    await Tortoise.generate_schemas()


async def main():
    await init_db()

    # 创建一个3级队列调度器,每级的超时时间分别为10, 20, 30秒
    scheduler = MultiLevelQueueScheduler(3, [10, 20, 30])

    # 创建一些测试案例
    cases = [
        Case(1, 8),
        Case(2, 15),
        Case(3, 25),
        Case(4, 5),
        Case(5, 12),
    ]

    # 将案例添加到调度器
    for case in cases:
        scheduler.add_case(case)

    # 运行案例
    await scheduler.run_cases()

    # 查询并打印数据库中的结果
    results = await CaseModel.all()

    table = Table(title="Database Records")
    table.add_column("Case ID", style="cyan", no_wrap=True)
    table.add_column("Predicted", style="magenta")
    table.add_column("Actual", style="green")
    table.add_column("Level", style="yellow")
    table.add_column("Status", style="bold")

    for result in results:
        table.add_row(
            str(result.case_id),
            f"{result.predicted_runtime:.2f}",
            f"{result.actual_runtime:.2f}",
            str(result.queue_level),
            result.status,
        )

    console.print(table)

    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(main())
