from debversion import Block


def test_basic():
    """
    Check that we can handle AND relation in the parsed block.
    """
    x = Block("foo, bar, baz")
    assert [z.targets[0].package for z in x.relations] == ["foo", "bar", "baz"]


def test_basic_or():
    """
    Check that we can handle OR relation in the parsed block.
    """
    block = Block("foo | bar")
    relation ,= block.relations
    assert ["foo", "bar"] == [x.package for x in relation.targets]


def test_advanced_or():
    """
    Check that we can handle OR relation in the parsed block.
    with a few AND things.
    """
    block = Block("fnord, foo | bar, read")
    fnord, or_, read ,= block.relations

    fnord ,= fnord.targets
    read ,= read.targets

    assert fnord.package == "fnord"
    assert read.package == "read"
    assert ["foo", "bar"] == [x.package for x in or_.targets]
