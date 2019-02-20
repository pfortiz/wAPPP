#
# datOz18 : ozArgs
# Author: Patricio F. Ortiz
# Date:  February 01, 2019
#
# Version 1.0 Method to handle arguments from the command line or from a
# **kwargs dictionary in order to have a uniform way of generting errors,
# and help messages. 
#
# I may add support for ordered arguments, although I definitively favour
# the key/value approach now

# An additional aim of this package is to help with the documentation, and
# every single element is present, including the default values.
#
# I could even imagine to be able to generate tex documents based on the
# arguments. Nothing else is needed.

# A stupid line to introduce a change

import sys
import numpy as np

version = "1.0.0"


# The kind of arguments is something to be defined (I will
# describe the structure later on)

# Mandatory arguments. Easy to understand, if they are not present, throw error
#
# N must be present from a list of arguments. This is a more complex
# scenario. What it means is that sometimes we need to have one or more
# arguments present from a selection of arguments. They are not optional,
# they are not all mandatory. Those present are given values, the
# non-present are given None values
#
# Optioanl arguments. They may be present, when they are not present, a
# None is assigned to their value, otherwise, its value is assigned

# The results with the arguments is stored in a dictionary, with keys in
# lowercase.

# It is up to de user to define the argument dictionary, or not?

# I could create:
#   addMandatory()
#   addOptional()
#   addSemiOptional()
#   cleanArgs()
#   makeHelp()

# The arguments for each function would be: argName, type, explanation,
# demo-value, [posible-values] and default in the case of optional
# arguments


# Optional arguments are only accepted in the form key=value. But this is
# not necessarily true :-(

# It looks like I will need a positional-optional category, especially if I
# want to use this package to document in other languages, like perl
# Gotta think about this one.

class Argument(object):
#    def __init__(self, _name, _demo, _type, _expl, _pv, _def, _dep):
    def __init__(self, _name, _demo, _type, _expl, _kind, **argos):
        self.identity = "an argument"
        self.name = _name
        self.demo = _demo
        self.type = _type
        self.expl = _expl
        self.kind = _kind
        self.pv = None
        self.pvn = None
        self.pvd = None
        self.default = None
        self.dependsOn = None
        self.example = None
        self.eg = None
        if argos:
            if "pv" in argos:
                self.pv = argos["pv"]
#                print "POSVAL: ", self.pv
                self.pvn = [] # the name
                self.pvd = [] # dictionary with all elements
                for pv in self.pv:
                    self.pvn.append(pv[0])
                    try:
                        needs = pv[3]
                    except:
                        needs = None
                    dic = {"name":pv[0], "expl":pv[1], "demo":pv[2], "must":needs}
                    self.pvd.append(dic)
#                print self.pvn
            if "example" in argos:
                self.example = argos["example"]
            if "default" in argos:
                self.default = argos["default"]
            if "needs" in argos:
                self.dependsOn = argos["needs"]
            if "eg" in argos:
                self.eg = argos["eg"]

    def __str__(self):
        return "---Arguments: {}".format(self.__dict__)


class methods(object):

    t1 = 0
    maxDaysToProcess = 23

    def __init__(self, codeName, uberDict):
        """
            rice is eithher True or False and indicates whether a raise
            condition is thrown (True) or just messages are printed (False)
        """
        self.identifier = 1
        self.cn = "ozArgs"
        self.verbose = True
        self.name = codeName
        self.label = codeName
        self.forceRaise = False
        self.uberD = uberDict
        # optional field using key/value notation
        self.optionalKV = []
        # optional fields by position
        self.optionalFields = []
        # mandatory values in key/value fashion
        self.mandatoryKV = []
        self.nKVMandatory = 0
        # mandatory values in value-only fashion
        self.mandatoryFields = []
        self.nMandatoryFields = 0
        self.allFields = {}
        self.tuttiFields = []
        self.internalMap = {}
        # multiple Choices args (from 1 to whatever), always k/v
        self.multiChoice = {}
        self.usage = None
        self.description = "Generic description"
        self.isComment = False


    # this is kind of basic, but sooner or later I'll have to create an
    # equivalent for web (HTML) and another for LaTeX in order to make
    # things easier.
    def shortHelp(self, pre):
        mappy, theArgs = self.makeMap()
        if self.isComment:
            print self.description,"\n"
            return

        print self.label
#        print "NAME:", self.name
        print "  ",self.description
        if self.name == "main":
            print "  Usage:", self.usage
        else:
            print "  Usage:", pre, self.usage
#        print "   Usage ", self.label, self.usage
        arguments = mappy["all"]
        arguments = theArgs
        for arg in arguments:
            mf = self.allFields[arg]
            if mf.eg is None:
                print "  {}\n    {}".format( mf.name, mf.expl)
            else:
                print "  {} eg, {}\n    {}".format( mf.name, mf.eg, mf.expl)
            if not mf.dependsOn is None:
                print "    {} requires:".format(mf.dependsOn)
            if not mf.default is None:
                print "    Default: {}:".format(mf.default)
            if not mf.pv is None:
                print "    {} can take any of the following values:".format(mf.name)
                ilen = 0
                for pv in mf.pv:
                    olen = len(pv[0])
                    if olen > ilen:
                        ilen = olen
                
                for pv in mf.pv:
    #                print "> Missing argument: %-*s : %s" %(mlen, manda, kvm.expl)
                    if len(pv) > 3:
    #                    self._markReview("{}={}".format(key,value), pv[3], revDic)
                        print "      %-*s: %s"%(ilen, pv[0], pv[1])
                        print "      %-*s: requires: %s"%(ilen, "", pv[3])
                    else:
                        print "      %-*s: %s"%(ilen, pv[0], pv[1])
            if not mf.example is None:
                print "    Example:", mf.example
        print ""
        return

    def showHelp(self, moi):
        mappy, theArgs = self.makeMap()
#        print theArgs
#        print mappy
        paste = []
        arguments = []
        paste.append(moi)
        for mf in self.mandatoryFields:
#            print "MAF", mf
            paste.append(mf.demo)
            arguments.append(mf.name)
        for mf in self.mandatoryKV:
            paste.append(mf.demo)
            arguments.append(mf.name)
        print "Usage ", " ".join(paste)
#        print "Argz:", " ".join(arguments)
#        print "uberD:", self.uberD.keys()
        allArgs = []
        allArgs.extend(self.mandatoryFields)
        allArgs.extend(self.mandatoryKV)
        allArgs = self.allFields

        for arg in theArgs:
#            print "ARGO:", arg
            mf = self.allFields[arg]
            print "  {}\n    {}".format( mf.demo, mf.expl)
            if mf.pv is None:
                continue
            print "  {} can take any of the following values:".format(mf.name)
            ilen = 0
            for pv in mf.pv:
                olen = len(pv[0])
                if olen > ilen:
                    ilen = olen
            
            for pv in mf.pv:
#                print "> Missing argument: %-*s : %s" %(mlen, manda, kvm.expl)
                print "      %-*s: %s"%(ilen, pv[0], pv[1])

        return

        sys.exit()
        for arg in theArgs:
#            for mf in self.mandatoryFields:
            for mf in allArgs:
                print "MF:", mf
                if mf.name == arg:
                    print "  {}\n    {}".format( mf.demo, mf.expl)
#                    print mf.name, mf.demo, mf.expl
                    try:
                        k = self.uberD[arg].allFields[arg]
#                       print "K", k
                        if len(k["pv"]) > 0:
                            print "    where <{}> can be any of the following:".format(arg)
                            for pv in k["pv"]:
                                print "      {} {}\n        {}".format(pv[0], pv[2],pv[1])
                    except:
                        pass
#                       print arg, "OK, carry on"
#            for mf in self.mandatoryKV:
#                if mf.name == arg:
##                    print "  ", mf["demo"], mf.expl
#                    print "  {}\n    {}".format( mf["demo"], mf.expl)
##                    print mf.name, mf["demo"], mf.expl

#    def addKVMandatories(self, mandatoryArray):
#        self.mandatoryKV = mandatoryArray

    def addMandatoryTest(self, name, demo, typo, explanation, **kvargs):
        ent0 = Argument(name, demo, typo, explanation, "test", **kvargs)
        ent0.newName = "shit"
#        print ent0
        print ent0.name
        print ent0.kind
        print "New-name:", ent0.newName
        
    # posVal is an array of arrays describing the possible values,
    # explanation, and usage:
    # [ ["name", "expla", "usage"], ... ]
    def addMandatoryKV(self, name, demo, typo, explanation, **kvargs):
        ent = Argument(name, demo, typo, explanation, "mkv", **kvargs)

#        ent  = { "name":name.lower(), "demo":demo, "type":typo, 
#                 "expl":explanation, "pv":posVal}
        self.mandatoryKV.append( ent )
        self.tuttiFields.append( ent )
        self.allFields[name] = ent
#        self.mandatoryKV.append( { "name":name.lower(),
#                                 "demo":demo, 
#                                 "type":typo, 
#                                 "expl":explanation,
#                                 "pv":posVal} ) 

    def addMandatoryField(self, name, demo, typo, explanation, **kvargs):
        ent = Argument(name, demo, typo, explanation, "mfd", **kvargs)
        self.mandatoryFields.append( ent )
        self.allFields[name] = ent
        self.tuttiFields.append( ent )

    def addSeparator(self, name, demo, typo, explanation, **kvargs):
        ent = Argument(name, demo, typo, explanation, "sep", **kvargs)
#        self.mandatoryFields.append( ent )
#        self.allFields[name] = ent
        self.tuttiFields.append( ent )

    def addOptionals(self, optionalsArray):
        self.optional = optionalsArray

    def addOptionalKV(self, name, demo, typo, explanation, **kvargs):
#        ent = { "name":name.lower(), "demo":demo, "type":typo, 
#                "expl":explanation, "default":default, "pv":posVal}
        ent = Argument(name, demo, typo, explanation, "okv", **kvargs)
        self.optionalKV.append( ent ) 
        self.allFields[name] = ent
        self.tuttiFields.append( ent )

    def addOptionalField(self, name, demo, typo, explanation, **kvargs):
#        ent = { "name":name.lower(), "demo":demo, "type":typo, 
#                "expl":explanation, "default":default, "pv":posVal}
        ent = Argument(name, demo, typo, explanation, "ofd", **kvargs)
        self.allFields[name] = ent
        self.tuttiFields.append( ent )
        self.optionalFields.append(ent) 

    def addDescription(self, description):
        self.description = description

    def asComment(self, comment):
        self.description = comment
        self.isComment = True

    def addLabel(self, label):
        self.label = label

    def addMultiChoice(self, groupID, nPicks, name, demo, typo,
                             explanation, **kvargs):
        try:
            a = self.multiChoice[groupID]["args"]
        except:
            self.multiChoice[groupID] = {}
            self.multiChoice[groupID]["pick"] = nPicks
            self.multiChoice[groupID]["args"] = []
            a = self.multiChoice[groupID]["args"]

        a.append(name) 
#        ent = { "name":name.lower(), "demo":demo, "type":typo, 
#                "expl":explanation, "default":default, "pv":posVal}
        ent = Argument(name, demo, typo, explanation, "okv", **kvargs)
        self.optionalKV.append( ent ) 
        self.allFields[name] = ent
        self.tuttiFields.append( ent )
        
        
        
#    def seeHelp(self):
#        print "Arguments for", self.name
#        for mandy in self.mandatoryKV:
#            print "  {}={} ({}) {}".format(mandy["name"], mandy["demo"],
#                                 mandy["type"], mandy["expl"])
#        for opti in self.optional:
#            print "  [{}={}] ({}) {}".format(opti["name"], opti["demo"],
#                                 opti["type"], opti["expl"])

    def makeMap(self):
        """ internal method to build the internal map """
        mapo = {}
#        present = {}
        theArgs = []
        ordArgs = []
        seq = 0
        # an entry in the map has the form: name, type (mf, mkv, optkv,
        # optord) and possible other things
        mapo["mandatories"] = []
        mapo["present"] = {}
        mapo["usage"] = []
        mapo["ordered-usage"] = []
        mapo["all"] = []
        musa = mapo["usage"]
        pusa = mapo["ordered-usage"]
        mall = mapo["all"]
        mpp = mapo["present"]

        for argos in self.tuttiFields:
            name = argos.name
            kind = argos.kind
#            print "Tutti", name, kind
            if kind == "mfd":
                pusa.append(name)
            elif kind == "ofd":
                pusa.append("[{}]".format(name))
            elif kind == "mkv":
                pusa.append("{}={}".format(name, argos.demo))
            elif kind == "okv":
                pusa.append("[{}={}]".format(name, argos.demo))
            ordArgs.append("{}".format(name))

#            pusa.append(name)
        for argos in self.mandatoryFields:
#            mKeys[argos["name"]] = None
            name = argos.name
            theArgs.append("{}".format(name))
            mapo[name] = { "name":name, "kind":"mf", "seq":seq, "arg":argos }
            mapo["mandatories"].append(name)
            musa.append(name)
            mall.append(name)
            mpp[name] = False
            seq += 1
        for argos in self.optionalFields:
#            name = argos["name"]
#            theArgs.append("[{}]".format(argos["name"]))
            name = argos.name
            theArgs.append("{}".format(name))
            mapo[name] = { "name":name, "kind":"opf", "seq":seq, "arg":argos }
            mpp[name] = False
            musa.append("[{}]".format(name))
            mall.append(name)
            seq += 1

        for argos in self.mandatoryKV:
#            name = argos["name"]
#            theArgs.append("{}={}".format(argos["name"], argos["demo"]))
            name = argos.name
            theArgs.append("{}".format(name))
            mapo[name] = { "name":name, "kind":"nmkv", "seq":seq, "arg":argos }
            mapo["mandatories"].append(name)
            mpp[name] = False
            musa.append("{}={}".format(name, argos.demo))
            mall.append(name)
            seq += 1

        for argos in self.optionalKV:
#            name = argos["name"]
#            theArgs.append("[{}={}]".format(argos["name"], argos["demo"]))
            name = argos.name
            theArgs.append("{}".format(name))
            mapo[name] = { "name":name, "kind":"okv", "seq":seq, "arg":argos }
            mpp[name] = False
            musa.append("[{}={}]".format(name, argos.demo))
            mall.append(name)
            seq += 1

#            oKeys[opti["name"]] = None
#            oArgs.append("[{}={}]".format(opti["name"], opti["demo"]))
#            leDic[opti["name"]] = opti["default"]

#        print "Defining usage"
#        usage = "Usage: {} {} {} {}".format(prePath, self.name, ' '.join(mArgs),
#                            ' '.join(oArgs))

        mapo["nmkv"] = len(self.mandatoryKV)#  + len(self.mandatoryFields)
        mapo["nmf"] = len(self.mandatoryFields)
        mapo["nokv"] = len(self.optionalKV)
        mapo["nof"] = len(self.optionalFields)
        mapo["nargs"] = {"nmkv":0, "nmf":0, "nokv":0, "nof":0}
        self.usage = "{} {}".format(self.label, " ".join(pusa))
        return mapo, ordArgs

    def _markReview(self, key, dependents, revDec):
        for dep in dependents:
            revDec[dep] = key


    def _validate(self, possibleValues, key, value, revDic):
        fail = True
        allVal = []
        for pv in possibleValues:
            pv0 = pv[0]
            allVal.append(pv0)
            if pv0 == value:
                if len(pv) > 3:
                    self._markReview("{}={}".format(key,value), pv[3], revDic)
                fail = False
                break

        if fail:
             print "{} Invalid value '{}', not in {}".format(key, value, allVal)
        return fail

    def check(self, args, prePath):
        __name__ = "check"
#        print "CHECKING: ", self.name
        mappy, theArgs = self.makeMap()
#        print "theArgs:", theArgs
#        print "Mappy:", mappy
        self.nKVMandatory = len(self.mandatoryKV)
#        print "Len(kvmandatory):", self.nKVMandatory, nMandatory
        leDic = {}
        leDic["_argumentsPresent"] = mappy["present"]
        dap = leDic["_argumentsPresent"]
        nArgs = mappy["nargs"]

        usage = "Usage: {} {} {}".format(prePath, self.name, ' '.join(mappy["usage"]))
#                            ' '.join(oArgs))

        # load the different arguments into a dictionary
        fail = False
#        print "ARGS: ", args
#        if len(args) < nmf + nMandatory:
#            print usage
#            fail = True
#            return {}, fail
            
        mfi = 0
        nof = 0
        nNokv = 0
        review = {}
        for arg in args:
#            print "checking ", arg
            if "=" in arg:
                parts = arg.split("=")
                key = parts[0].lower()
                if len(parts) == 2:
                    val = parts[1]
                else:
                    val = "=".join(parts[1:])

                try:
                    ak = mappy[key]["kind"]
                    try:
                        nArgs[ak] += 1
                    except:
                        nArgs[ak] = 1
                except:
                    print "WARNING: Unrecognized argument name:", key
                    continue

#                pv = self.allFields[key].pv
#                if not pv is None:
#                    fail = self._validate(pv, key, val)
#                    
#                depOn = self.allFields[key].dependsOn
#                if not depOn is None:
#                    review[key] = depOn
#
#                dap[key] = True
#                leDic[key] = val

#            except:
#                print "invalid argument", arg, " Not in the form key=value"
#                fail = True
            else:
#                print "arg is passed by mandatory order", arg
                if nNokv < mappy["nmf"]:
                    mandy = self.mandatoryFields[nNokv]
                    mfi += 1
                    try:
                        nArgs["nmf"] += 1
                    except:
                        nArgs["nmf"] = 1
                else:
#                    print "nNokv = ", nNokv
                    nNokv -= mappy["nmf"]
#                    print nNokv, mappy["nof"]
                    if nNokv < mappy["nof"]:
                        mandy = self.optionalFields[nNokv]
                        nof += 1
                        try:
                            nArgs["nof"] += 1
                        except:
                            nArgs["nof"] = 1
                    else:
                        print "Unexpected argument ", arg, "Ignored."
                        nNokv += 1
                        continue
                key = mandy.name
                val = arg

#                pv = self.allFields[key].pv
#                if not pv is None:
#                    fail = self._validate(pv, key, val)
##                print "Assigning", val, "to ", key
#                leDic[key] = val
#                dap[key] = True
##                mfi += 1
                nNokv += 1

            pv = self.allFields[key].pv
            if not pv is None:
                fail = self._validate(pv, key, val, review)
                    
            depOn = self.allFields[key].dependsOn
            if not depOn is None:
#                review.extend(depOn)
                self._markReview(key, depOn, review)

            dap[key] = True
            leDic[key] = val
        
#        if fail:
#            print usage
#            sys.exit()

        if nArgs["nmf"] != mappy["nmf"]:
            fail = True
        if nArgs["nmkv"] != mappy["nmkv"]:
            fail = True

        # Now, I need to check the multiple choice cases, and see if they
        # are present

#        print "MC:", self.multiChoice
        for mc in self.multiChoice.keys():
            mco = self.multiChoice[mc]
#            print mc, mco
            args = mco["args"]
            npick = mco["pick"]
            nn = 0
            for arg in args:
                try:
                    a = leDic[arg]
                    nn += 1
                except:
                    pass
#            print "found: ", nn, "expected: ", npick
            if nn != npick:
                if nn > npick:
                    tag = "only"
                else:
                    tag = ""
                print tag, npick, "of the following arguments must be present, found", nn
                for arg in args:
                    print "< %-*s : %s" %(15, arg, self.allFields[arg].expl)
                fail = True

        if fail:
            mlen = 0
            mandatories = mappy["mandatories"]
            for kvm in mandatories:
                mk = kvm
#                mandaK.append(mk)
                if len(mk) > mlen:
                    mlen = len(mk)
            print usage
            for manda in mandatories:
                kvm = self.allFields[manda]
                try:
                    leDic[manda]
                except:
#                    print "Missing argument: ", manda
                    print "> Missing argument: %-*s : %s" %(mlen, manda, kvm.expl)
                    if kvm.pv is None:
                        continue
                    print ">>    {} must be any of {}".format(manda, kvm.pvn)
                    fail = True

#        print "MUST REVIEW:", review
        for rw in review.keys():
            try:
                a = leDic[rw]
            except:
                print "> Missing argument: {} required by {}".format(rw,review[rw])
                fail = True
        return leDic, fail

        



#    def splitArgs(self, args, nmandatory):
#        __name__ = "splitArgs()"
#        if len(args) < self.nKVMandatory:
#            if self.forceRaise:
#                raise ValueError("{} arguments, expecting {}".format(len(args), nmandatory))
#            else:
#                self.do_showHelp({}, {}, {}, [], [self.laAction])
#        doThis = {}
#        todo = []
#        for arg in args:
#            lcarg = arg.lower()
#            if "=" in lcarg:
#                lcparts = lcarg.split("=")
#                parts = arg.split("=")
#                doThis[lcparts[0]] = parts[1]
#                todo.append(lcparts[0])
#                if lcparts[0] == "src":
#                    doThis["assetsFile"] = parts[1]
#                    assetsFile = parts[1]
#            else:
#                doThis[lcarg] = None
#                todo.append(lcarg)
#    
#    #    print __name__, "AssetsFile: ", assetsFile
#        return (doThis, todo)
#
#
#    def checkPresence(self, doit, mustHave, oneAtLeast):
#        fmh = False
#        answer = {}
#        answer["truth"] = False
#        answer["why"] = []
#        for mh in mustHave:
#            if mh not in doit:
#                print "{}=x not defined".format(mh)
#                answer["why"].append("{}=x not defined".format(mh))
#                fmh = True
#            else:
#                answer[mh] = doit[mh]
#        if fmh:
#            answer["truth"] =  True
#        
#        hasList = False
#        k1 = {}
#        for al1 in oneAtLeast:
#            if "list" in str(type(al1)):
#                hasList = True
#                for p in al1:
#                    k1[p] = 1
#            else:
#                k1[al1] = 1
#                pass
#                
#    
#        koneAtLeast = k1.keys()
#        if set(koneAtLeast) != set(mustHave) and len(koneAtLeast) > 0:
#            foal = False
#    
#            missing = {}
#            for mh in oneAtLeast:
#    #            print __name__, "Looking for", mh
#                if "list" in str(type(mh)):
#                    foal = True
#                    for q in mh:
#    #                    print __name__, "is ", q, "in", mh
#                        if q not in doit:
#                            foal = False
#                            missing[q] = True
#                elif mh in doit:
#    #                print __name__, "I've found", mh
#                    foal = True
#                    ass_et = doit[mh]
#                    if mh == "sensorid":
#                        answer[mh] = self.getSensor(ass_et)
#                    elif mh == "siteid":
#                        answer[mh] = self.getSite(ass_et)
#                    elif mh == "pairid":
#                        answer[mh] = self.getPair(ass_et)
#                    elif mh == "detid":
#                        answer[mh] = self.getDetector(ass_et)
#                    elif mh == "type":
#                        if ass_et == "site" or ass_et == "sensor":
#                            answer[mh] = ass_et
#                        pass
#                    break
#                else:
#                    missing[mh] = True
#            if foal == False:
#    #            print "one of {} must be defined".format(oneAtLeast)
#                print "one of {} must be defined".format(missing.keys())
#                answer["truth"] =  True
#        if answer["truth"]:
#            print "I've failed"
#            return answer
##            sys.xit()
#        return answer
#    
