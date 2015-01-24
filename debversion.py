import re


class Block(object):
    def __init__(self, block):
        self.relations = [Relation(x.strip()) for x in block.split(",")]

    def __repr__(self):
        return ", ".join((repr(x) for x in self.relations))


class Relation(object):
    """
    Each Relation needs to be satisfied to have the block satisfied.
    """

    def __init__(self, frame):
        self.targets = [Target(x.strip()) for x in frame.split("|")]

    def __repr__(self):
        return " | ".join((repr(x) for x in self.targets))


class Arch(object):
    """
    Relationships may be restricted to a certain set of architectures. This is
    indicated in brackets after each individual package name and the optional
    version specification. The brackets enclose a non-empty list of Debian
    architecture names in the format described in Architecture specification
    strings, Section 11.1, separated by whitespace. Exclamation marks may be
    prepended to each of the names. (It is not permitted for some names to be
    prepended with exclamation marks while others aren't.)
    """

    classification = None
    CLASSIFICATIONS = (
        ("arch", "required arch"),
        ("not-arch", "required not on this arch"),
    )

    def __init__(self, arch):
        self.arch = arch

    def __repr__(self):
        x = "["
        if self.classification == "not-arch":
            x += "!"
        x += "{}]".format(self.arch)
        return x


class Version(object):
    """
    The relations allowed are <<, <=, =, >= and >> for strictly earlier,
    earlier or equal, exactly equal, later or equal and strictly later,
    respectively. The deprecated forms < and > were confusingly used to mean
    earlier/later or equal, rather than strictly earlier/later, and must not
    appear in new packages (though dpkg still supports them with a warning).
    """

    classification = None
    CLASSIFICATIONS = (
        ("<<", "strictly earlier"),
        ("<=", "ealier or exact match"),
        ("=", "exact match"),
        (">=", "later or exact match"),
        (">>", "strictly later"),
    )

    def __init__(self, version):
        operator, target = version.split(" ", 1)
        self.classification = operator
        self.version = target

    def __repr__(self):
        x = "({} {})".format(self.classification, self.version)
        return x


class Target(object):
    """
    This is a concerete target of a dep. This may be blocked out behind
    an OR or something. Has arch and version constraints.
    """

    arch = None
    version = None
    package = None

    def __init__(self, target):
        if " " not in target:
            self.package = target
            return

        package, qualifiers = target.split(" ", 1)
        self.package = package
        qualifiers = dict(self._tokenize(qualifiers))
        self._assign(**qualifiers)

    def __repr__(self):
        stream = "{}".format(self.package)

        if self.arch:
            stream += " {}".format(self.arch)

        if self.version:
            stream += " {}".format(self.version)

        return stream

    def _assign(self, arch=None, version=None):
        self.arch = Arch(arch) if arch is not None else arch
        self.version = Version(version) if version is not None else arch

    def _tokenize(self, relation):
        relation = relation.strip()

        aqual = relation.find("[")
        aqual = aqual if aqual >= 0 else None

        vqual = relation.find("(")
        vqual = vqual if vqual >= 0 else None

        if aqual is None and vqual is None:
            return

        if (vqual is None) or (aqual is not None and aqual < vqual):
            closing = relation.find("]")
            yield ("arch", relation[aqual+1:closing])
            yield from self._tokenize(relation[closing:])
            return

        if (aqual is None) or (vqual is not None and vqual < aqual):
            closing = relation.find(")")
            yield ("version", relation[vqual+1:closing])
            yield from self._tokenize(relation[closing:])
            return

        print(aqual, vqual)
        raise ValueError("OMG WTF BBQ")