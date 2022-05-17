###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
# Notes

#--------------------------------------------------------------------
# Set global constants
#--------------------------------------------------------------------

import sys
import wini

import AdminConfig
import AdminControl

#version number of config file must match version number expected by this script
CONFIG_VERSION = '1.0'

'''Read in config file, check for config format version, check cell and node exist as named in file, and check for other common errors.'''
def validateConfigFile(configFile):
    try:
        print "\n"  
        print "---------------------------------------------------------------"
        print " Read in config file "
        print " configFile:                    "+str(configFile)
        print "---------------------------------------------------------------"
        
        # wini.py reads windows-style ini files & returns nested dict named 'cfgDict'
        cfgDict=wini.load(open(configFile))
    
        configInfo = cfgDict['configInfo']
        confver=configInfo['confver'].strip()
        if (confver != CONFIG_VERSION):
            print "Version numbers of configFile and this script must match."
            print "   Version of configFile: " + str(confver)
            print "   Version of script: " + str(CONFIG_VERSION)
            sys.exit("CONFIG_VERSION mismatch")
    
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()

        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        if serverInfoDict:
            nodeList = "nodeList not defined yet"
            for serverInfoKey in serverInfoDict.keys():  # for each server
                si = serverInfoDict[serverInfoKey]
                nodeList = si['nodeList'].split()
                nodeHostList = si['nodeHostList'].split()
                if len(nodeList) != len(nodeHostList):
                    print "Config file must supply a host name for \n  every node in node list in server clause, and vice versa"
                    sys.exit("host alias and node list mismatch")

        # checking if the required value exists
        path='/Cell:'+cellName+'/'
        cellId= AdminConfig.getid(path)
        wsadminCell = AdminControl.getCell( )
        if (len(cellId) == 0):
            print "\nThe cell you are connected to: " + wsadminCell + " does not match cell: " + cellName + " specified in config file."
            print "Cell name must exactly match name specified in config file."
            sys.exit("wrong cell")

        print "Target cell found: \n    " + cellId
        if serverInfoDict:

            print "Target nodes found: "

            for nodeName in nodeList:
                path='/Node:'+nodeName+'/'
                nodeId= AdminConfig.getid(path)
                if (len(nodeId) == 0):
                    print "\nThe specified node: " + nodeName + " does not exist."
                    print "Node(s) must already exist with name(s) as defined in config file."
                    sys.exit("can't find node")
                #print "Found wsadmin config id for node: " + nodeName
                print "    " + nodeId
    except:
        print "\n\nException in validateConfigFile() when checking general config & cell info"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
        
    return cfgDict
    


