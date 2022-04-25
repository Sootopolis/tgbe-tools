def input_names():
    names = []
    print("Input names:")
    while True:
        name = input().lower().split()
        if name:
            names += name
        else:
            break
    names.sort()
    return names
