from random import randint

vals = ['P', 'K', 'N']
stats = [0, 0, 0]


def game(games):
    for i in range(games):
        while True:
            print("Podaj swój wybór (P-papier\tK-kamień\tN-nożyce): ", end="")
            player = input().upper()
            if player != "P" and player != "K" and player != "N":
                print("Zły wybór!")
                continue
            else:
                break
        comp: str = vals[randint(0, 2)]
        print("Komputer wybrał: " + comp)

        if player == comp:
            print("REMIS!")
            stats[1] += 1
        elif player == "P":
            if comp == "K":
                print("WYGRAŁEŚ!")
                stats[0] += 1
            else:
                print("PRZEGRAŁEŚ!")
                stats[2] += 1
        elif player == "K":
            if comp == "N":
                print("WYGRAŁEŚ!")
                stats[0] += 1
            else:
                print("PRZEGRAŁEŚ!")
                stats[2] += 1
        else:
            if comp == "P":
                print("WYGRAŁEŚ!")
                stats[0] += 1
            else:
                print("PRZEGRAŁEŚ!")
                stats[2] += 1

    print("Koniec gry!\nTwoje statystyki:\nRozegrane gry: {}\nWygrane: {}\nRemisy: {}\nPrzegrane: {}\n".format(games,
                                                                                                               stats[0],
                                                                                                               stats[1],
                                                                                                               stats[
                                                                                                                   2]))
    if stats[0] > stats[2]:
        print("WYGRAŁEŚ!")
    elif stats[2] > stats[0]:
        print("PRZEGRAŁEŚ!")
    else:
        print("ZREMISOWAŁEŚ!")


if __name__ == "__main__":
    print("Witaj w grze papier, kamień, nożyce!")
    try:
        print("Podaj liczbe rund: ", end="")
        rounds = int(input())
        game(rounds)
    except ValueError:
        print("Podano złą wartość na wejściu!")
        exit()
