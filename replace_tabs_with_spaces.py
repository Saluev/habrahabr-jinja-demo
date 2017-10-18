from jinja2 import Environment
from jinja2.ext import Extension
from jinja2 import nodes


class ReplaceTabsWithSpacesExtension(Extension):

    tags = {"replacetabs"}

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        body = parser.parse_statements(
            ["name:endreplacetabs"], drop_needle=True)
        return nodes.CallBlock(
            self.call_method("_process", [nodes.Const("    ")]), [], [], body, lineno=lineno)

    def _process(self, replacement, caller):
        text = caller()
        return text.replace("\t", replacement)


if __name__ == "__main__":
    env = Environment(extensions=[ReplaceTabsWithSpacesExtension])
    template = env.from_string(u"""
{% replacetabs %}
from itertools import count

def some_function(x, y, n=3):
\tfor z in count():
\t\tif x ** n + y ** n == z ** n:
\t\t\treturn z
{% endreplacetabs %}
    """)
    print(template.render())
