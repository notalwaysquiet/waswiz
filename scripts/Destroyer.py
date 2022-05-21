###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
# Notes
#   This top-level Jython script includes the following procedures:
#       
#       blowAwayEnv(configFile)
#       blowAwayAllCellScopedWebsphereVariable(cfgDict)
#       blowAwayOneCellScopedWebsphereVariable(variableNameToBlowAway)
#      zeroOutOneNodeScopedWebsphereVariable
#       blowAwayAllVirtualHosts(cfgDict)
#       blowAwayOneVirtualHost(virtualHostName)
#       blowAwayOneServersVirtualHost(serverBaseNameItsFor)
#       blowAwayAllClustersServers(cfgDict)
#       blowAwayCluster(clusterName)
#       blowAwayServer(nodeName, serverName)
#       blowAwayAllJaas(cfgDict)
#       blowAwayOneJaas(aliasToDelete)
#       blowAwayOneServersJdbcProvider(cellName, nodeName, serverName, dbType)
#       blowAwayOneServersDatasource(cellName, nodeName, serverName, dbType, dataSourceName)
#       blowAwayOneServersQueueConnectionFactory(cellName, nodeName, serverName, factoryName)
#       blowAwayOneServersQueue(cellName, nodeName, serverName, queueName)
#       blowAwayOneServersListenerPort(cellName, nodeName, serverName, listenerName)
#       
#  
# . . . . and imports the following Jython scripts (not listed in order):
#   ItemExists.py
#   wini.py

# Linux
# sudo /opt/IBM/wasv9/profiles/dmgrPlum/bin/wsadmin.sh -f Destroyer.py cell_level_v1_0.ini

# standalone environment - windows
# wsadmin.bat -p C:\qdr\ETP_dev\config_scripts\wsadmin_properties_files\custom.properties -f c:/qdr/ETP_dev/config_scripts/Destroyer.py c:/qdr/ETP_dev/ standalone_config_windows_c_drive_servers.ini

#   It is required to explicitly "import" sub-scripts into each script that will call them

#
#   Special requirements:
#   This script requires a cell named as in ini file, and server node(s) named likewise, quit otherwise
#
#
###############################################################################


import os
import sys
import time

SCRIPT_CONFIG_VERSION = '1.0'

def blowAwayEnv(configFile):
    '''Delete from your Websphere environment everything in config file. Leaves cell and node intact, along with any other config not mentioned in file. '''
    # wini.py reads windows-style ini files & returns nested dict named 'cfgDict'
    try:
        cfgDict=wini.load(open(configFile))
    except:
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        print "\n Can't find config file, "
        print "  or other problem with config file: " + configFile
        print "Exiting."
        sys.exit("error parsing config file")

    try:
        configInfo = cfgDict['configInfo']
        confver = configInfo['confver']
    except:
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        print "\n Can't find the version of config file.\n"
        print "Exiting."
        sys.exit("error reading config file version")
        
    if (confver != SCRIPT_CONFIG_VERSION):
        print "\n Version numbers of configFile and this script must match."
        print "   Version of configFile: *" + str(confver) + "*"
        print "   Version of script: *" + str(SCRIPT_CONFIG_VERSION) + "*"
        print "Exiting."
        sys.exit("config file version mismatch")

    try:
        print "\n"  
        print "---------------------------------------------------------------"
        print " Blow away a Websphere Environment from config file"
        print "---------------------------------------------------------------"
        print "\n\n"
        
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()
        
        try:
            if ItemExists.cellExists(cellName):
                print "Target cell: \n    " + cellName
            else:
                print "\nThe specified cell: " + cellName + " does not exist."
                actual_cell = Utilities.get_cell_name()
                print "This script is being run in cell: " + actual_cell
                print "Run this script from wsadmin for dmgr profile of the target cell."
                sys.exit("wrong cell")
 
        except:
            print "\n\nException in blowAwayEnv() when checking general config & cell info"
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            sys.exit(1)

        try:
            blowAwayAllClustersServers(cfgDict)

        except:
            print "\n\nException in blowAwayEnv() when blowing away clusters/servers"
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            print "\n\n    Continuing . . . \n\n"
        try:
            pass
            blowAwayAllJaas(cfgDict)
        except:
            print "\n\nException in blowAwayEnv() when blowing away jaas/j2c auth entries"
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            print "\n\n    Continuing . . . \n\n"

        try:
            pass
            blowAwayAllCellScopedWebsphereVariable(cellName, cfgDict)
        except:
            print "\n\nException in blowAwayEnv() when blowing away cell-scoped websphere variables"
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            print "\n\n    Continuing . . . \n\n"

        try:
            pass
            blowAwayAllVirtualHosts(cfgDict)
        except:
            print "\n\nException in blowAwayEnv() when blowing away virtual hosts"
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            print "\n\n    Continuing . . . \n\n"

        try:
            pass
            blowAwayAllRepDomains(cfgDict)
        except:
            print "\n\nException in blowAwayEnv() when blowing away replication domains"
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            print "\n\n    Continuing . . . \n\n"
            
            
    except:
        print "\n\nException in blowAwayEnv() when calling various submethods"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        print "\n\n    Continuing . . . \n\n"            
    try:
        AdminConfig.save()
    except:
        print "\n\nException in blowAwayEnv() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    print "\nend of blowAwayEnv()"


def blowAwayAllCellScopedWebsphereVariable(cellName, cfgDict):
    '''Delete all specified cell-scoped Websphere variables '''
    print "\n"
    print "begin blowAwayAllCellScopedWebsphereVariable()"
    try:
        websphereVariablesDict = wini.getPrefixedClauses(cfgDict,'websphereVariables:' + 'cellLevel' +':')
        for websphereVariablesKey in websphereVariablesDict.keys():
            wv = websphereVariablesDict[websphereVariablesKey]
            variableNameToBlowAway = wv['symbolicName']
            blowAwayOneCellScopedWebsphereVariable(cellName, variableNameToBlowAway)

    except:
        print "\n\nException in blowAwayAllCellScopedWebsphereVariable()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    
    print "\nend of blowAwayAllCellScopedWebsphereVariable()"


def blowAwayOneCellScopedWebsphereVariable(cellName, variableNameToBlowAway):
    '''Delete a cell-scoped Websphere variable '''
    print "\n"
    print "begin blowAwayOneCellScopedWebsphereVariable()"
    try:
        if (variableNameToBlowAway == 'WAS_CELL_NAME'):
            print "\nCan not blow away variable: 'WAS_CELL_NAME' or Websphere will break\n"
            return

        variableId = ItemExists.cellScopedVariableExists(cellName, variableNameToBlowAway)
        if variableId:
            AdminConfig.remove(variableId)
            print "blew away cell-level websphere variable: " + variableNameToBlowAway
            AdminConfig.save()
        else:
            print "cell-scoped variable: " + variableNameToBlowAway + " not found"

    except:
        print "\n\nException in blowAwayOneCellScopedWebsphereVariable()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    
    print "end of blowAwayOneCellScopedWebsphereVariable()"


def zeroOutAllNodeScopedWebsphereVariable(cfgDict):
    '''Zero out the values for all node level WAS vars.'''
    print "\n"
    print "begin zeroOutAllNodeScopedWebsphereVariable()"
    nodeName = "nodeName not assigned yet"
    try:
        websphereVariablesDict = wini.getPrefixedClauses(cfgDict,'websphereVariables:' + 'nodeLevel' +':')
        #print "websphereVariablesDict: "
        #print websphereVariablesDict
        nodeList = Utilities.get_node_name_list()
        
        for websphereVariablesKey in websphereVariablesDict.keys():
            wv = websphereVariablesDict[websphereVariablesKey]
            variableNameToBlowAway = wv['symbolicName']
            for nodeName in nodeList:
                #print "nodeName: " + nodeName
                zeroOutOneNodeScopedWebsphereVariable(nodeName, variableNameToBlowAway)
    except:
        print "\n\nException in zeroOutAllNodeScopedWebsphereVariable()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    
    print "end of zeroOutAllNodeScopedWebsphereVariable()"


def zeroOutOneNodeScopedWebsphereVariable(nodeName, variableNameToBlowAway):
    '''Zero out the value for node level WAS var. Primarily for JDBC drivers, which for some reason are created blank when node is created in WAS 6.1 & WAS7 (but not for MySQL). Not sure about later versions.'''
    print "\n"
    print "begin zeroOutOneNodeScopedWebsphereVariable() for node name: " + nodeName
    try:
        nodeId = AdminConfig.getid("/Node:" + nodeName + "/")
        #print "nodeID: *" + nodeId + "*"
        #print 'AdminConfig.list("VariableSubstitutionEntry", nodeId): '
        #print "*" + AdminConfig.list("VariableSubstitutionEntry", nodeId) + "*"
        varSubstitutions = Utilities.convertToList(AdminConfig.list("VariableSubstitutionEntry", nodeId))

        for varSubst in varSubstitutions:
           getVarName = AdminConfig.showAttribute(varSubst, "symbolicName")
           if getVarName == variableNameToBlowAway:
              newVarValue = ""
              AdminConfig.modify(varSubst,[["value", newVarValue]])
              break
    except:
        print "\n\nException in zeroOutOneNodeScopedWebsphereVariable()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    
    print "end of zeroOutOneNodeScopedWebsphereVariable()"


def blowAwayAllVirtualHosts(cfgDict):
    '''Delete all specified virtual hosts '''
    print "\n"
    print "begin blowAwayAllVirtualHosts()"
    try:
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            hostsWebApps = si['hostsWebApps']
            if (hostsWebApps == 'true'):
                virtualHostName = si['virtualHostName']
                blowAwayOneVirtualHost(virtualHostName)

    except:
        print "\n\nException in blowAwayAllVirtualHosts(cfgDict)"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    print "\nend of blowAwayAllVirtualHosts()"


def blowAwayOneVirtualHost(virtualHostName):
    '''Delete a virtual host by name'''
    print "\n"
    print "begin blowAwayOneVirtualHost()"
    try:
        virtualHostId = ItemExists.virtualHostExists(virtualHostName)
        if virtualHostId:
            AdminConfig.remove(virtualHostId)
            print "blew away virtual host: " + virtualHostName
            AdminConfig.save()
        else:
            print "virtual host: " + virtualHostName + " not found"
    except:
        print "\n\nException in blowAwayOneVirtualHost()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    print "end of blowAwayOneVirtualHost()"

    
def blowAwayOneServersVirtualHost(cfgDict, serverBaseNameItsFor):
    '''Delete a server's virtual host. To be called manually after deleting a single server, to clean up. '''
# to do: call it
    print "\n"
    print "begin blowAwayOneServersVirtualHost()"
    try:
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            baseServerName = si['baseServerName']
            if (baseServerName == serverBaseNameItsFor):
                hostsWebApps = si['hostsWebApps']
                if (hostsWebApps == 'true'):
                    virtualHostName = si['virtualHostName']
                    blowAwayOneVirtualHost(virtualHostName)
                else:
                    print "According to config file, server: " + serverBaseNameItsFor + " isn't supposed to have a virtualhost."
                    print "Please check hostsWebApps property for server: " + serverBaseNameItsFor
                    print "Virtual host name in config file: " + virtualHostName + " (if it exists) will not be deleted."
                    sys.exit(1)

    except:
        print "\n\nException in blowAwayOneServersVirtualHost(serverBaseNameItsFor)"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    print "end of blowAwayOneServersVirtualHost()"
    

def blowAwayAllClustersServers(cfgDict):
    '''Delete all clusters & servers that are listed in config dict. Also blows away any servers in each cluster, and blows away all server-level data sources etc. '''
    print "\n"
    print "begin blowAwayAllClustersServers()"
    try:
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            nodeList = si['nodeList'].split()
            baseServerName = si['baseServerName']
            isClustered = si['isClustered']
            #print '\n\nbaseServerName is: ' + baseServerName
            if (isClustered == 'true'):
                clusterName = si['clusterName']
                blowAwayCluster(clusterName)
                
                #make sure all the servers are really gone
                # i.e., server(s) may not have successfully gotten clustered
                nodeNumber = 0
                for nodeName in nodeList:
                    nodeNumber += 1
                    serverName = baseServerName + str(nodeNumber)
                    serverId = AdminConfig.getid('/Node:'+nodeName+'/Server:'+serverName+'/')
                    if (len(serverId) >0):
                        blowAwayServer(nodeName, serverName)
            else:
                #server was not clustered
                serverName = baseServerName + "1"
                nodeName = nodeList[0]
                blowAwayServer(nodeName, serverName)

    except:
        print "\n\nException in blowAwayAllClustersServers(cfgDict)"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    
    print "\nend of blowAwayAllClustersServers()"


def blowAwayCluster(clusterName):
    ''' Delete cluster. Also blows away any servers in cluster, server-level data sources etc. '''
    print "\n"
    print "begin blowAwayCluster()"
    try:
        clusterId = ItemExists.clusterExists(clusterName)
        if clusterId:
            AdminConfig.remove(clusterId)
            print "blew away cluster: " + clusterName
            AdminConfig.save()
        else:
            print "cluster: " + clusterName + " not found"
    except:
        print "\n\nException in blowAwayCluster()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    
    print "end of blowAwayCluster()"


def blowAwayServer(nodeName, serverName):
    ''' Delete a server, including its server-level jdbc provider, data sources etc. '''
    print "\n"
    print "begin blowAwayServer()"
    try:    
        serverId=ItemExists.serverExists(nodeName,serverName)
        if serverId :
            AdminConfig.remove(serverId)
            print "blew away server: " + serverName
            AdminConfig.save()
        else:
            print "server: " + serverName + " not found"
    except:
        print "\n\nException in blowAwayServer()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    
    print "end of blowAwayServer()"


def blowAwayAllJaas(cfgDict):
    ''' Delete all specified Jaas entries '''
    print "\n"
    print "begin blowAwayAllJaas()"
    try:
        jaasList = Utilities.convertToList(AdminConfig.list('JAASAuthData'))
        print '\njaasList before is: ' 
        #print jaasList
        for jaasId in jaasList:
            print AdminConfig.showAttribute(jaasId, 'alias')

        jaasAuthEntryDict = wini.getPrefixedClauses(cfgDict,'jaasAuthEntry:' + 'cellLevel' +':')
        for jaasAuthEntryKey in jaasAuthEntryDict.keys():
            jae = jaasAuthEntryDict[jaasAuthEntryKey]
            aliasToDelete = jae['alias']
            blowAwayOneJaas(aliasToDelete)

        jaasList = Utilities.convertToList(AdminConfig.list('JAASAuthData'))
        print '\njaasList afterwards is: ' 
        #print jaasList
        for jaasId in jaasList:
            print AdminConfig.showAttribute(jaasId, 'alias')
        #AdminConfig.save()
    except:
        print "\n\nException in blowAwayAllJaas()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
    print "\nend of blowAwayAllJaas()"


def blowAwayOneJaas(aliasToDelete):
    ''' Delete a Jaas entry '''
    print "\n"
    print "begin blowAwayOneJaas()"
    try:
        jaasId = ItemExists.jaasAliasExists(aliasToDelete)
        if jaasId:
            AdminConfig.remove(jaasId)
            print "removed JAASAuthData alias: " + aliasToDelete
            AdminConfig.save()
        else:
            print "aliasToDelete: " + aliasToDelete + " not found"
    except:
        print "\n\nException in blowAwayOneJaas() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
    print "end of blowAwayOneJaas()"


def blowAwayOneServersJvmCustomProperty(nodeName, serverName, jvmCustomPropName):
    ''' Delete one server's JVM custom property '''
    print "\n"
    print "begin blowAwayOneServersJvmCustomProperty()"
    try:
        id = ItemExists.jvmCustomPropExists(nodeName, serverName, jvmCustomPropName)
        if id:
            AdminConfig.remove(id)
            print "removed JVM custom property: " + jvmCustomPropName + " for server: " + serverName
            AdminConfig.save()
        else:
            print "JVM custom property: " + jvmCustomPropName + " for server: " + serverName + " not found"
    except:
        print "\n\nException in blowAwayOneServersJvmCustomProperty() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
    print "end of blowAwayOneServersJvmCustomProperty()"


def blowAwayOneServersJdbcProvider(cellName, nodeName, serverName, dbType):
    ''' Delete one server's JDBC Provider '''
    print "\n"
    print "begin blowAwayOneServersJdbcProvider()"
    try:
        id = ItemExists.serverScopedJdbcProviderExists(cellName, nodeName, serverName, dbType)
        if id:
            AdminConfig.remove(id)
            print "removed JDBC Provider: " + dbType + " for server: " + serverName
            AdminConfig.save()
        else:
            print "JDBC Provider: " + dbType + " for server: " + serverName + " not found"
    except:
        print "\n\nException in blowAwayOneServersJdbcProvider() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
    print "end of blowAwayOneServersJdbcProvider()"


def blowAwayOneServersDatasource(cellName, nodeName, serverName, dbType, dataSourceName):
    ''' Delete one server's datasource '''
    print "\n"
    print "begin blowAwayOneServersDatasource()"
    try:
        id = ItemExists.serverScopedDataSourceExists(cellName, nodeName, serverName, dbType, dataSourceName)
        if id:
            AdminConfig.remove(id)
            print "removed datasource: " + dataSourceName + " for server: " + serverName
            AdminConfig.save()
        else:
            print "datasource: " + dataSourceName + " for server: " + serverName + " not found"
    except:
        print "\n\nException in blowAwayOneServersDatasource() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
    print "end of blowAwayOneServersDatasource()"


def blowAwayOneClustersDatasource(clusterName, dbType, dataSourceName):
    ''' Delete one cluster's datasource '''
    print "\n"
    print "begin blowAwayOneClustersDatasource()"
    try:
        id = ItemExists.clusterScopedDataSourceExists(clusterName, dbType, dataSourceName)
        if id:
            AdminConfig.remove(id)
            print "removed datasource: " + dataSourceName + " for cluster: " + clusterName
            AdminConfig.save()
        else:
            print "datasource: " + dataSourceName + " for cluster: " + clusterName + " not found"
    except:
        print "\n\nException in blowAwayOneClustersDatasource() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
    print "end of blowAwayOneClustersDatasource()"


def blowAwayOneServersQueueConnectionFactory(cellName, nodeName, serverName, factoryName):
    '''Delete Queue Connection Factory for one server '''
    print "\n"
    print "begin blowAwayOneServersQueueConnectionFactory()"
    try:
        id = ItemExists.serverScopedQueueConnectionFactoryExists(cellName, nodeName, serverName, factoryName)
        if id:
            AdminConfig.remove(id)
            print "removed MQ queue connection factory: " + factoryName + " for server: " + serverName
            AdminConfig.save()
        else:
            print "MQ queue connection factory: " + factoryName + " for server: " + serverName + " not found"
    except:
        print "\n\nException in blowAwayOneServersQueueConnectionFactory() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
    print "end of blowAwayOneServersQueueConnectionFactory()"


def blowAwayOneClustersQueueConnectionFactory(cellName, clusterName, factoryName):
    '''Delete Queue Connection Factory for one cluster '''
    print "\n"
    print "begin blowAwayOneClustersQueueConnectionFactory()"
    try:
        id = ItemExists.clusterScopedQueueConnectionFactoryExists(cellName, clusterName, factoryName)
        if id:
            AdminConfig.remove(id)
            print "removed MQ queue connection factory: " + factoryName + " for cluster: " + clusterName
            AdminConfig.save()
        else:
            print "MQ queue connection factory: " + factoryName + " for cluster: " + clusterName + " not found"
    except:
        print "\n\nException in blowAwayOneClustersQueueConnectionFactory() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
    print "end of blowAwayOneClustersQueueConnectionFactory()"


def blowAwayOneServersQueue(cellName, nodeName, serverName, queueName):
    '''Delete queue for one server '''
    print "\n"
    print "begin blowAwayOneServersQueue()"
    try:
        id = ItemExists.serverScopedQueueExists(cellName, nodeName, serverName, queueName)
        if id:
            AdminConfig.remove(id)
            print "removed MQ queue: " + queueName + " for server: " + serverName
            AdminConfig.save()
        else:
            print "MQ queue: " + queueName + " for server: " + serverName + " not found"
    except:
        print "\n\nException in blowAwayOneServersQueue() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
    print "end of blowAwayOneServersQueue()"


def blowAwayOneClustersQueue(cellName, clusterName, queueName):
    '''Delete queue for one cluster '''
    print "\n"
    print "begin blowAwayOneClustersQueue()"
    try:
        id = ItemExists.clusterScopedQueueExists(cellName, clusterName, queueName)
        if id:
            AdminConfig.remove(id)
            print "removed MQ queue: " + queueName + " for cluster: " + clusterName
            AdminConfig.save()
        else:
            print "MQ queue: " + queueName + " for cluster: " + clusterName + " not found"
    except:
        print "\n\nException in blowAwayOneClustersQueue() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
    print "end of blowAwayOneClustersQueue()"


def blowAwayOneServersListenerPort(cellName, nodeName, serverName, listenerName):
    '''Delete server's Message Listener Port '''
    print "\n"
    print "begin blowAwayOneServersListenerPort()"
    try:
        id = ItemExists.serverScopedListenerPortExists(cellName, nodeName, serverName, listenerName)
        if id:
            AdminConfig.remove(id)
            print "removed Message Listener Port: " + listenerName + " for server: " + serverName
            AdminConfig.save()
        else:
            print "Message Listener Port: " + listenerName + " for server: " + serverName + " not found"
    except:
        print "\n\nException in blowAwayOneServersListenerPort() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
    print "end of blowAwayOneServersListenerPort()"


def blowAwayOneRepDomain(cellName, domainName):
    '''Delete specified replication domain  '''
    print "\n"
    print "begin blowAwayOneRepDomain()"
    
    try:
        id = ItemExists.replicationDomainExists(cellName, domainName)
        if id:
            AdminConfig.remove(id)
            print "removed replication domain: " + domainName
    
        else:
            print "replication domain: " + domainName + " not found in WAS"
        
        AdminConfig.save()
                    
    except:
        print "\n\nException in blowAwayOneRepDomain() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
    print "end of blowAwayOneRepDomain()"


def blowAwayAllRepDomains(cfgDict):
    '''Delete all replication domains in config file that also have servers specified in same config file '''
    print "\n"
    print "begin blowAwayAllRepDomains()"
    
    try:
        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()
        domainName = "domainName not defined yet"
        replicationDomainIsBlownAway = 'false'
        
        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        replicationDomainInfoDict = wini.getPrefixedClauses(cfgDict,'sessionReplicationDomain:')

        for replicationDomainInfoKey in replicationDomainInfoDict.keys():
            ri = replicationDomainInfoDict[replicationDomainInfoKey]
            replicationDomainMembersList = ri['replicationDomainMembers'].split()

            for serverInfoKey in serverInfoDict.keys():
                si = serverInfoDict[serverInfoKey]
                baseServerName = si['baseServerName']
                if (baseServerName in replicationDomainMembersList):
                    replicationDomainForServerIsFoundInCfg = 'true'
                    domainName = ri['name'].strip()

                    # in theory, lion_server & tiger_server could both use same rep domain
                    # so don't try to blow away rep domain if it has already been done
                    if (replicationDomainIsBlownAway == 'false'):
                        blowAwayOneRepDomain(cellName, domainName)
                        replicationDomainIsBlownAway = 'true'
        
        AdminConfig.save()
        
    except KeyError:
        print "\n   . . . skipping a step:"                
        print "   No stanza found in config file for any replication domains for any servers while looking for server: " + baseServerName 
        print ""
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        return
                    

    except:
        print "\n\nException in blowAwayAllRepDomains() on domain: " + domainName
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

        
    print "end of blowAwayAllRepDomains()"


def blowAwayOneServersAsynchBeanWorkManager(nodeName, serverName, workManagerName):
    '''Delete asych bean work manager for one server '''
    print "\n"
    print "begin blowAwayOneServersAsynchBeanWorkManager()"
    try:
        id = ItemExists.serverScopedAsynchBeanWorkManagerExists(nodeName, serverName, workManagerName)
        if id:
            AdminConfig.remove(id)
            print "removed work manager: " + workManagerName + " for server: " + serverName
            AdminConfig.save()
        else:
            print "Work manager: " + workManagerName + " for server: " + serverName + " not found"
    except:
        print "\n\nException in blowAwayOneServersAsynchBeanWorkManager() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
    print "end of blowAwayOneServersAsynchBeanWorkManager()"


def blowAwayOneClustersAsynchBeanWorkManager(clusterName, workManagerName):
    '''Delete asych bean work manager for one cluster '''
    print "\n"
    print "begin blowAwayOneClustersAsynchBeanWorkManager()"
    try:
        id = ItemExists.clusterScopedAsynchBeanWorkManagerExists(clusterName, workManagerName)
        if id:
            AdminConfig.remove(id)
            print "removed work manager: " + workManagerName + " for cluster: " + clusterName
            AdminConfig.save()
        else:
            print "Work manager: " + workManagerName + " for cluster: " + clusterName + " not found"
    except:
        print "\n\nException in blowAwayOneClustersAsynchBeanWorkManager() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
    print "end of blowAwayOneClustersAsynchBeanWorkManager()"


#--------------------------------------------------------------------
# main
#--------------------------------------------------------------------
#when this module is being run as top-level, call the function
if __name__=="__main__":
    usage = " "
    usage = usage + " "
    usage = usage + "Usage: <wsadmin command> -f <this py script><config file name>"
    usage = usage + " . . . and must have modified soap.client.props of target wsadmin profile if security is enabled\n"
    print "\n\n"

    if len(sys.argv) == 1:
        #----------------------------------------------------------------------
        # Add references for the WebSphere Admin objects to sys.modules
        # sys.modules - dictionary that maps module names to modules which
        # have already been loaded.
        #----------------------------------------------------------------------
        wsadmin_objects = {
                        'AdminApp'      : AdminApp    ,
                        'AdminConfig'   : AdminConfig ,
                        'AdminControl'  : AdminControl,
                        'AdminTask'     : AdminTask,
                      }
        sys.modules.update(wsadmin_objects)

        #----------------------------------------------------------------------
        # Add the scripts dir to python path
        # I can't find any way to get wsadmin to display name & path
        #   of currently running script
        # and it's way too awkward to make scripts dir be an arg
        # so we require script must be run from scripts dir
        # e.g., home/hazel/was_configurator/scripts
        pwd = os.getcwd()
        scripts_dir = pwd
        sys.path.append(scripts_dir)

        #----------------------------------------------------------------------
        # Find the config file
        # we expect the config_files dir to be a sister dir of pwd
        parent_dir = os.path.split(scripts_dir)[0]
        config_dir = os.path.join(parent_dir, 'config_files')
        config_filename = sys.argv[0]
        configFile = os.path.join(config_dir, config_filename)

        #----------------------------------------------------------------------
        # Import all the modules this module uses at runtime
        # we expect these modules to be in the directory we just appended
        #   to search path
        import ItemExists
        import Utilities
        import wini

        blowAwayEnv(configFile)
    else:
        print usage
        sys.exit(1)
  
else:
    # being run as module, not top-level script
    import AdminConfig

    import ItemExists
    import Utilities
    import wini
