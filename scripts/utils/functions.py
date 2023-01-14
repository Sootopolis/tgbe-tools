def type_names() -> list[str]:
    acc = []
    print(("input names (enter blank to stop):"))
    while cur := input().lower().split():
        acc += cur
    return acc
