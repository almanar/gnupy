#
# Copyright Michael Groys, 2014
#
import sys
from bin_utils import *

usage = "Usage: wc  <file>...\n  Calculates line/word/character count"

exitOnInterrupt()

if len(sys.argv)>1 and sys.argv[1] in ["-h", "--help"]:
    print usage
    sys.exit()
else:
    files = expandFiles(sys.argv[1:])


def wc(fileObj, fileNameToPrint):
    lines = 0
    words = 0
    chars = 0
    for line in fileObj:
        lines += 1
        words += len(line.split())
        chars += len(line)
    if fileNameToPrint:
        print "%s\t%d\t%d\t%d" % (fileNameToPrint, lines, words, chars)
    else:
        print "%d\t%d\t%d" % (lines, words, chars)

if files:
    for fileName in files:
        if fileName == "-":
            wc(sys.stdin, "<stdin>")
        else:
            try:
                fileObj = open(fileName, "r")
            except Exception as e:
                print >> sys.stderr, str(e)
                sys.exit(1)
            wc(fileObj, fileName)
            fileObj.close()
else:
    wc(sys.stdin, None)
