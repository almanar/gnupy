#
# Copyright Michael Groys, 2015
#
import argparse
import sys
import os
import stat
import time
from bin_utils import *

options=None
def filenameKey(fileEntry):
    return fileEntry[0].lower()
def sizeKey(fileEntry):
    return fileEntry[1].st_size
def timeKey(fileEntry):
    global options
    # by default sort order is time decreasing thus minus
    return -options.timeFunc(fileEntry[1])
def extKey(fileEntry):
    root,ext = os.path.splitext(fileEntry[0].lower())
    return (ext, root)
def dirFirstKey(fileEntry):
    isDir = stat.S_ISDIR(fileEntry[1].st_mode)
    return (not isDir, fileEntry[0])

def getMTime(st):
    return st.st_mtime
def getATime(st):
    return st.st_atime
def getCTime(st):
    return st.st_ctime

def parseOptions():
    parser = argparse.ArgumentParser(prog="ls", description='list directory contents', usage="ls [OPTION]... [FILE]...")
    parser.add_argument('-a', '--all', dest="all", action='store_true',  help="show hidden files")
    parser.add_argument('-r', '--reverse', dest="reverse", action='store_true',  help="reverse sort")
    parser.add_argument('-f', dest="dont_sort", action='store_true',  help="do not sort")
    parser.add_argument("-l", dest="long", action="store_true", help="use a long listing format")
    parser.add_argument("-1", dest="single_line", action="store_true", help="list one file per line")
    parser.add_argument("-d", "--directory", dest="list_dir", action="store_true",
                        help="list directories themselves, not their contents")
    parser.add_argument("-F", "--classify", action="store_true", help="append indicator (one of */) to entries")
    parser.add_argument("-S", dest="sortKey", action="store_const", const=sizeKey, help="sort by size")
    parser.add_argument("-t", dest="sortKey", action="store_const", const=timeKey, help="sort by modification time")
    parser.add_argument("-X", dest="sortKey", action="store_const", const=extKey, help="sort by extension")
    parser.add_argument("-D", "--group-directories-first", dest="sortKey", action="store_const", const=dirFirstKey, help="group directories before files")
    parser.add_argument("-c", dest="timeFunc", action="store_const", const=getCTime, help="with -lt, sort and show creation instead of modification time")
    parser.add_argument("-u", dest="timeFunc", action="store_const", const=getATime, help="with -lt, sort and show last access instead of modification time")
    parser.set_defaults(sortFunc=filenameKey, timeFunc=getMTime)
    parser.add_argument('files', metavar="file", nargs='*', help="Files list")

    return parser.parse_args()

options = parseOptions()
if not options.files:
    files = []
else:
    files = expandFiles(options.files)

doStat = options.all or (options.sortKey is not filenameKey) and (options.sortKey is not extKey)

def shouldPrint(fileName, stat):
    if options.all or not fileName.startswith("."):
        return True
    else:
        return False

def pjoin(d, f):
    if not d:
        return f
    else:
        return os.path.join(d,f)

def sortFiles(files):
    if options.dont_sort:
        return files
    return sorted(files, key=options.sortKey, reverse=options.reverse)

attrMask = { 0: "---", stat.S_IROTH: "r--", stat.S_IWOTH: "-w-", stat.S_IXOTH: '--x',
             stat.S_IROTH+stat.S_IWOTH: "rw-", stat.S_IROTH+stat.S_IXOTH: "r-x",
             stat.S_IROTH+stat.S_IWOTH+stat.S_IXOTH: "rwx", stat.S_IWOTH+stat.S_IXOTH: "-wx"}

def getAttr(fullPath, st):
    attr = ""
    mode = st.st_mode
    isDir = stat.S_ISDIR(mode)
    attr += "d" if isDir else "-"
    attr += attrMask[(mode & stat.S_IRWXU)>>6]
    attr += attrMask[(mode & stat.S_IRWXG)>>3]
    attr += attrMask[(mode & stat.S_IRWXO)]
    return attr
    
def printItem(d, f, st=None):
    if not shouldPrint(f[0], stat):
        return
    if not options.long:
        print f[0]
    fullPath = pjoin(d,f[0])
    if not st:
        try:
            st = os.stat(fullPath)
        except Exception as e:
            print >>sys.stderr, "stat %s: %s" % (fullPath, str(e))
    attr = getAttr(fullPath, st)
    item = "%s  %10d  %s  %s" % (attr, st.st_size, time.ctime(options.timeFunc(st)), f[0])
    if options.classify:
        if stat.S_ISDIR(st.st_mode):
            item += os.path.sep
        elif st.st_mode & stat.S_IXUSR:
            item += '*'

    print item

def listdir(d):
    global doStat
    files = []
    for f in os.listdir(d):
        if doStat:
            st = os.stat(os.path.join(d,f))
        else:
            st = None
        files.append( (f, st) )
    return files

def printDir(d, printName=None):
    try:
        files = listdir(d)
    except Exception as e:
        print >>sys.stderr, "Dir listing failed:",  str(e)
        sys.exit(1)
    if printName:
        print
        print "%s:" % printName
    for f in sortFiles(files):
        printItem(d, f)
    if printName:
        print   

#print files
if files:
    for f in files:
        if os.path.isdir(f) and not options.list_dir:
            printDir(f, printName=f if len(files)>1 else None)
        else:
            printItem("", (f, None))
else:
    printDir(".")
        
    

