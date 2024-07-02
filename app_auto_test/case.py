from rich.panel import Panel
from rich.text import Text


class Case:
    def __init__(
        self,
        case_id,
        predicted_runtime,
        actual_runtime=None,
        queue_level=0,
        result_dir=None,
    ):
        self.case_id = case_id
        self.predicted_runtime = predicted_runtime
        self.actual_runtime = actual_runtime
        self.queue_level = queue_level
        self.result_dir = result_dir

    def __str__(self):
        return f"Case {self.case_id} (Predicted: {self.predicted_runtime}, Actual: {self.actual_runtime}, Level: {self.queue_level})"

    def rich_panel(self):
        content = Text()
        content.append(f"Case ID: {self.case_id}\n", style="bold cyan")
        content.append(f"Predicted Runtime: {self.predicted_runtime}\n", style="green")
        content.append(
            f"Actual Runtime: {self.actual_runtime or 'N/A'}\n", style="yellow"
        )
        content.append(f"Queue Level: {self.queue_level}\n", style="magenta")
        content.append(f"Result Directory: {self.result_dir or 'N/A'}", style="blue")
        return Panel(content, title="Case Info", border_style="bright_black")
