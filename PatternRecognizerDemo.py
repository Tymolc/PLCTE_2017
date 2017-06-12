import javalang

file = open("./VisitorDemo/VisitorDemo.java")
tree = javalang.parse.parse(file.read())
print(tree.children)