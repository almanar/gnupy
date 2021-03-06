#
# Copyright Michael Groys, 2014
#
import sys
import re
import optparse
from bin_utils import *


usage = "Usage: %prog [<options>] <PATTERN>  [<file>]..."
parser = optparse.OptionParser(usage=usage, version="1.0", prog="grep")
def help_callback(option, opt_str, value, parser, *args, **kwargs):
    parser.print_help()
    sys.exit(1)

def parseOptions():
    parser.add_option("-i", "--ignore-case", dest="ignore_case", action="store_true",
                      help="Ignore case distinctions  in  both  the PATTERN and the input files.")
    parser.add_option("-H", "--with-filename", dest="with_filename", action="store_true",
                      help="Print the filename for each match.")
    parser.remove_option("-h")
    parser.add_option("--help", action="callback", callback=help_callback)
    parser.add_option("-h", "--no-filename", dest="no_filename", action="store_true",
                      help="Suppress the  prefixing of filenames on output when multiple files are searched.")
    parser.add_option("-n", "--line-number", dest="lineno", action="store_true",
                      help="Prefix each line of output with the line number within its input file.")
    parser.add_option("-q", "--quiet", "--silent", dest="silent", action="store_true",
                      help="Do not write anything. Exit immediately with 0 if match was found")
    parser.add_option("-r", "-R", "--recursive", dest="recursive", action="store_true",
                      help="Read all files under each directory, recursively")
    parser.add_option("-U", "--binary", dest="binary", action="store_true",
                      help="Reads file in binary mode")
    parser.add_option("-v", "--invert-match", dest="invert", action="store_true",
                      help="Invert the sense of matching, to select non-matching lines.")
    parser.add_option("--include", dest="include_pattern",
                      help="Recurse in directories only searching file matching PATTERN.")
    parser.add_option("--exclude", dest="exclude_pattern",
                      help="Recurse in directories skip file matching PATTERN.")
    parser.add_option("-A", "--after-context", dest="after_context", metavar="num", type="int", default=0,
                      help="Print NUM lines of trailing context after matching lines. Places a line containing a group separator (--) between contiguous groups of matches.")

    (options, args) = parser.parse_args()
    return (options, args)

(options, args) = parseOptions()

def getRecursive(files):
    import fnmatch
    filesOut = []
    for file in files:
        if os.path.isfile(file):
            filesOut.append(file)
        else:
            filesOut.extend(getTreeFiles(file, options.include_pattern, options.exclude_pattern))
    return filesOut

if len(args) == 0:
    parser.print_usage(sys.stderr)
    print >>sys.stderr, "Try `grep --help' for more information."
    sys.exit(2)
elif len(args) == 1:
    files = ["/dev/stdin"]
else:
    files = expandFiles(args[1:])

if options.recursive:
    files = getRecursive(files)

pattern = args[0]

try:
    compileFlags = 0
    if options.ignore_case:
        compileFlags |= re.IGNORECASE
         
    regexp = re.compile(pattern, compileFlags)
except re.error as e:
    print >>sys.stderr, "Invalid regular expression:", str(e)
    sys.exit(2)

count_matches = 0
if options.invert:
    invert = True
else:
    invert = False

if options.binary:
    openFlags = "rb"
else:
    openFlags = "r"

def dump_text(filename, lineno, text):
    print text,
def dump_lineno_text(filename, lineno, text):
    print ("%d:" % lineno), text,
def dump_filename_text(filename, lineno, text):
    print "%s:" % filename, text,
def dump_filename_lineno_text(filename, lineno, text):
    print "%s:%d:" % (filename, lineno), text,
def dump_silent(filename, lineno, text):
    pass

if options.silent:
    dumpFunc = dump_silent
elif len(files) == 1 and not options.recursive:
    if options.with_filename:
        if options.lineno:
            dumpFunc = dump_filename_lineno_text
        else:
            dumpFunc = dump_filename_text
    elif options.lineno:
        dumpFunc = dump_lineno_text
    else:
        dumpFunc = dump_text
else:
    if options.no_filename:
        if options.lineno:
            dumpFunc = dump_lineno_text
        else:
            dumpFunc = dump_text
    else:
        if options.lineno:
            dumpFunc = dump_filename_lineno_text
        else:
            dumpFunc = dump_filename_text

for fileName in files:
    linesToPrint = -1
    if fileName == "/dev/stdin":
        fileObj = sys.stdin
        reopenFileInBinMode(sys.stdin)
    else:
        try:
            fileObj = open(fileName, openFlags)
        except Exception as e:
            print >> sys.stderr, str(e)
            sys.exit(3)
    lineno = 0
    if invert:
        for line in readlineGenerator(fileObj):
            match = regexp.search(line)
            lineno += 1
            if not match:
                count_matches += 1
                if linesToPrint >= 0 and (options.after_context>0):
                    print "--"
                linesToPrint = options.after_context + 1
            if linesToPrint > 0:
                dumpFunc(fileName, lineno, line)
            linesToPrint -= 1
    else:
        for line in readlineGenerator(fileObj):
            match = regexp.search(line)
            lineno += 1
            if match:
                count_matches += 1
                if linesToPrint >= 0 and (options.after_context>0):
                    print "--"
                linesToPrint = options.after_context + 1
            #print "linesToPrint", linesToPrint
            if linesToPrint > 0:
                dumpFunc(fileName, lineno, line)
            linesToPrint -= 1
    if fileObj != sys.stdin:
        fileObj.close()

if count_matches:
    sys.exit(0)
else:
    sys.exit(1)
