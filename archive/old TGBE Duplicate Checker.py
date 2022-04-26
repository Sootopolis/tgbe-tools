def binary_search(name, namelist):
    if len(namelist) == 0:
        return False, 0
    if len(namelist) == 1:
        if name == namelist[0]:
            return True, 1
        if name < namelist[0]:
            return False, 0
        else:
            return False, 1
    left = 0
    right = len(namelist) - 1
    mid = (left + right) // 2
    while left <= right:
        mid = (left + right) // 2
        if name < namelist[mid]:
            right = mid - 1
        elif name > namelist[mid]:
            left = mid + 1
        else:
            return True, mid
    else:
        return False, max(mid, left)


def names_input(names, namelist):
    duplicates = []
    new = []
    for name in names:
        bi = binary_search(name, namelist)
        if bi[0]:
            duplicates.append(name)
        else:
            new.append(name)
            namelist.insert(bi[1], name)
    print("Successfully added ({}):".format(len(new)))
    print(*new) if len(new) else print("(None)")
    print("Duplicates avoided ({}):".format(len(duplicates)))
    print(*duplicates) if len(duplicates) else print("(None)")
    return " ".join(namelist)


def check_duplicates(names, namelist):
    new = []
    duplicates = []
    for name in names:
        bi = binary_search(name, namelist)
        if bi[0]:
            duplicates.append(name)
        else:
            new.append(name)
    print("New names ({}):".format(len(new)))
    print(*new) if len(new) else print("(None)")
    print("Duplicates found ({}):".format(len(duplicates)))
    print(*duplicates) if len(duplicates) else print("(None)")
    return


def clever_input():
    names = []
    print("Input names, separate by new lines or spaces:")
    while True:
        name = input().lower().split()
        if name:
            names += name
        else:
            break
    names.sort()
    return names


while True:
    command = input("Enter command - Input(I), Output(O), Check(C), Quit(Q):\n").upper()
    if command == "I":
        usernames = clever_input()
        with open("../invited.txt", "r") as file:
            invited = file.readline().strip().split()
        with open("../invited.txt", "w") as file:
            file.write(names_input(usernames, invited))
        print()
    elif command == "O":
        with open("../invited.txt", "r") as file:
            invited = file.readline().strip().split()
        print("Current list: ({})".format(len(invited)))
        print(*invited) if len(invited) else print("(None)")
        print()
    elif command == "C":
        with open("../invited.txt", "r") as file:
            invited = file.readline().strip().split()
        usernames = clever_input()
        check_duplicates(usernames, invited)
        print()
    elif command == "Q":
        break
    else:
        print("Invalid command.")
        print()
