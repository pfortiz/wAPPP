# #!/usr/bin/python
# broken hash-bang to force this script to be run as python <name> <args>
# to make it work across sites

# Script to transfer a list of files from a remote server for a specific
# date. It could be one file or a number of files
#
# ftp address, username, password and destination directory will be
# configurable (readable from the first argument). Second argument shall be
# the date in format YYYY-MM-DD
#
# We could use wget, but that remains to be seen. In fact, it sounds like a
# good idea, but we have to make sure that if we use it, Darren will be
# able to use it at ACRI from his virtual machine
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
if nargs < 3:
    print "Usage: ", sys.argv[0], "description-file YYYY-MM-DD"
    sys.exit()

dataFile = sys.argv[1]
laDate = sys.argv[2]
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

user     = "dazghent"
kwd      = "be10mbre"
site     = "ftp.copernicus.vgt.vito.be"
site     = fdict["ftpsite"]
lpath    = fdict["localPath"]
rpath    = fdict["remotePath"]
mode     = fdict["dateDir"]
project  = fdict["project"]

if "product" in fdict:
    product  = fdict["product"]


dcomp = laDate.split("-")
remoteDir = rpath
year = dcomp[0]
month = dcomp[1]
day = dcomp[2]
dateTag =  "{}{}{}".format(year, month, day)
localDir =  lpath + "/{}{}{}-tmp".format(year, month, day)
if project == "ostia":
    localDir =  lpath + "/{}/{}".format(year, month)
    dateTag =  "{}{}{}".format(year, month, day)
    remoteDir = rpath + "/{}/{}".format(year, month)
elif project == "phobos":
    dateTag =  "{}{}".format(year, dcomp[3].zfill(3))
    localDir =  lpath + "/{}".format(year)
    remoteDir = rpath + "/{}".format(year)

#print "From: ", remoteDir, " to ", localDir
#print "DateTag: ", dateTag

root = []
rot = []
ftp = None
try:
#    print "try connection to ", site
#    ftp = FTP_TLS(site, user, kwd)
    #[host[, user[, passwd[, acct[, keyfile[, certfile[, context[, timeout]]]]]]]])
    ftp = FTP(site, user, kwd)
except Exception, e:
    print "ftp-error", e
#    ftp.close()
    sys.exit()
#    print "message after connection: ", ftp.error_reply

#print "attempting cwd ", remoteDir
try:
#    ftp.login(user=user, passwd=kwd)
    ftp.dir(root.append)
    ftp.retrlines('MLSD', rot.append)

#    ftp.cwd(remoteDir)
except Exception, q:
    print "ftp-erroR ", q
    ftp.close()
    sys.exit()
#    print "Exception caught message after cwd: ", ftp.error_reply

#print "managed to change to ", remoteDir

nextracted = 0;
for l in root:
    parts = l.split()
    name = parts[-1]
#    print "dirs: ", name, l
    ftp.cwd(name)
    sub1 = []
    ftp.dir(sub1.append)
    for l1 in sub1:
        parts = l1.split()
        name = parts[-1]
#        print "sub1: ", name, l1
        ftp.cwd(name)
        sub2 = []
        ftp.dir(sub2.append)
        for l2 in sub2:
            parts = l2.split()
            lasty = len(parts)-1
            name = parts[-1]
            size = parts[lasty-4]
            isize = int(size)
            if dateTag in name and not "xml" in name:
                # we can extract
#                print "sub2: ", name
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
                    except Exception, x:
                        print "ftp-error: ", x
                        ftp.close()
                        sys.exit()
                nextracted += 1
#            else: 
#                print "!SUB2: ", name


#for l in rot:
#    print "DIRS: ", l

#sys.exit()
#
#
#there = []
#ftp.dir(there.append)
#psizes = {1:1}
#nextracted = 0
#for line in there:
#    parts = line.split()
#    lasty = len(parts)-1
#    name = parts[lasty]
#    size = parts[lasty-4]
#    isize = int(size)
##    print line, "?"
##    if dateTag in line:
##        print name, isize
#         
##        print datetime.datetime.now()


ftp.close()
if nextracted > 0:
    print "Successful-ftp"
elif nextracted == 0:
    print "Nothing-to-retrieve"
else:
    print "Unsuccessful-ftp"


sys.exit()

