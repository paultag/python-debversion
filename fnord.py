from parsimonious import Grammar, NodeVisitor
from collections import defaultdict


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

    version_string = ~"[^)]*"i
    version = ws? "(" ws? operator ws? version_string ws? ")" ws?
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


tree = grammar.parse("foo (>= 1:1.0-1fnord1~lawl2+b2), bar | baz [!amd64]")
