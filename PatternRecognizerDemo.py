import javalang

def insertLine(path, position, value):
    global offset
    file = open(path, "r")
    contents = file.readlines()
    file.close()

    file = open(path, "a")
    file.seek(0)
    file.truncate()
    contents.insert(position + offset - 1, value + "\n")
    file.writelines(contents)
    file.close()

    offset += 1

def getIndexOfClassNameInClasses(className):
    global classes
    index = next((i for i, c in enumerate(classes) if c.name == className), None)
    return index

def hasVisitorStructure(className):
    global classes
    global commentedAlready
    goodCandidates = []

    #################################################
    # Visitor should have super class,
    # find classes that have className as super class
    _subClasses = [c for c in classes if c.implements         != None and
                                         c.implements[0].name == className]
    if len(_subClasses) == 0:
        return False

    for index in range(len(_subClasses)):
        goodCandidates.append(index)

    for c in goodCandidates:
        idx = getIndexOfClassNameInClasses(_subClasses[c].name)
        if idx not in commentedAlready:
            commentedAlready.append(
                getIndexOfClassNameInClasses(_subClasses[c].name))
            insertLine(path, _subClasses[c].position[0],
                       "// Visitor pattern detected here (Visitor)")
    return True

def hasVisiteeStructure(_class):
    # should have a virtual parent class
    if _class.implements == None:
        return False

    for method in _class.methods:
        goodCandidate = False

        # accept function should be public
        if 'public' not in method.modifiers:
            break

        for parameter in method.parameters:
            if hasVisitorStructure(parameter.type.name):
                goodCandidate = True

        if goodCandidate:
            insertLine(path, method.position[0],
                       "// Visitor pattern detected here (Visitee)")

# ------------------------------------------------------------------------------

offset = 0
path = "./VisitorDemo/VisitorDemo.java"
classes = []
commentedAlready = []

with open(path, "r") as file:
    tree = javalang.parse.parse(file.read())

    # collect all classes
    for structure, node in tree.filter(javalang.tree.ClassDeclaration):
        classes.append(node)

    for _class in classes:
        hasVisiteeStructure(_class)

    # print(classes[0].methods[0].children)
    # for node in classes.filter(javalang.tree.ClassDeclaration)
    file.close()