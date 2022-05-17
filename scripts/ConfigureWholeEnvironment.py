###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
# Notes
#   This "master" i.e. top-level Jython script includes the following procedures:
#       validateConfigFile(configFile)
#       createEnvironmentFromConfigFile(configFile)
#   
#
#   . . . . which call the following Jython scripts (not listed in order):
#   Configurator.py
#   wini.py (config file parser)
#
# Call this script specifying properties file that in turn specifies a python "profile" script to be run that will
#  cause the wsadmin objects to be available to all levels of scripts
#
#   It is required to explicitly "import" sub-scripts into each script that will call them
#
#   Special requirements:
#   Config dir path, Config file (as paramsto script)    
#   This script quits if a cell and server nodes as named in config file are not found in target WAS installation
#   Version number of config file & script must match
#
###############################################################################


import sys
import time

#see "main" method for lots more import statements



#version number of config file must match version number expected by this script
SCRIPT_CONFIG_VERSION = '.12'

#--------------------------------------------------------------------
# Read in config file
# Check for config format version
# Check cell and node exist as named in file
#--------------------------------------------------------------------
def validateConfigFile(configFile):
    try:
        print "\n"  
        print "---------------------------------------------------------------"
        print " Read in config file "
        print " configFile:                    "+configFile
        print "---------------------------------------------------------------"
        print "\n"
        
        # wini.py reads windows-style ini files & returns nested dict named 'cfgDict'
        cfgDict=wini.load(open(configFile))
    
        configInfo = cfgDict['configInfo']
        confver=configInfo['confver'].strip()
        if (confver != SCRIPT_CONFIG_VERSION):
            print "Version numbers of configFile and this script must match."
            print "   Version of configFile: " + str(confver)
            print "   Version of script: " + str(SCRIPT_CONFIG_VERSION)
            sys.exit(1)
    
        environmentGenInfo = cfgDict['cellInfo']
        
        cellName = environmentGenInfo['cellName'].strip()
        nodeList = environmentGenInfo['nodeList'].split()
    
        # make sure we have a host alias for every node
        if len(environmentGenInfo['nodeHostList']) > 0:
            nodeHostList = environmentGenInfo['nodeHostList'].split()
        if len(nodeList) != len(nodeHostList):
            print "Config file must supply a host name for \n  every node in node list in cellInfo, and vice versa"
            sys.exit(1)

        # checking if the required value exists
        path='/Cell:'+cellName+'/'
        cellId= AdminConfig.getid(path)
        if (len(cellId) == 0):
            print "\nThe specified cell: " + cellName + " does not exist."
            print "Cell must already exist with name as defined in config file."
            sys.exit(1)

        print "Target cell: \n    " + cellId
        print "Target node list: "

        for nodeName in nodeList:
            path='/Node:'+nodeName+'/'
            nodeId= AdminConfig.getid(path)
            if (len(nodeId) == 0):
                print "\nThe specified node: " + nodeName + " does not exist."
                print "Node(s) must already exist with name(s) as defined in config file."
                sys.exit(1)
            #print "Found wsadmin config id for node: " + nodeName
            print "    " + nodeId
    except:
        print "\n\nException in validateConfigFile() when checking general config & cell info"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
        
    return cfgDict
    



#--------------------------------------------------------------------
# Create WAS environment from config file
# (cell and node must already exist as named in file)
#--------------------------------------------------------------------
def createEnvironmentFromConfigFile(configFile):
        
    try:

        print "\n\n\n"  
        print "---------------------------------------------------------------"
        print " Create WAS environment from config file "
        print " configFile:                    "+configFile
        print "---------------------------------------------------------------"


        cfgDict = validateConfigFile(configFile)
        
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()
        
        Configurator.doWebsphereVariables(cellName, cfgDict)
        Configurator.doNodeLevelWebsphereVariables(cellName, cfgDict)
        Configurator.doJaasEntries(cfgDict)
        Configurator.doServers(cfgDict)
        
    except:
        print "\n\nException in createEnvironmentFromConfigFile() when calling sub methods"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
        

    print "\nend of createEnvironmentFromConfigFile()"



#--------------------------------------------------------------------
# main
#--------------------------------------------------------------------


usage = " "
usage = usage + " "
usage = usage + "Usage: <wsadmin command> -p < properties file, which in turn specifies profile script to run>] -f <this py script> <config dir e.g., c:/qdr/ETP_dev/> <config file name>"
usage = usage + " . . . and must have modified soap.client.props of target wsadmin profile if security is enabled\n"
print "\n\n"

if len(sys.argv) == 2:
    configDir=sys.argv[0]
    print "configDir " + configDir
    # e.g., C:/qdr/ETP_dev/
    print

    #sys.path.append('C:/qdr/ETP_dev/config_scripts')          
    sys.path.append(configDir + 'config_scripts')

    # modules are expected to be in the directory we just appended to search path
    import wini
    print
    print 'got to here zzz'
    print
    import Configurator

    configFile=sys.argv[1]
    print "configFile: " + configFile
    configPath = configDir + "config_files/" 
    print "configPath " + configPath

    
else:
    print usage
    sys.exit(1)
#when this module is being run as top-level, call the appropriate function    
if __name__=="__main__":
    createEnvironmentFromConfigFile(configPath + configFile)
