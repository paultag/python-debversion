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

tree = grammar.parse("foo (>= 1:1.0-1fnord1~lawl2+b2), bar | baz [!amd64 sparc]")


def tfilter(tree, test):
    if test(tree):
        yield tree
    for el in tree.children:
        yield from tfilter(el, test)


def tfilter_name(tree, name):
    return tfilter(tree, lambda x: x.expr_name == name)


class Block:
    def __init__(self, tree):
        self.relations = [Relation(x) for x in tfilter_name(tree, 'relation')]

    def to_dict(self):
        return {"relations": [x.to_dict() for x in self.relations]}


class Relation:
    def __init__(self, tree):
        self.targets = [Target(x) for x in tfilter_name(tree, 'target')]

    def to_dict(self):
        return {
            "targets": [x.to_dict() for x in self.targets]
        }


class Target:
    def __init__(self, tree):
        package, = [Package(x) for x in tfilter_name(tree, 'package')]

        self.package = package
        self.qualifiers = list(qualifiers(tree))

    def to_dict(self):
        return {"package": self.package.to_dict(),
                "qualifiers": [x.to_dict() for x in self.qualifiers]}


class Arch:
    def __init__(self, tree):
        self.negated = list(tfilter_name(tree, 'negate')) != []
        arch, = list(tfilter_name(tree, 'arch_string'))
        self.arch = arch.text

    def to_dict(self):
        return {"negated": self.negated, "arch": self.arch}


class Profile:
    def __init__(self, tree):
        pass

    def to_dict(self):
        return {"negated": False, "arch": None}


class Version:
    def __init__(self, tree):
        pass

    def to_dict(self):
        return {"negated": False, "arch": None}


def qualifiers(tree):

    def arches(tree):
        for arch in tfilter_name(tree, 'arch'):
            yield Arch(arch)

    def versions(tree):
        yield Version(tree)

    for node in tfilter(tree, lambda x: x.expr_name in [
        'archs', 'profiles', 'version'
    ]):
        yield from {
            "archs": arches,
            "version": versions,
        }[node.expr_name](node)


class Package:
    def __init__(self, tree):
        self.name = tree.text

    def to_dict(self):
        return self.name


x = Block(tree)
print(x.to_dict())
