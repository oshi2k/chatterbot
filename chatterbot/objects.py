import re
import sys
import importlib
import threading
from socket import socket, AF_INET, SOCK_STREAM
from tomorrow import threads
from helpers import pp, is_command
from commands import *


class Command(object):
    def __init__(self, chat, message):
        self.chat = chat
        self.message = message
        self.command = message.message.split()[0][1:].lower()

    def _fire(self):
        function = getattr(importlib.import_module('chatterbot.commands.{}'.format(self.command)),
                           self.command)
        reply = function(self.message)

        if reply:
            self.chat.send_message(str(reply), channel=self.message.channel.name)

    def exists(self):
        return 'chatterbot.commands.{}'.format(self.command) in sys.modules.keys()

    def run(self):
        threading.Thread(target=self._fire).start()


class Channel(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def get_viewers(self):
        pass

    def get_game(self):
        pass


class Message(object):
    def __init__(self, **kwargs):
        self.type = 'unknown'
        self.sender = ''
        self.message = ''
        self.channel = ''

        if 'type' in kwargs:
            self.type = kwargs['type']
        if 'sender' in kwargs:
            self.sender = kwargs['sender']
        if 'message' in kwargs:
            self.message = kwargs['message']
        if 'channel' in kwargs:
            self.channel = kwargs['channel']

    def __repr__(self):
        return self.message


class Chat(object):
    def __init__(self, config):
        self._config = config
        self._channels = {}
        self._messages = []
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._connect()

    def _connect(self):
        self._socket.connect((self._config.server['host'], self._config.server['port']))
        self.send_message('USER {}'.format(self._config.login['username']))
        self.send_message('PASS {}'.format(self._config.login['password']))
        self.send_message('NICK {}'.format(self._config.login['username']))
        self.send_message('JOIN {}'.format(','.join(['#{}'.format(channel) for channel in self._config.channels])))

    def _handle_data(self, data):
        match = re.match(r'^:.+\!.+@([a-zA-Z0-9_]+)\.tmi\.twitch\.tv PRIVMSG #([a-zA-Z0-9_]+) :(.*)$', data)

        if match:
            channel = Channel(match.group(2))
            sender = match.group(1)
            message = match.group(3)
            if is_command(message):
                type = 'command'
            else:
                type = 'message'
            self._messages.append(Message(type=type, sender=sender, channel=channel, message=message))

        if data == 'PING: ':
            self.send_message('PONG tmi.twitch.tv')

    def get_messages(self):
        messages = self._messages
        self._messages = []
        return messages

    def send_message(self, message, channel=''):
        if not channel:
            self._socket.send(b'{}\r\n'.format(message.encode('utf8')))
        else:
            self._socket.send(b'PRIVMSG #{0} :{1}\r\n'.format(channel, message.encode('utf8')))

    def join_channel(self, channel_name):
        self.send_message('JOIN #{}'.format(channel_name))
        self._channels[channel_name] = Channel(channel_name)

    def leave_channel(self, channel_name):
        self.send_message('PART #{}'.format(channel_name))
        del self._channels[channel_name]

    @threads(1)
    def run(self):
        while True:
            data = self._socket.recv(1024)

            if data:
                self._handle_data(data)


class ChatterBot(object):
    def __init__(self, config):
        self.chat = Chat(config)

    def run(self):
        self.chat.run()

        while True:
            messages = self.chat.get_messages()

            if not messages:
                continue

            for message in messages:
                if message.type == 'command':
                    command = Command(self.chat, message)
                    if command.exists():
                        command.run()

                pp(message.message, message.type, message.sender, message.channel.name)
