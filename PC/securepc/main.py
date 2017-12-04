import logging
from ui.welcome import welcome

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    welcome()


if __name__ == '__main__':
    main()
