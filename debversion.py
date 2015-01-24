

class Block(object):
    def __init__(self, block):
        self.relations = [Relation(x.strip()) for x in block.split(",")]


class Relation(object):
    """
    Each Relation needs to be satisfied to have the block satisfied.
    """

    def __init__(self, frame):
        self.targets = [Target(x.strip()) for x in frame.split("|")]


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
        pass


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
        pass


class Target(object):
    """
    This is a concerete target of a dep. This may be blocked out behind
    an OR or something. Has arch and version constraints.
    """

    arch = None
    version = None

    def __init__(self, target):
        pass
