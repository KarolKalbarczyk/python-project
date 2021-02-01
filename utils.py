

def find(list, fun, default = None):
    for element in list:
        if fun(element):
            return element
    return default

def flat_map(elemToList, list):
    newList = []
    for elem in list:
        elemList = elemToList(elem)
        for e in elemList:
            newList.append(e)
    return newList

