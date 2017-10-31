import qrcode

def main():
    string = 'Hello World'
    print(string)
    qr = qrcode.make(string).show()


if __name__ == '__main__':
    main()