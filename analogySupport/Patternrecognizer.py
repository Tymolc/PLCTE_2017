import sublime
import sublime_plugin

import sys
from os.path import dirname

# request-dists is the folder in our plugin
sys.path.append(dirname(__file__))

import javalang

class Comment(object):
    def __init__(self, path, position, text):
        self.path = path
        self.position = position
        self.text = text

def insertLine(comment):
    global offset
    file = open(comment.path, "r")
    contents = file.readlines()
    file.close()

    file = open(comment.path, "a")
    file.seek(0)
    file.truncate()
    contents.insert(comment.position + offset - 1, comment.text + "\n")
    file.writelines(contents)
    file.close()

    offset += 1

def addComment(path, position, value):
    global comments
    comments.append(Comment(path, position, value))

def addCommentIfNotAlreadyDone(path, position, value):
    global commentedAlready

    if position not in commentedAlready:
        commentedAlready.append(position)
        addComment(path, position, value)

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

def hasVisitorStructure(className):
    global classes
    goodCandidates = []  # [classIndex, methodIndex]

    ###########################################################################
    # Visitor should have super class,
    # find classes that have className as super class
    _subClasses = [c for c in classes if c.implements != None and
                   any(imp.name == className for imp in c.implements)]

    if len(_subClasses) == 0:
        return False

    ###########################################################################
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

        #######################################################################
        # filter candidates whose superclass only occurs once
        for superClassInfo in superClasses:
            for candidate in goodCandidates:
                if candidate[2] == superClassInfo[1]:
                    if superClassInfo[0] <= 1:
                        goodCandidates.remove(candidate)

    ###########################################################################
    # if all rules are passed, add a comment to method
    for c in goodCandidates:
        addCommentIfNotAlreadyDone(path, _subClasses[c[0]].methods[c[1]].position[0],
                                   "// Visitor pattern detected here (Visitor)")

    if len(goodCandidates) > 0:
        return True
    else:
        return False


def hasVisiteeStructure(_class):
    ###########################################################################
    # visitee should have a virtual parent class
    if _class.implements == None:
        return False

    ###########################################################################
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

def doesLazyInitialization(_body, field):
    ###########################################################################
    # check if there is a check that instance is non
    ifStatements = [child for child in _body if type(child) is javalang.tree.IfStatement]
    for ifStatement in ifStatements:
        if ifStatement.condition.operator == "==" and \
           ifStatement.condition.operandl.member == field.declarators[0].name and \
           ifStatement.condition.operandr.value == "null":
           return True

    return False

def hasSingletonStructure(_class):
    goodCandidates = []
    instanceFieldCandidates = []
    possibleComments = []

    ###########################################################################
    # singleton should have a private static field that holds the instance
    for field in _class.fields:
        if {'private', 'static'}.issubset(field.modifiers):
            instanceFieldCandidates.append(field)

    ###########################################################################
    # singleton should have a public static accessor method that returns
    # instance
    for method in _class.methods:
        for field in instanceFieldCandidates:
            if method.return_type.name == field.type.name:
                if doesLazyInitialization(method.body, field):
                    possibleComments.append(Comment(path, field.position[0],
                        "// Singleton pattern detected here (Instance Field)"))
                    possibleComments.append(Comment(path, method.position[0],
                        "// Singleton pattern detected here (Accessor Function)"))

    publicCtors = [ctor for ctor in _class.constructors if "public" in ctor.modifiers]

    ###########################################################################
    # all constructors should be private or protected
    if len(publicCtors) == 0:
        for comment in possibleComments:
            addCommentIfNotAlreadyDone(comment.path, comment.position, comment.text)

# ------------------------------------------------------------------------------

offset = 0
classes = []
path = ''
commentedAlready = []
comments = []

class Patternrecognizer(sublime_plugin.TextCommand):
    def run(self, edit):
        global path
        path = self.view.file_name()
        global comments
        with open(self.view.file_name(), "r") as file:
            tree = javalang.parse.parse(file.read())

            # collect all classes
            for structure, node in tree.filter(javalang.tree.ClassDeclaration):
                classes.append(node)

            for _class in classes:
                hasVisiteeStructure(_class)
                hasVisitorStructure(_class)
                hasSingletonStructure(_class)

            file.close()

            comments = sorted(comments, key=lambda comment: comment.position)

            for comment in comments:
                insertLine(comment)
###############################################################################
# sort comment by position to avoid misalignment


