
from chat_client_class import *

def main():
    import argparse
    parser = argparse.ArgumentParser(description='chat client argument')
    parser.add_argument('-d', type=str, default=None, help='server IP addr')
    args = parser.parse_args()
    args.d = '10.209.3.65'
    client = Client(args)
    client.run_chat()

main()
