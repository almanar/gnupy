#
# Copyright Michael Groys, 2015
#
import argparse
import sys
import os
from bin_utils import *

def parseOptions(args):
    if len(args)<1 or (args[0] not in ["dos2unix", "unix2dos"]):
        print >> sys.stderr, "Program name should be either uni2dos or dos2unix"
        sys.exit(1)
    if args[0] == "unix2dos":
        unix2dos = True
        parser = argparse.ArgumentParser(prog="unix2dos", description='UNIX to DOS text file format converter',
                                         usage="unix2dos [-o file ...] [-n infile outfile ...]\ndos2unix [-o file ...] [-n infile outfile ...]")
    elif args[0] == "dos2unix":
        unix2dos = False
        parser = argparse.ArgumentParser(prog="dos2unix", description='DOS to UNIX text file format converter',
                                         usage="dos2unix [-o file ...] [-n infile outfile ...]\ndos2unix [-o file ...] [-n infile outfile ...]")
    
    parser.add_argument('-n', '--newfile', metavar="infile  outfile", nargs="+", dest="newFiles",  action=ExtendAction, help="Converts infile to outfile provided in pairs")
    parser.add_argument('-o', '--oldfile', metavar="file", nargs="+", dest="files", action=ExtendAction, help="Convert files in place")
    parser.add_argument('files',           action=ExtendAction,  metavar="file", nargs='*',  help="Files to convert")

    options = parser.parse_args(args[1:])
    options.unix2dos = unix2dos
    return options

options = parseOptions(sys.argv[1:])

if options.newFiles and len(options.newFiles)%2 != 0:
    print >> sys.stderr, "new files (-n infile outfile ...) should be specified in pairs"
    sys.exit(1)

if options.unix2dos:
    readFlag = "rb"
    writeFlag = "w"
else:
    readFlag = "r"
    writeFlag = "wb"

tempSuffix = ".unix2dos.tmp.423"
rc = 0
# convert newFiles
if options.newFiles:
    for fromId in range(0, len(options.newFiles), 2):
        fromFileName = options.newFiles[fromId]
        toFileName = options.newFiles[fromId+1]
        try:
            with open(fromFileName, readFlag) as fromFile, open(toFileName, writeFlag) as toFile:
                copyStream(fromFile, toFile)
        except Exception as e:
            print >>sys.stderr, str(e)
            rc=1

# convert new files
if options.files:
    for fromFileName in expandFiles(options.files):
        toFileName = fromFileName + tempSuffix
        try:
            with open(fromFileName, readFlag) as fromFile, open(toFileName, writeFlag) as toFile:
                copyStream(fromFile, toFile)
        except Exception as e:
            print >>sys.stderr, str(e)
            rc=1
            
        replace(toFileName, fromFileName)

# if no new/old files were provided - do it wit stdin to stdout
if not options.files and not options.newFiles:
    if options.unix2dos:
        reopenFileInBinMode(sys.stdin)
    else:
        reopenFileInBinMode(sys.stdout)
    copyStream(sys.stdin, sys.stdout)
    
sys.exit(rc)
