from pathlib import Path

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import select_autoescape


TEMPLATES_DIR = (
    Path(__file__).parent / "templates"
)


class EmailRenderer:

    def __init__(self) -> None:
        self._env = Environment(
            loader=FileSystemLoader(
                TEMPLATES_DIR,
            ),
            autoescape=select_autoescape(
                ["html"],
            ),
        )

    def render(
        self,
        template_name: str,
        **context,
    ) -> str:
        template = self._env.get_template(
            template_name,
        )

        return template.render(**context)