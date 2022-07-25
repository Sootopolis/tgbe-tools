def update_invited(usernames: list[str]):
    confirm = input("confirm inviting these players by typing 'Y': ")
    if confirm == "Y":
        with open("invited.txt", "r") as file:
            invited = file.read().strip(" \n").split("\n")
        invited += usernames
        invited.sort()
        with open("invited.txt", "w") as file:
            file.write("\n".join(invited))
        print(f"{len(usernames)} players invited")
    else:
        print("confirmation failed. please update manually later.")


def print_bold(s: str, end="\n", sep=" "):
    print("\033[1m" + s + "\033[0m", end=end, sep=sep)


def type_names():
    names = []
    print("input names:")
    while True:
        name = input().lower().split()
        if name:
            names += name
        else:
            break
    return names
