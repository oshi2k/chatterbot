import os
from helpers import pp
from core import main

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        os._exit(0)
