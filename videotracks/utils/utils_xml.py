
###################
# xml
###################

def getFirstChildWithName(parentNode, name):
    for node in parentNode.childNodes:
        # print(f"video - node.localName: {node.localName}")
        if name == node.localName:
            return node
    return None


