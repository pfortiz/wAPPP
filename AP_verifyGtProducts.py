# #! /usr/bin/env python2.7
# breaking the hash-bang means that this script needs to be given to python
# as an argument, needing the same treatment across sites.

#########################################################################
# DISCLAIMER:
# 
# The University of Leicester cannot accept any responsibility for the
# accuracy and completeness of the computer code contained in this file.
# 
# The programs in this file should not be redistributed to any other parties
# without the permission of the University of Leicester Earth Observation
# Science Group.
#########################################################################

# 
# Patricio Ortiz,
# March 10, 2017

# python2.7 works at CEMS
# plain python works at Alice

# Script to examine the contents of all files located in a given directory,
# identifying first the  product type (the last component of its path
# name), and figure out from a database the characteristics of the
# product(s) to examine and go and validate as much as possible


import sys
#sys.path.append(plotPath)

# to access netCDF4, do the following next:
# module load python/2.7.3
# else, alter the sys/path in order to include that path into the current
# path, quite likely, the preferred approach 

#import netCDF4_utils as netCDF4
from netCDF4 import Dataset
import numpy as np
import os.path
import math
import numbers
import socket
import string


# put the functions here.

def examineFile(theFileName, component, theGdic, theGlobs, theDims, theVars, \
                theVarDict, errors ):
#    print "hello there {}".format(theFileName)
    # is it a valid netcdf file?


    status = 0
    lerrors = []
    try:
        # if there is a problem
        ncfile = Dataset(theFileName, 'r')
    except:
        # catch it and report it as failed in a comment line
        err =  "error Invalid netCDF "
#        print err
        errors.append(theFileName)
        errors.append(err)
#        nErrors += 1
        status = -1
        return status

    fgat = ncfile.ncattrs()
    fgdic = {1:1}
    for gat in fgat:
        atv = getattr(ncfile,gat)
        fgdic[gat] = atv
        tatv = type(atv)
        try:
            rat = theGdic[gat]
            if rat == "undef":
                continue
#            print "File: ", gat, type(atv), atv
#            print "Tmpt: ", gat, type(rat), rat
            if tatv == unicode:
                atv = '"' + atv + '"'
                if atv != rat:
                    err =  "error: gatt-mismatch: {} template: {} v file: {}".format(gat, rat,atv)
#                    print err
                    lerrors.append(err)
                    fail = 1
            elif tatv == np.int32 or tatv == np.int16:
                uv = int(atv)
                av = int(rat)
                if av != uv:
                    err =  "error: gatt-mismatch: {} template: {} v file: {}".format(gat, rat,atv)
                    lerrors.append(err)
                    fail = 1
            elif tatv == np.float32:
                uv = float(atv)
                if rat[-1] == "f":
                    rat = rat[:-1]
                av = float(rat)
                if abs(av - uv) > 1e-5:
                    err =  "error: gatt-mismatch: {} template: {} v file: {}".format(gat, rat,atv)
                    lerrors.append(err)
                    fail = 1
        except:
            err =  "error: gatt-not-in-template: {}".format(gat)
            lerrors.append(err)
            fail = 1

    for dk in md[theGlobs]:
        try:
            a = fgdic[dk[0]]
        except:
            err =  "error: gatt-missing: {}".format(dk[0])
            lerrors.append(err)
            fail = 1

    # what about its dimensions?
    dims = ncfile.dimensions.keys()
#    print dims
    fail = 0
    for ld in theDims:
        try:
            dime = ncfile.dimensions[ld[0]]
            dimValue =  len(dime)
        except:
            err =  "error: Dimension {} not in".format(ld[0])
            lerrors.append(err)
#            print err
            fail = 1
            continue

        if ld[1] == "undef":
#            print "ignore", ld[1], dimValue
            pass
        else:
            if int(ld[1]) != int(dimValue):
                err =  "error: Dimension {} = {} not {}".format(ld[0], dimValue, ld[1])
                lerrors.append(err)
                fail = 1
#                print err
#            print ld[1], dimValue

    if fail == 1:
        errors.append(theFileName)
#        nErrors += 1
        for e in lerrors:
            errors.append(e)
        status = -1
        return status

#    sys.exit();
    # test the number of LST valid pixels right away
    if component == "_LST_":
        try:
            lst = ncfile.variables['LST'][:]
            if isinstance(lst, np.ma.MaskedArray):
                validLst = lst.count()
                if validLst == 0:
                    err = "error: no valid LST pixels"
#                    print err
                    errors.append(theFileName)
                    errors.append(err)
                    status = -1
                    return status
    #            if validLst == 1:
    #                print stheFileName, " single valued LST."
        except:
            errors.append(theFileName)
#            nErrors += 1
            errors.append("error: has no LST variable.")
            status = -1
            return status
        
 
    nc_vars = [var for var in ncfile.variables]
#    print nc_vars
    for nv in  nc_vars:
#        print "whole var: ", nv
#        print "just name: ", nv.name
        if nv not in theVarDict:
            err =  "error: Variable {} not expected.".format(nv)
            lerrors.append(err)
            fail = 1
#            print "variable ", nv, " not in the template"
#        else:
#            print "variable ", nv, " is in the template :-)"

#    print fvars, lstVars
    # it is,  let's examine its variables
    fail = 0
    for lv in theVars:
        vname = lv[0]
        vmin = lv[1]
        vmax = lv[2]
#        vdim1 = lv[3]
#        vdim2 = lv[4]
#        print "{}-VAR: {}".format(component,vname)
        try:
            var1 = ncfile.variables[vname][:]
#            print "XT- ", vname, vmin, vmax
            if vmin != "---" and vmax != "---":
#                print vname, vmin, vmax
                vmin = float(vmin)
                vmax = float(vmax)
#                print vmin, vmax
                v1min = var1.min()
                v1max = var1.max()
#                if v1min == v1max:
#                    nmasked = var1.count()
                if v1min < vmin:
#                    print "Min Comparing ", vname, " ", v1min, " vs ", vmin
#                    err = "error: OOR Min "+ vname+ " : "+ v1min+ " < "+ vmin
                    err =  "error: OOR Min {} : {} < {}".format(vname, v1min, vmin)
#                    print err
                    lerrors.append(err)
                    fail = 1
                if v1max > vmax:
#                    print "Max Comparing ", vname, " ", v1max, " vs ", vmax
#                    err =  "error: OOR Max "+ vname+ " : "+ v1max+ " > "+ vmax
                    err =  "error: OOR Max {} : {} > {}".format(vname, v1max, vmax)
#                    print err
                    lerrors.append(err)
                    fail = 1
                
            # try now with the variable attributes
            # attributes in the dictionary:
            atKey = "{}{}_atts".format(component,vname)
            vatD = {1:1}
#            print "template attributes for ", vname, atKey, md[atKey]
            for tat in md[atKey]:
                vatD[tat[0]] = tat[1]
#                print "T-att: ", vname, tat[0], tat[1]
#            print "file variable attributes: "
#            for nv in  nc_vars:
#                if nv == vname:
#                    print "varIDS: ", nv, vname
#                    break
#            nc_atts = [att for att in ncfile.variables[nv]]
            ncvar = ncfile.variables[vname]
            fatt =  ncfile.variables[vname].ncattrs()
#            print fatt
            fvatD = {1:1}
            for fvat in fatt:
#                aval = getattr(ncvar,fvat)
#                fvatD[fvat] = getattr(ncvar,fvat)
                fvatD[fvat] = getattr(ncvar,fvat)
#                print "kind of attribute", vname, fvat, type(fvatD[fvat])
                if fvat not in vatD:
#                    print vname, fvat, getattr(ncvar,fvat), " unneeded."
#                    print vname, fvat, aval, " unneeded."
                    err =  "error: non-required {}.{}".format(vname,fvat)
#                    print err
                    lerrors.append(err)
                    fail = 1
#                else:
#                    pass
#                    print vname, fvat, getattr(ncvar,fvat), " OK."

            for tat in md[atKey]:
#                vatD[tat[0]] = tat[1]
                an = tat[0];
                av = tat[1];
                if an not in fvatD:
#                    print "T-MIA: ", vname, an, av
                    err =  "error: missing-attribute {}.{}".format(vname,an)
#                    print err
                    lerrors.append(err)
                    fail = 1
                elif av != "undef":
                    typat = type(fvatD[an])
                    if typat == unicode:
                        if fvatD[an] == "":
                            print "< ", av,"\n> ", uv
#                        print "It picked up unicode"
                        uv = '"' + fvatD[an] + '"'
                        if av != uv:
#                            print "AKDR: ", vname, an, av, uv
#                        else:
#                            print "RATS!: ", vname, an, av, uv
                            err =  "error: att-mismatch {}.{} : template: {} v file: {}".format(vname,an, av, uv)
                            print err
                            fail = 1
                            lerrors.append(err)
                    elif typat == np.int16 or typat == np.int32:
#                        print "It picked up numpy.int16 or numpy.int32"
                        uv =  int(fvatD[an])
                        av = int(av)
                        if av != uv:
#                            print "iAKDR: ", vname, an, av, uv
#                        else:
#                            print "iRATS!: ", vname, an, av, uv
#  err =  "error: att-mismatch {}.{} : {} v {}".format(vname,an, av, uv)
                            err =  "error: att-mismatch {}.{} : template: {} v file: {}".format(vname,an, av, uv)
#                            print err
                            lerrors.append(err)
                            fail = 1
                    elif typat == np.float32:
#                        print "It picked up numpy.float32"
                        uv = float(fvatD[an])
                        av = float(av)
                        if abs(av - uv) > 1e-5:
                            err =  "error: att-mismatch {}.{} : template: {} v file: {}".format(vname,an, av, uv)
                            lerrors.append(err)
                            fail = 1
                    elif typat == np.ndarray:
#                        print "It picked up numpy.ndarray"
#                        print "template: ", type(av), av
                        aaaa = fvatD[an]
#                        satv = np.array_str(fvatD[an])
                        satv = "{}".format(aaaa[0]);
#                        print "file: ", satv
                        for aa in aaaa[1:]:
                            satv = satv + ", {}".format(aa)
#                        print "file: ", satv
                        if av != satv:
#                            print "sAKDR: ", vname, an, av, satv
#                        else:
#                            print "sRATS!: ", vname, an, av, satv
#                            err =  "error: att-mismatch {}.{} : {} v {}".format(vname,an, av, satv)
                            err =  "error: att-mismatch {}.{} : template: {} v file: {}".format(vname,an, av, satv)
#                            print err
                            lerrors.append(err)
                            fail = 1
#                    if '"' in av:
#                        uv = '"' + fvatD[an] + '"'
#                        if av == uv:
#                            print "AKDR: ", vname, an, av, uv
#                        else:
#                            print "RATS!: ", vname, an, av, uv
#                    elif ',' in av:
#                        print "Found comma in ", an, av
##                        uv = '"' + type(fvatD[an]) + '"'
#                        print "Found comma in ", an, av, type(fvatD[an])
#                        if av == uv:
#                            print ",AKDR: ", vname, an, av, uv
#                        else:
#                            print ",RATS!: ", vname, an, av, uv
#                    else:
##                        uv = fvatD[an]
#                        uv = float(fvatD[an])
#                        av = float(av)
#                        if abs(av - uv) < 1e-7:
#                            print "nAKDR: ", vname, an, av, uv
#                        else:
#                            print "nRATS!: ", vname, an, av, uv

#                    uv.replace('"')
#                    if av == fvatD[an]:
                    
        except:
#            print vname, " not present in ", theFileName, RuntimeError
            err = "error: {} not present.".format(vname)
#            print err
            lerrors.append(err)
            fail = 1
#            break

    # this is the point where we should start comparing the global
    # attributes for each file

    if fail == 1:
#        nErrors += 1
        errors.append(theFileName)
        for e in lerrors:
            errors.append(e)
        status = -1
    else:
        status = 1

    return status


# now the general code (main)

host = socket.gethostname()


topPath = ""
if "jc.rl.ac.uk" in host:
    topPath = "/group_workspaces/cems/leicester/"
else:   # case Alice
    topPath = "/data/atsr/"

productDB = topPath + "GT_PRODUCT_DB"
#print host, productDB

#sys.exit()


nargs = len(sys.argv)
#print "arguments: ", sys.argv, nargs
if nargs < 2:
    print "Usage: ", sys.argv[0], "directory-path"
    sys.exit()
#print unicode
#print int
#sys.exit()

path = sys.argv[1]
e = os.path.exists(path)

if e == 0: 
    print "Invalid path ", path
    sys.exit()

#words = path.split("/");
w = path.split("/");
product = w[-1]
#print "{}/{}/{}/{}".format(w[-4],w[-3],w[-2],w[-1])
dbfile = productDB+"/"+product+".mdata"
#print "product to examine: ", product
#print "dbFile to examine: ", dbfile

e = os.path.exists(dbfile)
if e == 0: 
    print dbfile, " does not exist"
    sys.exit()

with open(dbfile) as f:
    dblines = f.readlines()

theComponents = []
md = {1 : 1} 
lstVarDict = {1 : 1}
auxVarDict = {1 : 1}
component = ""
varKey = ""
for line in dblines:
    allParts = []
    # get rid of newline and trailing blanks
    l = line.rstrip()
    if line[0] == "#": 
        continue
    wds = l.split(" ");
    nwds = len(wds)
    fstwd = wds[0]
    if fstwd == "components":
        allParts = wds[1:]
#        print l, allParts
    elif fstwd == "component":
        component = wds[1]
#        print "Compo: ", component
        theComponents.append(component)
        varKey = component+"variables"
        varGlob = component+"globatts"
        md[varKey] = []
        md[varGlob] = []
    elif fstwd == "dimensions":
        current = "dimensions"
        key = component+"dimensions"
        md[key] = []
    elif fstwd == "dimension":
        if nwds > 2:
            allParts = wds[1:]
        else:
            allParts = [wds[1],"undef"]
        md[key].append(allParts)
        
#    elif fstwd == "globalAttributes":
#        varName = wds[1]
#        allParts = wds[1:]
#        md[varKey].append(allParts)
#        varAtt = component+varName + "_atts"
#        md[varAtt] = []

    elif fstwd == "gat":
        gatName = wds[1]
        if nwds > 2:
            if '"' in wds[2]:
                allParts = ' '.join(wds[2:])
            else:
                allParts = wds[2]
        else:
            allParts = "undef"
        md[varGlob].append([gatName, allParts])

    elif fstwd == "var":
        current = "variables"
        varName = wds[1]
        allParts = wds[1:]
        md[varKey].append(allParts)
        varAtt = component+varName + "_atts"
        md[varAtt] = []

    elif fstwd == "varat":
        # wds[2] can be empty
        if nwds > 2:
            if '"' in wds[2] or ',' in l:
                allParts = ' '.join(wds[2:])
            else:
                allParts = wds[2]
        else:
            allParts = "undef"
        md[varAtt].append([wds[1], allParts])
    else:   # anything else
        pass

#    print l, nwds

#print "And now, the components... ", theComponents
#print "And the dictionary\n", md



lstVarTag = "_LST_variables";
lstDimTag = "_LST_dimensions";

lstVars = md[lstVarTag]
lstDims = md[lstDimTag]

auxVarTag = "_AUX_variables";
auxDimTag = "_AUX_dimensions";

auxVars = md[auxVarTag]
auxDims = md[auxDimTag]

for lv in lstVars:
    vname = lv[0]
    lstVarDict[vname] = 1

for lv in auxVars:
    vname = lv[0]
    auxVarDict[vname] = 1

examine_variables_only = 0

if examine_variables_only == 1:
    print "LST variables", lstVars
    for lv in lstVars:
        lenv = len(lv)
        print "LSTVAR: ", lenv
        vname = lv[0]
        att_tag = "_LST_"+ vname + "_atts"
        vats = md[att_tag]
        vmin = lv[1]
        vmax = lv[2]
        vdim1 = lv[3]
    #    vdim2 = lv[4]
        print "LSTVAR: ", vname, vdim1
        for bat in vats:
            print vname, ":", bat
    sys.exit()

lstVarGlob = "_LST_" +"globatts"
lstgdic = {1:1}
for dk in md[lstVarGlob]:
    lstgdic[dk[0]] = dk[1]

auxVarGlob = "_AUX_" +"globatts"
auxgdic = {1:1}
for dk in md[auxVarGlob]:
    auxgdic[dk[0]] = dk[1]

filesToExamine = os.listdir(path)
nLstFiles = 0
nAuxFiles = 0
nLstErrors = 0
nauxErrors = 0
errors = []
for sfileName in filesToExamine:
    fileName = path+"/" + sfileName
    if "_LST" in fileName:
        COMP = "_LST_"
        nLstFiles += 1

#        if nLstFiles > 3:
#            break


        lerrors = []
        status = 0
        status = examineFile(fileName, COMP, lstgdic, lstVarGlob, lstDims,\
                lstVars, lstVarDict, errors)
#        print status, fileName 
        if status < 0:
            nLstErrors += 1

        afileName = sfileName
        afileName = string.replace(afileName,"_LST_", "_AUX_", 1)
#        print "auxFile: ", afileName
        sfileName = path+"/" + afileName
        if not os.path.exists(sfileName):
            err = "No AUX file for {}".format(fileName)
            if status == 0:
                errors.append(fileName)
            errors.append(err)
            continue
        nAuxFiles += 1

        status = examineFile(sfileName, "_AUX_", auxgdic, auxVarGlob, \
                    auxDims, auxVars, auxVarDict, errors)
#        print status, sfileName 
        if status < 0:
            nauxErrors += 1



print "{}/{}/{}/{} {} {}   {} {}".format(w[-4],w[-3],w[-2],w[-1], nLstFiles, nLstErrors, nAuxFiles, nauxErrors)
print "NLstFiles: ", nLstFiles
print "NLstFilesWithErrors: ", nLstErrors
print "NauxFiles: ", nAuxFiles
print "NauxFilesWithErrors: ", nauxErrors

for e in errors:
    print e


sys.exit()

