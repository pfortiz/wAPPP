# #!/usr/bin/python
# broken hash-bang to force this script to be run as python <name> <args>
# to make it work across sites


# Script to transfer a list of files from a remote server for a specific
# date. It could be one file or a number of files
#
# ftp address, username and password will be configurable (readable from the
# first argument).
#
# Second argument shall be the remote-path (pointing to a directory
# where files to transfer must exist)
#
# Third argument shall be the local-path -pointing to a directory where
# files are to be transferred. This directory shall be created if it
# doesn't exist.
#
# The fourth argument is optional, and it should be a particular pattern
# which file-names must contain in order to be included in the transfer.
#
# Files already in the system with identical size to the remote ones are
# not transferred.
#
#
#   Author: Patricio F. Ortiz
#   Date:   March 2, 2017




daysInMonths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
daysInYear = sum(daysInMonths)

import sys
import os.path
import datetime

from ftplib import FTP

nargs = len(sys.argv)
#print "arguments: ", sys.argv, nargs
if nargs < 4:
    print "Usage: ", sys.argv[0], "description-file remote-path local-path [pattern]"
    sys.exit()

dataFile = sys.argv[1]
remoteDir = sys.argv[2]
localDir = sys.argv[3]
if nargs == 5:
    dateTag = sys.argv[4]
else:
    dateTag = ""

e = os.path.isfile(dataFile)
if e == 0: 
    print dataFile, " does not exist. Quiting"
    sys.exit()

lynes = tuple(open(dataFile, 'r'))
forcePush = 1

lines = [line.rstrip('\n') for line in lynes]

fdict = {}

for l in lines:
    if "#" in l or l == "":
        continue
    key, val = l.split('=')
    fdict[key] = val
#    print key, val

user     = fdict["uname"]
kwd      = fdict["pwd"]
site     = fdict["ftpsite"]

try:
    ftp = FTP(site)
except Exception, e:
    print "ftp-error", e
    ftp.close()
    sys.exit()
#    print "message after connection: ", ftp.error_reply

#print "attempting cwd ", remoteDir
try:
    ftp.login(user=user, passwd=kwd)
    ftp.cwd(remoteDir)
except:
    print "ftp-error"
    ftp.close()
    sys.exit()
#    print "Exception caught message after cwd: ", ftp.error_reply

#print "managed to change to ", remoteDir

there = []
ftp.dir(there.append)
psizes = {1:1}
nextracted = 0
for line in there:
    parts = line.split()
    lasty = len(parts)-1
    name = parts[lasty]
    size = parts[lasty-4]
    isize = int(size)
#    print line, "?"
    if dateTag in line:
#        print name, isize
        if not os.path.isdir(localDir):
            os.makedirs(localDir)
        fileName = localDir + "/" + name
#        print fileName
        lFileSize = 0;
        if os.path.exists(fileName):
            lFileSize = os.path.getsize(fileName)
        while lFileSize != isize:
            file = open(fileName, 'w')
            try: 
                ftp.retrbinary('RETR '+name, file.write)
                lFileSize = os.path.getsize(fileName)
#                print lFileSize, " l-x ", isize

#                if lFileSize == isize:
#                    break
            except:
                print "ftp-error"
                ftp.close()
                sys.exit()
        nextracted += 1
         
#        print datetime.datetime.now()


ftp.close()
if nextracted > 0:
    print "Successful-ftp"
else:
    print "Unsuccessful-ftp"


sys.exit()

