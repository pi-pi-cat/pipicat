import asyncio
import heapq
import random
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID

console = Console()


class MultiLevelQueueScheduler:
    def __init__(self, num_levels, level_timeouts, test_session, total_cases):
        self.num_levels = num_levels
        self.level_timeouts = level_timeouts
        self.queues = [[] for _ in range(num_levels)]
        self.test_session = test_session
        self.total_cases = total_cases
        self.progress = Progress()
        self.task_id = None

    def add_case(self, case):
        heapq.heappush(self.queues[case.queue_level], (case.predicted_runtime, case))

    def get_next_case(self):
        for level in range(self.num_levels):
            if self.queues[level]:
                return heapq.heappop(self.queues[level])[1]
        return None

    def move_to_next_queue(self, case):
        if case.queue_level < self.num_levels - 1:
            case.queue_level += 1
            self.add_case(case)
        else:
            print(f"Case {case.case_id} has failed in all queues.")

    async def execute_case(self, case):
        # 模拟案例执行
        case.actual_runtime = random.uniform(
            0.5 * case.predicted_runtime, 1.5 * case.predicted_runtime
        )
        await asyncio.sleep(0.1)  # 模拟执行时间

        success = case.actual_runtime <= self.level_timeouts[case.queue_level]
        status = "Success" if success else "Failure"

        # 将案例结果写入数据库
        await CaseModel.create(
            case_id=case.case_id,
            predicted_runtime=case.predicted_runtime,
            actual_runtime=case.actual_runtime,
            queue_level=case.queue_level,
            result_dir=case.result_dir,
            status=status,
            session=self.test_session,
        )

        console.print(case.rich_panel())
        if success:
            console.print(
                f"[green]Case {case.case_id} executed successfully in {case.actual_runtime:.2f} seconds[/green]"
            )
        else:
            console.print(
                f"[red]Case {case.case_id} failed to execute within time limit[/red]"
            )

        # 暂停进度条显示以打印案例信息
        self.progress.stop()
        console.print(case.rich_panel())
        self.progress.start()

        return success

    async def run_cases(self):
        with self.progress:
            self.task_id = self.progress.add_task(
                "[cyan]Executing cases...", total=self.total_cases
            )

            while True:
                case = self.get_next_case()
                if not case:
                    break

                console.print(f"\n[bold]Running[/bold]", case.rich_panel())
                success = await self.execute_case(case)

                if not success:
                    self.move_to_next_queue(case)

                self.progress.update(self.task_id, advance=1)
