from rich.console import Console
from datetime import datetime


class Log:
    console = Console(highlight=False)

    @classmethod
    def info(self, text):
        time = datetime.now().strftime('%H:%M:%S')
        self.console.print(
            f"[[bold cyan]{time}[/]] [[bold green]INFO[/]] {text}")

    @classmethod
    def warning(self, text):
        time = datetime.now().strftime('%H:%M:%S')
        self.console.print(
            f"[[bold cyan]{time}[/]] [[bold yellow]WARNING[/]] {text}")


    @classmethod
    def high(self, text):
        time = datetime.now().strftime('%H:%M:%S')
        self.console.print(
            f"[[bold cyan]{time}[/]] [[bold red]CRITICAL[/]] {text}")