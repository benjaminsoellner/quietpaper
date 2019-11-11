import daemon
import sys
from quietpaper.config import controller as QPC

def main():
    QPC.loop()

if __name__ == "__main__":
    main()