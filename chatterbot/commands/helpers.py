import re

def validate_args(args, regex):
    return re.match(r'{}'.format(regex), ' '.join(args))

def get_args(message):
    return message.message.split()[1:]
