import os
import sys


def printTree(path, level):
    if level == 0:
        print(path)
    for elem in os.listdir(path):
        full = os.path.join(path, elem)

        for i in range(level):
            print("\t", end="")

        print("|--" + elem)

        if os.path.isdir(full):
            printTree(full, level+1)


if __name__ == "__main__":
    printTree(sys.argv[1], 0)
