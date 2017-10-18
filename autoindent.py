# -*- encoding: utf-8 -*-

import re

from jinja2 import Environment
from jinja2.ext import Extension
from jinja2.lexer import Token
from jinja2 import lexer, nodes


class RichToken(Token):
    pass


class AutoindentExtension(Extension):

    tags = {"autoindent"}

    _indent_regex = re.compile(r"^ *")
    _whitespace_regex = re.compile(r"^\s*$")

    def __init__(self, environment):
        super(AutoindentExtension, self).__init__(environment)

    def filter_stream(self, stream):
        return lexer.TokenStream(self._generator(stream), stream.name, stream.filename)

    def parse(self, parser):
        last_indent = nodes.Const(parser.stream.current.last_indent)
        lineno = next(parser.stream).lineno
        body = parser.parse_statements(["name:endautoindent"], drop_needle=True)
        return nodes.CallBlock(
            self.call_method("_autoindent", [last_indent]), [], [], body, lineno=lineno)

    def _generator(self, stream):
        last_line = ""
        last_indent = 0
        for token in stream:
            if token.type == lexer.TOKEN_DATA:
                last_line += token.value
                if "\n" in last_line:
                    _, last_line = last_line.rsplit("\n", 1)
                last_indent = self._indent(last_line)
            token = RichToken(*token)
            token.last_indent = last_indent
            yield token

    def _autoindent(self, last_indent, caller):
        text = caller()
        lines = text.split("\n")
        if len(lines) < 2:
            return text
        first_line, tail_lines = lines[0], lines[1:]
        min_indent = min(
            self._indent(line)
            for line in tail_lines
            if not self._whitespace_regex.match(line)
        )
        if min_indent <= last_indent:
            return text
        dindent = min_indent - last_indent
        tail = "\n".join(line[dindent:] for line in tail_lines)
        return "\n".join((first_line, tail))

    def _indent(self, string):
        return len(self._indent_regex.match(string).group())


if __name__ == "__main__":
    env = Environment(extensions=[AutoindentExtension])
    template = env.from_string(u"""
{%- autoindent -%}
    {%- if True -%}
        What is true, is true.
    {%- endif %}
    {%- if not False %}
        But what is false, is not true.
    {%- endif -%}
{%- endautoindent -%}
    """)
    print(template.render())
