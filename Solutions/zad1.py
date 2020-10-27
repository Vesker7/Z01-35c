import os
import sys


def printFilesWithExtension(directory, extension):
    files = os.listdir(directory)

    for file in files:
        if file.endswith(extension):
            print(file)


if __name__ == "__main__":
    printFilesWithExtension(sys.argv[1], sys.argv[2])
