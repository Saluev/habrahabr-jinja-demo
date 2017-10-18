from jinja2 import Environment
from jinja2.ext import Extension
from jinja2 import lexer


class VariablesCustomRenderingExtension(Extension):

    def __init__(self, environment):
        super(VariablesCustomRenderingExtension, self).__init__(environment)
        self._filter_name = "jinja_or_str"
        environment.filters.setdefault(self._filter_name, self._jinja_or_str)

    def filter_stream(self, stream):
        return lexer.TokenStream(self._generator(stream), stream.name, stream.filename)

    def _generator(self, stream):
        for token in stream:
            if token.type == lexer.TOKEN_VARIABLE_END:
                yield lexer.Token(token.lineno, lexer.TOKEN_RPAREN, ")")
                yield lexer.Token(token.lineno, lexer.TOKEN_PIPE, "|")
                yield lexer.Token(token.lineno, lexer.TOKEN_NAME, self._filter_name)
            yield token
            if token.type == lexer.TOKEN_VARIABLE_BEGIN:
                yield lexer.Token(token.lineno, lexer.TOKEN_LPAREN, "(")

    @staticmethod
    def _jinja_or_str(obj):
        try:
            return obj.__jinja__()
        except AttributeError:
            return obj


class Kohai(object):

    def __jinja__(self):
        return "senpai rendered me!"


if __name__ == "__main__":
    env = Environment(extensions=[VariablesCustomRenderingExtension])
    template = env.from_string("""Kohai says: {{ kohai }}""")
    print(template.render(kohai=Kohai()))
