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
    index = next((i for i, c in enumerate(classes)
                  if c.name == className), None)
    return index


def getSuperClassByClassName(className):
    global classes
    index = getIndexOfClassNameInClasses(className)
    if index != None:
        _class = classes[index]
        return _class.implements
    else:
        return None


def addCommentIfNotAlreadyDone(path, position, value):
    global commentedAlready

    if position not in commentedAlready:
        commentedAlready.append(position)
        insertLine(path, position, value)


def hasVisitorStructure(className):
    global classes
    goodCandidates = []  # [classIndex, methodIndex]

    ##########################################################################
    # Visitor should have super class,
    # find classes that have className as super class
    _subClasses = [c for c in classes if c.implements != None and
                   any(imp.name == className for imp in c.implements)]

    if len(_subClasses) == 0:
        return False

    ##########################################################################
    # visitor should have multiple methods that get exactly one parameter of
    # a class that implements the same super class
    counter = 0
    for classIndex, _class in enumerate(_subClasses):
        superClasses = [[0, None]]
        for methodIndex, method in enumerate(_class.methods):
            for parameter in method.parameters:
                paramSuperClasses = getSuperClassByClassName(parameter.type.name)
                if paramSuperClasses != None:
                    for paramSuperClass in paramSuperClasses:
                        id = next((i for i, superClassInfo in enumerate(superClasses)
                                   if paramSuperClass.name in superClassInfo), None)
                        if id != None:
                            superClasses[id][0] += 1
                            goodCandidates.append([classIndex, methodIndex, paramSuperClass.name])
                        else:
                            superClasses.append([1, paramSuperClass.name])
                            goodCandidates.append([classIndex, methodIndex, paramSuperClass.name])
        for superClassInfo in superClasses:
            for candidate in goodCandidates:
                if candidate[2] == superClassInfo[1]:
                    if superClassInfo[0] <= 1:
                        goodCandidates.remove(candidate)

    ##########################################################################
    # if all rules are passed, add index of class to
    # good candidates array and add a comment to it
    # for index in range(len(_subClasses)):
    #     goodCandidates.append(index)

    for c in goodCandidates:
        addCommentIfNotAlreadyDone(path, _subClasses[c[0]].methods[c[1]].position[0],
                                   "// Visitor pattern detected here (Visitor)")

    return True


def hasVisiteeStructure(_class):
    ##########################################################################
    # visitee should have a virtual parent class
    if _class.implements == None:
        return False

    ##########################################################################
    # loop over all methods
    for method in _class.methods:
        goodCandidate = False

        #######################################################################
        # "accept" function must be public (i.e. callable)
        # by visitor
        if 'public' not in method.modifiers:
            break

        #######################################################################
        # accept function should have visitor superclass
        # as parameter
        for parameter in method.parameters:
            if hasVisitorStructure(parameter.type.name):
                goodCandidate = True

        #######################################################################
        # if all rules are passed, add comment
        if goodCandidate:
            addCommentIfNotAlreadyDone(path, method.position[0],
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
        hasVisitorStructure(_class.name)

    file.close()
