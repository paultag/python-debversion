from parsimonious import Grammar
from .models import Block


class DebVersionGrammar:
    grammar = Grammar(
        """
        relations = relation*
        relation = (target target_delim?)* relation_delim?

        relation_delim = ws? "," ws?
        target_delim = ws? "|" ws?

        target = package qualifiers*

        package_string = ~"[A-Z0-9\\+\\.-]*"i
        package_multiarch_string = ~"[A-Z0-9\\+\\.-]*"i
        package_multiarch = ":" package_multiarch_string

        package = package_string package_multiarch?

        qualifiers = archs
                   / version
                   / profiles

        version_string = ~"[^)]*"i
        version = ws? "(" ws? operator ws? version_string ws? ")" ws?
        # 1:1.0-1fnord1~lawl2+b2

        operator = ">=" / "<="
                 / "<<" / ">>"
                 / "="

        arch_string = ~"[^]\ ]*"i
        arch    = (ws? (ws? negate ws?)? arch_string ws?)
        archs   = ws? "[" arch+ "]" ws?
        # [amd64] // [amd i386] // [!linux-any amd64]

        profile_string = ~"[^>\ ]*"i
        profile = (ws? (ws? negate ws?)? profile_string ws?)
        profiles = ws? "<" profile+ ">" ws?
        # <fnord> // <stage1 cross> <stage1> // <!cross> <!stage1>

        ws = wss+
        wss = " "
            / "\\n"
            / "\\r"
            / "\\t"
        negate = "!"
        """)

    @classmethod
    def parse(cls, stream):
        tree = cls.grammar.parse(stream)
        return Block(tree)
