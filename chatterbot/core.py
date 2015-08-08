import config
from objects import ChatterBot
from helpers import get_oauth_password


def main():
    if not config.login['password']:
        config.login['password'] = get_oauth_password()

    ChatterBot(config).run()
