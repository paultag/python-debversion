

def get_one(stream):
    els = list(stream)
    if els == []:
        return None
    return els[0].text


def tfilter(tree, test):
    if test(tree):
        yield tree
    for el in tree.children:
        yield from tfilter(el, test)


def tfilter_name(tree, name):
    return tfilter(tree, lambda x: x.expr_name == name)



