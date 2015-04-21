from .utils import tfilter_name, tfilter, get_one


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


class Package:
    def __init__(self, tree):
        self.arch = get_one(tfilter_name(tree, 'package_multiarch_string'))
        self.package = get_one(tfilter_name(tree, 'package_string'))

    def to_dict(self):
        return {
            "arch": self.arch,
            "package": self.package,
        }
