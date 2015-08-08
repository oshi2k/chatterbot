def pp(message, type='info', sender='', channel=''):
    output = '[{}]'.format(type.upper())

    if type in ['message', 'command']:
        output += ' [#{}]'.format(channel)
        output += ' {}:'.format(sender)

    output += ' {}'.format(message)

    print output


def get_oauth_password():
    pp('Please visit http://twitchapps.com/tmi/ to generate your OAuth password')
    return raw_input('Enter your OAuth token: ')


def is_command(message):
    return message.startswith('!')
