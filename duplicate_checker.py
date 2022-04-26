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


while True:
    command = input("enter command - output (o), check (c), input(i), quit (q): ").lower()

    if command not in ('o', 'c', 'i', 'q'):
        print('invalid command')
        continue

    if command == 'q':
        break

    with open('invited.txt', 'r') as file:
        invited = file.read().strip(' \n').split('\n')

    if command == 'o':
        print('players invited:')
        for player in invited:
            print(player, end=' ')
        print(f'\ntotal: {len(invited)}')
        continue

    players = type_names()
    invited = set(invited)
    old = []
    new = []
    for player in players:
        if player in invited:
            old.append(player)
        else:
            new.append(player)
    print(f'duplicates: ({len(old)})')
    for player in old:
        print(player, end=' ')
    print()
    print(f'new players: ({len(new)})')
    for player in new:
        print(player, end=' ')
    print()

    if command == 'i':
        confirm = input("confirm inviting the new players by typing 'Y': ")
        if confirm == 'Y':
            invited = list(invited)
            invited += new
            invited.sort()
            with open('invited.txt', 'w') as file:
                file.write('\n'.join(invited))
            print(f'{len(new)} players invited')
