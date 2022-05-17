###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
# Notes
#   This Python module includes the following procedures:
#       getWasVersion
#       createEnvironmentFromConfigFile
#       limitLTPACookiesToSSLOnly
#       doWebsphereVariables
#       doNodeLevelWebsphereVariables
#       doJaasEntries
#       createVirtualHosts - not currently called anywhere
#       createOneVirtualHost
#       createServer
#       addServersToCluster
#       setPorts
#       setJvmProcessDefinition
#       setJvmLogRolling
#       createJvmCustomProps
#       setTransactionServiceProperties
#       setDefaultVirtualHost
#       setWebContainerProperties
#       setWebContainerThreadPoolProperties
#       setWebContainerCustomProperties
#       setSessionCookieSettings
#       extractServerArchive
#       createOneServersJdbcProviders
#       createOneServersDatasources
#       addOneServersDatasourcesCustomProps
#       createOneServersQueueConnectionFactories
#       modifyOneServersQCFPoolProps
#       modifyOneQCFPool
#       modifyAllQCFPoolPropsInCell
#       createOneServersQueue
#       createOneServersListenerPorts
#       createOneServersJMSActivationSpecs
#       createOneServersReplicationDomain
#       addHTTPSessionManagerToDomain
#       enableM2MSessionReplication
#       createSharedLibraries
#       createServerClassLoader
#       modifyAsynchBeanDefaultWorkManager
#       createAsynchBeanNonDefaultWorkManagers
#       setCyberArkOptions
#       cyberArkIt
#       modifyHttpQueueTuningParams
#       doServer
#       doServers
#   
#
#   . . . . which call the following Jython scripts (not listed in order):
#   WebsphereVariables.py
#   Jaas.py
#   Virtualhosts.py
#   ServerImport.py
#   ServerCluster.py
#   ServerPorts.py
#   Jvm.py
#   JdbcProviders.py
#   ServerArchive.py
#   Datasources.py
#   WebContainer.py
#   wini.py (config file parser)
#   ItemExists.py
#   Mq.py
#   Library.py
#   ClassLoader.py
#   CyberarkDefaults.py
#
# Call this module from a script that reads & validates a custom config file &
#   then calls the appropriate methods to create &/or configure the desired WAS settings
#   for a specific use case, e.g., configure existing server or create whole WAS environment
#
# Call the top-level script which will cause the wsadmin objects to be available to all levels of scripts/modules
#
#   It is required to explicitly "import" sub-scripts into each script that will call them, and this cannot be in a method

###############################################################################


import sys
import time
# wsadmin objects used in this module
import AdminConfig
import AdminControl

# modules of was_configurator
import ClassLoader
import ConfigFile
import ContainerServices
import CyberarkDefaults
import Datasources
import Ha
import ItemExists
import Jaas
import JdbcProviders
import Jvm
import Library
import Mq
import MqDefaults
import Security
import ServerArchive
import ServerCluster
import ServerImport
import ServerPorts
import CustomSecurityRelatedDefaults
import Utilities
import Virtualhosts
import WASPropertyFiles
import WebContainer
import WebsphereVariables
import wini
import WorkManagers


'''return a string containing the WAS major version, e.g., "9"'''
def getWasVersion():
    try:
        server = AdminControl.completeObjectName('type=Server,name=dmgr,*')
        versionString = AdminControl.getAttribute(server, 'serverVersion')
        # include white space to distinguish it from Version Directory
        # make spaces a little shorter because it might vary a little between versions
        theindex = versionString.index("Version              ")
        WASversion = versionString[theindex + 7:theindex + 33].strip()
        WASmajorVersion = WASversion[:WASversion.index(".")].strip()
        # e.g., "7" or "8"
        return WASmajorVersion
    except:
        print "\n\nException in getWasVersion() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
        

''' Create WAS environment from config file. (cell and node must already exist as named in file). May not currently being called anywhere. Also, see UserInterface.py '''
def createEnvironmentFromConfigFile(configFile):
    try:
        print "\n\n\n"  
        print "---------------------------------------------------------------"
        print " Create WAS environment from custom config file "
        print " configFile:                    "+configFile
        print "---------------------------------------------------------------"

        cfgDict = ConfigFile.validateConfigFile(configFile)
        
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()
        limitLTPACookiesToSSLOnly()
        doWebsphereVariables(cellName, cfgDict)
        doNodeLevelWebsphereVariables(cellName, cfgDict)
        doJaasEntries(cfgDict)
        doServers(cfgDict)
        
    except:
        print "\n\nException in createEnvironmentFromConfigFile() when calling sub methods"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
        
    print "\nend of createEnvironmentFromConfigFile()"



def limitLTPACookiesToSSLOnly():
    try:
        LTPACookieRequiresSSL = CustomSecurityRelatedDefaults.getLTPACookieRequiresSSL()
        Security.modifyLTPASingleSignon(LTPACookieRequiresSSL)
        print "   Limited LTPA Cookies to SSL only"
        
    except:
        msg = "\n\nException in limitLTPACookiesToSSLOnly() "
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    


''' Websphere variables.  These ones are global, per cell.
  jvm custom props can use these for substitutions'''
def doWebsphereVariables(cellName, cfgDict):
    try:
        environmentGenInfo = cfgDict['cellInfo']
        
        websphereVariablesDict = wini.getPrefixedClauses(cfgDict,'websphereVariables:' + 'cellLevel' +':')
        if (len(websphereVariablesDict) == 0):
            print "\n   . . . skipping a step:"                
            print "   No stanza found in config file for cell-level websphere variables"
            return
        
        for websphereVariablesKey in websphereVariablesDict.keys():
            wv = websphereVariablesDict[websphereVariablesKey]
            symbolicName = wv['symbolicName']
            value = wv['value']
            description = wv['description']
            #print 'symbolicName is: ' + symbolicName
            #print 'value is: ' + value
            if ItemExists.cellScopedVariableExists(cellName, symbolicName):
                print "\n   . . . skipping a step:"                
                print "   Cell-scoped Websphere variable already exists: " + symbolicName
            else:
                WebsphereVariables.setGlobalWebsphereVariableEntry(symbolicName, value)

    except:
        print "\n\nException in doWebsphereVariables() when setting up global websphere variables"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        print "\n\n   Exiting . . . \n\n"
        sys.exit(1)


''' Websphere variables to be created at node level for each server node Primarily needed for JDBC driver locations. Vars for most driver providers are BUILT-IN with empty string vals:
 * DB2
 * Oracle
 * Microsoft SQL Server
 * BUT NOT MySql for some reason
 We must modify the blank vars at node level. In theory could be created only at cell level, but the blank node-level var would override cell-level one if we didn't remove it. IBM recommends to manage these at node-level not cell-level.'''
def doNodeLevelWebsphereVariables(cellName, cfgDict):
    nodeName = "nodeName not assigned yet"
    try:
        websphereVariablesDict = wini.getPrefixedClauses(cfgDict,'websphereVariables:' + 'nodeLevel' +':')
        nodeList = Utilities.get_node_name_list()

        if (len(websphereVariablesDict) == 0):
            print "\n   . . . skipping a step:"                
            print "   No stanza found in config file for node-level websphere variables"
            return
		
        for websphereVariablesKey in websphereVariablesDict.keys():
            wv = websphereVariablesDict[websphereVariablesKey]
            symbolicName = wv['symbolicName']
            value = wv['value']
            # to do: add description to method 
            description = wv['description']
            for nodeName in nodeList:
                variableId = ItemExists.nodeScopedVariableExists(cellName, nodeName, symbolicName)
                if variableId == None:
                    print "\n Variable name does not already exist: " + symbolicName
                    print " Creating new variable: " + symbolicName
                    # for user-defined jdbc drivers, e.g., mysql, item will not already exist
                    # there is a pre-defined variable "User-defined_JDBC_DRIVER_PATH" but I prefer to put MySql in the name
                    WebsphereVariables.createNodeLevelWebsphereVariableEntry(nodeName, symbolicName, value, description)
                else:                
                    # for standard jdbc drivers, item will already exist
                    # this method will only change value for existing var if it was ""
                    print "\n Variable name exists: " + symbolicName
                    print "\n\n\n\n Modifying existing variable only if it is blank: " + symbolicName
                    print "\n -----------------> To change a non-blank existing variable, use 'replace' function instead of 'add' function."
                    WebsphereVariables.setBlankNodeLevelWebsphereVariableEntry(nodeName, symbolicName, value)

    except:
        print "\n\nException in doNodeLevelWebsphereVariables() when setting up node-level websphere variables for node: " + nodeName
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        print "\n\n   Exiting . . . \n\n"
        sys.exit(1)

#--------------------------------------------------------------------
# jaas / j2c entries
#  these are global, per cell
#  must be set up before datasources
#--------------------------------------------------------------------
def doJaasEntries(cfgDict):
    try:

        # Suppress dmgr node name from being prefixed to new JAAS/J2C authentication entries
        #  new feature in was7
        #
        # # for the same thing in admin console:
        #    Security > Global security > (Authentication) > Java Authentication and Authorization Service > 
        #     J2C authentication data 
        #    uncheck "Prefix new aliasName names with the node name of the cell (for compatibility with earlier releases)"
        #
        # #  this will make it easier to assign them to the datasources - will be the same across was installations
        # #  applies to jaas created either way, both with admin console & scripted

        
        jaasAuthEntryDict = wini.getPrefixedClauses(cfgDict,'jaasAuthEntry:' + 'cellLevel' +':')
        if (len(jaasAuthEntryDict) == 0):
            print "\n   . . . skipping a step:"                
            print "   No stanza found in config file for JAAS entries"
            return
        
        for jaasAuthEntryKey in jaasAuthEntryDict.keys():
            jae = jaasAuthEntryDict[jaasAuthEntryKey]
            alias = jae['alias']
            userid = jae['userid']
            password = jae['password']
            #print 'alias is: ' + alias
            #print 'userid is: ' + userid
            if ItemExists.jaasAliasExists(alias):
                print "\n   . . . skipping a step:"                
                print "   Jaas auth alias already exists: " + alias
            else:
                Jaas.setJaasAuthEntry(alias, userid, password)

    except:
        print "\n\nException in doJaasEntries() when setting up jaas/j2c entries"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        print "\n\n   Exiting . . . \n\n"
        sys.exit(1)


#--------------------------------------------------------------------
# Virtual Hosts
#--------------------------------------------------------------------
# these are set up per cell (Environment > Virtual hosts)
# vh's can have 2 kinds of entries: 
#   1) for requests via web server 2) for requests via app server's embedded http server
# for 2nd kind we have to look at server info, for 1st kind, we don't
# all vh's have the 2nd kind, even if server is not clustered
# not all virtual hosts have 1st kind (e.g., coloured servers for Dev)
# for 2nd kind we use plan 2b in ports new plans.xls to
# create vh for a server or a set of clustered servers at one go (server1 & server2 on same ports + portOffsetForClusterMembers)
#--------------------------------------------------------------------
def createOneVirtualHost(cfgDict, baseNameOfServerItsFor):
    try:
        print "\n"  
        print "---------------------------------------------------------------"
        print " Create specified server's virtual host"
        print " server it's for:               "+baseNameOfServerItsFor        
        print "---------------------------------------------------------------"

        # get WAS major version (e.g., "7" or "8")
        wasVersion = getWasVersion()
        httpPortOffset = 'httpPortOffset not defined yet'
        httpsPortOffset = 'httpsPortOffset not defined yet'
        if (str(wasVersion) == "7"):
            httpPortOffset = 16
            httpsPortOffset = 17
        elif (str(wasVersion) == "8"):
            httpPortOffset = 18
            httpsPortOffset = 19
        elif (str(wasVersion) == "9"):
            httpPortOffset = 18
            httpsPortOffset = 19

        print "WAS version is: " + str(wasVersion)
        print "httpPortOffset is: " + str(httpPortOffset)
        print "httpsPortOffset is: " + str(httpsPortOffset)

        try:
            virtualHostName = "virtualHostName not defined yet"
            #collect list of vh's listed under server clause in config
            #use this list later on to make sure we don't create 
            #   type 1 vh's (external web-server type) for servers that aren't in config file
            virtualHostList = []
            serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')

            for serverInfoKey in serverInfoDict.keys():
                si = serverInfoDict[serverInfoKey]
                baseServerName = si['baseServerName']
                if (baseServerName == baseNameOfServerItsFor):

                    hostsWebApps = si['hostsWebApps']
                    if (hostsWebApps == 'true'):

                        nodeList = si['nodeList'].split()
                        nodeHostList = si['nodeHostList'].split()
                        #print '\n\nbaseServerName is: ' + baseServerName

                        if len(nodeList) != len(nodeHostList):
                            print "\n\nError in server info for server: " + baseServerName
                            print "    Config file must supply a host name for every node in node list in server info"
                            print "    Can't make virtual host without full & correct host alias info."
                            print '    len(nodeList) is: ' + str(len(nodeList))
                            print '    len(nodeHostList) is: ' + str(len(nodeHostList))
                            sys.exit(1)
                    else:
                        print "\n   . . . not making a virtual host for server: " + baseNameOfServerItsFor
                        print " because hostsWebApps is false for this server in config file."
                        return
            
        except:
            print "\n\nException in createOneVirtualHost() when reading virtual host values from config file"
            print "    when reading values for server: " + baseServerName
            print "\n\nStack trace is: "
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            sys.exit(1)
        try:

            #read through the same loop again, each time do a step in the process: create vh's
            for serverInfoKey in serverInfoDict.keys():
                si = serverInfoDict[serverInfoKey]
                baseServerName = si['baseServerName']
                if (baseServerName == baseNameOfServerItsFor):
            
                    hostsWebApps = si['hostsWebApps']
                    if (hostsWebApps == 'true'):
                    
                        virtualHostName = si['virtualHostName']
                        if ItemExists.virtualHostExists(virtualHostName):
                            print "\n   . . . skipping a step:"                
                            print "   Virtual host already exists: " + virtualHostName
                            return
                        else:
                            virtualHostList.append(virtualHostName)
                            Virtualhosts.createVirtualHost(virtualHostName)
                            #stop looping through servers
                            break
                    else:
                        print "\n\nError in server info for server: " + baseServerName
                        print "    Config file value for hostsWebApps must be true for virtual host to be created."
                        print "    Config file value for hostsWebApps is: " + hostsWebApps
                        print ""
                        sys.exit(1)
        except:
            print "\n\nException in createOneVirtualHost() when creating virtual host: " + virtualHostName
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            sys.exit(1)
        try:

            #read through the same loop again, each time do a step in the process: set entries for embedded-http server
            virtualHostName = 'virtualHostName not defined yet'
            node1PortList = 'node1PortList not defined yet'
            node2PortList = 'node2PortList not defined yet'
            foundServer = "false"
            for serverInfoKey in serverInfoDict.keys():
                if (foundServer == "true"):
                    break
                si = serverInfoDict[serverInfoKey]
                baseServerName = si['baseServerName']
                if (baseServerName == baseNameOfServerItsFor):
                    foundServer = "true"
                    hostsWebApps = si['hostsWebApps']
                    if (hostsWebApps == 'true'):

                        nodeList = si['nodeList'].split()
                        nodeHostList = si['nodeHostList'].split()
                        server1PortRangeStart = si['portRangeStart']
                        virtualHostName = si['virtualHostName']
                        isClustered = si['isClustered']
                        portOffsetForClusterMembers = si['portOffsetForClusterMembers']
                        createAsteriskHostAlias = si['createAsteriskHostAlias']
                        server1_WC_defaulthost_port = int(server1PortRangeStart) + int(httpPortOffset)
                        server1_WC_defaulthost_secure_port = int(server1PortRangeStart) + int(httpsPortOffset)
                        node1PortList = [server1_WC_defaulthost_port, server1_WC_defaulthost_secure_port]
                        
                        print "node1PortList: "
                        print node1PortList
                        
                        if (isClustered == 'true'):
                            if (len(nodeHostList) == 1):
                                pass
                            elif (len(nodeHostList) == 2):
                                # port offsets for: 
                                #   server on node 1's WC_defaulthost, 
                                #   node 1 WC_defaulthost_secure, 
                                #   node 2 WC_defaulthost, 
                                #   node 2 WC_defaulthost_secure, 
                                server2_WC_defaulthost_port = int(server1_WC_defaulthost_port) + int(portOffsetForClusterMembers)
                                server2_WC_defaulthost_secure_port = int(server1_WC_defaulthost_secure_port) + int(portOffsetForClusterMembers)
                                node2PortList = [server2_WC_defaulthost_port, server2_WC_defaulthost_secure_port]

                                print "node2PortList: "
                                print node2PortList
                                
                            else:
                                print "\n\n"
                                print "               Wow!! more than 2 nodes!!"
                                print "Please add remaining ports to virtual host manually \n\n"

                        # keep track of hostnames so we do not do duplicate hostnames more than once
                        #builtin sets are not supported in version of python in WASv7, so we make our own set
                        nodeHostSet = []
                        for hostname in nodeHostList:
                            if (hostname in nodeHostSet):
                                break
                            else: 
                                nodeHostSet.append(hostname)
                            
                        nodeCount = 0
                        for nodeName in nodeList:
                            nodeCount += 1
                            hostCount = 0                            
                            for hostname in nodeHostSet:
                                hostCount += 1
                                #print ''
                                #print 'baseServerName is: ' + baseServerName
                                #print 'server1PortRangeStart is: ' + str(server1PortRangeStart)
                                #print 'virtualHostName is: ' + virtualHostName
                                #print 'hostname is: ' + hostname + '\n'
                                #print "nodeCount: " + str(nodeCount)
                                #print "hostCount: " + str(hostCount)
                                #print "nodeName: " + nodeName
                                #print "hostname: " + hostname
                                if ((nodeCount == 1) and (hostCount == 1)):
                                    #print "(nodeCount == 1 && hostCount == 1)"
                                    for port in node1PortList:
                                        Virtualhosts.setVirtualHostEntry(virtualHostName, hostname, port)
                                elif (nodeCount == 2): 
                                    if (len(nodeHostSet) == 1):
                                        if (hostCount == 1):
                                            #print "len(nodeHostSet) == 1 and ((nodeCount == 2) and (hostCount == 1))"
                                            for port in node2PortList:
                                                Virtualhosts.setVirtualHostEntry(virtualHostName, hostname, port)
                                    elif (len(nodeHostSet) == 2):
                                        if (hostCount == 2):
                                            #print "len(nodeHostSet) == 2 and((nodeCount == 2) and (hostCount == 2))"
                                            for port in node2PortList:
                                                Virtualhosts.setVirtualHostEntry(virtualHostName, hostname, port)
                                    
                            
                        if (createAsteriskHostAlias == 'true'):
                            # for non-Prod environments
                            for port in node1PortList:
                                Virtualhosts.setVirtualHostEntry(virtualHostName, '*', port)
                            if (len(nodeList) == 2):
                               for port in node2PortList:
                                    Virtualhosts.setVirtualHostEntry(virtualHostName, '*', port)
                                    
        except KeyError:
            print "\n\nException in createOneVirtualHost() when setting embedded-server entry for virtual host: " + virtualHostName
            print "      . . . a required attribute is missing from config file."
            print "      Please see stack trace for name of the missing attribute."
            print "\n\nStack trace is: "
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            sys.exit(1)
        
        except:
            print "\n\nException in createOneVirtualHost() when setting embedded-server entry for virtual host: " + virtualHostName
            print "\n\nStack trace is: "
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            sys.exit(1)
        try:
            print "\n\n    Starting on external web-server type of virtual host entry now (if any) . . . "
            #should only be 1 vh in the list, I think
            for type2VirtualHost in virtualHostList:
                virtualHostDict = wini.getPrefixedClauses(cfgDict,'virtualHost:' + type2VirtualHost)

                # see if there's additional host/port entries (type 1) to make for the vh
                # note: 
                #   virtual host name must *also* be listed in server info for some server 
                #   in order for virtual host to have been created
                for virtualHostKey in virtualHostDict.keys():
                    vh = virtualHostDict[virtualHostKey]
                    virtualHostName = type2VirtualHost
                    hostname = vh['hostname'].strip()
                    port = str(vh['port']).strip()
                    #print '\n\nvirtualHostName is: ' + virtualHostName
                    #print 'port is: ' + str(port)
                    #print 'hostname is: ' + hostname
                    Virtualhosts.setVirtualHostEntry(virtualHostName, hostname, port)
        except:
            print "\n\nException in createOneVirtualHost() when setting web-server entry for virtual host: " + virtualHostName
            print "\n\nStack trace is: "
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            sys.exit(1)

    except:
        print "\n\nException in createOneVirtualHost()."
        print "\n\nStack trace is: "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        print "\n\n   Exiting . . . \n\n"
        sys.exit(1)


''' Create server with specified full name from specified custom config file on specified node only. (cell and node must already exist as named in file).  Assumes sequence number has already been appended to base name whether clustered or not '''
def createServer(cfgDict, nodeName, serverNameToCreate):
    try:
        print "\n\n\n"  
        print "---------------------------------------------------------------"
        print " Create specified server from specified custom config file"
        print " full name of server to create:      "+serverNameToCreate
        print "---------------------------------------------------------------"

        carDict = cfgDict['serverConfigurationArchive']
        
    except:
        msg = "\n\nException in createServer() when getting archive info out of config object"
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit("no serverConfigurationArchive clause in config object")

    try:
        serverTemplate = 'serverTemplate not defined yet'
        serverConfigTemplateDir = carDict['serverConfigTemplateDir'].strip()
        serverConfigTemplateFilename = carDict['serverConfigTemplateFilename'].strip()
        serverTemplate = serverConfigTemplateDir + serverConfigTemplateFilename
        if ItemExists.serverExists(nodeName, serverNameToCreate):
            print "\n   . . . skipping a step:"
            print "   Server: " + serverNameToCreate + " already exists"
            sys.exit(1)
        else:
            ServerImport.importServer(serverTemplate, nodeName, serverNameToCreate)
    except:
        msg = "\n\nException in createServer() when creating server: " + serverNameToCreate
        msg + msg + " \n    from template file: " + serverTemplate
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
#   Add server to cluster (if applic.)
# if clustered, servers will also be created on all nodes in server's nodeList
#if server is not clustered, any additional nodes in node list will be ignored
#--------------------------------------------------------------------
def addServersToCluster(cfgDict, serverNameToCluster):
    try:
        clusterName = 'clusterName not defined yet'
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
    except:
        msg = "\n\nException in addServersToCluster() when getting server info out of config object"
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            baseServerName = si['baseServerName']
            if (baseServerName == serverNameToCluster):
                nodeList = si['nodeList'].split()
                isClustered = si['isClustered']
                clusterName = si['clusterName']
                #print '\n\nbaseServerName is: ' + baseServerName
                if (isClustered == 'true'):
                    nodeNumber = 0
                    for nodeName in nodeList:
                        nodeNumber += 1
                        serverName = baseServerName + str(nodeNumber)
                        if (nodeNumber == 1):
                            if ItemExists.clusterExists(clusterName):
                                print "\n   . . . skipping a step:"                
                                print "   Cluster already exists: " + clusterName

                            else:
                                ServerCluster.convertServerToCluster(nodeName, serverName, clusterName)
                        else:
                            ServerCluster.addAnotherServerToCluster(nodeName, serverName, clusterName)
                else:
                    print "\n   . . . not clustering server: " + serverNameToCluster
                    print "Because server property isClustered is set to false"
                    return
                        
    except:
        print "\n\nException in addServersToCluster() when adding server: " + serverNameToCluster + " to cluster: " + clusterName 
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
# Set ports for specified server from specified custom config file
# (cell and node must already exist as named in file)
# if clustered, server will be created on all nodes in server's nodeList
#--------------------------------------------------------------------
def setPorts(cfgDict, serverNameToCreate):
    try:
        wasVersion = getWasVersion()
        startPort = 0
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        serverNameIsFoundInCfg = 'false'
        
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            baseServerName = si['baseServerName']
            if (baseServerName == serverNameToCreate):
                serverNameIsFoundInCfg = 'true'
                nodeList = si['nodeList'].split()
                server1PortRangeStart = si['portRangeStart'] 
                startPort = server1PortRangeStart
                #print 'startPort is: ' + str(startPort)
                nodeNumber = 0
                for nodeName in nodeList:
                    nodeNumber += 1
                    print 'nodeNumber is: ' + str(nodeNumber)
                    serverName = baseServerName + str(nodeNumber)
                    print 'serverName is: ' + serverName 
                    if (nodeNumber == 1):
                        pass
                    elif (nodeNumber > 1 and nodeNumber < 5):
                        portOffsetForClusterMembers = si['portOffsetForClusterMembers']
                        startPort = int(server1PortRangeStart) + int(portOffsetForClusterMembers)
                    else:
                        print "\n\nMore than 4 nodes specified for server: " + serverName
                        print "    Please check config file.\n\n"
                        sys.exit(1)

                    print "\n\nstartPort is: " + str(startPort) + "\n\n"
                    ServerPorts.setEndPointsStartPort(nodeName, serverName, startPort, wasVersion)

        if (serverNameIsFoundInCfg == 'false'):
            msg = '\n\nSpecified serverName: ' + serverNameToCreate + ' not found in config file.'                    
            print msg  
            sys.exit(1)
    except:
        msg = "\n\nException in setPorts() when setting ports for server: " + serverNameToCreate
        msg = msg + "    with start port: " + str(startPort)
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def setJvmProcessDefinition(cfgDict, serverNameToCreate):
    try:
        jvmProcessDefDict = cfgDict['jvmProcessDefinition:' + serverNameToCreate]
    except KeyError:
        #there is no stanza found for jvm process def for this server
        print "\n   . . . skipping a step:"                
        print "   No stanza found in config file for JVM process definition for server: " + serverNameToCreate
        return
    except:
        msg = "\n\nException in setJvmProcessDefinition() when getting jvm process def dict for server: " + serverNameToCreate
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:            
        jvmProcessDefPropertyListString = ''
        for jvmProcessDefKey in jvmProcessDefDict.keys():
            #print ""
            #print "jvmProcessDefKey: " + jvmProcessDefKey
            #print "jvmProcessDefDict[jvmProcessDefKey]: " + str(jvmProcessDefDict[jvmProcessDefKey])
            jvmProcessDefPropertyListString +='[' + jvmProcessDefKey + ' ' + str(jvmProcessDefDict[jvmProcessDefKey]) + '] '
            #print "jvmProcessDefPropertyListString: "
            #print jvmProcessDefPropertyListString
            #print ""

        #Using Jython string format for the arguments
        #'[[name1 val1] [name2 val2] [name3 val3]]'
        jvmProcessDefPropertyListString = "[" + jvmProcessDefPropertyListString
        jvmProcessDefPropertyListString = jvmProcessDefPropertyListString + "]"
        #print "\njvmProcessDefPropertyListString: " + jvmProcessDefPropertyListString
        
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        serverNameIsFoundInCfg = 'false'
        
        try:
            for serverInfoKey in serverInfoDict.keys():
                si = serverInfoDict[serverInfoKey]
                baseServerName = si['baseServerName']
                if (baseServerName == serverNameToCreate):
                    serverNameIsFoundInCfg = 'true'
                    nodeList = si['nodeList'].split()
                    nodeNumber = 0
                    for nodeName in nodeList:
                        nodeNumber += 1
                        serverName = baseServerName + str(nodeNumber)
                        serverId = ItemExists.serverExists(nodeName, serverName)
                        if serverId:
                            Jvm.setJvmProcessDefinition(nodeName, serverName, jvmProcessDefPropertyListString)
                        else:
                            print "\n Server not found: " + serverNameToCreate
                            sys.exit(1)
        except:
            msg = "\n\nException in setJvmProcessDefinition() when modifying jvmID for server: " + serverNameToCreate
            print msg
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            sys.exit(1)


    except:
        msg = "\n\nException in setJvmProcessDefinition() for server: " + serverNameToCreate
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def setJvmLogRolling(cfgDict, serverNameToCreate):
    try:
        jvmLogRollingDict = cfgDict['jvmLogRolling:' + serverNameToCreate]
    except KeyError:
        #there is no stanza found for jvm log rolling for this server
        print "\n   . . . skipping a step:"                
        print "   No stanza found in config file for JVM log rolling for server: " + serverNameToCreate
        return
    except:
        msg = "\n\nException in setJvmLogRolling() when getting jvm log rolling dict for server: " + serverNameToCreate
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:            
        jvmLogRollingPropertyListString = ''
        for jvmLogRollingKey in jvmLogRollingDict.keys():
            #print ""
            #print "jvmLogRollingKey: " + jvmLogRollingKey
            #print "jvmLogRollingDict[jvmLogRollingKey]: " + str(jvmLogRollingDict[jvmLogRollingKey])
            jvmLogRollingPropertyListString +='[' + jvmLogRollingKey + ' ' + str(jvmLogRollingDict[jvmLogRollingKey]) + '] '
            #print "jvmLogRollingPropertyListString: "
            #print jvmLogRollingPropertyListString
            #print ""

        #Using Jython string format for the arguments
        #'[[name1 val1] [name2 val2] [name3 val3]]'
        jvmLogRollingPropertyListString = "[" + jvmLogRollingPropertyListString
        jvmLogRollingPropertyListString = jvmLogRollingPropertyListString + "]"
        #print "\njvmLogRollingPropertyListString: " + jvmLogRollingPropertyListString
        
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        serverNameIsFoundInCfg = 'false'
        
        try:
            for serverInfoKey in serverInfoDict.keys():
                si = serverInfoDict[serverInfoKey]
                baseServerName = si['baseServerName']
                if (baseServerName == serverNameToCreate):
                    serverNameIsFoundInCfg = 'true'
                    nodeList = si['nodeList'].split()
                    nodeNumber = 0
                    for nodeName in nodeList:
                        nodeNumber += 1
                        serverName = baseServerName + str(nodeNumber)
                        if ItemExists.serverExists(nodeName, serverName):
                            Jvm.setJvmLogRolling(nodeName, serverName, jvmLogRollingPropertyListString)
                        else:
                            print "\n Server not found: " + serverNameToCreate
                            sys.exit(1)
        except:
            msg = "\n\nException in setJvmLogRolling() when modifying jvmID for server: " + serverNameToCreate
            print msg
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            sys.exit(1)


    except:
        msg = "\n\nException in setJvmLogRolling() for server: " + serverNameToCreate
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def createJvmCustomProps(cfgDict, serverNameToCreate):
    try:
        propertyName = 'propertyName not defined yet'
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        serverNameIsFoundInCfg = 'false'
        
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            baseServerName = si['baseServerName']
            if (baseServerName == serverNameToCreate):
                serverNameIsFoundInCfg = 'true'
                nodeList = si['nodeList'].split()

                jvmCustomPropertyDict = wini.getPrefixedClauses(cfgDict,'jvmCustomProperty:' + baseServerName +':')
                for jvmCustomPropertyKey in jvmCustomPropertyDict.keys():
                    jvcp = jvmCustomPropertyDict[jvmCustomPropertyKey]
                    propertyName = jvcp['propertyName']
                    propertyValue = jvcp['propertyValue']
                    propertyDescription = jvcp['propertyDescription']
                    nodeNumber = 0
                    for nodeName in nodeList:
                        nodeNumber += 1
                        serverName = baseServerName + str(nodeNumber)
                        if ItemExists.jvmCustomPropExists(nodeName, serverName, propertyName):
                            print "\n   . . . skipping a step:"                
                            print "   JVM custom prop: '" + propertyName + "' already exists: " + propertyName + " for server: " + serverName
                        else:
                            Jvm.setJvmCustomProperty(nodeName, serverName, propertyName, propertyValue, propertyDescription)

        if (serverNameIsFoundInCfg == 'false'):
            msg = '\n\nSpecified serverName: ' + serverNameToCreate + ' not found in config file.'                    
            print msg  
            sys.exit(1)
    except:
        print "\n\nException in createJvmCustomProps() when setting jvm custom props for server: " + serverNameToCreate
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
#   set server's transaction service properties, e.g., Total transaction lifetime timeout
#--------------------------------------------------------------------
def setTransactionServiceProperties(cfgDict, serverNameToCreate):
    try:
        transactionServiceDict = ''
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        serverNameIsFoundInCfg = 'false'
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            baseServerName = si['baseServerName']
            if (baseServerName == serverNameToCreate):
                serverNameIsFoundInCfg = 'true'
                try:
                    transactionServiceDict = cfgDict["transactionService:" + serverNameToCreate]
                except KeyError:
                    print "\n   . . . skipping a step:"                
                    print "   No stanza found in config file for transaction service properties for server: " + serverNameToCreate
                    print "\n\n"
                    return
                except:
                    msg = "\n\nException in setTransactionServiceProperties() when getting dict for server: " + serverNameToCreate
                    print msg
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
        if (serverNameIsFoundInCfg == 'false'):
            msg = '\n\nSpecified serverName: ' + serverNameToCreate + ' not found in config file.'                    
            print msg  
            sys.exit(1)
    
    except:
        msg = "\n\nException in setTransactionServiceProperties() when looking up server config for server: " + serverNameToCreate
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        transactionServicePropertyListString = ''
        for transactionServiceKey in transactionServiceDict.keys():
            #print ""
            #print "transactionServiceKey: " + transactionServiceKey
            #print "transactionServiceDict[transactionServiceKey]: " + str(transactionServiceDict[transactionServiceKey])
            transactionServicePropertyListString +='[' + transactionServiceKey + ' ' + str(transactionServiceDict[transactionServiceKey]) + '] '
            #print "transactionServicePropertyListString: "
            #print transactionServicePropertyListString
            #print ""

        #Using Jython string format for the arguments
        #'[[name1 val1] [name2 val2] [name3 val3]]'
        transactionServicePropertyListString = "[" + transactionServicePropertyListString
        transactionServicePropertyListString = transactionServicePropertyListString + "]"
        #print "\ntransactionServicePropertyListString: " + transactionServicePropertyListString
    except:
        msg = "\n\nException in setTransactionServiceProperties() when looking up web container properties for server: " + serverNameToCreate
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            baseServerName = si['baseServerName']
            if (baseServerName == serverNameToCreate):
                nodeList = si['nodeList'].split()
                nodeNumber = 0
                for nodeName in nodeList:
                    nodeNumber += 1
                    serverName = baseServerName + str(nodeNumber)
                    if ItemExists.serverExists(nodeName, serverName):
                        ContainerServices.setTransactionServiceProperties(nodeName, serverName, transactionServicePropertyListString)
                    else:
                        print "\n Server not found: " + serverNameToCreate
                        sys.exit(1)
    except:
        print "\n\nException in setTransactionServiceProperties() when setting web container properties for server: " + serverNameToCreate
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
#   set server's default virtual host
#--------------------------------------------------------------------
def setDefaultVirtualHost(cfgDict, serverNameToCreate):
    try:
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        virtualHostName = 'virtualHostName not defined yet'        
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            baseServerName = si['baseServerName']
            if (baseServerName == serverNameToCreate):
            
                hostsWebApps = si['hostsWebApps']

                if (hostsWebApps == 'true'):
                    virtualHostName = si['virtualHostName']

                    baseServerName = si['baseServerName']
                    nodeList = si['nodeList'].split()
                    nodeNumber = 0
                    for nodeName in nodeList:
                        nodeNumber += 1
                        serverName = baseServerName + str(nodeNumber)

                        Virtualhosts.setServerDefaultVirtualHost(nodeName, serverName, virtualHostName)
                else:                        
                    print "\n   . . . not setting a default virtual host for server: " + serverNameToCreate
                    print "because hostsWebApps is false for this server in config file"
                    return
    except:
        print "\n\nException in setDefaultVirtualHost() when setting default virtual host for server: " + serverNameToCreate
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
#   set server's web container properties, e.g., servlet caching
#--------------------------------------------------------------------
def setWebContainerProperties(cfgDict, serverNameToCreate):
    try:
        webContainerDict = ''
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        serverNameIsFoundInCfg = 'false'
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            baseServerName = si['baseServerName']
            if (baseServerName == serverNameToCreate):
                serverNameIsFoundInCfg = 'true'
                hostsWebApps = si['hostsWebApps']

                if (hostsWebApps == 'true'):
                    try:
                        webContainerDict = cfgDict["webContainer:" + serverNameToCreate]
                    except KeyError:
                        print "\n   . . . skipping a step:"                
                        print "   No stanza found in config file for web container properties for server: " + serverNameToCreate
                        return
                    except:
                        msg = "\n\nException in setWebContainerProperties() when getting web container dict for server: " + serverNameToCreate
                        print msg
                        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                        sys.exit(1)
                else:
                    print "\n   . . . not setting web container properties for server: " + serverNameToCreate
                    print "because hostsWebApps is false in config file for this server."
                    return
        if (serverNameIsFoundInCfg == 'false'):
            msg = '\n\nSpecified serverName: ' + serverNameToCreate + ' not found in config file.'                    
            print msg  
            sys.exit(1)
    
    except:
        msg = "\n\nException in setWebContainerProperties() when looking up server config for server: " + serverNameToCreate
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        webContainerPropertyListString = ''
        for webContainerKey in webContainerDict.keys():
            #print ""
            #print "webContainerKey: " + webContainerKey
            #print "webContainerDict[webContainerKey]: " + str(webContainerDict[webContainerKey])
            webContainerPropertyListString +='[' + webContainerKey + ' ' + str(webContainerDict[webContainerKey]) + '] '
            #print "webContainerPropertyListString: "
            #print webContainerPropertyListString
            #print ""

        #Using Jython string format for the arguments
        #'[[name1 val1] [name2 val2] [name3 val3]]'
        webContainerPropertyListString = "[" + webContainerPropertyListString
        webContainerPropertyListString = webContainerPropertyListString + "]"
        #print "\nwebContainerPropertyListString: " + webContainerPropertyListString
    except:
        msg = "\n\nException in setWebContainerProperties() when looking up web container properties for server: " + serverNameToCreate
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            baseServerName = si['baseServerName']
            if (baseServerName == serverNameToCreate):
                nodeList = si['nodeList'].split()
                nodeNumber = 0
                for nodeName in nodeList:
                    nodeNumber += 1
                    serverName = baseServerName + str(nodeNumber)
                    if ItemExists.serverExists(nodeName, serverName):
                        WebContainer.setWebContainerProperties(nodeName, serverName, webContainerPropertyListString)
                    else:
                        print "\n Server not found: " + serverNameToCreate
                        sys.exit(1)
    except:
        print "\n\nException in setWebContainerProperties() when setting web container properties for server: " + serverNameToCreate
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
#   set server's web container properties, e.g., servlet caching
#--------------------------------------------------------------------
def setWebContainerThreadPoolProperties(cfgDict, serverNameToCreate):
    try:
        webContainerDict = ''
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        serverNameIsFoundInCfg = 'false'
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            baseServerName = si['baseServerName']
            if (baseServerName == serverNameToCreate):
                serverNameIsFoundInCfg = 'true'
                hostsWebApps = si['hostsWebApps']

                if (hostsWebApps == 'true'):
                    try:
                        webContainerThreadPoolDict = cfgDict["webContainerThreadPool:" + serverNameToCreate]
                    except KeyError:
                        print "\n   . . . skipping a step:"                
                        print "   No stanza found in config file for web container Thread Pool properties for server: " + serverNameToCreate
                        return
                    except:
                        msg = "\n\nException in setWebContainerThreadPoolProperties() when getting Thread Pool dict for server: " + serverNameToCreate
                        print msg
                        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                        sys.exit(1)
                else:
                    print "\n   . . . not setting web container thread pool properties for server: " + serverNameToCreate
                    print "because hostsWebApps is false in config file for this server."
                    return
        if (serverNameIsFoundInCfg == 'false'):
            msg = '\n\nSpecified serverName: ' + serverNameToCreate + ' not found in config file.'                    
            print msg  
            sys.exit(1)
    
    except:
        msg = "\n\nException in setWebContainerThreadPoolProperties() when looking up server config for server: " + serverNameToCreate
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        webContainerThreadPoolPropertyListString = ''
        for webContainerThreadPoolKey in webContainerThreadPoolDict.keys():
            #print ""
            #print "webContainerThreadPoolKey: " + webContainerThreadPoolKey
            #print "webContainerThreadPoolDict [webContainerThreadPoolKey]: " + str(webContainerThreadPoolDict [webContainerThreadPoolKey])
            webContainerThreadPoolPropertyListString +='[' + webContainerThreadPoolKey + ' ' + str(webContainerThreadPoolDict [webContainerThreadPoolKey]) + '] '
            #print "webContainerThreadPoolPropertyListString: "
            #print webContainerThreadPoolPropertyListString
            #print ""

        #Using Jython string format for the arguments
        #'[[name1 val1] [name2 val2] [name3 val3]]'
        webContainerThreadPoolPropertyListString = "[" + webContainerThreadPoolPropertyListString
        webContainerThreadPoolPropertyListString = webContainerThreadPoolPropertyListString + "]"
        #print "\nwebContainerThreadPoolPropertyListString: " + webContainerThreadPoolPropertyListString
    except:
        msg = "\n\nException in setWebContainerThreadPoolProperties() when looking up web container properties for server: " + serverNameToCreate
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            baseServerName = si['baseServerName']
            if (baseServerName == serverNameToCreate):
                nodeList = si['nodeList'].split()
                nodeNumber = 0
                for nodeName in nodeList:
                    nodeNumber += 1
                    serverName = baseServerName + str(nodeNumber)
                    if ItemExists.serverExists(nodeName, serverName):
                        WebContainer.setWebContainerThreadPoolProperties(nodeName, serverName, webContainerThreadPoolPropertyListString)
                    else:
                        print "\n Server not found: " + serverNameToCreate
                        sys.exit(1)
    except:
        print "\n\nException in setWebContainerThreadPoolProperties() when setting web container properties for server: " + serverNameToCreate
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
#   set custom properties for a server's web container 
#--------------------------------------------------------------------
def setWebContainerCustomProperties(cfgDict, serverNameToCreate):
    try:
        webContainerCustomPropsDict = ''
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        serverNameIsFoundInCfg = 'false'
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            baseServerName = si['baseServerName']
            nodeList = si['nodeList'].splitlines()
            if (baseServerName == serverNameToCreate):
                serverNameIsFoundInCfg = 'true'
                hostsWebApps = si['hostsWebApps']
                if (hostsWebApps == 'true'):
                    try:
                        webContainerCustomPropsDict = wini.getPrefixedClauses(cfgDict,"webContainerCustomProps:" + serverNameToCreate + ":")
                        #print "\n\n\nwebContainerCustomPropsDict: "
                        #print webContainerCustomPropsDict
                        #print "\n\n"
                        if (len(webContainerCustomPropsDict) == 0):
                            print "\n   . . . skipping a step:"                
                            print "   No stanza found in config file for web container custom properties for server: " + serverNameToCreate
                            print ""
                            return
                    except:
                        msg = "\n\nException in setWebContainerCustomProperties() when getting custom props dict for server: " + serverNameToCreate
                        print msg
                        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                        sys.exit(1)
                else:
                    print "\n   . . . not setting web container custom properties for server: " + serverNameToCreate
                    print "because hostsWebApps is false in config file for this server."
                    return
        if (serverNameIsFoundInCfg == 'false'):
            msg = '\n\n setWebContainerCustomProperties: Specified serverName: ' + serverNameToCreate + ' not found in config file.'                    
            print msg  
            sys.exit(1)
    except:
        msg = "\n\n Exception in setWebContainerCustomProperties() when looking up server config for server: " + serverNameToCreate
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            baseServerName = si['baseServerName']
            if (baseServerName == serverNameToCreate):
                nodeList = si['nodeList'].split()
                nodeNumber = 0
                for nodeName in nodeList:
                    nodeNumber += 1
                    serverName = baseServerName + str(nodeNumber)
                    for webContainerCustomPropertyKey in webContainerCustomPropsDict.keys():
                        wccp = webContainerCustomPropsDict[webContainerCustomPropertyKey]
                        propertyName = wccp['propertyName']
                        propertyValue = wccp['propertyValue']
                        propertyDescription = wccp['propertyDescription']
                        if (propertyName == 'HttpSessionCloneId'):
                            propertyValue = propertyValue + str(nodeNumber)
                        #Using Jython string format for the arguments, as all the nested[ drive me mental otherwise
                        #'[[name1 val1] [name2 val2] [name3 val3]]'
                        # this is a wierd situation: 1 property which happens to be named "properties" & is nested, and of type collection, i.e., it has an extra set of [  around it
                        propertyListString = '[[ properties [[[name "' + propertyName + '"] [value "' + propertyValue + '"] [description "' + propertyDescription + '"]]]]]'
                        #print "\npropertyListString: " + propertyListString
                        #print ""

                        if ItemExists.webContainerCustomPropExists(nodeName, serverName, propertyName):
                            print "\n   . . . skipping a step:"                
                            print "   web container custom prop already exists: " + propertyName + " for server: " + serverName
                        else:
                            WebContainer.setWebContainerProperties(nodeName, serverName, propertyListString)
    except:
        msg = "\n\n Exception in setWebContainerCustomProperties() when creating web container properties for server: " + serverNameToCreate
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
#   set default session cookie properties for a server
#   Can be overridden at app level if session management is overridden
#--------------------------------------------------------------------
def setSessionCookieSettings(cfgDict, serverNameToCreate):
    try:
        wasVersion = getWasVersion()
        defaultSessionCookieSettingsSecure = 'defaultSessionCookieSettingsSecure not defined yet'
        defaultSessionCookieSettingsHttpOnly = 'defaultSessionCookieSettingsHttpOnly not defined yet'
        defaultSessionCookieSettingsUseContextRootAsPath = 'defaultSessionCookieSettingsUseContextRootAsPath not defined yet'
        webContainerCustomPropsDict = ''
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        serverNameIsFoundInCfg = 'false'
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            baseServerName = si['baseServerName']
            nodeList = si['nodeList'].split()
            if (baseServerName == serverNameToCreate):
                serverNameIsFoundInCfg = 'true'
                hostsWebApps = si['hostsWebApps']
                if (hostsWebApps == 'true'):
                    try:
                        defaultCookieSettingsDict = wini.getPrefixedClauses(cfgDict,"defaultCookieSettings:" + serverNameToCreate)
                        #print "\n\n\ndefaultCookieSettingsDict: "
                        #print defaultCookieSettingsDict
                        #print "\n\n"
                        if (len(defaultCookieSettingsDict) == 0):
                            print "\n   No stanza found in config file for session cookie settings for server: " + serverNameToCreate
                            print "\n\n   Setting reasonable defaults for session cookie properties, as specified in CustomSecurityRelatedDefaults.py."
                            print "   If these are NOT desired for a particular server, override by adding 'defaultCookieSettings' stanza to server config file."
                            print ""
                            nodeNumber = 0
                            for nodeName in nodeList:
                                nodeNumber += 1
                                serverName = baseServerName + str(nodeNumber)
                                defaultSessionCookieSettingsSecure = CustomSecurityRelatedDefaults.getDefaultSessionCookieSettingsSecure()
                                defaultSessionCookieSettingsHttpOnly = CustomSecurityRelatedDefaults.getDefaultSessionCookieSettingsHttpOnly()
                                defaultSessionCookieSettingsUseContextRootAsPath = CustomSecurityRelatedDefaults.getDefaultSessionCookieSettingsUseContextRootAsPath()
                                WebContainer.setSessionCookieSettings(nodeName, serverName, wasVersion, defaultSessionCookieSettingsSecure, defaultSessionCookieSettingsHttpOnly, defaultSessionCookieSettingsUseContextRootAsPath)
                            return
                    except:
                        msg = "\n\nException in setSessionCookieSettings() when getting dict for server: " + serverNameToCreate
                        print msg
                        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                        sys.exit(1)
                else:
                    print "\n   . . . not setting session cookie settings for server: " + serverNameToCreate
                    print "because hostsWebApps is false in config file for this server."
                    return
        if (serverNameIsFoundInCfg == 'false'):
            msg = '\n\n setSessionCookieSettings: Specified serverName: ' + serverNameToCreate + ' not found in config file.'                    
            print msg  
            sys.exit(1)
    except:
        msg = "\n\n Exception in setSessionCookieSettings() at point XYZ123 for server: " + serverNameToCreate
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            baseServerName = si['baseServerName']
            if (baseServerName == serverNameToCreate):
                nodeList = si['nodeList'].split()
                nodeNumber = 0
                for nodeName in nodeList:
                    nodeNumber += 1
                    serverName = baseServerName + str(nodeNumber)
                    for defaultCookieSettingsKey in defaultCookieSettingsDict.keys():
                        dcsd = defaultCookieSettingsDict[defaultCookieSettingsKey]
                        try:
                            defaultSessionCookieSettingsSecure = dcsd['defaultSessionCookieSettingsSecure']
                        except KeyError:
                            valToBeSet = CustomSecurityRelatedDefaults.getDefaultSessionCookieSettingsSecure()
                            print "\n   No setting found in config file for defaultSessionCookieSettingsSecure for server: " + baseServerName
                            print "   Setting reasonable default value of: " + valToBeSet
                            print "   If this is NOT desired, override by adding 'defaultCookieSettings' stanza to server config file."                            
                            defaultSessionCookieSettingsSecure = valToBeSet
                        try:    
                            defaultSessionCookieSettingsHttpOnly = dcsd['defaultSessionCookieSettingsHttpOnly']
                        except KeyError:
                            valToBeSet = CustomSecurityRelatedDefaults.getDefaultSessionCookieSettingsHttpOnly()
                            print "\n   No setting found in config file for defaultSessionCookieSettingsHttpOnly for server: " + baseServerName
                            print "   Setting reasonable default value of: " + valToBeSet
                            print "   If this is NOT desired, override by adding 'defaultCookieSettings' stanza to server config file."                            
                            defaultSessionCookieSettingsHttpOnly = valToBeSet
                        try:    
                            defaultSessionCookieSettingsUseContextRootAsPath = dcsd['defaultSessionCookieSettingsUseContextRootAsPath']
                        except KeyError:
                            valToBeSet = CustomSecurityRelatedDefaults.getDefaultSessionCookieSettingsUseContextRootAsPath()
                            print "\n   No setting found in config file for defaultSessionCookieSettingsUseContextRootAsPath for server: " + baseServerName
                            print "   Setting reasonable default value of: " + valToBeSet
                            print "   If this is NOT desired, override by adding 'defaultCookieSettings' stanza to server config file."                            
                            defaultSessionCookieSettingsUseContextRootAsPath = valToBeSet

                        WebContainer.setSessionCookieSettings(nodeName, serverName, wasVersion, defaultSessionCookieSettingsSecure, defaultSessionCookieSettingsHttpOnly, defaultSessionCookieSettingsUseContextRootAsPath)
    except:
        msg = "\n\n Exception in setSessionCookieSettings() when setting session cookie settings for server: " + serverNameToCreate
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    

'''Make a configuration archive (car) file for each server. Binary zip of 5 or 6 files that define server, minus names etc. (car = Configuration ARchive)'''
def extractServerArchive(cfgDict, serverNameToCreate):
    try:
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        carDict = cfgDict['serverConfigurationArchive']
        environmentNickname = carDict['environmentNickname'].strip()
        serverConfigArchiveDir = carDict['serverConfigArchiveDir']
        serverConfigFileNameBase = carDict['serverConfigFileNameBase'].strip()
        label=time.strftime('_'+'%Y'+'_'+'%m'+'_'+'%d',time.localtime())
        if environmentNickname != '':
            label='_' + environmentNickname + label
        fileNamePart1 = serverConfigArchiveDir + serverConfigFileNameBase + '_'
        fileNamePart2 = label + '.car' #car = Configuration ARchive

        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            baseServerName = si['baseServerName']
            if (baseServerName == serverNameToCreate):            
                nodeList = si['nodeList'].split()

                nodeNumber = 0
                for nodeName in nodeList:
                    nodeNumber += 1
                    serverName = baseServerName + str(nodeNumber)
                    serverConfigArchiveFilename = fileNamePart1 + serverName + fileNamePart2
                    
                    ServerArchive.archiveServer(nodeName, serverName, serverConfigArchiveFilename)
    except:
        print "\n\nException in extractServerArchive() when creating configuration archive (car) file for server: " + serverNameToCreate
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)        



'''extract configuration props file for each server. This is a flat text
file including names and ids.'''
def extractServerPropsFile(cfgDict, serverNameToCreate):
    try:
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        carDict = cfgDict['serverConfigurationArchive']
        environmentNickname = carDict['environmentNickname'].strip()
        serverConfigArchiveDir = carDict['serverConfigArchiveDir']
        label=time.strftime('_'+'%Y'+'_'+'%m'+'_'+'%d',time.localtime())
        if environmentNickname != '':
            label='_' + environmentNickname + label
        fileNamePart1 = serverConfigArchiveDir + 'serverPropsFile' + '_'
        fileNamePart2 = label + '.props'

        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            baseServerName = si['baseServerName']
            if (baseServerName == serverNameToCreate):            
                nodeList = si['nodeList'].split()

                nodeNumber = 0
                for nodeName in nodeList:
                    nodeNumber += 1
                    serverName = baseServerName + str(nodeNumber)
                    serverPropsFilename = fileNamePart1 + serverName + fileNamePart2
                    WASPropertyFiles.extractOneServersPropsFile(serverConfigArchiveDir, environmentNickname, nodeName, serverName)
    except:
        print "\n\nException in extractServerArchive() when extract configuration props file for server: " + serverNameToCreate
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)        


'''returns true if at least one datasource is defined in the server config
file '''
def serverHasAtLeastOneDatasource(cfgDict, baseServerName, theDbType):
    try:
        dataSourceName = "dataSourceName not defined yet"
        dataSourceDict = wini.getPrefixedClauses(cfgDict,'dataSource:' + baseServerName +':')
        for dataSourceKey in dataSourceDict.keys():
            ds = dataSourceDict[dataSourceKey]
            dataSourceName = ds['dataSourceName'].strip()
            dbType = ds['db2OrOracle'].strip()
            if (dbType.lower() == theDbType.lower()):
                return 'true'
    except:
        msg = "\n\nException in serverHasAtLeastOneDatasource() for server: " + baseServerName + " when checking what jdbd providers to make\n"
        msg += "\n dataSourceName: " + dataSourceName
        msg += "serverHasAtLeastOneDatasource: " + serverHasAtLeastOneDatasourceDb2
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
#  JDBC Providers
#  server/cluster must be created before jdbc provider
#  creates provider at cluster level if server is clustered; otherwise at server level
#  does not create provider if there are no datasources required for that db type
#--------------------------------------------------------------------
def createOneServersJdbcProviders(cfgDict, baseServerName):
    try:
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()
        nodeName = 'nodeName not defined yet'
        dbType = 'dbType not defined yet'
        dbTypeList=['db2', 'mysql', 'oracle', 'sqlserver']
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')

        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['baseServerName'] == baseServerName):
                isClustered = si['isClustered'].strip()
                if (isClustered == 'true'):
                    clusterName = si['clusterName'].strip()
                    for dbType in dbTypeList:
                        if (serverHasAtLeastOneDatasource(cfgDict, baseServerName, dbType) == 'true'):
                            if ItemExists.clusterScopedJdbcProviderExists(clusterName, dbType):
                                print "\n   . . . skipping a step:"                
                                print "   DB Type: " + dbType + " JDBC provider already exists for cluster: " + clusterName
                            else:
                                JdbcProviders.createClusterScopedJdbcProvider(clusterName, dbType)
                        else: 
                            print "\n   . . . skipping a step:"  
                            print "   Not creating JDBC provider for DB Type: " + dbType + " for cluster: " + clusterName
                            print "   Because no datasources required for DB Type: " + dbType + " for cluster: " + clusterName
                            print ""
                            
                else:
                # server is not clustered; so there should only be 1 node
                    nodeList = si['nodeList'].split()
                    nodeName = nodeList[0]
                    print "nodeName: " + nodeName
                    nodeNumber = 1
                    serverName = baseServerName + str(nodeNumber)
                    for dbType in dbTypeList:
                        if (serverHasAtLeastOneDatasource(cfgDict, baseServerName, dbType) == 'true'):                    
                            if ItemExists.serverScopedJdbcProviderExists(cellName, nodeName, serverName, dbType):
                                print "\n   . . . skipping a step:"                
                                print "   DB Type: " + dbType + " JDBC provider already exists for server: " + serverName
                            else:
                                JdbcProviders.createServerScopedJdbcProvider(nodeName, serverName, dbType)
                        else: 
                            print "\n   . . . skipping a step:"  
                            print "   Not creating JDBC provider for DB Type: " + dbType + " for server: " + serverName
                            print "   Because no datasources required for DB Type: " + dbType + " for for server: " + serverName
                            print ""

    except:
        print "\n\nException in createOneServersJdbcProviders() when creating JDBC provider for DB type: " + dbType + " for server: " + baseServerName
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "Exception in createOneServersJdbcProviders() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def createOneServersDatasources(cfgDict, baseServerName):
#--------------------------------------------------------------------
#   Datasources
#   jdbc provider (per server or cluster) & associated jaas entries & WAS vars (per cell) must be created first
#--------------------------------------------------------------------
    try:
        print "\nCreating JDBC providers, if necessary  ...\n"
        createOneServersJdbcProviders(cfgDict, baseServerName)
    except:
        msg = "\n\nException in createOneServersDatasources() when creating jdbc providers for server: " + baseServerName
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    
    try:
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()
        nodeName = 'nodeName not defined yet'
        dataSourceName = 'dataSourceName not defined yet'
        cyberarkThisDatasource = "false"
        mappingAuthDataAlias = 'mappingAuthDataAlias not defined yet'
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['baseServerName'] == baseServerName):
                nodeList = si['nodeList'].split()
                dataSourceDict = wini.getPrefixedClauses(cfgDict,'dataSource:' + baseServerName +':')
                isClustered = si['isClustered']
                for dataSourceKey in dataSourceDict.keys():
                    ds = dataSourceDict[dataSourceKey]
                    dataSourceName = ds['dataSourceName'].strip()
                    jndiName = ds['jndiName'].strip()
                    authDataAlias = ds['authDataAlias']
                    # by default, a prefix gets added to all jaas entries
                    # this can be turned off in fixpack over (?) 7.0.0.5 (7?), but it doesn't seem to work right
                    stupidNodePrefix = AdminControl.getNode()
                    authDataAlias = stupidNodePrefix + '/' + authDataAlias
                    try:
                        cyberarkThisDatasource = ds['cyberarkThisDatasource'].strip()
                    except KeyError:
                        pass
                    
                    description = ds['description']
                    statementCacheSize = ds['statementCacheSize']
                    maxConnections = ds['maxConnections']
                    dbType = ds['db2OrOracle'].strip()
                    #print 'dbType is: ' + dbType
                    purgePolicy = ""
                    try:
                        purgePolicy = ds['purgePolicy']
                    except KeyError:
                        pass
                        
                    if (isClustered == 'true'):
                        clusterName = si['clusterName']
                        if ItemExists.clusterScopedDataSourceExists(clusterName, dbType, dataSourceName):
                            print "\n   . . . skipping a step:"      
                            print "   A dataSource named: '" + dataSourceName + "' already exists for cluster: " + clusterName
                            continue
                        if ItemExists.clusterScopedDataSourceByJndiExists(clusterName, dbType, jndiName):
                            print "\n   . . . skipping a step:"      
                            print "   A dataSource with JNDI name:'" + jndiName + "' already exists for cluster: " + clusterName
                            continue
                    else:
                    # not clustered, so look for existing thing at server level isntead
                        nodeNumber = 1
                        nodeName = nodeList[0]
                        serverName = baseServerName + str(nodeNumber)
                        if ItemExists.serverScopedDataSourceExists(cellName, nodeName, serverName, dbType, dataSourceName):
                            print "\n   . . . skipping a step:"                
                            print "   A dataSource named: '" + dataSourceName + "' already exists for server: " + serverName
                            continue
                        if ItemExists.serverScopedDataSourceByJndiExists(cellName, nodeName, serverName, dbType, jndiName):
                            print "\n   . . . skipping a step:"      
                            print "   A dataSource with JNDI name:'" + jndiName + "' already exists for serverer: " + serverName
                            continue

                            
                    import DatasourceDefaults
                    if purgePolicy == "":
                        purgePolicy = DatasourceDefaults.getPurgePolicy()
                    
                    if (dbType.lower().strip() == 'db2'):
                        databaseServerName = ds['databaseServerName']
                        databaseName = ds['databaseName']
                        readOnly = ds['readOnly']
                        currentSchema = ds['currentSchema']
                        retrieveMessagesFromServerOnGetMessage = ds['retrieveMessagesFromServerOnGetMessage']
                        
                        if (isClustered == 'true'):
                            datasourceId = Datasources.setClusterLevelDb2Datasource(clusterName, dataSourceName, databaseServerName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, databaseName, readOnly, currentSchema, retrieveMessagesFromServerOnGetMessage)
                            print "\n   . . . fixing connection pool defaults to match admin console defaults (purgePolicy = EntirePool)"
                            Datasources.modifyClusterLevelDatasourceConnectionPool(clusterName, dbType, dataSourceName, "", "", "", "", purgePolicy, "", "")
                        else:
                            # not clustered so there should be only 1 node
                            nodeNumber = 1
                            nodeName = nodeList[0]
                            serverName = baseServerName + str(nodeNumber)
                            datasourceId = Datasources.setServerLevelDb2Datasource(nodeName, serverName, dataSourceName, databaseServerName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, databaseName, readOnly, currentSchema, retrieveMessagesFromServerOnGetMessage)
                            print "\n   . . . fixing connection pool defaults to match admin console defaults (purgePolicy = EntirePool)"
                            Datasources.modifyServerLevelDatasourceConnectionPool(nodeName, serverName, dbType, dataSourceName, "", "", "", "", purgePolicy, "", "")
                    elif (dbType.lower().strip() == 'mysql'):
                        url = ds['url']
                        
                        if (isClustered == 'true'):
                            datasourceId = Datasources.setClusterLevelMySqlDatasource(clusterName, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, url)
                            #print "\n   . . . fixing connection pool defaults to match admin console defaults (purgePolicy = EntirePool)"
                            #Datasources.modifyClusterLevelDatasourceConnectionPool(clusterName, dbType, dataSourceName, "", "", "", "", purgePolicy, "", "")
                        else:
                            nodeNumber = 1
                            nodeName = nodeList[0]
                            serverName = baseServerName + str(nodeNumber)
                            datasourceId = Datasources.setServerLevelMySqlDatasource(nodeName, serverName, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, url)
                            #print "\n   . . . fixing connection pool defaults to match admin console defaults (purgePolicy = EntirePool)"
                            #Datasources.modifyServerLevelDatasourceConnectionPool(nodeName, serverName, dbType, dataSourceName, "", "", "", "", purgePolicy, "", "")
                    elif (dbType.lower().strip() == 'oracle'):
                        url = ds['url']
                        
                        if (isClustered == 'true'):
                            datasourceId = Datasources.setClusterLevelOracleDatasource(clusterName, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, url)
                            #print "\n   . . . fixing connection pool defaults to match admin console defaults"      
                            #Datasources.modifyClusterLevelDatasourceConnectionPool(clusterName, dbType, dataSourceName, "", "", "", "", purgePolicy, "", "")
                        else:
                            nodeNumber = 1
                            nodeName = nodeList[0]
                            serverName = baseServerName + str(nodeNumber)
                            datasourceId = Datasources.setServerLevelOracleDatasource(nodeName, serverName, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, url)
                            #print "\n   . . . fixing connection pool defaults to match admin console defaults"      
                            #Datasources.modifyServerLevelDatasourceConnectionPool(nodeName, serverName, dbType, dataSourceName, "", "", "", "", purgePolicy, "", "")
                    elif (dbType.lower().strip() == 'sqlserver'):
                        databaseServerName = ds['databaseServerName']
                        databaseName = ds['databaseName']
                        if (isClustered == 'true'):
                            datasourceId = Datasources.setClusterLevelSqlServerDatasource(clusterName, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, databaseName, databaseServerName)
                            #print "\n   . . . fixing connection pool defaults to match admin console defaults"
                            #Datasources.modifyClusterLevelDatasourceConnectionPool(clusterName, dbType, dbType, dataSourceName, "", "", "", "", purgePolicy, "", "")
                        else:
                            nodeNumber = 1
                            nodeName = nodeList[0]
                            serverName = baseServerName + str(nodeNumber)
                            datasourceId = Datasources.setServerLevelSqlServerDatasource(nodeName, serverName, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections,databaseName, databaseServerName)
                            #print "\n   . . . fixing connection pool defaults to match admin console defaults"
                            #Datasources.modifyServerLevelDatasourceConnectionPool(nodeName, serverName, dbType, dataSourceName, "", "", "", "", purgePolicy, "", "")
                    else:
                        print "\n   . . . cannot make datasource for server: " + baseServerName
                        print "Config file does not specify whether datasource is Db2, SQLServer or Oracle\n"
                        print "dbType must be 'db2', 'sqlserver' or 'oracle' (caps insensitive)"
                        sys.exit(1)
                for dataSourceKey in dataSourceDict.keys():
                    ds = dataSourceDict[dataSourceKey]
                    dataSourceName = ds['dataSourceName'].strip()
                    try:
                        cyberarkThisDatasource = ds['cyberarkThisDatasource'].strip()
                    except KeyError:
                        pass

                    if cyberarkThisDatasource == "true":
                        print
                        print ">>>>>>>>>>>>>>>>>>>>>>>>>"
                        print
                        print " About to attempt to cyberark an existing datasource: '" + dataSourceName + "' for server: " + baseServerName
                        # if there is any value for authDataAlias, override it as there should not be any
                        authDataAlias = ""
                        #dev0_t1_lion_server
                        serverOrClusterNameSubstring = baseServerName[:-7]
                        mappingConfigAlias = CyberarkDefaults.getLoginModuleAliasName()
                        try:
                            mappingAuthDataAlias = ds['mappingAuthDataAlias'].strip()                        
                        except KeyError:
                            print "\n   . . . Oooops:"                
                            print "   No value found in config file for mappingAuthDataAlias for ds: " + dataSourceName + " for server: " + baseServerName
                            print "   Please specify a 'mappingAuthDataAlias' or set 'cyberarkThisDatasource' to false."
                            print ""
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            return
                        try:
                            dataSourceId = ItemExists.datasourceByServerOrClusterNameSubstringExists(serverOrClusterNameSubstring, dataSourceName)
                        except:
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            print "Exception in createOneServersDatasources() when retrieving datasource id to cyberark it"
                        
                        Datasources.modifyDatasourceCredMappingByDatasourceId(dataSourceId, dataSourceName, mappingConfigAlias, mappingAuthDataAlias)
    except:
        msg = "\n\nException in createOneServersDatasources() when creating datasources for server: " + baseServerName
        msg = msg + "\n    dataSourceName: " + dataSourceName
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def addOneServersDatasourcesCustomProps(cfgDict, baseServerName):
    try:
        print "\nCreating Datasource custom props, if necessary  ...\n"
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()
        nodeName = 'nodeName not defined yet'
        clusterName = 'clusterName not defined yet'
        dataSourceName = 'dataSourceName not defined yet'
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['baseServerName'] == baseServerName):
                nodeList = si['nodeList'].split()
                dataSourceDict = wini.getPrefixedClauses(cfgDict,'dataSource:' + baseServerName +':')
                isClustered = si['isClustered']
                for dataSourceKey in dataSourceDict.keys():
                    ds = dataSourceDict[dataSourceKey]
                    dataSourceName = ds['dataSourceName'].strip()
                    jndiName = ds['jndiName'].strip()
                    dbType = ds['db2OrOracle'].strip()
                    #print 'dbType is: ' + dbType
                    
                    if (dbType.lower().strip() == 'db2'):
                        dataSourceCustomPropDict = wini.getPrefixedClauses(cfgDict,'dataSourceCustomProperty:' + baseServerName + ':' + jndiName + ':')
                        for customPropKey in dataSourceCustomPropDict.keys():
                            cp = dataSourceCustomPropDict[customPropKey]
                            dataSourceCustomPropertyName = cp['dataSourceCustomPropertyName']
                            dataSourceCustomPropertyType = cp['dataSourceCustomPropertyType']
                            dataSourceCustomPropertyValue = cp['dataSourceCustomPropertyValue']
                            try:
                                dataSourceCustomPropertyDescription = cp['dataSourceCustomPropertyDescription']
                            except KeyError:
                                dataSourceCustomPropertyDescription = "Custom property created by WAS configurator script but no description provided in config file"

                            if (isClustered == 'true'):
                                clusterName = si['clusterName']
                                if ItemExists.clusterScopedDataSourceCustomPropExists(clusterName, dbType, dataSourceName, dataSourceCustomPropertyName):
                                    print "\n   . . . skipping a step:"      
                                    print "   A dataSource custom prop named: '" + dataSourceCustomPropertyName + "' already exists for datasource: " + dataSourceName + " for cluster: " + clusterName
                                    continue
                            else:
                            # not clustered, so look for existing thing at server level isntead
                                nodeNumber = 1
                                nodeName = nodeList[0]
                                serverName = baseServerName + str(nodeNumber)
                                if ItemExists.serverScopedDataSourceCustomPropExists(cellName, nodeName, serverName, dbType, dataSourceName, dataSourceCustomPropertyName):
                                    print "\n   . . . skipping a step:"                
                                    print "   A dataSource custom prop named: '" + dataSourceCustomPropertyName + "' already exists for datasource: " + dataSourceName + " for server: " + serverName
                                    continue
                            print "TBD: Datasource custom prop: " + dataSourceCustomPropertyName + " for server base name: " + baseServerName
                                    
                            if (isClustered == 'true'):
                                Datasources.addCustomPropToClusterLevelDb2Datasource(clusterName, jndiName, dataSourceCustomPropertyName, dataSourceCustomPropertyType, dataSourceCustomPropertyValue, dataSourceCustomPropertyDescription)
                            else:
                                # not clustered so there should be only 1 node
                                nodeNumber = 1
                                nodeName = nodeList[0]
                                serverName = baseServerName + str(nodeNumber)
                                Datasources.addCustomPropToServerLevelDb2Datasource(nodeName, serverName, jndiName, dataSourceCustomPropertyName, dataSourceCustomPropertyType, dataSourceCustomPropertyValue, dataSourceCustomPropertyDescription)
                                    
                            
                            
                    else:
                        print "\n   . . . skipping a step:"      
                        print "   Custom props are not (yet) supported for DB type: " + dbType.lower().strip()
                        print "   (Only supported for DB2)"
                        continue
                        
    except:
        msg = "\n\nException in addOneServersDatasourcesCustomProps() when creating datasource custom props for server: " + baseServerName
        msg = msg + "\n    dataSourceName: " + dataSourceName
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

def createArbitraryServersJdbcProviders(cfgDict, serverName):
    try:
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()
        nodeName = 'nodeName not defined yet'
        dbType = 'db2'
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')

        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['fullServerName'] == serverName):

                nodeList = si['nodeList'].split()
                nodeName = nodeList[0]
                print "nodeName: " + nodeName
                if ItemExists.serverScopedJdbcProviderExists(cellName, nodeName, serverName, dbType):
                    print "\n   . . . skipping a step:"                
                    print "   DB Type: " + dbType + " JDBC provider already exists for server: " + serverName
                else:
                    JdbcProviders.createServerScopedJdbcProvider(nodeName, serverName, dbType)
    except:
        print "\n\nException in createOneServersJdbcProviders() when creating JDBC provider for DB type: " + dbType + " for server: " + serverName
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "Exception in createOneServersJdbcProviders() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def createArbitraryServersDatasources(cfgDict, serverName):
    try:
        print "\nCreating JDBC providers, if necessary  ...\n"
        createArbitraryServersJdbcProviders(cfgDict, serverName)
    except:
        msg = "\n\nException in createOneServersDatasources() when creating jdbc providers for server: " + serverName
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    
    try:
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()
        nodeName = 'nodeName not defined yet'
        dataSourceName = 'dataSourceName not defined yet'
        cyberarkThisDatasource = "false"
        mappingAuthDataAlias = 'mappingAuthDataAlias not defined yet'
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['fullServerName'] == serverName):
                nodeList = si['nodeList'].split()
                dataSourceDict = wini.getPrefixedClauses(cfgDict,'dataSource:' + serverName +':')

                for dataSourceKey in dataSourceDict.keys():
                    ds = dataSourceDict[dataSourceKey]
                    dataSourceName = ds['dataSourceName'].strip()
                    jndiName = ds['jndiName'].strip()
                    authDataAlias = ds['authDataAlias']
                    # by default, a prefix gets added to all jaas entries
                    # this can be turned off in fixpack over (?) 7.0.0.5 (7?), but it doesn't seem to work right
                    stupidNodePrefix = AdminControl.getNode()
                    authDataAlias = stupidNodePrefix + '/' + authDataAlias
                    try:
                        cyberarkThisDatasource = ds['cyberarkThisDatasource'].strip()
                    except KeyError:
                        pass
                    
                    description = ds['description']
                    statementCacheSize = ds['statementCacheSize']
                    maxConnections = ds['maxConnections']
                    dbType = ds['db2OrOracle'].strip()
                    #print 'dbType is: ' + dbType
                    purgePolicy = ""
                    try:
                        purgePolicy = ds['purgePolicy']
                    except KeyError:
                        pass
                        
                    # there should be only one node specified in config file
                    nodeName = nodeList[0]
                    if ItemExists.serverScopedDataSourceExists(cellName, nodeName, serverName, dbType, dataSourceName):
                        print "\n   . . . skipping a step:"                
                        print "   A dataSource named: '" + dataSourceName + "' already exists for server: " + serverName
                        continue
                    if ItemExists.serverScopedDataSourceByJndiExists(cellName, nodeName, serverName, dbType, jndiName):
                        print "\n   . . . skipping a step:"      
                        print "   A dataSource with JNDI name:'" + jndiName + "' already exists for serverer: " + serverName
                        continue

                            
                    import DatasourceDefaults
                    if purgePolicy == "":
                        purgePolicy = DatasourceDefaults.getPurgePolicy()
                    
                    if (dbType.lower().strip() == 'db2'):
                        databaseServerName = ds['databaseServerName']
                        databaseName = ds['databaseName']
                        readOnly = ds['readOnly']
                        currentSchema = ds['currentSchema']
                        retrieveMessagesFromServerOnGetMessage = ds['retrieveMessagesFromServerOnGetMessage']
                        
                        # there should be only one node specified in config file
                        nodeName = nodeList[0]
                        datasourceId = Datasources.setServerLevelDb2Datasource(nodeName, serverName, dataSourceName, databaseServerName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, databaseName, readOnly, currentSchema, retrieveMessagesFromServerOnGetMessage)
                        print "\n   . . . fixing connection pool defaults to match admin console defaults (purgePolicy = EntirePool)"
                        Datasources.modifyServerLevelDatasourceConnectionPool(nodeName, serverName, dbType, dataSourceName, "", "", "", "", purgePolicy, "", "")
                    else:
                        print "\n   . . . cannot make datasource for server: " + serverName
                        print "dbType must be 'db2'"
                        sys.exit(1)
                for dataSourceKey in dataSourceDict.keys():
                    ds = dataSourceDict[dataSourceKey]
                    dataSourceName = ds['dataSourceName'].strip()
                    try:
                        cyberarkThisDatasource = ds['cyberarkThisDatasource'].strip()
                    except KeyError:
                        pass

                    if cyberarkThisDatasource == "true":
                        print
                        print ">>>>>>>>>>>>>>>>>>>>>>>>>"
                        print
                        print " About to attempt to cyberark an existing datasource: '" + dataSourceName + "' for arbitrary server: " + serverName
                        # if there is any value for authDataAlias, override it as there should not be any
                        authDataAlias = ""
                        #dev0_t1_lion_server
                        serverOrClusterNameSubstring = serverName
                        mappingConfigAlias = CyberarkDefaults.getLoginModuleAliasName()
                        try:
                            mappingAuthDataAlias = ds['mappingAuthDataAlias'].strip()                        
                        except KeyError:
                            print "\n   . . . Oooops:"                
                            print "   No value found in config file for mappingAuthDataAlias for ds: " + dataSourceName + " for arbitrary server: " + serverName
                            print "   Please specify a 'mappingAuthDataAlias' or set 'cyberarkThisDatasource' to false."
                            print ""
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            return
                        try:
                            dataSourceId = ItemExists.datasourceByServerOrClusterNameSubstringExists(serverOrClusterNameSubstring, dataSourceName)
                        except:
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            print "Exception in createOneServersDatasources() when retrieving datasource id to cyberark it"
                        
                        Datasources.modifyDatasourceCredMappingByDatasourceId(dataSourceId, dataSourceName, mappingConfigAlias, mappingAuthDataAlias)
    except:
        msg = "\n\nException in createOneServersDatasources() when creating datasources for arbitrary server: " + serverName
        msg = msg + "\n    dataSourceName: " + dataSourceName
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

def addOneArbitraryServersDatasourcesCustomProps(cfgDict, serverName):
    try:
        print "\nCreating Datasource custom props, if necessary  ...\n"
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()
        nodeName = 'nodeName not defined yet'
        clusterName = 'clusterName not defined yet'
        dataSourceName = 'dataSourceName not defined yet'
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['fullServerName'] == serverName):
                nodeList = si['nodeList'].split()
                dataSourceDict = wini.getPrefixedClauses(cfgDict,'dataSource:' + serverName +':')
                
                for dataSourceKey in dataSourceDict.keys():
                    ds = dataSourceDict[dataSourceKey]
                    dataSourceName = ds['dataSourceName'].strip()
                    jndiName = ds['jndiName'].strip()
                    dbType = 'db2'
                    
                    dataSourceCustomPropDict = wini.getPrefixedClauses(cfgDict,'dataSourceCustomProperty:' + serverName + ':' + jndiName + ':')
                    for customPropKey in dataSourceCustomPropDict.keys():
                        cp = dataSourceCustomPropDict[customPropKey]
                        dataSourceCustomPropertyName = cp['dataSourceCustomPropertyName']
                        dataSourceCustomPropertyType = cp['dataSourceCustomPropertyType']
                        dataSourceCustomPropertyValue = cp['dataSourceCustomPropertyValue']
                        try:
                            dataSourceCustomPropertyDescription = cp['dataSourceCustomPropertyDescription']
                        except KeyError:
                            dataSourceCustomPropertyDescription = "Custom property created by WAS configurator script but no description provided in config file"

                        nodeName = nodeList[0]
                        if ItemExists.serverScopedDataSourceCustomPropExists(cellName, nodeName, serverName, dbType, dataSourceName, dataSourceCustomPropertyName):
                            print "\n   . . . skipping a step:"                
                            print "   A dataSource custom prop named: '" + dataSourceCustomPropertyName + "' already exists for datasource: " + dataSourceName + " for server: " + serverName
                            continue
                        print "TBD: Datasource custom prop: " + dataSourceCustomPropertyName + " for arbitrary server name: " + serverName
                                
                        Datasources.addCustomPropToServerLevelDb2Datasource(nodeName, serverName, jndiName, dataSourceCustomPropertyName, dataSourceCustomPropertyType, dataSourceCustomPropertyValue, dataSourceCustomPropertyDescription)
                                
                        
                        
                        
    except:
        msg = "\n\nException in addOneServersDatasourcesCustomProps() when creating datasource custom props for server: " + serverName
        msg = msg + "\n    dataSourceName: " + dataSourceName
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


# enableCyberarkOrOriginal specifies whether to (Scenario 1) enable all the cyberarked ds's specified in config file and disable originals 
# or (Scenario 2) disable all the the cybberarked ds's in the config file and enable the originals
def toggleCyberarkedDatasources(cfgDict, enableCyberarkOrOriginal):
    try:
        baseServerName = ""
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            baseServerName = si['baseServerName']
            dataSourceDict = wini.getPrefixedClauses(cfgDict,'dataSource:' + baseServerName +':')
            isClustered = si['isClustered']
            dataSourceId = ""
            dataSourceNameProp = []
            jndiNameProp = []
            jndiName = ""
            configFileCyberarkedDataSourceName = 'configFileCyberarkedDataSourceName not defined yet'
            origDataSourceName = 'origDataSourceName not defined yet'
            cyberarkThisDatasource = "false"
            mappingAuthDataAlias = 'mappingAuthDataAlias not defined yet'
            
            for dataSourceKey in dataSourceDict.keys():
                ds = dataSourceDict[dataSourceKey]
                
                try:
                    cyberarkThisDatasource = ds['cyberarkThisDatasource'].strip()
                except KeyError:
                    print "Error: toggleCyberarkedDatasources() was called but config file has no stanza for 'cyberarkThisDatasource'"
                    sys.exit(1)
                if cyberarkThisDatasource == "true":
                    configFileCyberarkedDataSourceName = ds['dataSourceName'].strip()
                    # example of cyberarked ds name: 'Salt Data Source Cyberark'
                    # slice off the ' Cyberark' to construct the name of the original datasource
                    origDataSourceName = configFileCyberarkedDataSourceName[:-9]
                
                    # this code expects that the user duplicated the original datasources to make the cyberarked ones, 
                    # leaving the orig ds's untouched(except for name and jndi name). (The orig ds's do not have to exist in the current config file as long as the names meet the convention.)
                    # we will need to find and edit both the cyberark and 'original' ds; first find the orig one because it "owns" the "real" jndi
                    
                    # example of base server name: dev0_t1_lion_server
                    # slice off the "_server" from end of base name of server, so it can match on either server or cluster name (datasource is at cluster level if server is clustered)
                    serverOrClusterNameSubstring = baseServerName[:-7]
                    
                    
                    if enableCyberarkOrOriginal == "cyberark":
                        print ">>>>>>>>>>>>>>>>>>>>>>>>>"
                        print "scenario 1: we are disabling the originals (if not done already) and enabling the cyberarked ds's (if not done already)"
                        try:
                            dataSourceId = ItemExists.datasourceByServerOrClusterNameSubstringExists(serverOrClusterNameSubstring, origDataSourceName)
                            if dataSourceId == None:
                            # if we didn't find it, maybe have already been modified to add ' Original' so search for that instead
                                print "data source: '" + origDataSourceName + "' not found, searching for '" + origDataSourceName + " Original'" + " instead."
                                origDataSourceName = origDataSourceName+' Original'
                                dataSourceId = ItemExists.datasourceByServerOrClusterNameSubstringExists(serverOrClusterNameSubstring, origDataSourceName)
                            #print "dataSourceId: " + str(dataSourceId)
                                
                            if dataSourceId == None:
                            # we still didn't find it, so dump out the params
                                print "id not found."
                                print "serverOrClusterNameSubstring: " + serverOrClusterNameSubstring
                                print "origDataSourceName: " + origDataSourceName
                                print 
                                                                
                                print "noncyberarked dataSourceId: " + str(dataSourceId)
                                print
                                doubblecheckdataSourceName = AdminConfig.showAttribute(dataSourceId, 'name') 
                                if doubblecheckdataSourceName != origDataSourceName:
                                    print "Error: names don't match."
                                    print "      double-check the name of the orig ds: " + str(doubblecheckdataSourceName)
                                    print "      should match the generated origDataSourceName: " + str(origDataSourceName)
                                    sys.exit(1)
                                    
                            jndiName = AdminConfig.showAttribute(dataSourceId, 'jndiName')                            
                            #print "      jndiName of orig ds: " + str(jndiName)
                        except:
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            print "Exception in toggleCyberarkedDatasources() in Scenario 1 when retrieving values for orig, non-cyberarked datasource"
                            
                        try:
                            # if ds name does not not already end in ' Original', add it to the end
                            alreadyDone = "true"
                            if origDataSourceName[-9:] == ' Original':
                                pass
                            else:
                                alreadyDone = "false"
                                origDataSourceName = origDataSourceName+' Original'
                            dataSourceNameProp = ['name', origDataSourceName]
                                
                            # if jndi name does not not already end in '_original', add it to the end
                            if jndiName[-9:] == '_original':
                                pass
                            else:
                                alreadyDone = "false"
                                jndiName = jndiName+'_original'
                            
                            if alreadyDone == "true":
                                print "datasource: '" + origDataSourceName + "' already has ' Original' added to name, and '_original' added to jndi name (i.e., it is disabled)."
                            if alreadyDone == "false":
                                jndiNameProp = ['jndiName', jndiName]
                                props = [dataSourceNameProp, jndiNameProp]
                                Datasources.modifyDatasourceByDatasourceId(dataSourceId, props)

                        except:
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            print "Exception in toggleCyberarkedDatasources() scenario 1 when modifying original ds matching cybberarked datasource: " + configFileCyberarkedDataSourceName
                        # now we are enabling the cyberarked ds, so zero out the vars
                        dataSourceId = ""
                        jndiName = ""
                        jndiNameProp = []
                        try:
                            dataSourceId = ItemExists.datasourceByServerOrClusterNameSubstringExists(serverOrClusterNameSubstring, configFileCyberarkedDataSourceName)
                            if dataSourceId == None:
                                # something is wrong
                                print "Error: didn't find any ds matching ds name: '" + configFileCyberarkedDataSourceName + "' for scope matching substring: " + serverOrClusterNameSubstring
                                sys.exit(1)
                            jndiName = AdminConfig.showAttribute(dataSourceId, 'jndiName')
                        except:
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            print "Exception in toggleCyberarkedDatasources() scenario 1 when retrieving values for cybberarked datasource: " + configFileCyberarkedDataSourceName
                            sys.exit(1)
                        try:    
                            # if jndi name ends in '_cyberark', remove it; otherwise do nothing
                            if jndiName[-9:] == '_cyberark':
                                jndiNameProp = ['jndiName', jndiName[:-9]]
                                props = [jndiNameProp]
                                Datasources.modifyDatasourceByDatasourceId(dataSourceId, props)
                            else:
                                print "datasource: '" + configFileCyberarkedDataSourceName + "' does not have expected suffix. May already be enabled."
                                
                        except:
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            print "Exception in toggleCyberarkedDatasources() scenario 1 when modifying cybberarked datasource: " + configFileCyberarkedDataSourceName
                            sys.exit(1)
                            

                    elif enableCyberarkOrOriginal == "original":
                        print ">>>>>>>>>>>>>>>>>>>>>>>>>"
                        print "scenario 2: we are disabling the cyberark ones from config file and re-enabling the matching originals"
                        dataSourceId = ""
                        jndiName = ""
                        jndiNameProp = []
                        try:
                            dataSourceId = ItemExists.datasourceByServerOrClusterNameSubstringExists(serverOrClusterNameSubstring, configFileCyberarkedDataSourceName)
                            if dataSourceId == "":
                                # something is wrong
                                print "Error: didn't find any ds matching ds name: '" + configFileCyberarkedDataSourceName + "' for scope matching substring: " + serverOrClusterNameSubstring
                                sys.exit(1)
                            jndiName = AdminConfig.showAttribute(dataSourceId, 'jndiName')
                        except:
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            print "Exception in toggleCyberarkedDatasources() scenario 2 when retrieving values for cybberarked datasource: " + configFileCyberarkedDataSourceName + "' for scope matching substring: " + serverOrClusterNameSubstring
                            sys.exit(1)
                        try:    
                            # if jndi name does not not already end in '_cyberark', add it to the end; otherwise do nothing
                            if jndiName[-9:] != '_cyberark':
                                jndiName = jndiName+'_cyberark'
                                #print "new jndiNameProp in Scenario 2 for cyberarked ds: " + str(jndiNameProp)
                                jndiNameProp = ['jndiName', jndiName]
                                props = [jndiNameProp]
                                Datasources.modifyDatasourceByDatasourceId(dataSourceId, props)
                            else:
                                print "datasource: '" + configFileCyberarkedDataSourceName + "' already disabled."
                                
                        except:
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            print "Exception in toggleCyberarkedDatasources() scenario 2 when modifying cybberarked datasource: " + configFileCyberarkedDataSourceName
                            sys.exit(1)
                        # now we are enabling the original ds, so zero out the vars
                        dataSourceId = ""
                        jndiName = ""
                        jndiNameProp = []
                        # for this scenario, datasource name has already been modified
                        origDataSourceName = origDataSourceName+' Original'
                        try:
                            dataSourceId = ItemExists.datasourceByServerOrClusterNameSubstringExists(serverOrClusterNameSubstring, origDataSourceName)
                            #print "at abbcxyz dataSourceId: " + str(dataSourceId) 
                            if dataSourceId == None:
                                # something is wrong
                                print "Error: didn't find any ds matching ds name: '" + origDataSourceName + "' for scope matching substring: " + serverOrClusterNameSubstring
                                sys.exit(1)
                            jndiName = AdminConfig.showAttribute(dataSourceId, 'jndiName')
                        except:
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            print "Exception in toggleCyberarkedDatasources() scenario 2 when retrieving values for originals ds matching the cybberarked datasource: " + configFileCyberarkedDataSourceName + "' for scope matching substring: " + serverOrClusterNameSubstring
                        try:    
                            # if jndi name end in '_original', remove it; otherwise do nothing
                            if jndiName[-9:] == '_original':
                                jndiName = jndiName[:-9]
                                jndiNameProp = ['jndiName', jndiName]
                                props = [jndiNameProp]
                                Datasources.modifyDatasourceByDatasourceId(dataSourceId, props)
                            else:
                                print "datasource: '" + origDataSourceName + "' didn't have the expected suffix; may already have had it removed."
                                
                        except:
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            print "Exception in toggleCyberarkedDatasources() scenario 2 when modifying originals ds matching the cybberarked datasource: " + configFileCyberarkedDataSourceName + "' for scope matching substring: " + serverOrClusterNameSubstring
                            sys.exit(1)
                   
                    else:
                        print "Error: value for 'enableCyberarkOrOriginal' not recognized: " + enableCyberarkOrOriginal
                        sys.exit(1)
                        
    except:
        print "\n\nException in toggleCyberarkedDatasources()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "Exception in toggleCyberarkedDatasources() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    

#--------------------------------------------------------------------
#   MQ queue connection factory
#--------------------------------------------------------------------
def createOneServersQueueConnectionFactories(cfgDict, baseServerName):
    try:
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()
        nodeName = 'nodeName not defined yet'
        factoryName = 'factoryName not defined yet'
        jndiName = 'jndiName not defined yet'
        description = 'description not defined yet'
        queueManager = 'queueManager not defined yet'
        host = 'host not defined yet'
        port = 'port not defined yet'
        channel = 'channel not defined yet'
        XAEnabled = 'XAEnabled not defined yet'
        transportType = 'transportType not defined yet'
        tempModel = 'tempModel not defined yet'
        
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['baseServerName'] == baseServerName):
                nodeList = si['nodeList'].split()
                isClustered = si['isClustered']
                try:
                
                    queueConnectionFactoryDict = wini.getPrefixedClauses(cfgDict,'queueConnectionFactory:' + baseServerName)
                except KeyError:
                    print "\n   . . . skipping a step:"                
                    print "   No stanza found in config file for queue connection factories for server: " + baseServerName 
                    print ""
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    return

                except:
                    msg = "\n\nException in createOneServersQueueConnectionFactories() when getting queue connection factories dict for server: " + baseServerName
                    print msg
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
                    
                try:
                    if (len(queueConnectionFactoryDict.keys()) == 0):
                        #print "len(queueConnectionFactoryDict.keys()):"
                        #print len(queueConnectionFactoryDict.keys())
                        print "\n   . . . skipping a step:"                
                        print "   No stanza found in config file for queue connection factories for server: " + baseServerName 
                        print ""
                        return
                      
                except:
                    msg = "\n\nException in createOneServersQueueConnectionFactories() when checking queue connection factories dict for server: " + baseServerName
                    print msg
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
                    
                try:    
                    
                    for factoryKey in queueConnectionFactoryDict.keys():
                        qcf = queueConnectionFactoryDict[factoryKey]
                        factoryName = qcf['name'].strip()
                        jndiName = qcf['jndiName'].strip()
                        description = qcf['description']
                        queueManager = qcf['queueManager'].strip()
                        host = qcf['host'].strip()
                        port = qcf['port']
                        channel = qcf['channel'].strip()
                        XAEnabled = qcf['XAEnabled'].strip()
                        transportType = qcf['transportType'].strip()
                        # tempModel. In admin console at [qcf] > Advanced properties > WebSphere MQ model queue name 
                        # tempModel. The model queue that is used as a basis for temporary queue definitions.
                        # Default is suppsed to be: SYSTEM.DEFAULT.MODEL.QUEUE but script-created qcf's do not get this set unless they explicitly set it
                        try:
                            tempModel = qcf['tempModel'].strip()
                            if (tempModel == ""):
                                raise Exception("No value provided for queue tempModel and tempModel not commented out.")
                        except KeyError:
                            tempModel = MqDefaults.getTempModel()
                            print "\n   . . . no queue temp model name-value pair was specified in config file for:" + baseServerName
                            print "    Using value it is supposed to be per Infocenter: " + tempModel
                            print "    If we didn't do this, wsadmin default is ''"
                            print "\n   If you actually want it to be '', set it manually after script runs."
                            print "    In admin console at [qcf] > Advanced properties > WebSphere MQ model queue name "
                        except Exception:
                            tempModel = MqDefaults.getTempModel()
                            print "\n   . . . empty string was specified in config file for queue temp model for:" + baseServerName
                            print "    Using value it is supposed to be per Infocenter: " + tempModel
                            print "    If we didn't do this, wsadmin default is ''"
                            print "\n   If you actually want it to be '', set it manually after script runs."
                            print "    In admin console at [qcf] > Advanced properties > WebSphere MQ model queue name "
                            

                        # note: the methods in Mq.py to create QCF also set the admin console 
                        #   defaults for non-advanced pool props (same ones for both 
                        #   connection & session pools)
                        
                        if (isClustered == 'true'):
                            clusterName = si['clusterName']
                            if ItemExists.clusterScopedQueueConnectionFactoryExists(cellName, clusterName, factoryName):
                                print "\n   . . . skipping a step:"                
                                print "   QCF named: " + factoryName + " already exists for cluster: " + clusterName
                                continue
                            else:
                                Mq.createQueueConnectionFactoryClusterLevel(clusterName, factoryName, description, jndiName, queueManager, host, port, channel, XAEnabled, transportType, tempModel)
                                

                        else:
                        # not clustered, so look for existing thing at server level isntead
                            nodeNumber = 1
                            nodeName = nodeList[0]
                            serverName = baseServerName + str(nodeNumber)
                            
                            if (ItemExists.serverScopedQueueConnectionFactoryExists(cellName, nodeName, serverName, factoryName)):
                                print "\n   . . . skipping a step:"                
                                print "   QCF named: " + factoryName + " already exists for server: " + serverName
                                continue
                            else:
                                Mq.createQueueConnectionFactoryServerLevel(nodeName, serverName, factoryName, description, jndiName, queueManager, host, port, channel, XAEnabled, transportType, tempModel)
                        
                        print "\n\n   . . . modifying qcf pool props (if any specified) for queue connection factory: " + factoryName
                        modifyOneQCFPool(cfgDict, baseServerName, factoryName)
                                
                except:
                    msg = "\n\nException in createOneServersQueueConnectionFactories() when creating queue connection factory: " + factoryName + " for server: " + baseServerName
                    print msg
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
                
                
    except:
        msg = "\n\nException in createOneServersQueueConnectionFactories() when creating factories for server: " + baseServerName
        msg = msg + "\n    factoryName: " + factoryName
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
#   MQ queue connection factory connection & session pool properties
#   If there are no QCFs defined, method just returns with message
#--------------------------------------------------------------------
def modifyOneServersQCFPoolProps(cfgDict, baseServerName):
    try:
        nodeName = 'nodeName not defined yet'
        factoryName = 'factoryName not defined yet'
        
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['baseServerName'] == baseServerName):
                nodeList = si['nodeList'].split()
                isClustered = si['isClustered']
                try:
                    queueConnectionFactoryDict = wini.getPrefixedClauses(cfgDict,'queueConnectionFactory:' + baseServerName)
                except KeyError:
                    print "   Not modifying pools for queue connection factories for server: " + baseServerName 
                    print "     because no qcf's found in config file for that server"
                    #sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    return

                except:
                    msg = "\n\nException in modifyOneServersQCFPoolProps() when getting queue connection factories dict for server: " + baseServerName
                    print msg
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
                    
                try:
                    if (len(queueConnectionFactoryDict.keys()) == 0):
                        #print "len(queueConnectionFactoryDict.keys()):"
                        #print len(queueConnectionFactoryDict.keys())
                        ## just return quietly
                        #print "\n   . . . skipping a step:"                
                        #print "   No stanza found in config file for queue connection factories for server: " + baseServerName 
                        #print ""
                        return
                      
                except:
                    msg = "\n\nException in modifyOneServersQCFPoolProps() when checking queue connection factories dict for server: " + baseServerName
                    print msg
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
                    
                try:    
                    for factoryKey in queueConnectionFactoryDict.keys():
                        qcf = queueConnectionFactoryDict[factoryKey]
                        factoryName = qcf['name'].strip()
                        modifyOneQCFPool(cfgDict, baseServerName, factoryName)

                except:
                    msg = "\n\nException in modifyOneServersQCFPoolProps() when modifying pool for queue connection factory: " + factoryName + " for server: " + baseServerName
                    print msg
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
    except:
        msg = "\n\nException in modifyOneServersQCFPoolProps() for server: " + baseServerName
        msg = msg + "\n    factoryName: " + factoryName
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
#   MQ queue connection factory connection & session pool properties
#--------------------------------------------------------------------
def modifyOneQCFPool(cfgDict, baseServerName, factoryName):
    try:
        #print 'factoryName is: ' + factoryName
        nodeName = 'nodeName not defined yet'
        connectionConnectionTimeout = 'connectionConnectionTimeout not defined yet'
        connectionMaxConnections = 'connectionMaxConnections not defined yet'
        connectionUnusedTimeout = 'connectionUnusedTimeout not defined yet'
        connectionMinConnections = 'connectionMinConnections not defined yet'
        connectionPurgePolicy = 'connectionPurgePolicy not defined yet'
        connectionAgedTimeout = 'connectionAgedTimeout not defined yet'
        connectionReapTime = 'connectionReapTime not defined yet'

        sessionConnectionTimeout = 'sessionConnectionTimeout not defined yet'
        sessionMaxConnections = 'sessionMaxConnections not defined yet'
        sessionUnusedTimeout = 'sessionUnusedTimeout not defined yet'
        sessionMinConnections = 'sessionMinConnections not defined yet'
        sessionPurgePolicy = 'sessionPurgePolicy not defined yet'
        sessionAgedTimeout = 'sessionAgedTimeout not defined yet'
        sessionReapTime = 'sessionReapTime not defined yet'
        
        factoryNotFound = 'true'
        noConnectionPoolPropsFound = 'true'
        noSessionPoolPropsFound = 'true'
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['baseServerName'] == baseServerName):
                nodeList = si['nodeList'].split()
                isClustered = si['isClustered']
                try:
                    queueConnectionFactoryDict = wini.getPrefixedClauses(cfgDict,'queueConnectionFactory:' + baseServerName)
                except KeyError:
                    print "   Returning from modifyOneQCFPool() code: AA for queue connection factory: " + factoryName + " for server: " + baseServerName 
                    print "     because no qcf's found in config file for that server"
                    #sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    return

                except:
                    msg = "\n\nException in modifyOneQCFPool() when getting queue connection factories dict for server: " + baseServerName
                    print msg
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
                    
                try:
                    if (len(queueConnectionFactoryDict.keys()) == 0):
                        print "   Returning from modifyOneQCFPool() code: AB for queue connection factory: " + factoryName + " for server: " + baseServerName 
                        print "     because no qcf's found in config file for that server"
                        return
                      
                except:
                    msg = "\n\nException in modifyOneQCFPool() when checking queue connection factories dict for server: " + baseServerName
                    print msg
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
                    
                try:    
                    for factoryKey in queueConnectionFactoryDict.keys():
                        qcf = queueConnectionFactoryDict[factoryKey]
                        name = qcf['name'].strip()
                        if (name == factoryName):
                            factoryNotFound = 'false'
                            print "\n   . . . connection pool . . . "
                        
                            try:
                                connectionConnectionTimeout = qcf['connectionConnectionTimeout']
                                if connectionConnectionTimeout == "":
                                    raise Exception("No value was provided and prop not commented out.")
                                noConnectionPoolPropsFound = 'false'
                            except (KeyError, Exception):
                                print "\n   No value was specified in config file for connectionConnectionTimeout for server: " + baseServerName
                                print "    ... for qcf name: " + factoryName
                                print "    Continuing."
                                connectionConnectionTimeout = ""
                            
                            try:
                                connectionMaxConnections = qcf['connectionMaxConnections']
                                if connectionMaxConnections == "":
                                    raise Exception("No value was provided and prop not commented out.")
                                noConnectionPoolPropsFound = 'false'
                            except (KeyError, Exception):
                                print "\n   No value was specified in config file for connectionMaxConnections for server: " + baseServerName
                                print "    ... for qcf name: " + factoryName
                                print "    Continuing."
                                connectionMaxConnections = ""

                            try:
                                connectionMinConnections = qcf['connectionMinConnections']
                                if connectionMinConnections == "":
                                    raise Exception("No value was provided and prop not commented out.")
                                noConnectionPoolPropsFound = 'false'
                            except (KeyError, Exception):
                                print "\n   No value was specified in config file for connectionMinConnections for server: " + baseServerName
                                print "    ... for qcf name: " + factoryName
                                print "    Continuing."
                                connectionMinConnections = ""
                                
                            try:
                                connectionReapTime = qcf['connectionReapTime']
                                if connectionReapTime == "":
                                    raise Exception("No value was provided and prop not commented out.")
                                noConnectionPoolPropsFound = 'false'
                            except (KeyError, Exception):
                                print "\n   No value was specified in config file for connectionReapTime for server: " + baseServerName
                                print "    ... for qcf name: " + factoryName
                                print "    Continuing."
                                connectionReapTime = ""

                            try:
                                connectionUnusedTimeout = qcf['connectionUnusedTimeout']
                                if connectionUnusedTimeout == "":
                                    raise Exception("No value was provided and prop not commented out.")
                                noConnectionPoolPropsFound = 'false'
                            except (KeyError, Exception):
                                print "\n   No value was specified in config file for connectionUnusedTimeout for server: " + baseServerName
                                print "    ... for qcf name: " + factoryName
                                print "    Continuing."
                                connectionUnusedTimeout = ""

                            try:
                                connectionAgedTimeout = qcf['connectionAgedTimeout']
                                if connectionAgedTimeout == "":
                                    raise Exception("No value was provided and prop not commented out.")
                                noConnectionPoolPropsFound = 'false'
                            except (KeyError, Exception):
                                print "\n   No value was specified in config file for connectionAgedTimeout for server: " + baseServerName
                                print "    ... for qcf name: " + factoryName
                                print "    Continuing."
                                connectionAgedTimeout = ""

                            try:
                                connectionPurgePolicy = qcf['connectionPurgePolicy'].strip()
                                if connectionPurgePolicy == "":
                                    raise Exception("No value was provided and prop not commented out.")
                                noConnectionPoolPropsFound = 'false'
                            except (KeyError, Exception):
                                pass
                                print "\n   No value was specified in config file for connectionPurgePolicy for server: " + baseServerName
                                print "    ... for qcf name: " + factoryName
                                print "    Continuing."
                                connectionPurgePolicy = ""

                            if (noConnectionPoolPropsFound == 'true'):
                                print "\n\n   No connection pool props were specified in config file for server: " + baseServerName
                                print "    ... for qcf name: " + factoryName
                                print "    Connection pool props not modified. \n"
                            else:
                                poolType = 'connection'
                            
                                if (isClustered == 'true'):
                                    clusterName = si['clusterName']
                                    if ItemExists.clusterScopedQueueConnectionFactoryExists(cellName, clusterName, factoryName):
                                        Mq.modifyQueueConnectionFactoryPoolClusterLevel(clusterName, poolType, factoryName, connectionConnectionTimeout, connectionMaxConnections, connectionUnusedTimeout, connectionMinConnections, connectionPurgePolicy, connectionAgedTimeout, connectionReapTime)
                                    else:
                                        msg = "\n\nNo QCF found at cluster level when modifying pool props for: " + factoryName + " for server: " + baseServerName
                                        print msg
                                        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                                        sys.exit(1)
                                else:
                                # not clustered, so look for existing thing at server level isntead
                                    nodeNumber = 1
                                    nodeName = nodeList[0]
                                    serverName = baseServerName + str(nodeNumber)
                                    if (ItemExists.serverScopedQueueConnectionFactoryExists(cellName, nodeName, serverName, factoryName)):
                                        Mq.modifyQueueConnectionFactoryPoolServerLevel(nodeName, serverName, poolType, factoryName, connectionConnectionTimeout, connectionMaxConnections, connectionUnusedTimeout, connectionMinConnections, connectionPurgePolicy, connectionAgedTimeout, connectionReapTime)
                                    else:
                                        msg = "\n\nNo QCF found at server level when modifying pool props for: " + factoryName + " for server: " + baseServerName
                                        print msg
                                        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                                        sys.exit(1)                                

                            print "\n   . . . session pool . . . " 
                            try:
                                sessionConnectionTimeout = qcf['sessionConnectionTimeout']
                                if sessionConnectionTimeout == "":
                                    raise Exception("No value was provided and prop not commented out.")
                                noSessionPoolPropsFound = 'false'
                            except (KeyError, Exception):
                                print "\n   No value was specified in config file for sessionConnectionTimeout for server: " + baseServerName
                                print "    ... for qcf name: " + factoryName
                                print "    Continuing."
                                sessionConnectionTimeout = ""
                            
                            try:
                                sessionMaxConnections = qcf['sessionMaxConnections']
                                if sessionMaxConnections == "":
                                    raise Exception("No value was provided and prop not commented out.")
                                noSessionPoolPropsFound = 'false'
                            except (KeyError, Exception):
                                print "\n   No value was specified in config file for sessionMaxConnections for server: " + baseServerName
                                print "    ... for qcf name: " + factoryName
                                print "    Continuing."
                                sessionMaxConnections = ""

                            try:
                                sessionMinConnections = qcf['sessionMinConnections']
                                if sessionMinConnections == "":
                                    raise Exception("No value was provided and prop not commented out.")
                                noSessionPoolPropsFound = 'false'
                            except (KeyError, Exception):
                                print "\n   No value was specified in config file for sessionMinConnections for server: " + baseServerName
                                print "    ... for qcf name: " + factoryName
                                print "    Continuing."
                                sessionMinConnections = ""
                                
                            try:
                                sessionReapTime = qcf['sessionReapTime']
                                if sessionReapTime == "":
                                    raise Exception("No value was provided and prop not commented out.")
                                noSessionPoolPropsFound = 'false'
                            except (KeyError, Exception):
                                print "\n   No value was specified in config file for sessionReapTime for server: " + baseServerName
                                print "    ... for qcf name: " + factoryName
                                print "    Continuing."
                                sessionReapTime = ""

                            try:
                                sessionUnusedTimeout = qcf['sessionUnusedTimeout']
                                if sessionUnusedTimeout == "":
                                    raise Exception("No value was provided and prop not commented out.")
                                noSessionPoolPropsFound = 'false'
                            except (KeyError, Exception):
                                print "\n   No value was specified in config file for sessionUnusedTimeout for server: " + baseServerName
                                print "    ... for qcf name: " + factoryName
                                print "    Continuing."
                                sessionUnusedTimeout = ""

                            try:
                                sessionAgedTimeout = qcf['sessionAgedTimeout']
                                if sessionAgedTimeout == "":
                                    raise Exception("No value was provided and prop not commented out.")
                                noSessionPoolPropsFound = 'false'
                            except (KeyError, Exception):
                                print "\n   No value was specified in config file for sessionAgedTimeout for server: " + baseServerName
                                print "    ... for qcf name: " + factoryName
                                print "    Continuing."
                                sessionAgedTimeout = ""

                            try:
                                sessionPurgePolicy = qcf['sessionPurgePolicy'].strip()
                                if sessionPurgePolicy == "":
                                    raise Exception("No value was provided and prop not commented out.")
                                noSessionPoolPropsFound = 'false'
                            except (KeyError, Exception):
                                print "\n   No value was specified in config file for sessionPurgePolicy for server: " + baseServerName
                                print "    ... for qcf name: " + factoryName
                                print "    Continuing."
                                sessionPurgePolicy = ""                                
                                

                            #print "\n\n noSessionPoolPropsFound: " + noSessionPoolPropsFound
                                    
                            if (noSessionPoolPropsFound == 'true'):
                                print "\n\n   No session pool props were specified in config file for server: " + baseServerName
                                print "    ... for qcf name: " + factoryName
                                print "    Session pool props not modified. \n"
                            else:
                                
                                poolType = 'session'
                            
                                if (isClustered == 'true'):
                                    clusterName = si['clusterName']
                                    if ItemExists.clusterScopedQueueConnectionFactoryExists(cellName, clusterName, factoryName):
                                        Mq.modifyQueueConnectionFactoryPoolClusterLevel(clusterName, poolType, factoryName, sessionConnectionTimeout, sessionMaxConnections, sessionUnusedTimeout, sessionMinConnections, sessionPurgePolicy, sessionAgedTimeout, sessionReapTime)
                                    else:
                                        msg = "\n\nNo QCF found at cluster level when modifying pool props for: " + factoryName + " for server: " + baseServerName
                                        print msg
                                        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                                        sys.exit(1)
                                else:
                                # not clustered, so look for existing thing at server level isntead
                                    nodeNumber = 1
                                    nodeName = nodeList[0]
                                    serverName = baseServerName + str(nodeNumber)
                                    if (ItemExists.serverScopedQueueConnectionFactoryExists(cellName, nodeName, serverName, factoryName)):
                                        Mq.modifyQueueConnectionFactoryPoolServerLevel(nodeName, serverName, poolType, factoryName, sessionConnectionTimeout, sessionMaxConnections, sessionUnusedTimeout, sessionMinConnections, sessionPurgePolicy, sessionAgedTimeout, sessionReapTime)
                                    else:
                                        msg = "\n\nNo QCF found at server level when modifying pool props for: " + factoryName + " for server: " + baseServerName
                                        print msg
                                        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                                        sys.exit(1)
                                
                            
                    if (factoryNotFound == 'true'):
                        print "   Returning from modifyOneQCFPool() code: AC for queue connection factory: " + factoryName + " for server: " + baseServerName 
                        print "     because qcf of that name not found in config file for that server"
                        return
                                
                except:
                    msg = "\n\nException in modifyOneQCFPool() when modifying pool for queue connection factory: " + factoryName + " for server: " + baseServerName
                    print msg
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
    except:
        msg = "\n\nException in modifyOneQCFPool() for server: " + baseServerName
        msg = msg + "\n    factoryName: " + factoryName
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)



#--------------------------------------------------------------------
#   MQ queue connection factory connection & session pool properties
#   Modify props for all servers or clusters in cell
#   Method provided because wsadmin default for qcf pool props does 
#     not match admin console defaults - after lots of them had been created
#   Even if that were not so, it is likely to be useful, e.g., for setting
#     timeouts as a "policy" in one swipe to whole cell
#--------------------------------------------------------------------
def modifyAllQCFPoolPropsInCell(cfgDict):
    try:
        cellName = 'cellName not defined yet'
        nodeName = 'nodeName not defined yet'
        serverName = 'serverName not defined yet'
        clusterName = 'clusterName not defined yet'
        baseServerName = 'baseServerName not defined yet'
        #description is for the set of qcf props, not for an individ qcf
        description = 'description not defined yet'

        # the following are non-advanced pool settings to apply to all qcf's found in cell
        connectionMaxConnections = 'connectionMaxConnections not defined yet'
        connectionMaxConnections = 'connectionMaxConnections not defined yet'
        connectionUnusedTimeout = 'connectionUnusedTimeout not defined yet'
        connectionMinConnections = 'connectionMinConnections not defined yet'
        connectionPurgePolicy = 'connectionPurgePolicy not defined yet'
        connectionAgedTimeout = 'connectionAgedTimeout not defined yet'
        connectionReapTime = 'connectionReapTime not defined yet'

        sessionMaxConnections = 'sessionMaxConnections not defined yet'
        sessionMaxConnections = 'sessionMaxConnections not defined yet'
        sessionUnusedTimeout = 'sessionUnusedTimeout not defined yet'
        sessionMinConnections = 'sessionMinConnections not defined yet'
        sessionPurgePolicy = 'sessionPurgePolicy not defined yet'
        sessionAgedTimeout = 'sessionAgedTimeout not defined yet'
        sessionReapTime = 'sessionReapTime not defined yet'
        
        noPropsFoundInConfigFile = 'true'
        noQcfsFoundAtClusterLevel = 'true'
        noQcfsFoundAtServerLevel = 'true'
        
        queueConnectionFactorySetDict = ()
        try:
            queueConnectionFactorySetDict = cfgDict['queueConnectionFactorySet:cellLevel']
        except KeyError:
            print "\n   . . . not modifying props for all QCF's found in cell"                
            print "   No stanza found in config file for global queue connection factory props. "
            print "   Expected to find stanza headed: [queueConnectionFactorySet:cellLevel]."
            print "   Returning from modifyAllQCFPoolPropsInCell()."
            print
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            return

        except:
            msg = "\n\nException in modifyAllQCFPoolPropsInCell() when getting dict of global queue connection factory props."
            print msg
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            sys.exit(1)
            
        if len(queueConnectionFactorySetDict) == 0:
            print "\n\n  queueConnectionFactorySetDict is zero length\n\n"
            print "\n   . . . not modifying props for all QCF's found in cell"                
            print "   No stanza found in config file for global queue connection factory props. "
            print "   Expected to find stanza headed: [queueConnectionFactorySet:cellLevel]."
            print "   Returning from modifyAllQCFPoolPropsInCell()."
            print
            return
        else:    
            try:
                #description is for the set of qcf props, not for an individ qcf
                description = queueConnectionFactorySetDict['description'].strip()
                print "\n   Reading props from global set of QCF pool props in config file: " + description
            except KeyError:
                print "\n   No value was specified in config file for description for this set of qcf pool props."
                description = "No description was specified in config file."
                print description
                print "\n Continuing."

            try:
                connectionConnectionTimeout = queueConnectionFactorySetDict['connectionConnectionTimeout']
                noPropsFoundInConfigFile = 'false'
            except KeyError:
                print "\n   No value was specified in config file for connectionConnectionTimeout for this set of global qcf pool props."
                print "    Continuing."
                connectionConnectionTimeout = ""
            
            try:
                connectionMaxConnections = queueConnectionFactorySetDict['connectionMaxConnections']
                noPropsFoundInConfigFile = 'false'
            except KeyError:
                print "\n   No value was specified in config file for connectionMaxConnections for this set of global qcf pool props."
                print "    Continuing."
                connectionMaxConnections = ""

            try:
                connectionMinConnections = queueConnectionFactorySetDict['connectionMinConnections']
                noPropsFoundInConfigFile = 'false'
            except KeyError:
                print "\n   No value was specified in config file for connectionMinConnections for this set of global qcf pool props."
                print "    Continuing."
                connectionMinConnections = ""
                
            try:
                connectionReapTime = queueConnectionFactorySetDict['connectionReapTime']
                noPropsFoundInConfigFile = 'false'
            except KeyError:
                print "\n   No value was specified in config file for connectionReapTime for this set of global qcf pool props."
                print "    Continuing."
                connectionReapTime = ""

            try:
                connectionUnusedTimeout = queueConnectionFactorySetDict['connectionUnusedTimeout']
                noPropsFoundInConfigFile = 'false'
            except KeyError:
                print "\n   No value was specified in config file for connectionUnusedTimeout for this set of global qcf pool props."
                print "    Continuing."
                connectionUnusedTimeout = ""

            try:
                connectionAgedTimeout = queueConnectionFactorySetDict['connectionAgedTimeout']
                noPropsFoundInConfigFile = 'false'
            except KeyError:
                print "\n   No value was specified in config file for connectionAgedTimeout for this set of global qcf pool props."
                print "    Continuing."
                connectionAgedTimeout = ""

            try:
                connectionPurgePolicy = queueConnectionFactorySetDict['connectionPurgePolicy'].strip()
                noPropsFoundInConfigFile = 'false'
            except KeyError:
                pass
                print "\n   No value was specified in config file for connectionPurgePolicy for this set of global qcf pool props."
                print "Continuing."
                connectionPurgePolicy = ""
                


            try:
                sessionMaxConnections = queueConnectionFactorySetDict['sessionMaxConnections']
                noPropsFoundInConfigFile = 'false'
            except KeyError:
                print "\n   No value was specified in config file for sessionMaxConnections for this set of global qcf pool props."
                print "    Continuing."
                sessionMaxConnections = ""
            
            try:
                sessionMaxConnections = queueConnectionFactorySetDict['sessionMaxConnections']
                noPropsFoundInConfigFile = 'false'
            except KeyError:
                print "\n   No value was specified in config file for sessionMaxConnections for this set of global qcf pool props."
                print "    Continuing."
                sessionMaxConnections = ""

            try:
                sessionMinConnections = queueConnectionFactorySetDict['sessionMinConnections']
                noPropsFoundInConfigFile = 'false'
            except KeyError:
                print "\n   No value was specified in config file for sessionMinConnections for this set of global qcf pool props."
                print "    Continuing."
                sessionMinConnections = ""
                
            try:
                sessionReapTime = queueConnectionFactorySetDict['sessionReapTime']
                noPropsFoundInConfigFile = 'false'
            except KeyError:
                print "\n   No value was specified in config file for sessionReapTime for this set of global qcf pool props."
                print "    Continuing."
                sessionReapTime = ""

            try:
                sessionUnusedTimeout = queueConnectionFactorySetDict['sessionUnusedTimeout']
                noPropsFoundInConfigFile = 'false'
            except KeyError:
                print "\n   No value was specified in config file for sessionUnusedTimeout for this set of global qcf pool props."
                print "    Continuing."
                sessionUnusedTimeout = ""

            try:
                sessionAgedTimeout = queueConnectionFactorySetDict['sessionAgedTimeout']
                noPropsFoundInConfigFile = 'false'
            except KeyError:
                print "\n   No value was specified in config file for sessionAgedTimeout for this set of global qcf pool props."
                print "    Continuing."
                sessionAgedTimeout = ""

            try:
                sessionPurgePolicy = queueConnectionFactorySetDict['sessionPurgePolicy'].strip()
                noPropsFoundInConfigFile = 'false'
            except KeyError:
                pass
                print "\n   No value was specified in config file for sessionPurgePolicy for this set of global qcf pool props."
                print "Continuing."
                sessionPurgePolicy = ""                
                
                
            
            if noPropsFoundInConfigFile == 'true':
                print "\n   No props found in config file for set of qcf props: " + description
                print "     Returning from modifyAllQCFPoolPropsInCell()"
                return
        
            environmentGenInfo = cfgDict['cellInfo']
            cellName = environmentGenInfo['cellName'].strip()
            serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
            for serverInfoKey in serverInfoDict.keys():
                si = serverInfoDict[serverInfoKey]
                baseServerName = si['baseServerName'].strip()
                nodeList = si['nodeList'].split()
                isClustered = si['isClustered'].strip()
                try:
                    # we will skip servers that don't have qcf's
                    queueConnectionFactoryDict = wini.getPrefixedClauses(cfgDict,'queueConnectionFactory:' + baseServerName)
                except KeyError:
                    print "\n For qcf pool props set: " + description
                    print "   Not modifying pools for queue connection factories for server: " + baseServerName 
                    print "     because no qcf's found in config file for that server"
                    # go on to next server in loop
                    continue
                except:
                    msg = "\n\nException in modifyAllQCFPoolPropsInCell() when getting queue connection factories dict for server: " + baseServerName
                    print msg
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

                try:
                    if (len(queueConnectionFactoryDict.keys()) == 0):
                        print "\n For qcf pool props set: " + description
                        print "   Not modifying pools for queue connection factories for server: " + baseServerName 
                        print "     because no qcf's found in config file for that server"
                        # go on to next server in loop
                        continue
                except:
                    msg = "\n\nException in modifyAllQCFPoolPropsInCell() when checking queue connection factories dict for server: " + baseServerName
                    print msg
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
                        
                try:    
                    if (isClustered == 'true'):
                        clusterName = si['clusterName']
                        # expect all qcf's for this server to be at cluster level
                        jmsProviderScopePath = '/Cell:' + cellName + '/ServerCluster:' + clusterName
                        try:
                            scopeId = AdminConfig.getid(jmsProviderScopePath)
                            queueConnectionFactoryIdList = AdminTask.listWMQConnectionFactories(scopeId).splitlines()
                        except:
                            msg = "\n\nException in modifyAllQCFPoolPropsInCell() when getting list of qcf's at cluster level for server: " + baseServerName + " cluster name: " + clusterName
                            print msg
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            sys.exit(1)
                        
                        for queueConnectionFactoryId in queueConnectionFactoryIdList:
                            factoryName = AdminConfig.showAttribute(queueConnectionFactoryId, 'name')
                            noQcfsFoundAtClusterLevel = 'false'
                            try:
                                poolType = 'connection'
                                Mq.modifyQueueConnectionFactoryPoolByScope(poolType, jmsProviderScopePath, factoryName, connectionConnectionTimeout, connectionMaxConnections, connectionUnusedTimeout, connectionMinConnections, connectionPurgePolicy, connectionAgedTimeout, connectionReapTime)
                                
                                poolType = 'session'
                                Mq.modifyQueueConnectionFactoryPoolByScope(poolType, jmsProviderScopePath, factoryName, sessionConnectionTimeout, sessionMaxConnections, sessionUnusedTimeout, sessionMinConnections, sessionPurgePolicy, sessionAgedTimeout, sessionReapTime)
                            except:
                                msg = "\n\nException in modifyAllQCFPoolPropsInCell() when modifying pool for queue connection factory: " + factoryName + " for clustered server: " + baseServerName
                                print msg
                                sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                                sys.exit(1)
                            
                        if noQcfsFoundAtClusterLevel == 'true':
                            msg = "\n\n QCFs exist at cluster level in config file for clustered server: " + baseServerName
                            msg += "But no QCFs were found in WAS cell at cluster level for cluster: " + clusterName
                            print "Exiting."
                            print msg
                            sys.exit(1)
                    else:
                    # not clustered, so look for existing thing at server level isntead
                        nodeNumber = 1
                        nodeName = nodeList[0]
                        serverName = baseServerName + str(nodeNumber)
                        jmsProviderScopePath='/Node:'+nodeName+'/Server:'+serverName+'/'
                        try:
                            scopeId = AdminConfig.getid(jmsProviderScopePath)
                            queueConnectionFactoryIdList = AdminTask.listWMQConnectionFactories(scopeId).splitlines()
                        except:
                            msg = "\n\nException in modifyAllQCFPoolPropsInCell() when getting list of qcf's at server level for server: " + baseServerName + " cluster name: " + clusterName
                            print msg
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            sys.exit(1)
                        
                        for queueConnectionFactoryId in queueConnectionFactoryIdList:
                            factoryName = AdminConfig.showAttribute(queueConnectionFactoryId, 'name')
                            noQcfsFoundAtServerLevel = 'false'
                            
                            try:
                                poolType = 'connection'
                                Mq.modifyQueueConnectionFactoryPoolByScope(poolType, jmsProviderScopePath, factoryName, connectionConnectionTimeout, connectionMaxConnections, connectionUnusedTimeout, connectionMinConnections, connectionPurgePolicy, connectionAgedTimeout, connectionReapTime)
                                
                                poolType = 'session'
                                Mq.modifyQueueConnectionFactoryPoolByScope(poolType, jmsProviderScopePath, factoryName, sessionConnectionTimeout, sessionMaxConnections, sessionUnusedTimeout, sessionMinConnections, sessionPurgePolicy, sessionAgedTimeout, sessionReapTime)
                            except:
                                msg = "\n\nException in modifyAllQCFPoolPropsInCell() when modifying pool for queue connection factory: " + factoryName + " for unclustered server: " + baseServerName
                                print msg
                                sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                                sys.exit(1)
                            
                        if noQcfsFoundAtServerLevel == 'true':
                            msg = "\n\n QCFs exist at server level in config file for unclustered server: " + baseServerName
                            msg += "But no QCFs were found in WAS cell at server level for server: " + clusterName
                            print "Exiting."
                            print msg
                            sys.exit(1)
                except:
                        msg = "\n\nException in modifyAllQCFPoolPropsInCell() when modifying pools for server: " + baseServerName
                        print msg
                        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                        sys.exit(1)
    except:
        msg = "\n\nException in modifyAllQCFPoolPropsInCell() "
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
#   MQ queue
#--------------------------------------------------------------------
def createOneServersQueue(cfgDict, baseServerName):
    try:
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()
        nodeName = 'nodeName not defined yet'
        queueName = 'queueName not defined yet'
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['baseServerName'] == baseServerName):
                nodeList = si['nodeList'].split()
                isClustered = si['isClustered']
                try:
                
                    queueDict = wini.getPrefixedClauses(cfgDict,'queue:' + baseServerName)

                except KeyError:
                    print "\n   . . . skipping a step:"                
                    print "   No stanza found in config file for queues for server: " + baseServerName 
                    print ""
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    return
                except:
                    msg = "\n\nException in createOneServersQueue() when getting queue dict for server: " + baseServerName
                    print msg
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

                try:
                    if (len(queueDict.keys()) == 0):
                        #print "len(queueDict.keys()):"
                        #print len(queueDict.keys())
                        print "\n   . . . skipping a step:"                
                        print "   No stanza found in config file for queues for server: " + baseServerName 
                        print ""
                        return
                      
                except:
                    msg = "\n\nException in createOneServersQueueConnectionFactories() when checking queue dict for server: " + baseServerName
                    print msg
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
                    
                try:    
                    for queueKey in queueDict.keys():
                        q = queueDict[queueKey]
                        queueName = q['name'].strip()
                        jndiName = q['jndiName'].strip()
                        description = q['description']
                        baseQueueName = q['baseQueueName'].strip()
                        baseQueueManagerName = q['baseQueueManagerName'].strip()
                        queueManagerHost = ""
                        queueManagerPort = 0
                        serverConnectionChannelName = ""
                        CCSID = ""
                        useNativeEncoding = ""
                        sendAsync = ""
                        readAhead = ""
                        try:
                            queueManagerHost = q['queueManagerHost'].strip()
                        except KeyError:
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])                        
                            print "\n   . . . Warning:"                
                            print "   No queueManagerHost found in config file for queue: " + queueName + " for server: " + baseServerName 
                            print "   This may be necessary for backout queue to work."
                            print "   At any rate, it is needed to view MQ queue details in admin console."
                            print "\n . . . . . continuing " 
                            print ""
                        try:
                            #.strip() - not needed as port is an int
                            queueManagerPort = q['queueManagerPort']
                        except KeyError:
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])                        
                            print "\n   . . . Warning:"                
                            print "   No queueManagerPort found in config file for queue: " + queueName + " for server: " + baseServerName 
                            print "   This may be necessary for backout queue to work."
                            print "   At any rate, it is needed to view MQ queue details in admin console."                            
                            print "\n . . . . . continuing "   
                            print ""                            
                        try:    
                            serverConnectionChannelName = q['serverConnectionChannelName'].strip()
                        except KeyError:
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            print "\n   . . . Warning:"                
                            print "   No serverConnectionChannelName found in config file for queue: " + queueName + " for server: " + baseServerName 
                            print "   This may be necessary for backout queue to work."
                            print "   At any rate, it is needed to view MQ queue details in admin console."                            
                            print "\n . . . . . continuing " 
                            print ""
                        try:    
                            CCSID = q['CCSID']
                            if CCSID == "":
                                raise Exception("No value was provided and prop not commented out.")
                        except (KeyError, Exception):
                            print "\n   . . . no coded character set identifier was specified for queue: " + queueName + " in config file for:" + baseServerName
                            CCSID = MqDefaults.getCCSID()
                            print "    Explicitly setting coded character set identifier to the default it is supposed to be per Infocenter: " + CCSID
                        try:    
                            useNativeEncoding = q['useNativeEncoding'].strip()
                            if useNativeEncoding == "":
                                raise Exception("No value was provided and prop not commented out.")
                        except (KeyError, Exception):
                            print "\n   . . . value for useNativeEncoding was not specified for queue: " + queueName + " in config file for:" + baseServerName
                            useNativeEncoding = MqDefaults.getUseNativeEncoding()                            
                            print "    Explicitly setting value to the default it is supposed to be per Infocenter: " + useNativeEncoding

                        try:    
                            sendAsync = q['sendAsync'].strip()
                            if sendAsync == "":
                                raise Exception("No value was provided and prop not commented out.")                                
                        except (KeyError, Exception):
                            print "\n   . . . value for sendAsync was not specified for queue: " + queueName + " in config file for:" + baseServerName
                            sendAsync = MqDefaults.getSendAsync()                            
                            print "    Explicitly setting value to the default it is supposed to be per Infocenter: " + sendAsync

                        try:    
                            readAhead = q['readAhead'].strip()
                            if readAhead == "":
                                raise Exception("No value was provided and prop not commented out.")                                
                        except (KeyError, Exception):
                            print "\n   . . . value for readAhead was not specified for queue: " + queueName + "  in config file for:" + baseServerName
                            readAhead = MqDefaults.getReadAhead()
                            print "    Explicitly setting value to the default it is supposed to be per Infocenter: " + readAhead
                            
                            
                        if (isClustered == 'true'):
                            clusterName = si['clusterName']
                            if ItemExists.clusterScopedQueueExists(cellName, clusterName, queueName):
                                print "\n   . . . skipping a step:"                
                                print "   Queue named: " + queueName + " already exists for cluster: " + clusterName
                            else:
                                Mq.createQueueClusterLevel(clusterName, queueName, description, jndiName, baseQueueName, baseQueueManagerName, queueManagerHost, queueManagerPort, serverConnectionChannelName, CCSID, useNativeEncoding, sendAsync, readAhead)
                            
                        else:
                        # not clustered, so look for existing thing at server level isntead
                            nodeNumber = 1
                            nodeName = nodeList[0]
                            serverName = baseServerName + str(nodeNumber)
                            if (ItemExists.serverScopedQueueExists(cellName, nodeName, serverName, queueName)):
                                print "\n   . . . skipping a step:"                
                                print "   Queue: " + queueName + " already exists for server: " + serverName
                            else:
                                Mq.createQueueServerLevel(nodeName, serverName, queueName, description, jndiName, baseQueueName, baseQueueManagerName, queueManagerHost, queueManagerPort, serverConnectionChannelName, CCSID, useNativeEncoding, sendAsync, readAhead)

                except:
                    msg = "\n\nException in createOneServersQueue() when creating queue: " + queueName + " for server: " + baseServerName
                    print msg
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

                            
    except:
        msg = "\n\nException in createOneServersQueue() when creating queues for server: " + baseServerName
        msg = msg + "\n    queueName: " + queueName
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
#   MDB listener ports
#--------------------------------------------------------------------
def createOneServersListenerPorts(cfgDict, baseServerName):
    try:
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()

        nodeName = 'nodeName not defined yet'
        listenerName = 'listenerName not defined yet'
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['baseServerName'] == baseServerName):
                nodeList = si['nodeList'].split()
                try:
                
                    listenerDict = wini.getPrefixedClauses(cfgDict,'listenerPort:' + baseServerName)
                    for listenerKey in listenerDict.keys():
                        l = listenerDict[listenerKey]
                        listenerName = l['name'].strip()
                        description = l['description']
                        connectionFactoryJNDIName = l['connectionFactoryJNDIName'].strip()
                        destinationJNDIName = l['destinationJNDIName'].strip()
                        maxSessions = l['maxSessions']
                        maxRetries = l['maxRetries']
                        maxMessages = l['maxMessages']

                        nodeNumber = 0
                        for nodeName in nodeList:
                            nodeNumber += 1
                            serverName = baseServerName + str(nodeNumber)
                            if ItemExists.serverScopedListenerPortExists(cellName, nodeName, serverName, listenerName):
                                print "\n   . . . skipping a step:"                
                                print "   Listener port: " + listenerName + " already exists for server: " + serverName
                                return

                            Mq.createListenerPort(nodeName, serverName, listenerName, description, connectionFactoryJNDIName, destinationJNDIName, maxSessions, maxRetries, maxMessages)
                            
                except KeyError:
                    print "\n   . . . skipping a step:"                
                    print "   No stanza found in config file for listener ports for server: " + baseServerName 
                    print ""
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    return
                except:
                    msg = "\n\nException in createOneServersListenerPorts() when getting listener ports dict for server: " + baseServerName
                    print msg
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
                            
    except:
        msg = "\n\nException in createOneServersListenerPorts() when creating listener ports for server: " + baseServerName
        msg = msg + "\n    listenerName: " + listenerName
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def createOneServersJMSActivationSpecs(cfgDict, baseServerName):
#--------------------------------------------------------------------
# JMS activation specs are from  Java EE Connector Architecture (JCA) 1.5
#  sort of combines together the idea of listener port + queueConnectionFactory
# will be created at cluster level if server is clustered; server level otherwise
#--------------------------------------------------------------------
    cellName = 'cellName not defined yet'
    nodeName = 'nodeName not defined yet'
    activationSpecName = 'activationSpecName not defined yet'
    jndiName = 'jndiName not defined yet'
    description = 'description not defined yet'
    destinationJndiName = 'destinationJndiName not defined yet'
    destinationType = 'destinationType not defined yet'
    qmgrName = 'qmgrName not defined yet'
    qmgrHostname = 'qmgrHostname not defined yet'
    qmgrPortNumber = 'qmgrPortNumber not defined yet'
    qmgrSvrconnChannel = 'qmgrSvrconnChannel not defined yet'
    wmqTransportType = 'wmqTransportType not defined yet'
    try:
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['baseServerName'] == baseServerName):
                nodeList = si['nodeList'].split()
                try:
                    jmsActivationSpecDict = wini.getPrefixedClauses(cfgDict,'jmsActivationSpec:' + baseServerName +':')

                except:
                    msg = "\n\nException in createOneServersJMSActivationSpecs() when getting jmsActivationSpecDict for server: " + baseServerName
                    print msg
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
                    
                try:
                    if (len(jmsActivationSpecDict.keys()) == 0):
                        #print "len(jmsActivationSpecDict.keys()):"
                        #print len(jmsActivationSpecDict.keys())
                        print "\n   . . . skipping a step:"                
                        print "   No stanza found in config file for jms activation specs for server: " + baseServerName 
                        print ""
                        return
                except:
                    msg = "\n\nException in createOneServersJMSActivationSpecs() when checking jmsActivationSpecDict for server: " + baseServerName
                    print msg
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

                isClustered = si['isClustered']
                for jmsActivationSpecKey in jmsActivationSpecDict.keys():
                    ja = jmsActivationSpecDict[jmsActivationSpecKey]
                    activationSpecName = ja['activationSpecName'].strip()
                    jndiName = ja['jndiName'].strip()
                    description = ja['description'].strip()
                    destinationJndiName = ja['destinationJndiName'].strip()
                    destinationType = ja['destinationType'].strip()
                    qmgrName = ja['qmgrName'].strip()
                    qmgrHostname = ja['qmgrHostname'].strip()
                    qmgrPortNumber = str(ja['qmgrPortNumber']).strip()
                    qmgrSvrconnChannel = ja['qmgrSvrconnChannel'].strip()
                    wmqTransportType = ja['wmqTransportType'].strip()
                    

                    try:
                        if (isClustered == 'true'):
                            clusterName = si['clusterName']
                            if ItemExists.clusterScopedJMSActivationSpecExists(cellName, clusterName, activationSpecName):
                                print "\n   . . . skipping a step:"                
                                print "   JMS Activation spec: " + activationSpecName + " already exists for cluster: " + clusterName
                                return
                            Mq.createJMSActivationSpecClusterLevel(clusterName, activationSpecName, jndiName, description, destinationJndiName, destinationType, qmgrName, qmgrHostname, qmgrPortNumber, qmgrSvrconnChannel, wmqTransportType)
                        else:
                        # not clustered, so look for existing ja at server level isntead
                            nodeNumber = 1
                            nodeName = nodeList[0]
                            serverName = baseServerName + str(nodeNumber)
                            if ItemExists.serverScopedJMSActivationSpecExists(cellName, nodeName, serverName, activationSpecName):
                                print "\n   . . . skipping a step:"                
                                print "   JMS Activation spec: " + activationSpecName + " already exists for server: " + serverName
                                return
                            Mq.createJMSActivationSpecServerLevel(nodeName, serverName, activationSpecName, jndiName, description, destinationJndiName, destinationType, qmgrName, qmgrHostname, qmgrPortNumber, qmgrSvrconnChannel, wmqTransportType)
                    
                    except:
                        msg = "\n\nException in createOneServersJMSActivationSpecs() when creating activationSpec for server: " + baseServerName
                        msg = msg + "\n    activationSpecName: " + activationSpecName
                        print msg
                        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                        sys.exit(1)

    except:
        msg = "\n\nException in createOneServersJMSActivationSpecs() for server: " + baseServerName
        msg = msg + "\n    activationSpecName: " + activationSpecName
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
#   session replication step 1: create domain for HTTP session replication
#--------------------------------------------------------------------
def createOneServersReplicationDomain(cfgDict, baseServerName):
    try:
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        name = "replication domain name not defined yet"
        numberOfReplicas = "numberOfReplicas not defined yet"
        requestTimeout = "requestTimeout not defined yet"
        encryptionType = "encryptionType not defined yet"
        useSSL = "useSSL not defined yet"
        replicateStatefulSessionBeans = "replicateStatefulSessionBeans not defined yet"
        try:
            replicationDomainInfoDict = wini.getPrefixedClauses(cfgDict,'sessionReplicationDomain:')

            for replicationDomainInfoKey in replicationDomainInfoDict.keys():
                ri = replicationDomainInfoDict[replicationDomainInfoKey]
                replicationDomainMembersList = ri['replicationDomainMembers'].split()
                #print "\n\n replicationDomainMembersList:\n"
                #print replicationDomainMembersList
                #print ""
                if (baseServerName in replicationDomainMembersList):
                    name = ri['name'].strip()
                    numberOfReplicas = ri['numberOfReplicas']
                    requestTimeout = ri['requestTimeout']
                    encryptionType = ri['encryptionType'].strip()
                    useSSL = ri['useSSL'].strip()
                    replicateStatefulSessionBeans = ri['replicateStatefulSessionBeans'].strip()
                    # to do - add some code to do ejb rep domain if it turns out we have any stateful session beans

                    if ItemExists.replicationDomainExists(cellName, name):
                        print "\n   . . . skipping a step:"                
                        print "   Replication domain: " + name + " already exists for server: " + baseServerName
                        return
                    
                    Ha.createReplicationDomain(cellName, name, numberOfReplicas, requestTimeout, encryptionType, useSSL)
                    
                else:
                    print "\n   . . . skipping a step:"                
                    print "No stanza found in config file for replication domain for server: " + baseServerName 
                    
        except KeyError:
            print "\n   . . . skipping a step:"                
            print "   No stanza found in config file for any replication domains"
            print ""
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            return
        except:
            msg = "\n\n Exception in createOneServersReplicationDomain() when getting dict & creating rep domain for server: " + baseServerName
            print msg
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            sys.exit(1)
                

    except:
        msg = "\n\n Exception in createOneServersReplicationDomain() for server: " + baseServerName
        msg = msg + "\n    replication domain name: " + name
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
#   session replication step 2: add server to all its rep domains
#--------------------------------------------------------------------
def addHTTPSessionManagerToDomain(cfgDict, baseServerName):
    try:
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()
        name = "replication domain name not defined yet"
        serverName = "serverName not defined yet"
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['baseServerName'] == baseServerName):
                nodeList = si['nodeList'].split()
        
        # in theory, the server can be added to multiple rep domains, 
        #  so multiple rep domains may be found in config file for same base servername 
        replicationDomainForServerIsFoundInCfg = 'false'
        domainName = "domainName not defined yet"
        try:
            replicationDomainInfoDict = wini.getPrefixedClauses(cfgDict,'sessionReplicationDomain:')

            for replicationDomainInfoKey in replicationDomainInfoDict.keys():
                ri = replicationDomainInfoDict[replicationDomainInfoKey]
                replicationDomainMembersList = ri['replicationDomainMembers'].split()
                if (baseServerName in replicationDomainMembersList):
                    replicationDomainForServerIsFoundInCfg = 'true'
                    domainName = ri['name'].strip()
                    nodeNumber = 0
                    for nodeName in nodeList:
                        nodeNumber += 1
                        #slap a number on the end of baseServerName regardless whether it is clustered or on multiple nodes
                        serverName = baseServerName + str(nodeNumber)
                        
                        Ha.addHTTPSessionManagerToDomain(nodeName, serverName, domainName)
                    
        except KeyError:
            print "\n   . . . skipping a step:"                
            print "   No stanza found in config file for any replication domains for any servers while looking for server: " + baseServerName 
            print ""
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            return
        except:
            msg = "\n\n Exception in addHTTPSessionManagerToDomain() when adding server: " + serverName + " for base server name: " + baseServerName + " to replication domain: " + domainName
            print msg
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            sys.exit(1)

        if (replicationDomainForServerIsFoundInCfg == 'false'):
            print "\n   . . . skipping a step:"                
            print "   Not adding server to any replication domain."
            print "   Because no stanza found in config file for replication domain for server: " + baseServerName 
                            
    except:
        msg = "\n\n Exception in addHTTPSessionManagerToDomain() when adding server to replication domain: " + name + " for server: " + baseServerName
        msg = msg + "\n    replication domain name: " + name + " and base server name: " + baseServerName 
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
#   session replication step 3: turn it on (also sets default tuning params recommmended by IBM)
#--------------------------------------------------------------------
def enableM2MSessionReplication(cfgDict, baseServerName):

    try:
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()
        name = "replication domain name not defined yet"
        serverName = "serverName not defined yet"
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['baseServerName'] == baseServerName):
                nodeList = si['nodeList'].split()
        
        # in theory, the server can be added to multiple rep domains, 
        #  so multiple rep domains may be found in config file for same base servername 
        replicationDomainForServerIsFoundInCfg = 'false'
        domainName = "domainName not defined yet"
        try:
            replicationDomainInfoDict = wini.getPrefixedClauses(cfgDict,'sessionReplicationDomain:')

            for replicationDomainInfoKey in replicationDomainInfoDict.keys():
                ri = replicationDomainInfoDict[replicationDomainInfoKey]
                replicationDomainMembersList = ri['replicationDomainMembers'].split()
                if (baseServerName in replicationDomainMembersList):
                    replicationDomainForServerIsFoundInCfg = 'true'
                    domainName = ri['name'].strip()
                    nodeNumber = 0
                    for nodeName in nodeList:
                        nodeNumber += 1
                        #slap a number on the end of baseServerName regardless whether it is clustered or on multiple nodes
                        serverName = baseServerName + str(nodeNumber)
                        
                        Ha.enableM2MSessionReplication(nodeName, serverName)
                    
        except KeyError:
            print "\n   . . . skipping a step:"                
            print "   No stanza found in config file for any replication domains for any servers while looking for server: " + baseServerName 
            print ""
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            return
        except:
            msg = "\n\n Exception in enableM2MSessionReplication() when adding server: " + serverName + " for base server name: " + baseServerName + " to replication domain: " + domainName
            print msg
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            sys.exit(1)

        if (replicationDomainForServerIsFoundInCfg == 'false'):
            print "\n   . . . skipping a step:"                
            print "   Not enabling memory to memory http session replication."
            print "   Because no stanza found in config file for replication domain for server: " + baseServerName 
                            
    except:
        msg = "\n\n Exception in enableM2MSessionReplication() when adding server to replication domain: " + name + " for server: " + baseServerName
        msg = msg + "\n    replication domain name: " + name + " and base server name: " + baseServerName 
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def createSharedLibraries(cfgDict, baseServerName):

    try:
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()
        libraryName = "library name not defined yet"
        serverName = "serverName not defined yet"
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['baseServerName'] == baseServerName):
                nodeList = si['nodeList'].split()
                isClustered = si['isClustered']
        
        # in theory, the server can have multiple shared libs, 
        #  so multiple libs may be found in config file for same base servername 

        try:
            sharedLibraryInfoDict = wini.getPrefixedClauses(cfgDict,'sharedLibrary:' + baseServerName)

            for sharedLibraryInfoKey in sharedLibraryInfoDict.keys():
                sli = sharedLibraryInfoDict[sharedLibraryInfoKey]
                libraryName = sli['libraryName']
                description = sli['description']
                # shared lib may have multiple classpath strings, separated by space, which is fine
                classPath = sli['classPath']
                useIsolatedClassLoader = sli['useIsolatedClassLoader']
                # classLoaderMode PARENT_LAST means the parent classes are overridden
                classLoaderMode = sli['classLoaderMode']
                
                if (isClustered == 'true'):
                    clusterName = si['clusterName']
                    if ItemExists.clusterScopedLibraryExists(clusterName, libraryName):
                        print "\n   . . . skipping a step:"                
                        print "   Library named: " + libraryName + " already exists for cluster: " + clusterName
                        return
                    
                    Library.createClusterScopedSharedLibrary(clusterName, libraryName, description, classPath, useIsolatedClassLoader)
                    
                else:
                # not clustered, so look for existing thing at server level isntead
                    nodeName = nodeList[0]
                    serverName = baseServerName + str(1)
                    if (ItemExists.serverScopedLibraryExists(nodeName, serverName, libraryName)):
                        print "\n   . . . skipping a step:"                
                        print "   Library: " + libraryName + " already exists for server: " + serverName
                        return
                        
                    Library.createServerScopedSharedLibrary(nodeName, serverName, libraryName, description, classPath, useIsolatedClassLoader)
                
                # regardless of scope of library, it gets bound to a classloader of the server, which we first have to define
                nodeNumber = 0
                for nodeName in nodeList:
                    nodeNumber += 1
                    serverName = baseServerName + str(nodeNumber)
                    ClassLoader.createServerClassLoader(nodeName, serverName, classLoaderMode)
                    Library.bindLibraryToServer(nodeName, serverName, libraryName)
                
        except KeyError:
            print "\n   . . . skipping a step:"                
            print "   No stanza found in config file for any shared libs for server: " + baseServerName 
            print ""
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            return
        except:
            msg = "\n\n Exception in createSharedLibraries() when creating & binding library: " + libraryName + " for server: " + serverName + " for base server name: " + baseServerName
            print msg
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            sys.exit(1)
        
                            
    except:
        msg = "\n\n Exception in createSharedLibraries() for server: " + baseServerName
        msg = msg + "\n    replication domain name: " + name + " and base server name: " + baseServerName 
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
#   setting needed by asynchronous bean in acfr_web app (company file)
#  in UserInterface script, can only be done by "modify" action, not as part of a "create whole file"
#--------------------------------------------------------------------
def modifyAsynchBeanDefaultWorkManager(cfgDict, baseServerName):

    try:
        name = "work manager name not defined yet"
        serverName = "serverName not defined yet"
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['baseServerName'] == baseServerName):
                nodeList = si['nodeList'].split()
                isClustered = si['isClustered']
                clusterName = si['clusterName']
        
        try:
            asynchBeanWorkManagerInfoDict = wini.getPrefixedClauses(cfgDict,'asynchBeanWorkManager:' + baseServerName)

            if (asynchBeanWorkManagerInfoDict == {} ):
                print "\n   . . . skipping a step:"                
                print "   No stanza found in config file for asynch bean work manager for server: " + baseServerName 
                print ""
                return
            
            # in theory there could be multiple work managers per base server
            for asynchBeanWorkManagerInfoKey in asynchBeanWorkManagerInfoDict.keys():
                abwm = asynchBeanWorkManagerInfoDict[asynchBeanWorkManagerInfoKey]
                name = abwm['name']
                allowOverrideToModifyExisting = abwm['allowOverrideToModifyExisting']
                jndiName = abwm['jndiName']
                category = abwm['category']
                description = abwm['description']
                workTimeout = abwm['workTimeout']
                workReqQSize = abwm['workReqQSize']
                workReqQFullAction = abwm['workReqQFullAction']
                numAlarmThreads = abwm['numAlarmThreads']
                minThreads = abwm['minThreads']
                maxThreads = abwm['maxThreads']
                threadPriority = abwm['threadPriority']
                isGrowable = abwm['isGrowable']
                serviceNames = abwm['serviceNames']
                
                if (isClustered == 'true'):
                    clusterId = ItemExists.clusterExists(clusterName)
                    if (clusterId == ""):
                        print "\n\n\n Error . . . "
                        print "   No cluster named : " + clusterName + " was found in your cell. Cluster must exist in order to add work mgr.\n"
                        sys.exit(1)
                    
                    workManagerId = ItemExists.clusterScopedAsynchBeanWorkManagerExists(clusterName, name)
                    if (workManagerId == ""):
                        print "\n\n\n Error  . . . "                
                        print "   WorkManager named: " + name + " must already exist for cluster: " + clusterName + " in order to modify it.\n\n"
                        sys.exit(1)
                        
                    else:
                        if (allowOverrideToModifyExisting == 'false'):
                            print "\n\n Error  . . . "                
                            print "   WorkManager named: " + name + " exists  for cluster: " + clusterName + " BUT 'allowOverrideToModifyExisting' is 'false'."
                            print "   If you really want to modify this existing work manager, use 'modify' action again BUT FIRST set allowOverrideToModifyExisting attribute to 'true'"
                            print "   Also pls note that it is apparently not possible to remove services from service name list for an existing work manager via script."
                            print "   If you need to remove services from service name list for an existing work manager, pls use admin console.\n"
                            sys.exit(1)
                else:
                # not clustered, so look for existing thing at server level isntead
                    nodeName = nodeList[0]
                    serverName = baseServerName + str(1)
                    serverId = ItemExists.serverExists(nodeName, serverName)
                    if (serverId == ""):
                        print "\n\n\n Error . . . "
                        print "   No server named : " + serverName + " was found in your cell. Server must exist in order to add work mgr.\n"
                        sys.exit(1)
                    
                    workManagerId = ItemExists.serverScopedAsynchBeanWorkManagerExists(nodeName, serverName, name)
                    if (workManagerId == ""):
                        print "\n\n\n Error  . . . "                
                        print "   WorkManager named: " + name + " must already exist for server: " + serverName + " in order to modify it.\n\n"
                        sys.exit(1)

                    else:
                        if (allowOverrideToModifyExisting == 'false'):
                            print "\n\n\n Error  . . . "                
                            print "   WorkManager named: " + name + " exists  for server: " + serverName + " BUT 'allowOverrideToModifyExisting' is 'false'."
                            print "   If you really want to modify this existing work manager, use 'modify' action again BUT FIRST set allowOverrideToModifyExisting attribute to 'true'"
                            print "   Also pls note that it is apparently not possible to remove services from service name list for an existing work manager via script."
                            print "   If you need to remove services from service name list for an existing work manager, pls use admin console.\n"
                            sys.exit(1)
                
                # replace values for name-type of attributes with defaults for the default work manager to prevent too much confusion
                if (name == "DefaultWorkManager"):
                    jndiName = "wm/default"
                    category = "Default"

                WorkManagers.modifyAsynchBeanWorkManager(workManagerId, name, jndiName, category, description, workTimeout, workReqQSize, workReqQFullAction, numAlarmThreads, minThreads, maxThreads, threadPriority, isGrowable, serviceNames)
                print "\n\n\n Warning:"
                print "   You have modified an EXISTING work manager: " + name + " for base server name: " + baseServerName + ".\n"
                print "   Note that it is apparently not possible to remove services from service name list for an existing work manager via script."
                print "   If you need to remove services from service name list for an existing work manager, pls use admin console.\n"
                if (name == "DefaultWorkManager"):
                    print "\n\n\n Warning:"
                    print "   You have modified the default work manager."
                    print "   Note that it may be better practice to create a new, explicitly named work manager for each application.\n"
                
        except KeyError:
            print "\n   . . . skipping a step:"                
            print "   No stanza found in config file for asynch bean work manager for server: " + baseServerName 
            print ""
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            return
        except:
            msg = "\n\n Exception in modifyAsynchBeanDefaultWorkManager() when modifying work manager: " + name + " for base server name: " + baseServerName
            print msg
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            sys.exit(1)
        
    except:
        msg = "\n\n Exception in modifyAsynchBeanDefaultWorkManager() for server: " + baseServerName
        msg = msg + "\n    work manager name: " + name 
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
#   would probably be better practice than modifying the default work manager
#--------------------------------------------------------------------
def createAsynchBeanNonDefaultWorkManagers(cfgDict, baseServerName):

    try:
        name = "work manager name not defined yet"
        serverName = "serverName not defined yet"
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['baseServerName'] == baseServerName):
                nodeList = si['nodeList'].split()
                isClustered = si['isClustered']
                clusterName = si['clusterName']                
        
        try:
            asynchBeanWorkManagerInfoDict = wini.getPrefixedClauses(cfgDict,'asynchBeanWorkManager:' + baseServerName)

            if (asynchBeanWorkManagerInfoDict == {} ):
                print "\n   . . . skipping a step:"                
                print "   No stanza found in config file for asynch bean work manager for server: " + baseServerName 
                print ""
                return
            
            # in theory there could be multiple work managers per base server
            for asynchBeanWorkManagerInfoKey in asynchBeanWorkManagerInfoDict.keys():
                abwm = asynchBeanWorkManagerInfoDict[asynchBeanWorkManagerInfoKey]
                allowOverrideToModifyExisting = abwm['allowOverrideToModifyExisting']
                name = abwm['name']
                jndiName = abwm['jndiName']
                category = abwm['category']
                description = abwm['description']
                workTimeout = abwm['workTimeout']
                workReqQSize = abwm['workReqQSize']
                workReqQFullAction = abwm['workReqQFullAction']
                numAlarmThreads = abwm['numAlarmThreads']
                minThreads = abwm['minThreads']
                maxThreads = abwm['maxThreads']
                threadPriority = abwm['threadPriority']
                isGrowable = abwm['isGrowable']
                serviceNames = abwm['serviceNames']
                if (jndiName == 'wm/default'):
                    if (allowOverrideToModifyExisting == 'false'):
                        print "\n\n Warning  . . . "                                    
                        print "   Cannot add the default work manager (jndi name: " + jndiName + ") for base server name: " + baseServerName + ". "
                        print "   To modify, set 'allowOverrideToModifyExisting' to 'true' and run modify action. \n\n"
            
                if (isClustered == 'true'):
                    clusterId = ItemExists.clusterExists(clusterName)
                    if (clusterId == ""):
                        print "\n\n Error . . . "
                        print "   No cluster named : " + clusterName + " was found in your cell. Cluster must exist in order to add work mgr.\n"
                        sys.exit(1)
                    
                    workManagerId = ItemExists.clusterScopedAsynchBeanWorkManagerExists(clusterName, name)
                    if (workManagerId != ""):
                        if (allowOverrideToModifyExisting == 'false'):
                            print "\n\n Warning:"
                            print "   WorkManager named: " + name + " already exists for cluster: " + clusterName + ". Work manager must NOT already exist for the 'create' action."
                            print "\n\n Warning:"
                            print "   The config file has 'allowOverrideToModifyExisting' is set to 'false' for this work manager.\n"
                            print "   If you really want to modify this existing work manager, use 'modify' action AND set allowOverrideToModifyExisting attribute to 'true'"
                            print "   And if any of the OTHER work managers in your config file have it set to 'false' you will need to remove them from the config file."
                            print "   Otherwise script will quit when it comes to them :-( (but it might modify this one if it comes to it first :-))."
                            print "   Also pls note that it is apparently not possible to remove services from service name list for an existing work manager via script."
                            print "   If you need to remove services from service name list for an existing work manager, pls use admin console. \n\n"
                            print "   Continuing ... \n"
                            
                        elif (allowOverrideToModifyExisting == 'true'):
                            print "\n\n Warning:"
                            print "   Work manager: " + name + " already exists for cluster: " + clusterName + ". Work manager must NOT already exist for the 'create' action."
                            print "   If you want to modify this work manager, please use 'modify' action."
                            print "   Note the 'modify' action is only valid when 'allowOverrideToModifyExisting' is set to 'true' (which it is for this work manager)."
                            print "   And if any of the OTHER work managers in your config file have it set to 'false' you will need to remove them from the config file."
                            print "   Otherwise script will quit when it comes to them :-( (but it might modify this one if it comes to it first :-))."
                            print "   Also pls note that it is apparently not possible to remove services from service name list for an existing work manager via script."
                            print "   If you need to remove services from service name list for an existing work manager, pls use admin console. \n\n"
                            print "   Continuing ... \n"
                            
                    elif (workManagerId == ""):
                        WorkManagers.createClusterLevelAsynchBeanWorkManager(clusterName, name, jndiName, category, description, workTimeout, workReqQSize, workReqQFullAction, numAlarmThreads, minThreads, maxThreads, threadPriority, isGrowable, serviceNames)
                        
                else:
                # not clustered, so look for existing thing at server level isntead
                    nodeName = nodeList[0]
                    serverName = baseServerName + str(1)
                    serverId = ItemExists.serverExists(nodeName, serverName)
                    if (serverId == ""):
                        print "\n\n Error . . . "
                        print "   No server named : " + serverName + " was found in your cell. Server must exist in order to add work mgr.\n"
                        sys.exit(1)

                    workManagerId = ItemExists.serverScopedAsynchBeanWorkManagerExists(nodeName, serverName, name)
                    if (workManagerId != ""):
                        #print "workManagerId: " + workManagerId
                        if (allowOverrideToModifyExisting == 'false'):
                            print "\n\n Warning  . . . "                
                            print "   WorkManager named: " + name + " already exists for server: " + serverName + ". Work manager must NOT already exist for the 'create' action."                            
                            print "\n\n Warning:"
                            print "   The config file has 'allowOverrideToModifyExisting' is set to 'false' for this work manager.\n"
                            print "   If you really want to modify this existing work manager, use 'modify' action AND set allowOverrideToModifyExisting attribute to 'true'"
                            print "   Also pls note that it is apparently not possible to remove services from service name list for an existing work manager via script."
                            print "   If you need to remove services from service name list for an existing work manager, pls use admin console. \n\n"
                            print "   Continuing ... \n"

                        elif (allowOverrideToModifyExisting == 'true'):
                            print "\n\n Warning:"
                            print "   Work manager: " + name + " already exists for server: " + serverName + ". Work manager must NOT already exist for the 'create' action."
                            print "   If you want to modify this work manager, please use 'modify' action."
                            print "   Note the 'modify' action is only valid when 'allowOverrideToModifyExisting' is set to 'true' (which it is for this work manager)."
                            print "   If any of the OTHER work managers in your config file have it set to 'false' you will need to remove them from the config file."
                            print "   Otherwise script will quit when it comes to them :-( (but it might modify this one if it comes to it first :-))."
                            print "   Also pls note that it is apparently not possible to remove services from service name list for an existing work manager via script."
                            print "   If you need to remove services from service name list for an existing work manager, pls use admin console. \n\n"
                            print "   Continuing ... \n"
                            
                    elif (workManagerId == ""):
                        WorkManagers.createServerLevelAsynchBeanWorkManager(nodeName, serverName, name, jndiName, category, description, workTimeout, workReqQSize, workReqQFullAction, numAlarmThreads, minThreads, maxThreads, threadPriority, isGrowable, serviceNames)
                
        except KeyError:
            print "\n   . . . skipping a step:"                
            print "   No stanza found in config file for asynch bean work manager for server: " + baseServerName 
            print ""
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            return
        except:
            msg = "\n\n Exception in createAsynchBeanNonDefaultWorkManagers() when adding work manager: " + name + " for base server name: " + baseServerName
            print msg
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            sys.exit(1)
                            
    except:
        msg = "\n\n Exception in createAsynchBeanNonDefaultWorkManagers() for server: " + baseServerName
        msg = msg + "\n    work manager name: " + name 
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


# creates or modifies (if options props already existing)
def setCyberArkOptions(WAScellName, appNickname, baseServerName, reasonStringToBind, localCacheLifeSpanStringToBind, usingCMSubjectCache):
    try:
        print "Attempting to set CyberArk options...."
        if reasonStringToBind == "default":
            reasonStringToBind = CyberarkDefaults.getReasonStringToBind(WAScellName, appNickname)
        if localCacheLifeSpanStringToBind == "default": 
            localCacheLifeSpanStringToBind = CyberarkDefaults.getLocalCacheLifeSpanStringToBind()
        if usingCMSubjectCache == "default": 
            usingCMSubjectCache = CyberarkDefaults.getUsingCMSubjectCache()
            usingCMSubjectCachePropDescription = CyberarkDefaults.getUsingCMSubjectCachePropDescription()
        
        if reasonStringToBind == "":
            print "Value specified for reasonStringToBind is empty string, using default."
            reasonStringToBind = CyberarkDefaults.getReasonStringToBind(WAScellName, appNickname)
            print "reasonStringToBind: " + reasonStringToBind
        name = appNickname + " reason for Cyberark cred fetch"
        nameInNameSpace = appNickname + "/Reason"
        stringToBind = reasonStringToBind
        if ItemExists.stringNameSpaceBindingExists(nameInNameSpace):
            WebsphereVariables.modifyStringNameSpaceBinding(name, nameInNameSpace, stringToBind)
        else:
            WebsphereVariables.createStringNameSpaceBinding(name, nameInNameSpace, stringToBind)

        if localCacheLifeSpanStringToBind == "":
            print "Value specified for localCacheLifeSpanStringToBind is empty string, using default"
            localCacheLifeSpanStringToBind = CyberarkDefaults.getLocalCacheLifeSpanStringToBind()
            print "localCacheLifeSpanStringToBind: " + localCacheLifeSpanStringToBind
        else:
            name = appNickname + " localCacheLifeSpan"
            nameInNameSpace = appNickname + "/LocalCacheLifeSpan"
            stringToBind = localCacheLifeSpanStringToBind
            if ItemExists.stringNameSpaceBindingExists(nameInNameSpace):
                WebsphereVariables.modifyStringNameSpaceBinding(name, nameInNameSpace, stringToBind)
            else:
                WebsphereVariables.createStringNameSpaceBinding(name, nameInNameSpace, stringToBind)



        # baseServerName does not have the sequence number at the end, so for clusters there is > 1 jvm
        jvmIDLIst = AdminConfig.list('JavaVirtualMachine', '*' + baseServerName + '*').splitlines()
        for id in jvmIDLIst:
            nodeName = id[id.find("nodes/")+6:id.find("servers/")-1]
            serverName = id[id.find("servers/")+8:id.find("server.xml")-1]
            propertyName = "usingCMSubjectCache"
            propertyValue = usingCMSubjectCache
            propertyDescription = usingCMSubjectCachePropDescription
            if ItemExists.jvmCustomPropExists(nodeName, serverName, propertyName):
                Jvm.modifyJvmCustomProperty(nodeName, serverName, propertyName, propertyValue, propertyDescription)
            else:
                Jvm.setJvmCustomProperty(nodeName, serverName, propertyName, propertyValue, propertyDescription)

        
    except:
        print "\n\nException in setCyberArkOptions()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        print "\n\n   Exiting . . . \n\n"
        sys.exit(1)
#--------------------------------------------------------------------
# If user chooses the "do the cyberark thing" option then:
# Cell-level Jaas entry will be generated, with name:
#    <DM node name>/appNickname
# 2 Cell-level string namespace bindings will be created, with following names generated from the nickname:
#     binding names 
#       appNickname App ID string binding
#       appNickname Query string binding
#     nameInNameSpace names 
#       appNickname/AppID
#       appNickname/Query
# Script will also: 
#    create the required JVM custom prop usingCMSubjectCache=false for each server that has a "server" clause in this file
#    look for datasources which have boolean cyberarkThisDatasource set to "true" and for each one:
#           set mappingAuthDataAlias to the generated name for the Jaas entry, based on appNickname
#           set mappingConfigAlias to the one specified in CyberarkDefaults.py
#--------------------------------------------------------------------
def cyberArkIt(cfgDict, baseServerName, appNickname, appIDStringToBind, queryStringToBind):
    try:
        if ItemExists.jaasAliasExists(appNickname):
            print "\n   . . . skipping a step:"                
            print "   Dummy Cyberark Jaas auth alias already exists: " + appNickname
        else:
            Jaas.setJaasAuthEntry(appNickname, "dummy", "dummy")
    except:
        print "\n\nException in cyberArkIt() when setting up dummy jaas/j2c entry"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        print "\n\n   Exiting . . . \n\n"
        sys.exit(1)
    try:
        name = appNickname + " App ID string binding"
        nameInNameSpace = appNickname + "/AppID"
        stringToBind = appIDStringToBind
        if ItemExists.stringNameSpaceBindingExists(nameInNameSpace):
            print "\n   . . . skipping a step:"                
            print "   String Namespace Binding nameInNameSpace already exists: " + nameInNameSpace
        else:
            WebsphereVariables.createStringNameSpaceBinding(name, nameInNameSpace, stringToBind)
            
        name = appNickname + " Query string binding"
        nameInNameSpace = appNickname + "/Query"
        stringToBind = queryStringToBind
        if ItemExists.stringNameSpaceBindingExists(nameInNameSpace):
            print "\n   . . . skipping a step:"                
            print "   String Namespace Binding nameInNameSpace already exists: " + nameInNameSpace
        else:
            WebsphereVariables.createStringNameSpaceBinding(name, nameInNameSpace, stringToBind)
    except:
        print "\n\nException in cyberArkIt() when setting up the global vars (aka string namespace bindings)"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        print "\n\n   Exiting . . . \n\n"
        sys.exit(1)
    try:
        createOneServersDatasources(cfgDict, baseServerName)
    except:
        print "\n\nException in cyberArkIt() when creating datasources for: " + baseServerName
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        print "\n\n   Exiting . . . \n\n"
        sys.exit(1)
        



def modifyHttpQueueTuningParams(cfgDict, baseServerName, portName):
    try:
        httpTuningInfoDict = {}
        tcpMaxOpenConnections = "tcpMaxOpenConnections not defined yet"
        tcpInactivityTimeout = "tcpInactivityTimeout not defined yet"
        tcpListenBacklog = "tcpListenBacklog not defined yet"
        httpKeepAlive = "httpKeepAlive not defined yet"
        httpMaximumPersistentRequests = "httpMaximumPersistentRequests not defined yet"
        httpPersistentTimeout = "httpPersistentTimeout not defined yet"
        httpReadTimeout = "httpReadTimeout not defined yet"
        httpWriteTimeout = "httpWriteTimeout not defined yet"
        noHttpTuningPropsFound = 'true'
        configMessage = ""
        try:
            serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
            for serverInfoKey in serverInfoDict.keys():
                si = serverInfoDict[serverInfoKey]
                if (si['baseServerName'] == baseServerName):
                    nodeList = si['nodeList'].split()
                    isClustered = si['isClustered']
        
            if portName == "WC_defaulthost":
                httpTuningInfoDict = wini.getPrefixedClauses(cfgDict,'httpTuningInfo:WC_defaulthost:' + baseServerName)
            elif portName == "WC_defaulthost_secure":
                httpTuningInfoDict = wini.getPrefixedClauses(cfgDict,'httpTuningInfo:WC_defaulthost_secure:' + baseServerName)
            else:
                print "\n\n portName: " + portName + " not recognized in modifyHttpQueueTuningParams()"
                print "Exiting."
                sys.exit(1)      

            if (len(httpTuningInfoDict) == 0):
                print "\n   . . . skipping a step:"                
                print "   No stanza found in config file for tuning port: " + portName + " for server: " + baseServerName 
                print ""
                return

            if (len(httpTuningInfoDict.keys()) == 0):
                #print "len(httpTuningInfoDict.keys()):"
                #print len(httpTuningInfoDict.keys())
                print "\n   . . . skipping a step:"                
                print "   No values found in config file for tuning port: " + portName + " for server: " + baseServerName 
                print ""
                return
            
            for key in httpTuningInfoDict.keys():
                ht = httpTuningInfoDict[key]
                break
                #example of ht: {'httpPersistentTimeout': 60, 'tcpListenBacklog': 200, 'httpWriteTimeout': 120, 'httpReadTimeout': 120, 'tcpInactivityTimeout': 120, 'httpKeepAlive': 'false', 'httpMaximumPersistentRequests': 10000, 'tcpMaxOpenConnections': 500}

            
        except:
            msg = "\n\nException in modifyHttpQueueTuningParams() when getting dict for portName: " + portName + " for server: " + baseServerName
            print msg
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            sys.exit(1)      
        
        try:
            tcpMaxOpenConnections = ht['tcpMaxOpenConnections']
            if tcpMaxOpenConnections == "":
                raise Exception("No value was provided and prop not commented out.")
            noHttpTuningPropsFound = 'false'
        except (KeyError, Exception):
            configMessage += "\n   No value in config file for tcpMaxOpenConnections for portName: " + portName + " for server: " + baseServerName
            tcpMaxOpenConnections = ""

            
        try:
            tcpInactivityTimeout = ht['tcpInactivityTimeout']
            if tcpInactivityTimeout == "":
                raise Exception("No value was provided and prop not commented out.")
            noHttpTuningPropsFound = 'false'
        except (KeyError, Exception):
            configMessage += "\n   No value in config file for tcpInactivityTimeout for portName: " + portName + " for server: " + baseServerName
            tcpInactivityTimeout = ""
            
            
        try:
            tcpListenBacklog = ht['tcpListenBacklog']
            if tcpListenBacklog == "":
                raise Exception("No value was provided and prop not commented out.")
            noHttpTuningPropsFound = 'false'
        except (KeyError, Exception):
            configMessage += "\n   No value in config file for tcpListenBacklog for portName: " + portName + " for server: " + baseServerName
            tcpListenBacklog = ""
            
            
        try:
            httpKeepAlive = ht['httpKeepAlive']
            if httpKeepAlive == "":
                raise Exception("No value was provided and prop not commented out.")
            noHttpTuningPropsFound = 'false'
        except (KeyError, Exception):
            configMessage += "\n   No value in config file for httpKeepAlive for portName: " + portName + " for server: " + baseServerName
            httpKeepAlive = ""
            
            
        try:
            httpMaximumPersistentRequests = ht['httpMaximumPersistentRequests']
            if httpMaximumPersistentRequests == "":
                raise Exception("No value was provided and prop not commented out.")
            noHttpTuningPropsFound = 'false'
        except (KeyError, Exception):
            configMessage += "\n   No value in config file for httpMaximumPersistentRequests for portName: " + portName + " for server: " + baseServerName
            httpMaximumPersistentRequests = ""
            
            
        try:
            httpPersistentTimeout = ht['httpPersistentTimeout']
            if httpPersistentTimeout == "":
                raise Exception("No value was provided and prop not commented out.")
            noHttpTuningPropsFound = 'false'
        except (KeyError, Exception):
            configMessage += "\n   No value in config file for httpPersistentTimeout for portName: " + portName + " for server: " + baseServerName
            httpPersistentTimeout = ""
            
            
        try:
            httpReadTimeout = ht['httpReadTimeout']
            if httpReadTimeout == "":
                raise Exception("No value was provided and prop not commented out.")
            noHttpTuningPropsFound = 'false'
        except (KeyError, Exception):
            configMessage += "\n   No value in config file for httpReadTimeout for portName: " + portName + " for server: " + baseServerName
            httpReadTimeout = ""
            
            
        try:
            httpWriteTimeout = ht['httpWriteTimeout']
            if httpWriteTimeout == "":
                raise Exception("No value was provided and prop not commented out.")
            noHttpTuningPropsFound = 'false'
        except (KeyError, Exception):
            configMessage += "\n   No value in config file for httpWriteTimeout for portName: " + portName + " for server: " + baseServerName
            httpWriteTimeout = ""

        if (noHttpTuningPropsFound == 'true'):
            print "\n\n   No HTTP tuning props were specified in config file for portName: " + portName + " for server: " + baseServerName
            print "    HTTP tuning props not modified. \n"
            print "Details:"
            print configMessage
        else:
            if configMessage != "":
                print configMessage
                print "\n    Continuing."
                
            nodeNumber = 0
            for nodeName in nodeList:
                nodeNumber += 1
                #print 'nodeNumber is: ' + str(nodeNumber)
                serverName = baseServerName + str(nodeNumber)
                #print 'serverName is: ' + serverName 
                WebContainer.modifyHttpQueueTuningParams(nodeName, serverName, portName, tcpMaxOpenConnections, tcpInactivityTimeout, tcpListenBacklog, httpKeepAlive, httpMaximumPersistentRequests, httpPersistentTimeout, httpReadTimeout, httpWriteTimeout)
            
    except:
        msg = "\n\n Exception in modifyHttpQueueTuningParams() for server: " + baseServerName
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    
#--------------------------------------------------------------------
# Call each server-level create method for the given base server name (minus the sequence number at end)
# If a server for the base name already exists on any node in 
# the node list, do nothing (i.e., have to blow away the servers first
# before running this method)
#--------------------------------------------------------------------
def doServer(cfgDict, baseServerName):
    try:
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        serverNameIsFoundInCfg = 'false'
        atLeastOneServerAlreadyExists = 'false'
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['baseServerName'] == baseServerName):
                serverNameIsFoundInCfg = 'true'
                nodeList = si['nodeList'].split()
                nodeNumber = 0
                for nodeName in nodeList:
                    nodeNumber += 1
                    #slap a number on the end of baseServerName whether it is clustered (on > 1 node) or not (1 node)
                    newServerName = baseServerName + str(nodeNumber)
                    if ItemExists.serverExists(nodeName, newServerName):
                        atLeastOneServerAlreadyExists = 'true'
                        print "\n\n   . . . oops:"
                        print "   Server already exists: " + newServerName + " on node: " + nodeName
                        print "   No changes will be made to this server."
                        
        if (serverNameIsFoundInCfg == 'false'):
            msg = '\n\nSpecified serverName: ' + baseServerName + ' not found in config file.'                    
            print msg  
            sys.exit(1)

        if (atLeastOneServerAlreadyExists == 'true'):      
            msg = " . . . . . . . . . . . . . . . "
            msg += '\n\nAt least one server with the specified base serverName: ' + baseServerName + ' already exists.\n'
            print msg  
            return
    except:
        msg = "\n\nException in doServer() for server: " + baseServerName + " when checking server name"
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)



        
    try:
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            if (si['baseServerName'] == baseServerName):

                createOneVirtualHost(cfgDict, baseServerName)
                
                nodeList = si['nodeList'].split()
                nodeNumber = 0
                for nodeName in nodeList:
                    nodeNumber += 1
                    #slap a number on the end of baseServerName whether it is clustered (on > 1 node) or not (1 node)
                    newServerName = baseServerName + str(nodeNumber)
                    # only create server on 1st node whether clustered or not
                    # i.e., if isClustered is false, ignore any extraneous nodes in node list
                    if (nodeNumber == 1):
                        
                        createServer(cfgDict, nodeName, newServerName)
                 
                # addServersToCluster has no effect if isClustered is false
                addServersToCluster(cfgDict, baseServerName)
                
                setPorts(cfgDict, baseServerName)
                setJvmProcessDefinition(cfgDict, baseServerName)
                setJvmLogRolling(cfgDict, baseServerName)
                createJvmCustomProps(cfgDict, baseServerName)
                setTransactionServiceProperties(cfgDict, baseServerName)
                setDefaultVirtualHost(cfgDict, baseServerName)
                setWebContainerProperties(cfgDict, baseServerName)
                setWebContainerThreadPoolProperties(cfgDict, baseServerName)
                setWebContainerCustomProperties(cfgDict, baseServerName)
                setSessionCookieSettings(cfgDict, baseServerName)
                createOneServersDatasources(cfgDict, baseServerName)
                addOneServersDatasourcesCustomProps(cfgDict, baseServerName)
                createOneServersQueueConnectionFactories(cfgDict, baseServerName)
                modifyOneServersQCFPoolProps(cfgDict, baseServerName)
                createOneServersQueue(cfgDict, baseServerName)
                createOneServersListenerPorts(cfgDict, baseServerName)
                createOneServersJMSActivationSpecs(cfgDict, baseServerName)                
                createOneServersReplicationDomain(cfgDict, baseServerName)
                addHTTPSessionManagerToDomain(cfgDict, baseServerName)
                enableM2MSessionReplication(cfgDict, baseServerName)
                createSharedLibraries(cfgDict, baseServerName)
                createAsynchBeanNonDefaultWorkManagers(cfgDict, baseServerName)
                extractServerArchive(cfgDict, baseServerName)
                extractServerPropsFile(cfgDict, baseServerName)                
    except:
        msg = "\n\nException in doServer() for server: " + baseServerName
        print msg
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        AdminConfig.save()
    except:
        print "Exception in doServer() for server: " + baseServerName + " when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
# Get list of servers from config
# call doServer() for each one
#--------------------------------------------------------------------
def doServers(cfgDict):
    try:
        try:
            baseServerName = 'baseServerName not defined yet'
            serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')

        except:
            msg = "\n\nException in doServers() when getting server info out of config object"
            print msg
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            sys.exit(1)

        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            baseServerName = si['baseServerName']
            doServer(cfgDict, baseServerName)
    except:
        print "\n\nException in doServers()  for server: " + baseServerName
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)




#when this module is being run as top-level script
if __name__=="__main__":
    usage = " "
    usage = usage + " "
    usage = usage + "Usage: not meant to be called as a top-level script."
    usage = usage + " . . . and must have modified soap.client.props of target wsadmin profile if security is enabled\n"
    print "\n\n" + usage


