# -*- encoding: utf-8 -*-

from jinja2 import Environment
from jinja2.ext import Extension
from jinja2 import nodes


class RepeatNTimesExtension(Extension):

    tags = {"repeat"}

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        index = nodes.Name("_", "store", lineno=lineno)
        how_many_times = parser.parse_expression()
        iterable = nodes.Call(nodes.Name("range", "load"), [how_many_times], [], None, None)
        parser.stream.expect("name:times")
        body = parser.parse_statements(["name:endrepeat"], drop_needle=True)
        return nodes.For(index, iterable, body, [], None, False, lineno=lineno)


if __name__ == "__main__":
    env = Environment()
    env.add_extension(RepeatNTimesExtension)
    template = env.from_string(u"""
        {%- repeat 3 times -%}
            {% if not loop.first and not loop.last %}, {% endif -%}
            {% if loop.last %} и ещё раз {% endif -%}
            учиться
        {%- endrepeat -%}
    """)
    print(template.render())
