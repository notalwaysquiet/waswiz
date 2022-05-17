###############################################################################
# WebSphere 7 script
# by Hazel Malloy 2010  
###############################################################################
# Notes
#   This "master" i.e. top-level Jython script includes the following procedures:
#       validateStandaloneConfigFile()
#       configureStandaloneServerFromConfigFile()
#
#   . . . . which call the following Jython scripts (not listed in order):
#   wini.py (config file parser)
#   Configurator.py
#
# Call this script using properties file that in turn specifies a python "profile" script to be run that will
#  cause the wsadmin objects to be available to all levels of scripts
#

# create etp standalone environment - windows
# wsadmin.bat -p C:\qdr\ETP_dev\config_scripts\wsadmin_properties_files\custom.properties -f c:/qdr/ETP_dev/config_scripts/ConfigureStandaloneServer.py c:/qdr/ETP_dev/ standalone_config_windows_c_drive.ini


# 

#   It is required to explicitly "import" sub-scripts into each script that will call them
#
#   Special requirements:
#   Config dir path, Config file (as paramsto script)    
#   This script quits if a cell and server node as named in config file are not found in target WAS installation
#   Version number of config file & script must match
#
###############################################################################


#--------------------------------------------------------------------
# Set global constants
#--------------------------------------------------------------------
import sys
import time

#see "main" method for lots more import statements



#version number of config file must match version number expected by this script
SCRIPT_CONFIG_VERSION = '.10'

#--------------------------------------------------------------------
# Read in config file
# Check for config format version
# Check cell and node exist as named in file, as "reality check"
#   to ensure we are not running script in the wrong profile
# Note the name of the server doesn't matter for standalone profiles
#   as there is only ever 1 server per profile
#--------------------------------------------------------------------
def validateStandaloneConfigFile(configFile, baseServerName):
    try:
        print "\n"  
        print "---------------------------------------------------------------"
        print " Read in config file for standalone profile"
        print " configFile:     "+configFile
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
        nodeHostList = environmentGenInfo['nodeHostList'].split()
        
        
        if len(nodeList) < 1:
            print "Pls supply nodename in config file."
            sys.exit(1)
        if len(nodeHostList) < 1:
            print "Pls supply node hostname in config file."
            sys.exit(1)
        
        # make sure there is only 1 node name in config file
        if len(nodeList) > 1:
            print "Expected only 1 node, found: " + str(len(nodeList)) + " nodes listed in config file."
            print "Pls remove extra node names from config file."
            sys.exit(1)
        if len(nodeHostList) > 1:
            print "Expected only 1 node host, found: " + str(len(nodeHostList)) + " node hosts listed in config file."
            print "Only first node host will be used."


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
                print "Node must already exist with name as defined in config file."
                sys.exit(1)
            #print "Found wsadmin config id for node: " + nodeName
            print "    " + nodeId
            
        
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        serverNameIsFoundInCfg = 'false'
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['baseServerName'] == baseServerName):
                serverNameIsFoundInCfg = 'true'
        
        if (serverNameIsFoundInCfg == 'false'):
            msg = '\n\n Specified serverName: ' + baseServerName + ' not found in config file.'   
            msg += '\n Pls ensure base server name in config file matches base name of server to be configured.'
            msg += '\n Base name is server name minus the last character'
            print msg  
            sys.exit(1)
            
    except:
        print "\n\nException in validateStandaloneConfigFile() when checking general config & cell info"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
        
    return cfgDict
    



#--------------------------------------------------------------------
# Create WAS environment from config file
# (cell and node must already exist as named in file)
# Server must already exist in WAS & it must be the only server in this node
# Server name can be anything, but in config file it must be "server"
#--------------------------------------------------------------------
def configureStandaloneServerFromConfigFile(configFile):
        
    try:

        print "\n\n\n"  
        print "---------------------------------------------------------------"
        print " Create standalone WAS environment from config file "
        print " configFile:                    "+configFile
        print "---------------------------------------------------------------"
        
        
        serverList =  AdminConfig.list('Server').splitlines()
        firstServerId = serverList[0]
        serverName = AdminConfig.showAttribute(firstServerId, 'name')
        
        # get the list of MBeans for active app servers
        activeServerMBObjectNameList = AdminControl.queryNames('type=Server,*').splitlines()
        # take the first one; for standalone there should only be one anyway
        # hopefully this is the jvm the wsadmin is connected to
        activeServerMBObjectName = activeServerMBObjectNameList[0]
        #print activeServerMBObjectName
        activeServerName = AdminControl.getAttribute(activeServerMBObjectName, 'name')
        #print activeServerName
        
        if (activeServerName != serverName):
            print "\n\n Something seems to be rather wrong."
            print "The first server listed in the WAS config is: " + serverName
            print "The name of the jvm this script is connected to is: " + activeServerName
            print "They don't seem to be the same. Shouldn't they be the same?"
            print ". . . exiting."
            sys.exit(1)

        
        if (len(serverList) > 1):
            print "WAS Cell configuration contains > 1 server."
            print "There is no way to start up extra servers on standalone nodes in WAS7."
            print "Only the first server in list will be configured and the extra servers will be ignored."
            print "\n Server list is:"
            for serverId in serverList:
                print "server name: " + AdminConfig.showAttribute(serverId, 'name')
            print ""  

        
        print "Name of server to be configured: " +  serverName
        print ""

        # remove the last character, which will usually be a "1"
        baseServerName = serverName[:-1]
        
        cfgDict = validateStandaloneConfigFile(configFile, baseServerName)

        cellName = AdminControl.getCell()
        
        
        
        Configurator.doWebsphereVariables(cellName, cfgDict)
        Configurator.doJaasEntries(cfgDict)
        
        #Configurator.setPorts(cfgDict, baseServerName)
        Configurator.setJvmProcessDefinition(cfgDict, baseServerName)
        Configurator.setJvmLogRolling(cfgDict, baseServerName)
        Configurator.createJvmCustomProps(cfgDict, baseServerName)
        Configurator.setTransactionServiceProperties(cfgDict, baseServerName)
        Configurator.setDefaultVirtualHost(cfgDict, baseServerName)
        Configurator.setWebContainerProperties(cfgDict, baseServerName)
        Configurator.setWebContainerThreadPoolProperties(cfgDict, baseServerName)
        Configurator.createOneServersJdbcProviders(cfgDict, baseServerName)
        Configurator.createOneServersDatasources(cfgDict, baseServerName)
        Configurator.createOneServersQueueConnectionFactory(cfgDict, baseServerName)
        Configurator.createOneServersQueue(cfgDict, baseServerName)
        Configurator.createOneServersListenerPorts(cfgDict, baseServerName)
        Configurator.extractServerArchive(cfgDict, baseServerName)


        
    except:
        print "\n\nException in configureStandaloneServerFromConfigFile() when calling sub methods"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
        

    print "\n end of configureStandaloneServerFromConfigFile()"





#--------------------------------------------------------------------
# main
#--------------------------------------------------------------------
#when this module is being run as top-level, call the configureStandaloneServerFromConfigFile(configFile) function
if __name__=="__main__":
    usage = " "
    usage = usage + " "
    usage = usage + "Usage: <wsadmin command> -p < properties file, which in turn specifies profile script to run>] -f <this py script> <config dir e.g., c:/qdr/ETP_dev/> <config file name>"
    usage = usage + " . . . and must have modified soap.client.props of target wsadmin profile if security is enabled\n"
    print "\n\n"

    if len(sys.argv) == 2:
        configDir=sys.argv[0]
        print "configDir " + configDir
        # e.g., C:/qdr/ETP_dev/
        
        #sys.path.append('C:/qdr/ETP_dev/config_scripts')          
        sys.path.append(configDir + 'config_scripts')
        
        # modules are expected to be in the directory we just appended to search path
        import Configurator
        import wini
 
        configFile=sys.argv[1]
        
        print ""
        print "configFile: " + configFile
        configPath = configDir + "config_files/" 
        print "configPath " + configPath

        configureStandaloneServerFromConfigFile(configPath + configFile)
    else:
        print usage
        sys.exit(1)

  

