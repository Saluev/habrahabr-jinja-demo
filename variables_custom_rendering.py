from jinja2 import Environment
from jinja2.ext import Extension
from jinja2 import lexer


class VariablesCustomRenderingExtension(Extension):

    def __init__(self, environment):
        super(VariablesCustomRenderingExtension, self).__init__(environment)
        environment.filters.setdefault("jinja_or_str", self._jinja_or_str)

    def filter_stream(self, stream):
        return lexer.TokenStream(self._generator(stream), stream.name, stream.filename)

    def _generator(self, stream):
        for token in stream:
            if token.type == lexer.TOKEN_VARIABLE_END:
                yield lexer.Token(token.lineno, lexer.TOKEN_RPAREN, ")")
                yield lexer.Token(token.lineno, lexer.TOKEN_PIPE, "|")
                yield lexer.Token(token.lineno, lexer.TOKEN_NAME, "jinja_or_str")
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
    env = Environment()
    env.add_extension(VariablesCustomRenderingExtension)
    template = env.from_string("""A object says: {{ a }}""")
    print(template.render(a=Kohai()))
