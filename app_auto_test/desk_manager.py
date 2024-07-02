import asyncio
from rich.console import Console


console = Console()


class DeskManager:
    def __init__(self, desk_id):
        self.desk_id = desk_id

    async def is_desk_alive(self):
        proc = await asyncio.create_subprocess_shell(
            f"ping -c 1 desk{self.desk_id}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        return proc.returncode == 0

    async def restart_desk(self):
        console.print(f"[yellow]Restarting desk {self.desk_id}[/yellow]")
        restart_command = (
            f"sshpass -p 'password' ssh user@desk{self.desk_id} 'sudo reboot'"
        )
        await asyncio.create_subprocess_shell(restart_command)
        await asyncio.sleep(60)  # 等待桌面重启
