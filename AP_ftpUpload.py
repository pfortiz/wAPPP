# # !/usr/bin/python
# broken hash-bang to force this script to be run as python <name> <args>
# to make it work across sites


# Script to transfer a list of files from a local server for a specific
# date to a remote server. 
#
# ftp address, username and password will be configurable (readable from the
# first argument).
#
# The second argument shall be the local-path -pointing to a directory where
# files are to be exported.

# The third argument shall be the remote-path This directory shall be created
# by this script if it doesn't exist.
#
#
# The fourth argument is optional, and it should be a particular pattern
# which file-names must contain in order to be included in the list of
# files to transfer.
#
# [Files already in the system with identical size to the remote ones are
# not transferred.] NOT TRUE at the moment
#
#
#   Author: Patricio F. Ortiz
#   Date:   March 22 + 31, 2017
#
#  After testing uploading data to ftp.acri.fr using uname=ftp_globtemp:
#
#   Ftp to acri is not always successful in creating the paths.
#   I'm not sure if this happens with other servers as well, but from
#   previous experience, ACRI did have problems with the creation of new
#   paths even when using ftp from perl.
#
#   When something fails, the script quits giving the Unsuccessful-ftp message,
#   which should be interpreted by AP_task-manager as a fail. No more details
#   given.
#
#   It is probably wise to give the task-manager the chance to launch a
#   ftp-tasks a number of times if it fails, particularly if transmitting
#   to ACRI
#
#   Midnight is approaching fast... and so is my access to Alice :-) :-)



daysInMonths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
daysInYear = sum(daysInMonths)

import sys
import os.path
import datetime

from ftplib import FTP

nargs = len(sys.argv)
#print "arguments: ", sys.argv, nargs
if nargs < 4:
    print "Usage: ", sys.argv[0], "description-file local-path remote-path [pattern]"
    sys.exit()

dataFile = sys.argv[1]
localDir = sys.argv[2]
remoteDir = sys.argv[3]
if nargs == 5:
    dateTag = sys.argv[4]
else:
    dateTag = ""

e = os.path.isfile(dataFile)
if e == 0: 
#    print dataFile, " does not exist. Quiting"
    print "Unsuccessful-ftp"
    sys.exit()

# check that local directory exists, otherwise print a message
if not os.path.isdir(localDir):
#    print localDir, " does not exist. Quiting"
    print "Unsuccessful-ftp"
    sys.exit()

# if it exist, let's change to that directory
os.chdir(localDir)

# Now, get a list of the files in that directory, and pick up only the ones
# which match a pattern (if present)

lfiles = os.listdir(localDir)
#print lfiles

lfilesize = {}
slfiles = []
if dateTag != "":
    for f in lfiles:
        if dateTag in f:
            slfiles.append(f)
            lfilesize[f] = os.path.getsize(f)
else:
    for f in lfiles:
        slfiles.append(f)
        lfilesize[f] = os.path.getsize(f)


#print lfilesize

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
#    print "Tryng to open connection to ", site
    ftp = FTP(site)
except Exception, e:
#    print "ftp-error", e
    print "Unsuccessful-ftp"
    ftp.close()
    sys.exit()
#    print "message after connection: ", ftp.error_reply

#print "attempting cwd ", remoteDir
try:
#    print "Tryng to login ", site
    ftp.login(user=user, passwd=kwd)
except Exception, e:
#    print "ftp-error", e
    print "Unsuccessful-ftp"
    ftp.close()
    sys.exit()

#print "in ", site
try:
    # we need to check whether remote directory exists, otherwise, create
    # it using ftp.CreateRemoteDir(remoteDir)
#    print "Exception caught message after cwd: ", ftp.error_reply
    path = remoteDir.split("/");
#    print path
    if path[0] == "":
        del path[0]  
    pathos = ""
    there = []
    here = []
    ftp.dir(there.append)
    for ew in there:
        dcomp = ew.split(" ")
        here.append(dcomp[-1])
#    print "HERE: ", here
    for p in path:
#        print "in ", p, " ::: ", here
        if p in here:
            there = []
            here = []
            ftp.cwd(p)
            ftp.dir(there.append)
            for ew in there:
                dcomp = ew.split(" ")
                here.append(dcomp[-1])
        else:
            ftp.mkd(p)
            ftp.cwd(p)
            there = []
#        pathos += " ", p

#    By the time we complete this loop, we should be sitting in remoteDir
#    ftp.cwd(remoteDir)
except Exception, e:
#    print "oops, ", pathos, " or ", remoteDir , " could not be created.", e
    print "Unsuccessful-ftp"
    sys.exit()

nuploaded = 0
ftp.sendcmd("TYPE i")
maxAttempts = 20     # We don't want this to go to an infinite loop
for f in slfiles:
    rsize = 0
    nAttempts = 0
    while rsize != lfilesize[f]: # try until the file uploaded is correct
        ftp.storbinary('STOR '+f, open(f, 'rb'))
#        print "trying with ", f
        rsize = ftp.size(f)
        nAttempts += 1
        if nAttempts > maxAttempts:
            break
    nuploaded += 1
ftp.close()

if nuploaded == len(slfiles):
    print "Successful-ftp"
else:
    print "Unsuccessful-ftp"
