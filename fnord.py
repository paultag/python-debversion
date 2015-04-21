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


class Block:
    def __init__(self, *relations):
        self.relations = relations

class Relation:
    def __init__(self, targets):
        self.targets = targets

class Target:
    def __init__(self, package, qualifiers=None):
        self.package = package
        self.qualifiers = qualifiers if qualifiers else []

class Package:
    def __init__(self, package):
        self.package = package

class Operator:
    def __init__(self, operator):
        self.operator = operator

class VersionNumber:
    def __init__(self, number):
        self.number = number

class Version:
    def __init__(self, operator, versionnumber):
        self.operator = operator
        self.number = versionnumber

class Qualifiers:
    def __init__(self, *qualifiers):
        self.qualifiers = qualifiers


def _ich(stream):
    return filter(lambda x: x is not None, stream)


def _tsplat(stream):
    return {el.__class__.__name__.lower(): el for el in _ich(stream)}


class DebversionVisitor(NodeVisitor):

    def visit_relations(self, node, visited_children):
        return Block(*_ich(visited_children))

    def visit_relation(self, node, visited_children):
        return Relation(*_ich(visited_children))

    def visit_target(self, node, visited_children):
        return Target(**_tsplat(visited_children))

    def visit_package(self, node, visited_children):
        return Package(node.text)

    def visit_operator(self, node, visited_children):
        return Operator(node.text)

    def visit_version_string(self, node, visited_children):
        return VersionNumber(node.text)

    def visit_version(self, node, visited_children):
        return Version(**_tsplat(visited_children))

    def visit_qualifiers(self, node, visited_children):
        return Qualifiers(*visited_children)

    ###

    def _noop(self, node, visited_children):
        visited_children = list(_ich(visited_children))
        if len(visited_children) == 1:
            return visited_children[0]
        if visited_children != []:
            return visited_children

    visit_relation_delim = _noop
    visit_ = _noop
    visit_target_delim = _noop
    visit_wss = _noop
    visit_ws = _noop



tree = grammar.parse("foo (>= 1:1.0-1fnord1~lawl2+b2), bar | baz")
x = DebversionVisitor()
print(x.visit(tree))
