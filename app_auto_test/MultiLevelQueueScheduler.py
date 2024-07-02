import asyncio
import heapq
import random
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from model import CaseModel
from desk_manager import DeskManager
from case_executor import CaseExecutor

console = Console()


class MultiLevelQueueScheduler:
    def __init__(
        self, num_levels, level_timeouts, test_session, total_cases, concurrency_limit=2
    ):
        self.num_levels = num_levels
        self.level_timeouts = level_timeouts
        self.concurrency_limit = concurrency_limit
        self.queues = [[] for _ in range(num_levels)]
        self.task_queue = asyncio.Queue()
        self.test_session = test_session
        self.total_cases = total_cases
        self.progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.1f}%",
            TimeElapsedColumn(),
        )
        self.progress_task = self.progress.add_task(
            "Processing cases...", total=total_cases
        )

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
            console.print(f"[red]Case {case.case_id} has failed in all queues.[/red]")

    async def worker(self, desk_id):
        desk_manager = DeskManager(desk_id)
        case_executor = CaseExecutor(desk_manager, self.test_session)

        while True:
            case = await self.task_queue.get()
            if case is None:
                self.task_queue.task_done()
                break
            console.print(
                f"\n[bold]Running on desk {desk_id}[/bold]", case.rich_panel()
            )
            success = await case_executor.execute_case(case, self.progress_task)
            if not success:
                self.move_to_next_queue(case)
            self.task_queue.task_done()
            await asyncio.sleep(10)

    async def run_cases(self):
        with self.progress:
            workers = [
                asyncio.create_task(self.worker(desk_id))
                for desk_id in range(self.concurrency_limit)
            ]

            while any(self.queues) or not self.task_queue.empty():
                while self.task_queue.qsize() < self.concurrency_limit:
                    case = self.get_next_case()
                    if case is None:
                        break
                    await self.task_queue.put(case)

                await asyncio.sleep(0.1)  # 避免过度占用CPU

            for _ in range(self.concurrency_limit):
                await self.task_queue.put(None)

            await self.task_queue.join()
            await asyncio.gather(*workers, return_exceptions=True)
