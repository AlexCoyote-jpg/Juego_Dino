# main.py
import argparse
from core.app import run_app

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    run_app(debug=args.debug)

if __name__ == "__main__":
    main()