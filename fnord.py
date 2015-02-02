from parsimonious.grammar import Grammar


grammar = Grammar(
    """
    relations = relation*
    relation = (target target_delim?)* relation_delim?

    relation_delim = ws? "," ws?
    target_delim = ws? "|" ws?

    target = package qualifiers*

    package = ~"[A-Z0-9\\.-]*"i

    qualifiers = arch
               / version
               / profile

    version = ws? "("      ws? operator ws?  ~"[^)]*"i ws? ")" ws?
    # 1:1.0-1fnord1~lawl2+b2

    operator = ">=" / "<="
             / "<<" / ">>"
             / "="

    arch    = ws? "[" (ws? (ws? negate ws?)? ~"[^]]*"i ws?)+ "]" ws?
    # [amd64] // [amd i386] // [!linux-any amd64]

    profile = ws? "<" (ws? (ws? negate ws?)? ~"[^>]*"i ws?)+ ">" ws?
    # <fnord> // <stage1 cross> <stage1> // <!cross> <!stage1>

    ws = wss+
    wss = " "
        / "\\n"
        / "\\r"
        / "\\t"
    negate = "!"
    """)

tree = grammar.parse("foo (>= 1:1.0-1fnord1~lawl2+b2), bar | baz")


class Block:
    def __init__(self, relations):
        self.relations = relations

class Relation:
    def __init__(self, relation):
        pass

class Target:
    def __init__(self, target):
        pass


_table = {}
def builds(type_):
    def _(fn):
        _table[type_] = fn
        return fn
    return _

class DebversionCompiler:

    def compile(self, el):
        name = el.expr_name
        return _table[name](self, el)

    @builds("")
    def compile_stream(self, el):
        return [self.compile(x) for x in el.children]

    @builds("relations")
    def compile_relations(self, el):
        return Block([self.compile(x) for x in el.children])

    @builds("relation")
    def compile_relation(self, el):
        return [Relation(*self.compile(x)) for x in el.children]

    @builds("target")
    def compile_target(self, el):
        return Target()


x = DebversionCompiler()
x.compile(tree)
