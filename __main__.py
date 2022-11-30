import sys
from musicshuffle import app

if __name__ == '__main__':
    print("hello - running on python %s.%s" %
        (sys.version_info[0], sys.version_info[1]))
    app.main()