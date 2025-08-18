import re
from pathlib import Path


class Template:
    def __init__(self, text: str):
        self.text = text

    def render(self, **context):
        pattern = re.compile(r"{{\s*(.*?)\s*}}")

        def repl(match):
            expr = match.group(1)
            try:
                return str(eval(expr, {}, context))
            except Exception:
                return ""

        return pattern.sub(repl, self.text)


class FileSystemLoader:
    def __init__(self, searchpath):
        self.searchpath = Path(searchpath)


class Environment:
    def __init__(self, loader=None, **kwargs):
        self.loader = loader
        self.filters = {}

    def get_template(self, template_path: str):
        path = self.loader.searchpath / template_path
        text = path.read_text()
        return Template(text)
