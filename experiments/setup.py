from components import Setup, print_bold
import json


setup = Setup()
parameters = list(vars(setup).keys())
n = len(parameters)
print_bold("for each parameter, enter without input to use default value")
for i, param in enumerate(parameters):
    print("{} / {}".format(i + 1, n))
    default = getattr(setup, param)
    t = type(default)
    value = input("{} [default = {}]: ".format(param, default))
    if value:
        if isinstance(default, bool):
            setattr(setup, param, bool(int(value)))
        else:
            setattr(setup, param, t(value))
    else:
        setattr(setup, param, default)
with open("setup.json", "w") as stream:
    json.dump(vars(setup), stream, indent=2)
print("setup updated")
