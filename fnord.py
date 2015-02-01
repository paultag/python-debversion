from parsimonious.grammar import Grammar


grammar = Grammar(
    """
    targets = target*
    target = package qualifiers*

    package = value

    qualifiers = arch
               / version

    arch = ws? "[" ws? value ws? "]" ws?
    version = ws? "(" ws? operator ws? value ws? ")" ws?
    operator = ">="
             / "<="
             / "<<"
             / ">>"
             / "="

    ws = " "+
    value = ~"[A-Z0-9\\.-]*"i
    """)

print(grammar.parse("foo [amd64] (>= 1.0)"))
