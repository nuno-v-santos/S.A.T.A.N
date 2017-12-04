import logging
from ui.main import MainUI

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    ui = MainUI()
    ui.start()


if __name__ == '__main__':
    main()
