import sys


def printSorted(lista):
    try:
        liczby = list(map(int, lista))
        liczby.sort()
        print(liczby)
        return liczby
    except ValueError:
        print("Wszystkie argumenty muszą być liczbami!")
        return


if __name__ == "__main__":
    printSorted(sys.argv[1:])
