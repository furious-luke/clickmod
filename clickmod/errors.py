from json import JSONDecodeError

from click import ClickException
from requests import Response
from rich.console import Console


class ApiError(ClickException):
    def __init__(self, response: Response):
        self.response = response
        self.data = self.parse_response(response)
        self.console = Console()
        super().__init__(self.build_message())

    def parse_response(self, response: Response) -> dict[str, str]:
        try:
            data = response.json()
        except JSONDecodeError:
            data = {}
        if response.status_code == 401:
            if data.get('code') is None:
                data['code'] = 'UNAUTHORIZED'
            if data.get('message') is None:
                data['message'] = 'Unauthorized.'
        if response.status_code == 404:
            data = {"code": "NOTFOUND", "message": "Not found."}
        return data

    def build_message(self):
        return self.data["message"] if self.data else ""

    def show(self):
        if self.data.get("code"):
            handler = getattr(self, "_" + self.data["code"].lower(), None)
            if handler:
                return handler()
        self.console.print(f"[bold red]Error:[/bold red] {str(self)}")
