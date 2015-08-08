from helpers import get_args, validate_args

def add(message):
    args = get_args(message)

    if validate_args(args, r'([0-9]\s)+'):
        return sum(map(int, args))
