import asyncio
from rich.console import Console
from model import CaseModel

console = Console()


class CaseExecutor:
    def __init__(self, desk_manager, test_session):
        self.desk_manager = desk_manager
        self.test_session = test_session

    async def execute_case(self, case, progress_task):
        while True:
            if not await self.desk_manager.is_desk_alive():
                console.print(
                    f"[red]Desk {self.desk_manager.desk_id} is down, restarting...[/red]"
                )
                await self.desk_manager.restart_desk()
            else:
                break

        ssh_command = f"sshpass -p 'password' ssh user@desk{self.desk_manager.desk_id} 'time /usr/bin/time -v your_command_here'"
        process = await asyncio.create_subprocess_shell(
            ssh_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        execution_time = None
        max_memory = None

        for line in stderr.decode().splitlines():
            if "Elapsed (wall clock) time" in line:
                execution_time = line.split(": ")[-1]
            elif "Maximum resident set size" in line:
                max_memory = line.split(": ")[-1]

        success = process.returncode == 0
        status = "Success" if success else "Failure"

        await CaseModel.create(
            case_id=case.case_id,
            predicted_runtime=case.predicted_runtime,
            actual_runtime=execution_time,
            queue_level=case.queue_level,
            result_dir=case.result_dir,
            status=status,
            session=self.test_session,
            max_memory=max_memory,
        )

        console.print(case.rich_panel())
        if success:
            console.print(
                f"[green]Case {case.case_id} executed successfully in {execution_time} seconds[/green]"
            )
            progress_task.update(advance=1)
        else:
            console.print(
                f"[red]Case {case.case_id} failed to execute within time limit[/red]"
            )

        return success
