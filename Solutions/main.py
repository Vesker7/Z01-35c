# Tree node
class Node(object):
    def __init__(self, value, left = None, right = None):
        self.value = value
        self.left = left
        self.right = right

    def __str__(self):
        return str(self.value)

# Func to get operator priority
def getPriority(c):
    if c == "(":
        return 0
    elif c == "+" or c == "-" or c == ")":
        return 1
    elif c == "*" or c == "/":
        return 2


# Func to convert infix arithmetic expression to postfix
def toPostfix(expression):
    result = ""
    stack = []

    for character in expression:
        if character in "0123456789.":
            result += character
        elif character in "+-*/":
            result += " "
            while stack != [] and getPriority(character) <= getPriority(stack[-1]):
                result += stack.pop() + " "
            stack.append(character)
        elif character == "(":
            stack.append(character)
        elif character == ")":
            try:
                while stack[-1] != "(":
                    result += " " + stack.pop()
                stack.pop()
            except IndexError:
                print("BŁĄD: W wyrażeniu źle umieszczono nawiasy!")
                exit()

    while stack:
        tmp = stack.pop()
        if tmp in "()":
            print("BŁĄD: W wyrażeniu źle umieszczono nawiasy!")
            exit()
        else:
            result += " " + tmp

    return result


#Build expression tree from infix arithmetic expression
def buildTree(infix_expression):
    stack = []
    postfix = toPostfix(infix_expression)
    tmp = ""
    # print("PREFIX: " + postfix)
    for character in postfix:
        if character in "0123456789.":
            tmp += character
        elif character == " ":
            if tmp != "":
                node = Node(float(tmp))
                stack.append(node)
            tmp = ""
        else:
            right_child = stack.pop()
            left_child = stack.pop()
            parent = Node(character, left_child, right_child)
            stack.append(parent)

    root = stack.pop()
    print(infix_expression + " = ", end = "")
    return root


def evaluate(root):
    if root is None:
        return 0
    if root.left is None and root.right is None:
        return root.value

    left_eval = evaluate(root.left)
    right_eval = evaluate(root.right)

    if root.value == "+":
        return left_eval + right_eval
    elif root.value == "-":
        return left_eval - right_eval
    elif root.value == "*":
        return left_eval * right_eval
    elif root.value == "/":
        return left_eval / right_eval


def printTree(node, level=0):
    if node != None:
        printTree(node.left, level + 1)
        print(" " * 8 * level + "--| ", end = " ")
        print(str(node.value) + " |")
        printTree(node.right, level + 1)


if __name__ == "__main__":
    tree = buildTree("((2+7)/3+(14-3)*4)/2")
    print(evaluate(tree), end = "\n\n\n")
    printTree(tree)
