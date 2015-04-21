from parsimonious import Grammar


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
        self.negated = list(tfilter_name(tree, 'negate')) != []
        profile, = list(tfilter_name(tree, 'profile_string'))
        self.profile = profile.text

    def to_dict(self):
        return {"negated": self.negated,
                "profile": self.profile}


class Profiles:
    def __init__(self, tree):
        self.profiles = [Profile(x) for x in tfilter_name(tree, 'profile')]

    def to_dict(self):
        return {"profiles": [x.to_dict() for x in self.profiles]}


class Version:
    def __init__(self, tree):
        operator, = list(tfilter_name(tree, 'operator'))
        version, = list(tfilter_name(tree, 'version_string'))
        self.operator = operator.text
        self.version = version.text

    def to_dict(self):
        return {"operator": self.operator, "version": self.version}


def qualifiers(tree):

    def arches(tree):
        for arch in tfilter_name(tree, 'arch'):
            yield Arch(arch)

    def profiles(tree):
        yield Profiles(tree)

    def versions(tree):
        yield Version(tree)

    for node in tfilter(tree, lambda x: x.expr_name in [
        'archs', 'profiles', 'version'
    ]):
        yield from {
            "archs": arches,
            "version": versions,
            "profiles": profiles,
        }[node.expr_name](node)


def get_one(stream):
    els = list(stream)
    if els == []:
        return None
    return els[0].text


class Package:
    def __init__(self, tree):
        self.arch = get_one(tfilter_name(tree, 'package_multiarch_string'))
        self.package = get_one(tfilter_name(tree, 'package_string'))

    def to_dict(self):
        return {
            "arch": self.arch,
            "package": self.package,
        }

# tree = grammar.parse("foo:amd64 (>= 1.0)")
# x = Block(tree)
# print(x.to_dict())
# import sys
# sys.exit()


from debian.deb822 import Deb822
import subprocess


for para in Deb822.iter_paragraphs(open(
        '/var/lib/apt/lists/http.debian.net_'
        'debian_dists_unstable_main_binary-amd64_Packages', 'r').read()):

    tree = grammar.parse(para.get('Depends', ""))
    x = Block(tree)
    print(x.to_dict())
