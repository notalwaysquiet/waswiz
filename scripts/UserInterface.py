"""UI module for waswiz script. Reads the config file, looks at the WAS
cell, displays info from both, and provides interactive menus for the
next level of modules such as Configurator and Destroyer."""
###############################################################################
# Copyright (c) Hazel Malloy 2022
###############################################################################

import glob  # used in whatConfigFileMenu()
import sys
import os

# wsadmin objects
import AdminApp
import AdminConfig
import AdminControl
import AdminTask

# waswiz modules (must be in path, e.g., same dir as this module)
import ConfigFile
import Configurator
import Destroyer
import ItemExists
import PoolDefaultsFixerUpper
import Utilities
import wini

# global variables-----------------
# variables for stuff already in the cell we are talking to
global WAScellName
global WASnodeIdList
global WASnodeList
global WAScellScopedWebsphereVariableList
global WASnodeScopedWebsphereVariableDict
global WASjaasAuthList
global WASvirtualHostList
global WASserverIdList
global WASserverList
global WASserverName
global WASclusterName
global WASjvmCustomPropertyList
global WASdataSourceList
global WASqueueConnectionFactoryList
global WASqueueList
global WASjmsActivationSpecList
global WASasynchBeanWorkManagerList
global foundInWAS
global isClustered

# variables for stuff from the config file
global cfgDict
global cellName
global nodeList
global cellScopedWebsphereVariableList
global nodeScopedWebsphereVariableList
global jaasAuthList
global virtualHostList
global serverList
global baseServerList
global serverInfoDict
global queueConnectionFactorySetList
global hasCyberarkConfig
global hasCyberarkOptions
global cyberarkCredInfoDict
global cyberarkCredOptionsDict
global serverIsClusteredInConfigFile
global clusterNameInConfigFile
global nodeNameInConfigFile
global jvmCustomPropertyList
global dataSourceList
global queueConnectionFactoryList
global queueList
global jmsActivationSpecList
global asynchBeanWorkManagerList
global queueConnectionFactoryDict

#spacers & dividers for display
#  _
sp1  = "   "
#    _
sp2 = sp1 + "   "
#   * _
sp2star = sp1 + " * "

#      _
sp3 = sp2 + "   "
div1 = "*****************************************************"

standard_prompt = "\nPlease enter number of your selection & press <ENTER>: "


def getSpacer(count):
    spacer = ".  "
    if count < 10:
        spacer = ".   "
    return spacer


def start(config_file):
    """ Do setup (read config file and look at existing WAS cell) and
    start the user interface (show "page one") """
    getWASinfo()
    getConfigInfo(config_file)
    pageOne(config_file)


def reDisplaypageOne(config_file):
    """ Re-load the WAS infor and then start the user interface at
    "page one" """
    getWASinfo()
    pageOne(config_file)


def getWASinfo():
    """ Inspect existing WAS cell and populate global variables about
    it."""
    # variables for stuff already in the cell we are talking to
    global WAScellName
    global WASnodeIdList
    global WASnodeList
    global WAScellScopedWebsphereVariableList
    global WASnodeScopedWebsphereVariableDict
    global WASjaasAuthList
    global WASvirtualHostList 
    global WASserverIdList 
    global WASserverList 

    # initialize the above global variables
    WASjaasAuthList = []
    WASnodeList = []
    WAScellScopedWebsphereVariableList = []
    WASnodeScopedWebsphereVariableDict = {}
    WASvirtualHostList = []
    WASserverList = []

    try:
        cellIdList = AdminConfig.list('Cell').splitlines()
        # normally we expect to find only 1 cell
        for id in cellIdList:
            WAScellName = id[0:id.find("(")]

        WASnodeIdList = AdminConfig.list('Node').splitlines()
        if WASnodeIdList:
            for configId in WASnodeIdList:
                nodeName = configId[0:configId.find("(")]
                WASnodeList.append(nodeName)
                # load up the node-level vars too while we are here
                path="/Node:" + nodeName +  "/VariableMap:/"
                nodeLevelvariableMapId = AdminConfig.getid(path)
                if nodeLevelvariableMapId:
                    variableIdListString = AdminConfig.showAttribute(nodeLevelvariableMapId, 'entries')
                    variableIdList = Utilities.convertToList(variableIdListString)
                    if variableIdList:
                        WASthisNodeScopedWebsphereVariableList = []
                        for variableId in variableIdList:
                            WASthisNodeScopedWebsphereVariableList.append(AdminConfig.showAttribute(variableId, 'symbolicName'))
                        WASnodeScopedWebsphereVariableDict[nodeName] = WASthisNodeScopedWebsphereVariableList
        
        path="/Cell:" + WAScellName +  "/VariableMap:/"
        variableMapId = AdminConfig.getid(path)
        if variableMapId:
            variableIdListString = AdminConfig.showAttribute(variableMapId, 'entries')
            variableIdList = Utilities.convertToList(variableIdListString)
            if variableIdList:
                for variableId in variableIdList:
                    WAScellScopedWebsphereVariableList.append(AdminConfig.showAttribute(variableId, 'symbolicName'))
        
        jaasIdList = AdminConfig.list("JAASAuthData").splitlines()
        if jaasIdList:
            for id in jaasIdList:
                WASjaasAuthList.append(AdminConfig.showAttribute(id, 'alias'))
        
        vhIdList = AdminConfig.list('VirtualHost').splitlines()
        if vhIdList:
            for id in vhIdList: 
                name = id[0:id.find("(")]
                WASvirtualHostList.append(name)
        
        WASserverIdList = AdminTask.listServers('[-serverType APPLICATION_SERVER ]').splitlines()
        if WASserverIdList:
            for id in WASserverIdList:
                name = id[0:id.find("(")]
                WASserverList.append(name)

    except:
        print "\n\nException in getWASinfo()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def displayWASinfo():
    """ Display info gotten by getWASinfo(), cross-referenced against
    config file with '*' to indicate thing is found in both. Part of
    "page one"."""
    # stuff already in the cell we are talking to
    # got populated by getWASinfo()
    global WAScellName
    global WASnodeIdList
    global WASnodeList
    global WAScellScopedWebsphereVariableList
    global WASjaasAuthList
    global WASvirtualHostList 
    global WASserverIdList 
    global WASserverList 
    
    # stuff from config file
    # got populated by getConfigInfo()
    global nodeList
    global cellScopedWebsphereVariableList
    global jaasAuthList
    global serverList

    try:
        display = ""
        display += div1 + "\n"
        display += "Existing in your WebSphere "
        display += "version " + str(Configurator.getWasVersion()) + "\n"
        display += "CELL and NODE level  \n"
        display += div1 + "\n"
        display += sp1 + "Cell: " + WAScellName + "\n"
        display += "\n"
        display += sp1 + "Nodes in cell: \n"
        for id in WASnodeIdList:
            name = id[0:id.find("(")]
            host = AdminConfig.showAttribute(id, 'hostName')
            if name in nodeList:
                display += sp2star + "Name: " + name + "\n"
            else:
                display += sp2 + "Name: " + name + "\n"
            display += sp2 + "Host: " + host + "\n"
            display += "\n"

        display += sp1 + "Existing servers in cell: \n"

        if len(WASserverIdList) == 0:
            display += sp2 + "No servers found"    
        else:    
            for id in WASserverIdList:
                name = id[0:id.find("(")]
                nodeName = id[id.find("nodes/")+6:id.find("servers/")-1]
                clusterName = AdminConfig.showAttribute(id, 'clusterName')
                if name in serverList:
                    display += sp2star + "Name: " + name + "\n"
                else:
                    display += sp2 + "Name: " + name + "\n"
                display += sp2 + "Node: " + nodeName + "\n"
                if clusterName:
                    display += sp2 + "Cluster: " + clusterName + "\n"    
                else:
                    display += sp2 + "(unclustered)\n"    
                display += "\n"

        if WAScellScopedWebsphereVariableList:
            display += "\n"
            display += sp1 + "Cell-scoped WebSphere variables: \n"
            for name in WAScellScopedWebsphereVariableList:
                if name in cellScopedWebsphereVariableList:
                    display += sp2star + name + "\n"
                else:   
                    display += sp2 + name + "\n"

        if WASnodeScopedWebsphereVariableDict:
            display += "\n"
            display += sp1 + "Node-scoped WebSphere variables: \n"
            for nodeName in nodeList:
                display += sp2 + "Node: " + nodeName + ": \n"
                WASthisNodeScopedWebsphereVariableList = WASnodeScopedWebsphereVariableDict[nodeName]
                WASthisNodeScopedWebsphereVariableList.sort()
                for name in WASthisNodeScopedWebsphereVariableList:
                    if name in nodeScopedWebsphereVariableList:
                        display += sp1 + sp2star + name + "\n"
                    else:
                        display += sp1 + sp2 + name + "\n"
                
        if WASjaasAuthList:                    
            display += "\n"
            display += sp1 + "JAAS authentication entries: \n"
            for name in WASjaasAuthList:
                if name in jaasAuthList:
                    display += sp2star + name + "\n"
                else:   
                    display += sp2 + name + "\n"

        if WASvirtualHostList:                    
            display += "\n"
            display += sp1 + "Virtual hosts: \n"
            for name in WASvirtualHostList:
                if name in virtualHostList:
                    display += sp2star + name + "\n"
                else:
                    display += sp2 + name + "\n"
        
        display += "\n\n"
        display += sp1 + "* indicates that an item of the same name is found in your config file \n"
        display += "\n"
        print display
    except:
        print "\n\nException in displayWASinfo() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def getConfigInfo(configFile):
    """ Read the config file and populate global variables about it."""
    # variables for stuff from the config file
    global cfgDict
    global cellName
    global nodeList
    global cellScopedWebsphereVariableList
    global nodeScopedWebsphereVariableList
    global jaasAuthList
    global serverList
    global baseServerList
    # serverInfoDict is used in whatServerMenu(config_file)
    global serverInfoDict
    global virtualHostList
    # queueConnectionFactorySetList is used in menuForCellThings()
    # this is for cell defaults for qcf, mainly for pool settings, e.g., timeouts
    global queueConnectionFactorySetList
    global hasCyberarkConfig
    global hasCyberarkOptions
    global cyberarkCredInfoDict
    global cyberarkCredOptionsDict
    
    cfgDict = {}
    cellName = ""
    nodeList = []
    cellScopedWebsphereVariableList = []
    nodeScopedWebsphereVariableList = []
    jaasAuthList = []
    serverList = []
    baseServerList = []
    virtualHostList = []
    queueConnectionFactorySetList = []
    hasCyberarkConfig = "false"
    hasCyberarkOptions = "false"
    cyberarkCredInfoDict = ()
    cyberarkCredOptionsDict = ()
    
    serverInfoDict = ()
    
    try:
        cfgDict = ConfigFile.validateConfigFile(configFile)

        environmentGenInfo = cfgDict['cellInfo']
        cellName = environmentGenInfo['cellName'].strip()
            
        cellScopedWebsphereVariablesDict = wini.getPrefixedClauses(cfgDict,'websphereVariables:' + 'cellLevel' +':')
        if cellScopedWebsphereVariablesDict:
            for cellScopedWebsphereVariablesKey in cellScopedWebsphereVariablesDict.keys():
                wv = cellScopedWebsphereVariablesDict[cellScopedWebsphereVariablesKey]
                symbolicName = wv['symbolicName']
                cellScopedWebsphereVariableList.append(symbolicName)

        nodeScopedWebsphereVariablesDict = wini.getPrefixedClauses(cfgDict,'websphereVariables:' + 'nodeLevel' +':')
        if nodeScopedWebsphereVariablesDict:
            for nodeScopedWebsphereVariablesKey in nodeScopedWebsphereVariablesDict.keys():
                wv = nodeScopedWebsphereVariablesDict[nodeScopedWebsphereVariablesKey]
                symbolicName = wv['symbolicName']
                nodeScopedWebsphereVariableList.append(symbolicName)
                
        jaasAuthEntryDict = wini.getPrefixedClauses(cfgDict,'jaasAuthEntry:' + 'cellLevel' +':')
        if jaasAuthEntryDict:
            dmNodeName = AdminControl.getNode()
            for jaasAuthEntryKey in jaasAuthEntryDict.keys():
                jae = jaasAuthEntryDict[jaasAuthEntryKey]
                alias = dmNodeName + '/' + jae['alias']
                jaasAuthList.append(alias)

        serverInfoDict = wini.getPrefixedClauses(cfgDict,'server:')
        if serverInfoDict:
            for serverInfoKey in serverInfoDict.keys():
                si = serverInfoDict[serverInfoKey]
                serverNodeList = si['nodeList'].split()
                isClustered = si['isClustered']
                #print 'si:' 
                #print si
                #print 'serverInfoKey: '
                #print serverInfoKey
                baseServerName = si['baseServerName']
                baseServerList.append(baseServerName)
                nodeNumber = 1
                if isClustered == 'true':
                    for nodeName in serverNodeList:
                        serverName = baseServerName + str(nodeNumber)
                        serverList.append(serverName)
                        nodeNumber += 1
                else:                        
                    serverName = baseServerName + str(nodeNumber)
                    serverList.append(serverName)
                hostsWebApps = si['hostsWebApps']
                if hostsWebApps == 'true':
                    virtualHostName = Configurator.getVirtualHostName(serverInfoDict, baseServerName)
                    virtualHostList.append(virtualHostName)

        # optional config items below here
        try:                
            queueConnectionFactorySetDict = cfgDict['queueConnectionFactorySet:cellLevel']
            if queueConnectionFactorySetDict:
                description = queueConnectionFactorySetDict['description']
                queueConnectionFactorySetList.append(description)
        except KeyError:
            pass

        try:
            cyberarkCredInfoDict = cfgDict['cyberarkCredInfo']
            if cyberarkCredInfoDict:
                hasCyberarkConfig = "true"
        except KeyError:
            pass

        try:
            cyberarkCredOptionsDict = cfgDict['cyberarkCredOptions']
            if cyberarkCredOptionsDict:
                hasCyberarkOptions = "true"
        except KeyError:
            pass
            
    except:
        print "\n\nException in getConfigInfo()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def displayConfigInfo(config_file):
    """ Display info gotten by getConfigInfo(), cross-referenced against
    existing WAS cell, with '*' to indicate thing is found in both.
    Part of "page one". """
    try:
        display = div1 + "\n"
        display += "Specified in your config file  \n"
        display += "CELL and NODE level  \n"
        display += div1 + "\n\n"
        
        display += sp1 + "Config file: " + config_file + "\n"
        display += "\n"
      
        display += sp1 + "Cell: " + WAScellName + "\n"
        display += "\n"
        display += sp1 + "Nodes: \n"
        for name in nodeList:
            if name in WASnodeList:
                display += sp2star + "Name: " + name + "\n"
            else:
                display += sp2 + "Name: " + name + "\n"
            display += "\n"

        if serverList:
            display += ""
            display += sp1 + "Servers: \n"
            for name in serverList:
                if name in WASserverList:
                    display += sp2star + name + "\n"
                else:   
                    display += sp2 + name + "\n"

        if cellScopedWebsphereVariableList:
            display += "\n"
            display += sp1 + "Cell-scoped WebSphere variables: \n"
            for name in cellScopedWebsphereVariableList:
                if name in WAScellScopedWebsphereVariableList:
                    display += sp2star + name + "\n"
                else:   
                    display += sp2 + name + "\n"

        if nodeScopedWebsphereVariableList:
            display += "\n"
            display += sp1 + "Node-scoped WebSphere variables: \n"
            for nodeName in nodeList:
                WASthisNodeScopedWebsphereVariableList = WASnodeScopedWebsphereVariableDict[nodeName]
                if nodeName in WASnodeList:
                    display += sp2star + "Node: " + nodeName + ": \n"
                else:
                    display += sp2 + "Node: " + nodeName + ": \n"
                for name in nodeScopedWebsphereVariableList:
                    if name in WASthisNodeScopedWebsphereVariableList:
                        display += sp1 + sp2star + name + "\n"
                    else:   
                        display += sp1 + sp2 + name + "\n"
                    
        if jaasAuthList:                    
            display += "\n"
            display += sp1 + "JAAS authentication entries: \n"
            for name in jaasAuthList:
                if name in WASjaasAuthList:
                    display += sp2star + name + "\n"
                else:   
                    display += sp2 + name + "\n"

        if virtualHostList:                    
            display += "\n"
            display += sp1 + "Virtual hosts: \n"
            for name in virtualHostList:
                if name in WASvirtualHostList:
                    display += sp2star + name + "\n"
                else:   
                    display += sp2 + name + "\n"

        if queueConnectionFactorySetList:   
            display += "\n"
            display += sp1 + "Pool settings for QCFs. To be applied to whole cell. \n"
            for name in queueConnectionFactorySetList:
                display += sp2 + "Description for these settings: "  + ": " + name + "\n"
                    
        display += "\n\n"
        display += sp1 + "* indicates that an item of the same name exists in your WebSphere cell \n"
        print display
 
    except:
        print "\n\nException in displayConfigInfo() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def getServerClusterConfigInfoDetail(baseServerName):
    """ Using info already gotten by getConfigInfo(), populate additional global variables about config file: isClustered. """
    global serverIsClusteredInConfigFile
    global clusterNameInConfigFile
    global nodeNameInConfigFile

    serverIsClusteredInConfigFile = "serverIsClusteredInConfigFile not defined yet"
    clusterNameInConfigFile  = "clusterNameInConfigFile not defined yet"
    nodeNameInConfigFile  = "nodeNameInConfigFile not defined yet"

    if serverInfoDict:
        for serverInfoKey in serverInfoDict.keys():
            si = serverInfoDict[serverInfoKey]
            thisBaseServerName = si['baseServerName']
            if thisBaseServerName == baseServerName:
                serverIsClusteredInConfigFile =  si['isClustered']
                if serverIsClusteredInConfigFile == 'true':
                    clusterNameInConfigFile = si['clusterName']
                elif serverIsClusteredInConfigFile == 'false':
                    nodeNameInConfigFile = si['nodeList']


def getServerConfigInfoDetail(baseServerName):
    """ Using info already gotten by getConfigInfo(), populate
    additional global list variables about config file: jvm custom
    props, data sources, qcfs, queues, jms actspecs, asynch bean work
    mgrs. """
    global jvmCustomPropertyList
    global dataSourceList
    global queueConnectionFactoryList
    global queueList
    global jmsActivationSpecList
    global asynchBeanWorkManagerList
    global queueConnectionFactoryDict
    
    jvmCustomPropertyList = []
    dataSourceList = []
    queueConnectionFactoryList = []
    queueList = []
    jmsActivationSpecList = []
    asynchBeanWorkManagerList = []
    
    try:
        if baseServerName is None:
            print "No server name supplied."
            return
        
        jvmCustomPropertyDict = wini.getPrefixedClauses(cfgDict,'jvmCustomProperty:' + baseServerName +':')
        if jvmCustomPropertyDict:
            for jvmCustomPropertyKey in jvmCustomPropertyDict.keys():
                jcp = jvmCustomPropertyDict[jvmCustomPropertyKey]
                propertyName = jcp['propertyName'].strip()
                jvmCustomPropertyList.append(propertyName)
        
        dataSourceDict = wini.getPrefixedClauses(cfgDict,'dataSource:' + baseServerName +':')
        if dataSourceDict:
            for dataSourceKey in dataSourceDict.keys():
                ds = dataSourceDict[dataSourceKey]
                jndiName = ds['jndiName'].strip()
                dataSourceList.append(jndiName)

        queueConnectionFactoryDict = wini.getPrefixedClauses(cfgDict,'queueConnectionFactory:' + baseServerName +':')
        if queueConnectionFactoryDict:
            for queueConnectionFactoryKey in queueConnectionFactoryDict.keys():
                qcf = queueConnectionFactoryDict[queueConnectionFactoryKey]
                jndiName = qcf['jndiName'].strip()
                queueConnectionFactoryList.append(jndiName)

        queueDict = wini.getPrefixedClauses(cfgDict,'queue:' + baseServerName +':')
        if queueDict:
            for queueKey in queueDict.keys():
                q = queueDict[queueKey]
                jndiName = q['jndiName'].strip()
                queueList.append(jndiName)

        jmsActivationSpecDict = wini.getPrefixedClauses(cfgDict,'jmsActivationSpec:' + baseServerName +':')
        if jmsActivationSpecDict:
            for jmsActivationSpecKey in jmsActivationSpecDict.keys():
                jms = jmsActivationSpecDict[jmsActivationSpecKey]
                jndiName = jms['jndiName'].strip()
                jmsActivationSpecList.append(jndiName)

        asynchBeanWorkManagerDict = wini.getPrefixedClauses(cfgDict,'asynchBeanWorkManager:' + baseServerName +':')
        if asynchBeanWorkManagerDict:
            for asynchBeanWorkManagerKey in asynchBeanWorkManagerDict.keys():
                ab = asynchBeanWorkManagerDict[asynchBeanWorkManagerKey]
                jndiName = ab['jndiName'].strip()
                asynchBeanWorkManagerList.append(jndiName)
                
        
    except:
        print "\n\nException in getServerConfigInfoDetail()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def getServerWASinfoDetail(baseServerName):
    """ Using info already gotten by getWASinfo(), populate additional
    global list variables about existing WAS cell: jvm custom props,
    data sources, qcfs,     queues, jms actspecs, asynch bean work mgrs. """
    global WASserverName
    global WASclusterName
    global WASjvmCustomPropertyList
    global WASdataSourceList
    global WASqueueConnectionFactoryList
    global WASqueueList
    global WASjmsActivationSpecList
    global WASasynchBeanWorkManagerList
    global foundInWAS
    global isClustered
    
    WASserverName = "WASserverName not defined yet"
    WASclusterName = "WASclusterName not defined yet"
    WASjvmCustomPropertyList = []
    WASdataSourceList = []
    WASqueueConnectionFactoryList = []
    WASqueueList = []
    WASjmsActivationSpecList = []
    WASasynchBeanWorkManagerList = []

    serverName = "serverName not defined yet"
    nodeName = "nodeName not defined yet"
    clusterName = "clusterName not defined yet"
    scopeName = "scopeName not defined yet"
    serverId = "serverId not defined yet"
    jvmId = "jvmId not defined yet"
    isClustered = "isClustered not defined yet"
    
    foundInWAS = "foundInWAS not defined yet"
    
    try:
        # get id of any server we find with same base name
        # look to see if at least one  server with same base name is found in WAS cell
        # if we don't find it in first node, keep looking
        # server can be named server2 in first node or vice versa
        if serverInfoDict:
            if len(serverInfoDict) != 0:
                for serverInfoKey in serverInfoDict.keys():
                    si = serverInfoDict[serverInfoKey]
                    #print 'si:' 
                    #print si
                    #print 'serverInfoKey: '
                    #print serverInfoKey
                    if baseServerName == si['baseServerName']:
                        serverNodeList = si['nodeList'].split()
                        
                        isClustered = si['isClustered']
                        if isClustered == "true":
                            clusterName = si['clusterName']
                            WASclusterName = clusterName

                        serverSequenceNumberList = [1, 2]
                        foundInWAS = "false"
                        
                            
                        for nodeName in serverNodeList:
                            if foundInWAS == "true":
                                    break
                            for serverSequenceNumber in serverSequenceNumberList:
                                serverName = baseServerName + str(serverSequenceNumber)
                                serverId = ItemExists.serverExists(nodeName, serverName)
                                if serverId is not None:
                                    foundInWAS = "true"
                                    break
                        if foundInWAS == "true":
                            WASserverName = serverName
                            break

        if foundInWAS == "false":
            return

        jvmId = AdminConfig.list('JavaVirtualMachine', serverId)
        
        #can't simply do splitlines() for these ones like you can the AdminConfig.list ones
        propertyIdList = Utilities.convertToList(AdminConfig.showAttribute(jvmId, 'systemProperties'))
        
        for configId in propertyIdList:
            name = configId[0:configId.find("(")]
            WASjvmCustomPropertyList.append(name)
            #WASjvmCustomPropertyList.append(AdminConfig.showAttribute(configId[0], 'propertyName'))

        if isClustered == "true":
            scopeName = clusterName            
        elif isClustered == "false":
            scopeName = serverName
        else:
            print "Config file must specify \
                   either 'true' or 'false' for isClustered"
            sys.exit("Can't determine scope")
            
        dataSouceIdList = AdminConfig.list('DataSource', '*' + scopeName + '*').splitlines()
        for configId in dataSouceIdList:
            WASdataSourceList.append(AdminConfig.showAttribute(configId, 'jndiName'))
        
        queueConnectionFactoryIdList = AdminConfig.list('MQQueueConnectionFactory', '*' + scopeName + '*').splitlines()
        for configId in queueConnectionFactoryIdList:
            WASqueueConnectionFactoryList.append(AdminConfig.showAttribute(configId, 'jndiName'))

        queueIdList = AdminConfig.list('MQQueue', '*' + scopeName + '*').splitlines()
        for configId in queueIdList:
            WASqueueList.append(AdminConfig.showAttribute(configId, 'jndiName'))
                    
        jmsActivationSpecIdList = AdminConfig.list('J2CActivationSpec', '*' + scopeName + '*').splitlines()
        for configId in jmsActivationSpecIdList:
            WASjmsActivationSpecList.append(AdminConfig.showAttribute(configId, 'jndiName'))

        asynchBeanWorkManagerList = AdminConfig.list('WorkManagerInfo', '*' + scopeName + '*').splitlines()
        for configId in asynchBeanWorkManagerList:
            WASasynchBeanWorkManagerList.append(AdminConfig.showAttribute(configId, 'jndiName'))
            
    except:
        print "\n\nException in getServerWASinfoDetail()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def displayWASServerDetail(config_file, baseServerName):
    """ Display info gotten by getServerWASinfoDetail(),
    cross-referenced against config file with '*' to indicate thing is
    found in both. """
    try:
        if baseServerName is None:
            sys.exit("No server name supplied")
        scope = "scope not defined yet"
        scopeName = "scopeName not defined yet"

        display = "\n"
        display += div1 + "\n"
        display += "Existing in your WebSphere  \n"
        display += "SERVER matching base name: " + baseServerName + "\n"
        display += div1 + "\n\n"   

        display += sp1 + "Config file: " + config_file + "\n"
        display += "\n"
        
        if foundInWAS == "true":
            display += "\n" + sp1+ "At least one server matching base name: " + baseServerName + " is found in your cell.\n"
            display += sp1 + "Name of matching server in WAS cell is: " + WASserverName + ".\n"
        elif foundInWAS == "false":
            display += "\n" + sp1 + "No server matching base name: " + baseServerName + " is found in your cell."
            print display
            return
        else:
            display += "\n" + sp1 + "Could not determine if server matching base name: " + baseServerName + " is found in your cell."
            print display
            return

        if isClustered == "true":
            display += "\n" +sp1 + "Server is clustered.\n"
            scope = "cluster"
            scopeName = WASclusterName
        elif isClustered == "false":
            display += "\n" + sp1 + "Server is not clustered.\n"
            scope = "server"
            scopeName = WASserverName
        else:
            display += "Scope could not be determined.\n"
            return
        
        print display

        display = "\n"        
        display += sp1 + "JVM custom properties in WAS cell for server: " + WASserverName + "\n"
        
        if len(WASjvmCustomPropertyList) == 0:
            display += sp2 + "No JVM custom properties found\n"    
        else:    
            for name in WASjvmCustomPropertyList:
                if name in jvmCustomPropertyList:
                    display += sp2star + "Name: " + name + "\n"
                else:
                    display += sp2 + "Name: " + name + "\n"
        
        display += "\n"        
        display += sp1 + "Datasources in WAS cell for " + scope + ": " + scopeName + "\n"

        if len(WASdataSourceList) == 0:
            display += sp2 + "No datasources found\n"    
        else:    
            for name in WASdataSourceList:
                if name in dataSourceList:
                    display += sp2star + "JNDI name: " + name + "\n"
                else:
                    display += sp2 + "JNDI name: " + name + "\n"

        display += "\n"
        display += sp1 + "MQ queue connection factories in WAS cell for " + scope + ": " + scopeName + "\n"

        if len(WASqueueConnectionFactoryList) == 0:
            display += sp2 + "No MQ queue connection factories found\n"    
        else:    
            for name in WASqueueConnectionFactoryList:
                if name in queueConnectionFactoryList:
                    display += sp2star + "JNDI name: " + name + "\n"
                else:
                    display += sp2 + "JNDI name: " + name + "\n"

        display += "\n"        
        display += sp1 + "MQ queues in WAS cell for " + scope + ": " + scopeName + "\n"

        if len(WASqueueList) == 0:
            display += sp2 + "No MQ queues found in WAS cell\n"    
        else:    
            for name in WASqueueList:
                if name in queueList:
                    display += sp2star + "JNDI name: " + name + "\n"
                else:
                    display += sp2 + "JNDI name: " + name + "\n"

        display += "\n"        
        display += sp1 + "JMS Activation Specifications in WAS cell for " + scope + ": " + scopeName + "\n"

        if len(WASjmsActivationSpecList) == 0:
            display += sp2 + "No JMS Activation Specifications found\n"    
        else:    
            for name in WASjmsActivationSpecList:
                if name in jmsActivationSpecList:
                    display += sp2star + "JNDI name: " + name + "\n"
                else:
                    display += sp2 + "JNDI name: " + name + "\n"


        display += "\n"        
        display += sp1 + "Asynch bean work managers in WAS cell for " + scope + ": " + scopeName + "\n"

        if len(WASasynchBeanWorkManagerList) == 0:
            display += sp2 + "No asynch bean work managers found\n"    
        else:    
            for name in WASasynchBeanWorkManagerList:
                if name in asynchBeanWorkManagerList:
                    display += sp2star + "JNDI name: " + name + "\n"
                else:
                    display += sp2 + "JNDI name: " + name + "\n"

        display += "\n\n"
        display += sp1 + "* indicates that an item of the same name is found in your config file \n"
        display += "\n"
        print display
                    
    except:
        print "\n\nException in displayWASServerDetail()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def displayServerConfigInfoDetail(config_file, baseServerName):
    """ Display info gotten by getServerConfigInfoDetail(),
    cross-referenced against existing WAS cell with '*' to indicate
    thing is found in both. """
    try:
        display = "\n\n"
        display += div1 + "\n"
        display += "Specified in your config file  \n"
        display += "SERVER base name: " + baseServerName + "\n"
        display += div1 + "\n\n"
        
        display += sp1 + "Config file: " + config_file + "\n"
        display += "\n"
        
        scope = "scope not defined yet"
        scopeName = "scopeName not defined yet"

        if isClustered == "true":
            display += "\n" +sp1 + "Server is clustered.\n"
            scope = "cluster"
            scopeName = WASclusterName
        elif isClustered == "false":
            display += "\n" + sp1 + "Server is not clustered.\n"
            scope = "server"
            scopeName = WASserverName
        else:
            display += "Scope could not be determined."
            return
        print display
        
        display = ""
        display += "\n"
        display += sp1 + "JVM custom properties in config file for server: " + baseServerName + "\n"
        
        if len(jvmCustomPropertyList) == 0:
            display += sp2 + "No JVM custom properties found in config file\n"    
        else:    
            for name in jvmCustomPropertyList:
                if name in WASjvmCustomPropertyList:
                    display += sp2star + "Name: " + name + "\n"
                else:
                    display += sp2 + "Name: " + name + "\n"
        
        display += "\n"
        display += sp1 + "Datasources in config file for " + scope + ": " + scopeName + "\n"

        if len(dataSourceList) == 0:
            display += sp2 + "No datasources found in config file\n"    
        else:    
            for name in dataSourceList:
                if name in WASdataSourceList:
                    display += sp2star + "JNDI name: " + name + "\n"
                else:
                    display += sp2 + "JNDI name: " + name + "\n"

        display += "\n"
        display += sp1 + "MQ queue connection factories in config file for " + scope + ": " + scopeName + "\n"

        if len(queueConnectionFactoryList) == 0:
            display += sp2 + "No MQ queue connection factories found in config file\n"    
        else:    
            for name in queueConnectionFactoryList:
                if name in WASqueueConnectionFactoryList:
                    display += sp2star + "JNDI name: " + name + "\n"
                else:
                    display += sp2 + "JNDI name: " + name + "\n"

        display += "\n"
        display += sp1 + "MQ queues in config file for " + scope + ": " + scopeName + "\n"

        if len(queueList) == 0:
            display += sp2 + "No MQ queues found in config file\n"    
        else:    
            for name in queueList:
                if name in WASqueueList:
                    display += sp2star + "JNDI name: " + name + "\n"
                else:
                    display += sp2 + "JNDI name: " + name + "\n"

        display += "\n"
        display += sp1 + "JMS Activation Specifications in config file for " + scope + ": " + scopeName + "\n"

        if len(jmsActivationSpecList) == 0:
            display += sp2 + "No JMS Activation Specifications found\n"    
        else:    
            for name in jmsActivationSpecList:
                if name in WASjmsActivationSpecList:
                    display += sp2star + "JNDI name: " + name + "\n"
                else:
                    display += sp2 + "JNDI name: " + name + "\n"

        display += "\n"
        display += sp1 + "Asynch bean work managers in config file for " + scope + ": " + scopeName + "\n"

        if len(asynchBeanWorkManagerList) == 0:
            display += sp2 + "No asynch bean work managers found\n"    
        else:    
            for name in asynchBeanWorkManagerList:
                if name in WASasynchBeanWorkManagerList:
                    display += sp2star + "JNDI name: " + name + "\n"
                else:
                    display += sp2 + "JNDI name: " + name + "\n"
                    
                    

        display += "\n\n"
        display += sp1 + "* indicates that an item of the same name exists in your WebSphere cell \n"
        print display
 
    except:
        print "\n\nException in displayServerConfigInfoDetail() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def pageOne(config_file):
    """ Display first page of user interface: info about existing WAS
    cell, and what is specified in the config file, cross-referenced
    against each other, plus menu of supported user actions. """
    try:
        display = "\n\n"
        display += div1 + "\n"
        display += "WebSphere Configurator Python Script \n"
        display += div1 + "\n\n"   
        print display

        displayWASinfo()
        displayConfigInfo(config_file)
        menuPageOne(config_file)

    except SystemExit:
        pass
    except:
        print "\n\nException in pageOne"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def menuPageOne(config_file):
    """ Display menu of supported user actions for "page one". First
    menu user sees, below the results of comparing WAS cell to config
    file. """
    display = "\n\n"
    display += div1 + "\n"
    display += "Options \n"
    display += div1 + "\n\n"

    display += sp1 + "Config file: " + config_file + "\n"
    display += "\n"

    menuNum = 1
    display += sp1+ str(menuNum) + sp1+ "Show server details ...\n"
    display += "\n"
    menuNum = 2
    display += sp1+ str(menuNum) + sp1+ "See supported actions for this config file ...\n"
    display += "\n"
    menuNum = 3
    display += sp1+ str(menuNum) + sp1+ "See supported actions for this whole WAS cell ...\n"
    display += "\n"
    menuNum = 99
    display += sp1+ str(menuNum) + sp1+ "Choose a different config file for this WAS cell ...\n"
    display += "\n"
    print display
    try:
        menu_response = raw_input(standard_prompt)
    # user hits control-C
    except EOFError:
        print "\nExiting."
        sys.exit(0)

    if menu_response == "":
        print "Menu response was: empty string"
        menu_response = raw_input("\nExit? (y | n): ")
        if menu_response.lower() == "n":
            print "Response was: " + str(menu_response)
            menuPageOne(config_file)
        else:
            if menu_response == "":
                print "Response was: empty string"
            else:
                print "Response was: " + str(menu_response)
            print "\nExiting."
            sys.exit(0)
    else:
        print "Menu response was: " + str(menu_response)
        if menu_response.isnumeric():
            if menu_response == '1':
                baseServerName = whatServerMenu(config_file)
                if baseServerName is not None:
                    pageServerDetail(config_file, baseServerName)
                else:
                    print "No server selected."
                    menuPageOne(config_file)
            elif menu_response == '2':
                menuAddOrReplace(config_file)
            elif menu_response == '3':
                menuForCellThings(config_file)
            elif menu_response == '99':
                menuToSwitchConfigFiles(config_file)
            else:
                print "Response was not recognized."
                menuPageOne(config_file)
        else:
            print "Response was non-numeric."
            print "\nExiting."
            sys.exit(0)


def pageServerDetail(config_file, baseServerName):
    """ Server Detail Page. Like "page one" but with more detail on a
    particular server, e.g., jvm custom props, resources, etc."""
    try:
        getServerWASinfoDetail(baseServerName)    
        getServerConfigInfoDetail(baseServerName)
        displayWASServerDetail(config_file, baseServerName)
        displayServerConfigInfoDetail(config_file, baseServerName)
        menuServerDetail(config_file, baseServerName)
    except SystemExit:
        pass
    except:
        print "\n\nException in pageServerDetail()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

        
def menuServerDetail(config_file, baseServerName):
    """ Menu of supported user actions for Server Detail Page """
    try:
        display = "\n\n"
        display += div1 + "\n"
        display += "Options \n"
        display += div1 + "\n\n"   

        display += sp1 + "Config file: " + config_file + "\n"
        display += "\n"
        
        menuNum = 1
        display += sp1+ str(menuNum) + sp1+ "Show more detailed info for this server ...\n"
        display += "\n"

        menuNum = 2
        display += sp1+ str(menuNum) + sp1+ "See supported actions for this config file ...\n"
        display += "\n"

        menuNum = 98
        display += sp1+ str(menuNum) + sp1+ "Redisplay the inspection for this WAS server ...\n"
        display += "\n"
        
        menuNum = 99
        display += sp1+ str(menuNum) + sp1+ "Choose a different config file for this WAS cell ...\n"
        display += "\n"

        display += sp2 + "[hit Enter twice to return to main display] \n"
        display += "\n"
        
        print display
        try:
            menu_response = raw_input(standard_prompt)
        # user hits control-C
        except EOFError:
            print "\nExiting."
            sys.exit(0)
        
        if menu_response == "":
            print "Menu response was: empty string"
            menu_response = raw_input("\nReturn to main display? (y | n): ")
            if menu_response.lower() == "n":
                print "Response was: " + str(menu_response)
                menuServerDetail(config_file, baseServerName)
            else:
                if menu_response == "":
                    print "Menu response was: empty string"
                else:
                    print "Response was: " + str(menu_response)
                print "Returning to main display."
                pageOne(config_file)
                return
        else:
            print "Menu response was: " + str(menu_response)
            if menu_response.isnumeric():
                if menu_response.lower() == '1':
                    menuToShowMoreDetail(config_file, baseServerName)
                elif menu_response.lower() == '2':
                    menuAddOrReplace(config_file)
                elif menu_response == '98':
                    pageServerDetail(config_file, baseServerName)
                elif menu_response == '99':
                    menuToSwitchConfigFiles(config_file)
                else:
                    print "Response was not recognized."
                    menuServerDetail(config_file, baseServerName)
            else:
                print "Response was non-numeric."
                print "Returning to main display."
                pageOne(config_file)
            
    except SystemExit:
        pass
    except:
        print "\n\nException in menuServerDetail()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def menuAddOrReplace(config_file):
    """ Main Menu. User gets this when they choose "See supported
    actions for this config file" (option 2 on page one) """
    global hasCyberarkConfig
    global hasCyberarkOptions
    global cyberarkCredInfoDict
    global cyberarkCredOptionsDict
    global WAScellName
    try:
        display = "\n\n"
        display += div1 + "\n"
        display += "Types of actions \n"
        display += div1 + "\n\n"   

        display += sp1 + "Config file: " + config_file + "\n"
        display += "\n"
        """
        print
        print
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        print "hasCyberarkConfig: " + str(hasCyberarkConfig)
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        print

        print
        print
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        print "hasCyberarkOptions: " + str(hasCyberarkOptions)
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        print
        """
        menuNum = 1
        display += sp1+ str(menuNum) + sp1+ "Add items to your WAS cell from contents of config file ...\n"
        display += sp3 + "i.e., NOT replace any items that already exist in cell \n"
        display += sp3 + "Only adds items from the config file that are missing in the WAS cell. \n"
        display += "\n"

        menuNum = 2
        display += sp1+ str(menuNum) + sp1+ "Replace items in your WAS cell from contents of config file ...\n"
        display += "\n"

        menuNum = 3
        display += sp1+ str(menuNum) + sp1+ "Modify items in your WAS cell from contents of config file ...\n"
        display += "\n"

        menuNum = 4
        display += sp1+ str(menuNum) + sp1+ "Delete items in your WAS cell from contents of config file ...\n"
        display += "\n"


        if hasCyberarkConfig == "true":
            menuNum = 5
            display += sp1+ str(menuNum) + sp1+ "Cyberark it! for the specified datasources in this config file (including options if any)...\n"
            display += "\n"

            menuNum = 6
            display += sp1+ str(menuNum) + sp1+ "Enable the cyberarked datasources in this config file and disable the original ones ...\n"
            display += "\n"

            menuNum = 7
            display += sp1+ str(menuNum) + sp1+ "Disable the cyberarked datasources and re-enable the original, non-cyberarked ones in this config file ...\n"
            display += "\n"

            menuNum = 8
            display += sp1+ str(menuNum) + sp1+ "Add or modify options for existing cyberark creds and jvms in this config file ...\n"
            display += "\n"

            menuNum = 9
            display += sp1+ str(menuNum) + sp1+ "Reset Cyberark options for existing creds and jvms in this config file using vals from defaults file...\n"
            display += "\n"

        menuNum = 98
        display += sp1+ str(menuNum) + sp1+ "Repeat the inspection of this WAS cell ...\n"
        display += "\n"
        
        menuNum = 99
        display += sp1+ str(menuNum) + sp1+ "Choose a different config file for this WAS cell ...\n"
        display += "\n"

        display += sp2 + "[hit Enter twice to return to main display] \n"
        display += "\n"
        
        print display
        
        try:
            menu_response = raw_input(standard_prompt)
        # user hits control-C        
        except EOFError:
            print "\nExiting."
            sys.exit(0)

        if menu_response == "":
            print "Menu response was: empty string"
            menu_response = raw_input("\nReturn to main display? (y | n): ")
            if menu_response.lower() == "n":
                print "Response was: " + str(menu_response)
                menuAddOrReplace(config_file)
            else:
                if menu_response == "":
                    print "Menu response was: empty string"
                else:
                    print "Response was: " + str(menu_response)
                print "Returning to main display."
                pageOne(config_file)
                return
        else:
            print "Menu response was: " + str(menu_response)
            if menu_response.isnumeric():

                if menu_response == '1':
                    menuToAddThings(config_file)

                elif menu_response == '2':
                    menuToReplaceThings(config_file)

                elif menu_response == '3':
                    menuToModifyThings(config_file)

                elif menu_response == '4':
                    menuToDeleteThings(config_file)

                elif menu_response == '5':
                    appNickname = ""
                    reasonStringToBind = ""
                    localCacheLifeSpanStringToBind = ""
                    usingCMSubjectCache = ""
                    if cyberarkCredInfoDict:
                        appNickname = cyberarkCredInfoDict['appNickname']
                        appIDStringToBind = cyberarkCredInfoDict['appIDStringToBind']
                        queryStringToBind = cyberarkCredInfoDict['queryStringToBind']
                        for baseServerName in baseServerList:   
                            Configurator.cyberArkIt(cfgDict, baseServerName, appNickname, appIDStringToBind, queryStringToBind)
                            Configurator.addOneServersDatasourcesCustomProps(cfgDict, baseServerName)
                    if cyberarkCredOptionsDict:
                        print "At least one Cyberark option was specified."
                        try:
                            reasonStringToBind = cyberarkCredOptionsDict['reasonStringToBind']
                            if reasonStringToBind == "":
                                reasonStringToBind = "default"
                                print "Setting reasonStringToBind to default because empty string was specified."
                            else:
                                print "Cyberark option reasonStringToBind was specified: " + str(reasonStringToBind)
                        except KeyError:
                            print "Setting reasonStringToBind to default because no value was specified."
                            reasonStringToBind = "default"
                            
                        try:
                            localCacheLifeSpanStringToBind = cyberarkCredOptionsDict['localCacheLifeSpanStringToBind']
                            if localCacheLifeSpanStringToBind == "":
                                localCacheLifeSpanStringToBind = "default"
                                print "Setting localCacheLifeSpanStringToBind to default because empty string was specified."
                            else:
                                print "Cyberark option localCacheLifeSpanStringToBind was specified: " + str(localCacheLifeSpanStringToBind)
                        except KeyError:
                            print "Setting localCacheLifeSpanStringToBind to default because no value was specified."
                            localCacheLifeSpanStringToBind = "default"
                        try:
                            usingCMSubjectCache = cyberarkCredOptionsDict['usingCMSubjectCache']
                            if usingCMSubjectCache == "":
                                usingCMSubjectCache = "default"
                                print "Setting usingCMSubjectCache to default because empty string was specified."
                            else:
                                print "Cyberark option usingCMSubjectCache was specified: " + str(usingCMSubjectCache)
                        except KeyError:
                            print "Setting usingCMSubjectCache to default because no value was specified."
                            usingCMSubjectCache = "default"
                    else:
                        # no cred options stanza provided (this is the normal case I think)
                        # script will get values from defaults file CyberarkDefaults.py
                        reasonStringToBind = "default"
                        localCacheLifeSpanStringToBind = "default"
                        usingCMSubjectCache = "default"
                        
                    for baseServerName in baseServerList:   
                        Configurator.setCyberArkOptions(WAScellName, appNickname, baseServerName, reasonStringToBind, localCacheLifeSpanStringToBind, usingCMSubjectCache)
                    readyAddOrReplaceMenu(menu_response)

                elif menu_response == '6':
                    enableCyberarkOrOriginal = "cyberark"
                    Configurator.toggleCyberarkedDatasources(cfgDict, enableCyberarkOrOriginal)
                    readyAddOrReplaceMenu(menu_response)

                elif menu_response == '7':
                    enableCyberarkOrOriginal = "original"
                    Configurator.toggleCyberarkedDatasources(cfgDict, enableCyberarkOrOriginal)
                    readyAddOrReplaceMenu(menu_response)

                elif menu_response == '8':
                    appNickname = ""
                    reasonStringToBind = ""
                    localCacheLifeSpanStringToBind = ""
                    usingCMSubjectCache = ""
                    if cyberarkCredInfoDict:
                        appNickname = cyberarkCredInfoDict['appNickname']
                    
                    if cyberarkCredOptionsDict:
                        print "At least one Cyberark option was specified."
                        try:
                            reasonStringToBind = cyberarkCredOptionsDict['reasonStringToBind']
                            if reasonStringToBind == "":
                                reasonStringToBind = "default"
                                print "Setting reasonStringToBind to default because empty string was specified."
                            else:
                                print "Cyberark option reasonStringToBind was specified: " + str(reasonStringToBind)
                        except KeyError:
                            print "Setting reasonStringToBind to default because no value was specified."
                            reasonStringToBind = "default"
                            
                        try:
                            localCacheLifeSpanStringToBind = cyberarkCredOptionsDict['localCacheLifeSpanStringToBind']
                            if localCacheLifeSpanStringToBind == "":
                                localCacheLifeSpanStringToBind = "default"
                                print "Setting localCacheLifeSpanStringToBind to default because empty string was specified."
                            else:
                                print "Cyberark option localCacheLifeSpanStringToBind was specified: " + str(localCacheLifeSpanStringToBind)
                        except KeyError:
                            print "Setting localCacheLifeSpanStringToBind to default because no value was specified."
                            localCacheLifeSpanStringToBind = "default"
                        try:
                            usingCMSubjectCache = cyberarkCredOptionsDict['usingCMSubjectCache']
                            if usingCMSubjectCache == "":
                                usingCMSubjectCache = "default"
                                print "Setting usingCMSubjectCache to default because empty string was specified."
                            else:
                                print "Cyberark option usingCMSubjectCache was specified: " + str(usingCMSubjectCache)
                        except KeyError:
                            print "Setting usingCMSubjectCache to default because no value was specified."
                            usingCMSubjectCache = "default"
                    else:
                        # no cred options stanza provided
                        # script will get values from defaults file CyberarkDefaults.py
                        reasonStringToBind = "default"
                        localCacheLifeSpanStringToBind = "default"
                        usingCMSubjectCache = "default"                        
                        
                    for baseServerName in baseServerList:   
                        Configurator.setCyberArkOptions(WAScellName, appNickname, baseServerName, reasonStringToBind, localCacheLifeSpanStringToBind, usingCMSubjectCache)
                    readyAddOrReplaceMenu(menu_response)

                elif menu_response == '9':
                    appNickname = ""
                    reasonStringToBind = ""
                    localCacheLifeSpanStringToBind = ""
                    usingCMSubjectCache = ""
                    if cyberarkCredInfoDict:
                        appNickname = cyberarkCredInfoDict['appNickname']

                    # script will get values from defaults file CyberarkDefaults.py
                    reasonStringToBind = "default"
                    localCacheLifeSpanStringToBind = "default"
                    usingCMSubjectCache = "default"                        
                        
                    for baseServerName in baseServerList:   
                        Configurator.setCyberArkOptions(WAScellName, appNickname, baseServerName, reasonStringToBind, localCacheLifeSpanStringToBind, usingCMSubjectCache)
                    readyAddOrReplaceMenu(menu_response)
                    
                elif menu_response == '98':
                    reDisplaypageOne(config_file)

                elif menu_response == '99':
                    menuToSwitchConfigFiles(config_file)

                else:
                    print "Response was not recognized."
                    menuAddOrReplace(config_file)
            else:
                print "Response was non-numeric."
                menuAddOrReplace(config_file)
        
    except SystemExit:
        pass
    except:
        print "\n\nException in menuAddOrReplace()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def readyAddOrReplaceMenu(menu_response):
    """ Print out the menu option that was just done, and confirm that
    it completed, to make it show in case log of user session is
    desired: Main Menu """
    print "\nEnd of Add Menu Option " + menu_response  
    try:
        what_response = raw_input("\nPress any key to continue.  ")
    except EOFError:
        print "\nExiting."
        sys.exit(0)
    #getWASinfo()  
    menuAddOrReplace(config_file)


def menuToAddThings(config_file):
    """ The "Add" Menu. """
    try:
        display = "\n\n"
        display += div1 + "\n"
        display += "Options for ADDING to your WAS cell \n"
        display += div1 + "\n\n"   

        display += sp1 + "Config file: " + config_file + "\n"
        display += "\n"
        
        print display

        display = "\n\n"
        display += div1 + "\n"
        display += "Please choose action to perform \n"
        display += div1 + "\n"   
        
        wsadminSvr = AdminControl.queryNames("node="+AdminControl.getNode( )+",type=Server,*" )
        wsadminServer = AdminControl.getAttribute(wsadminSvr, "name" )
        
        menuNum = 1
        display += sp1+ str(menuNum) + sp1+ "Add all items in config file \n"
        display += sp3 + "This will NOT replace any items that already exist in cell (marked *) \n"
        display += sp3 + "This will only add items from the config file that are missing in the WAS cell. \n"
        if wsadminServer == "server1":
            display += sp3 + "\n"
            display += sp3 + "You are connected to a standalone server -- i.e., server name is server1.\n"
            display += sp3 + "Script cannot add servers to standalone profile.\n"
            display += sp3 + "Non-server-level items (if any) in your config will be added. \n"
            display += sp3 + "To add server-level items to your WAS cell, use the individual\n"
            display += sp3 + "  'add' options, e.g., 'Add datasources'\n"
        display += "\n"

        if wsadminServer == "server1":
            pass
        else:
            menuNum = 2
            display += sp1+ str(menuNum) + sp1+ "Add server and all its config ...\n"
            display += "\n"

            menuNum = 3
            display += sp1+ str(menuNum) + sp1+ "Add virtual host entry(ies) for a server or cluster ...\n"
            display += "\n"

        menuNum = 4
        display += sp1+ str(menuNum) + sp1+ "Add datasource(s) for a server or cluster ...\n"
        display += "\n"

        menuNum = 41
        display += sp1+ str(menuNum) + sp1+ "Add datasource(s) at arbitrary scope ...\n"
        display += "\n"

        menuNum = 5
        display += sp1+ str(menuNum) + sp1+ "Add JVM custom property(ies) for a server or cluster ...\n"
        display += "\n"

        menuNum = 6
        display += sp1+ str(menuNum) + sp1+ "Add web container custom property(ies) for a server or cluster ...\n"
        display += "\n"

        menuNum = 7
        display += sp1+ str(menuNum) + sp1+ "Add MQ queue connection factory(ies) for a server or cluster ...\n"
        display += "\n"

        menuNum = 8
        display += sp1+ str(menuNum) + sp1+ "Add MQ queue definition(s) for a server or cluster ...\n"
        display += "\n"

        menuNum = 9
        display += sp1+ str(menuNum) + sp1+ "Add JMS Activation Spec(s) for a server or cluster ...\n"
        display += "\n"

        menuNum = 10
        display += sp1+ str(menuNum) + sp1+ "Add shared library(ies) (& classloader(s)) for a server or cluster ...\n"
        display += "\n"

        menuNum = 11
        display += sp1+ str(menuNum) + sp1+ "Add cell-scoped WebSphere variable(s) ...\n"
        display += "\n"

        menuNum = 12
        display += sp1+ str(menuNum) + sp1+ "Add node-scoped WebSphere variable(s) ...\n"
        sp = sp1+ "  " + sp1
        display += sp + "Use this action to add DB driver paths. Note that MySql vars are not built in, \n"
        display += sp + "but vars for DB2 & some others are BUILT INTO Websphere.\n"
        display += sp + "The built-in DB driver vars have empty string values, for all nodes. If you \n"
        display += sp + "want to add driver with built-in vars, you can use this action, but only if \n"
        display += sp + "vals are still blank.  This option will NOT change vals that are non-blank. \n"
        display += sp + "To modify non-blank vars, use the appropriate 'replace' action instead.\n\n"

        menuNum = 13
        display += sp1+ str(menuNum) + sp1+ "Add cell-scoped JAAS authentication entry(ies) ...\n"
        display += "\n"
        
        menuNum = 14
        display += sp1+ str(menuNum) + sp1+ "Add NEW asynch bean work manager(s) for a server or cluster ...\n"
        display += "\n"
        
        menuNum = 99
        display += sp1+ str(menuNum) + sp1+ "Return to previous menu ...\n"
        display += "\n"

        print display
        menu_response = ""
        try:
            menu_response = raw_input(standard_prompt)
        except EOFError:
            print "Exiting."
            sys.exit(0)
        print "Menu response was: " + str(menu_response)

        if menu_response.isnumeric():
            if menu_response == '1':
                try:
                    print "\nAdd all items in this config file to your WAS cell ..."
                    #ConfigureWholeEnvironment.createEnvironmentFromConfigFile((configPath + config_file))
                    #ideally, would make new menu item for cell-level items that do not depend on any config file
                    Configurator.limitLTPACookiesToSSLOnly()
                    Configurator.doWebsphereVariables(cellName, cfgDict)
                    Configurator.doNodeLevelWebsphereVariables(cellName, cfgDict)
                    Configurator.doJaasEntries(cfgDict)
                    if wsadminServer == "server1":
                        print "\n\nYou are connected to a standalone server -- i.e., server name is server1."
                        print "Script cannot add server(s) to standalone profile."
                        print "To add server-level items to your WAS cell, use the individual"
                        print "  'add' options, e.g., 'Add datasources'\n"
                        print "\nAdded only non-server-level items from your config file (if any).\n\n"
                    else:
                        Configurator.doServers(cfgDict)
                    readyAddMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToAddThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '2':
                try:
                    print "\nAdd a server ..."
                    if wsadminServer == "server1":
                        print "You are connected to a standalone server -- i.e., server name is server1."
                        print "\nScript cannot add servers to standalone profile."
                        print "To rebuild server1:"
                        print
                        print "    1  Recreate the profile using 'application server' as profile type. "
                        print "       New profile will have a new server1 with all defaults."
                        print
                        print "    2  Rerun this script and use the individual 'modify' actions to add datasources, etc."
                    else:    
                        baseServerName = whatServerMenu(config_file)
                        if baseServerName is not None:
                            print "\nAdding server: " + baseServerName + " ..."
                            Configurator.doServer(cfgDict, baseServerName)
                        else:
                            print "\nNo server chosen."
                            menuToAddThings(config_file)
                    readyAddMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToAddThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '3':
                try:
                    print "\nAdd virtual host for a server or cluster ..."
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\nAdding virtual host for: " + baseServerName + " ..."
                        Configurator.createOneVirtualHost(cfgDict, baseServerName)
                    else:
                        print "\nNo server chosen."
                        menuToAddThings(config_file)
                    readyAddMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToAddThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '4':
                try:
                    print "\nAdd datasources for a server or cluster ..."
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\nAdding datasources for: " + baseServerName + " ..."
                        Configurator.createOneServersDatasources(cfgDict, baseServerName)
                        Configurator.addOneServersDatasourcesCustomProps(cfgDict, baseServerName)
                    else:
                        print "\nNo server chosen."
                        menuToAddThings(config_file)
                    readyAddMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToAddThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '41':
                try:
                    print "\nAdd datasources at arbitrary server scope ..."
                    manually_entered_server_name = raw_input("\nPlease enter entire name of server:  ")
                    
                    if manually_entered_server_name is not None:
                        print "\nAdding datasources for: " + manually_entered_server_name + " ..."
                        Configurator.createArbitraryServersDatasources(cfgDict, manually_entered_server_name)
                        print "\nAdding custom props (if any) for datasources for: " + manually_entered_server_name + " ..."
                        Configurator.addOneArbitraryServersDatasourcesCustomProps(cfgDict, manually_entered_server_name)
                    else:
                        print "\nNo server chosen."
                        menuToAddThings(config_file)
                    readyAddMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToAddThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '5':
                try:
                    print "\nAdd JVM custom prop(s) for a server or cluster ..."
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\nAdding JVM custom prop(s) for: " + baseServerName + " ..."
                        Configurator.createJvmCustomProps(cfgDict, baseServerName)
                    else:
                        print "\nNo server chosen."
                        menuToAddThings(config_file)
                    readyAddMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToAddThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '6':
                try:
                    print "\nAdd web container custom prop(s) for a server or cluster ..."
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\nAdding web container custom prop(s) for: " + baseServerName + " ..."
                        Configurator.setWebContainerCustomProperties(cfgDict, baseServerName)
                    else:
                        print "\nNo server chosen."
                        menuToAddThings(config_file)
                    readyAddMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToAddThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '7':
                try:
                    print "\nAdd queue connection factorie(s) for a server or cluster ..."
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\nAdding queue connection factorie(s) for: " + baseServerName + " ..."
                        Configurator.createOneServersQueueConnectionFactories(cfgDict, baseServerName)
                    else:
                        print "\nNo server chosen."
                        menuToAddThings(config_file)
                    readyAddMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToAddThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '8':
                try:
                    print "\nAdd queue(s) for a server or cluster ..."
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\nAdding queue(s) for: " + baseServerName + " ..."
                        Configurator.createOneServersQueue(cfgDict, baseServerName)
                    else:
                        print "\nNo server chosen."
                        menuToAddThings(config_file)
                    readyAddMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToAddThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '9':
                try:
                    print "\nAdd Act spec(s) for a server or cluster ..."
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\nAdding Act spec(s) for: " + baseServerName + " ..."
                        Configurator.createOneServersJMSActivationSpecs(cfgDict, baseServerName)
                    else:
                        print "\nNo server chosen."
                        menuToAddThings(config_file)
                    readyAddMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToAddThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '10':
                try:
                    print "\nAdd shared lib(s) for a server or cluster ..."
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\nAdding shared lib(s) for: " + baseServerName + " ..."
                        Configurator.createSharedLibraries(cfgDict, baseServerName)
                    else:
                        print "\nNo server chosen."
                        menuToAddThings(config_file)
                    readyAddMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToAddThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '11':
                try:
                    print "\nAdding cell-level WAS vars ..."
                    Configurator.doWebsphereVariables(cellName, cfgDict)
                    readyAddMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToAddThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '12':
                try:
                    print "\nAdding node-level WAS vars ..."
                    Configurator.doNodeLevelWebsphereVariables(cellName, cfgDict)
                    readyAddMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToAddThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '13':
                try:
                    print "\nAdding JAAS entries ..."
                    Configurator.doJaasEntries(cfgDict)
                    readyAddMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToAddThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '14':
                try:
                    print "\nAdd NEW asynch bean work manager definitions for a server or cluster ..."
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\nAdding NEW asynch bean work manager definitions for: " + baseServerName + " ... \n"
                    Configurator.createAsynchBeanNonDefaultWorkManagers(cfgDict, baseServerName)
                    readyAddMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToAddThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
                    
            elif menu_response == '99':
                try:
                    menuAddOrReplace(config_file)
                except:
                    print "\n\nException in menuToAddThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
            else:
                print "Response was not recognized."
                menuToAddThings(config_file)
        else:
            print "Response was non-numeric."
            print "Returning to previous menu."
            menuAddOrReplace(config_file)
    except:
        print "\n\nException in menuToAddThings()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def readyAddMenu(config_file, menu_response):
    """ Print out the menu option that was just done, and confirm that
    it completed, to make it show in case log of user session is
    desired: the Add Menu """
    print "\nEnd of Add Menu Option " + menu_response  
    try:
        what_response = raw_input("\nPress any key to continue.  ")
    except EOFError:
        print "\nExiting."
        sys.exit(0)
    #getWASinfo()    
    menuToAddThings(config_file)


def whatServerMenu(config_file) :
    """ Let user choose a server listed in their config file. """
    count = 1
    foundInWAS = "false"
    display = ""
    display += sp1 + "Config file: " + config_file + "\n"
    if baseServerList:
        display = "\n\n"
        display += ""
        display += sp1 + "Servers in your config file: \n"
        # look to see if at least one  server with same base name is found in WAS cell
        if serverInfoDict:
            if len(serverInfoDict) != 0:
                for serverInfoKey in serverInfoDict.keys():
                    foundInWAS = "false"
                    si = serverInfoDict[serverInfoKey]
                    #print 'si:' 
                    #print si
                    #print 'serverInfoKey: '
                    #print serverInfoKey
                    #print "count: " + str(count)
                    baseServerName = si['baseServerName']
                    serverNodeList = si['nodeList'].split()
                    isClustered = si['isClustered']
                    nodeNumber = 1
                    for nodeName in serverNodeList:
                        serverName = baseServerName + str(nodeNumber)
                        nodeNumber += 1
                        if serverName in WASserverList:
                            foundInWAS = "true"
                            break
                    if foundInWAS == "true":
                        display += sp2star
                    else:
                        display += sp2
                    display += str(count) + getSpacer(count) + baseServerName + "      Clustered: " + isClustered + "\n"
                    count = count + 1
            else:
                try:
                    print "zero length serverInfoDict"
                    menu_response = raw_input("\nNo servers found in your config file. Press any key to continue: ")
                except EOFError:
                    print "\nExiting."
                    sys.exit(0)
                    
                menuPageOne(config_file)
        else:
            try:
                print "no serverInfoDict"
                menu_response = raw_input("\nNo servers found in your config file. Press any key to continue: ")
            except EOFError:
                print "\nExiting."
                sys.exit(0)
            menuPageOne(config_file)
    else:
        try:
            print "no baseServerList"
            menu_response = raw_input("\nNo servers found in your config file. Press any key to continue: ")
        except EOFError:
            print "\nExiting."
            sys.exit(0)
        menuPageOne(config_file)
        
    display += "\n"
    display += "* means that the item in your config file is found in your WAS cell."
    print display        
    try:
        what_server_response = raw_input("\nPlease enter number of server:  ")                    
    except EOFError:
        print "\nExiting."
        sys.exit(0)
    print "Menu response was: " + str(what_server_response)    
    if what_server_response is None or what_server_response == "":
        print "\nNo response made."
        #whatResponsepageOne(config_file)
        
    #print "what_server_response is: " + what_server_response
    if what_server_response.isnumeric():
        what_server_response = int(what_server_response)
        theChosenBaseServerName = baseServerList[what_server_response - 1]
        #print "theChosenBaseServerName is: " + theChosenBaseServerName
        return theChosenBaseServerName


def menuToReplaceThings(config_file):
    """ The "Replace" Menu """
    try:
        display = "\n\n"
        display += div1 + "\n"
        display += "Options for REPLACING items to your WAS cell \n\n"
        display += "These options will BLOW AWAY and REPLACE existing items in your WAS cell\n"
        display += sp3 + "... but ONLY items that are in this config file. \n"
        
        display += div1 + "\n\n"   
        display += sp1 + "Config file: " + config_file + "\n"
        print display

        display = "\n\n"
        display += div1 + "\n"
        display += "Please choose action to perform \n"
        display += div1 + "\n"   

        wsadminSvr = AdminControl.queryNames("node="+AdminControl.getNode( )+",type=Server,*" )
        wsadminServer = AdminControl.getAttribute(wsadminSvr, "name" )

        menuNum = 1
        display += sp1+ str(menuNum) + sp1+ "Rebuild all items in config file \n"
        if wsadminServer == "server1":
            display += sp3 + "\n"
            display += sp3 + "You are connected to a standalone server -- i.e., server name is server1.\n"
            display += sp3 + "Script will not rebuild standalone server.\n"
            display += sp3 + "Other items (if any) in your config will be rebuilt. \n"
        display += "\n"
        
        
        if wsadminServer == "server1":
            pass
        else:
            menuNum = 2
            display += sp1+ str(menuNum) + sp1+ "Rebuild a server ...\n"        
            display += "\n"
        
            menuNum = 3
            display += sp1+ str(menuNum) + sp1+ "Rebuild virtual host for a server or cluster ...\n"
            display += "\n"

        menuNum = 4
        display += sp1+ str(menuNum) + sp1+ "Rebuild datasource(s) for a server or cluster ...\n"
        display += "\n"

        menuNum = 5
        display += sp1+ str(menuNum) + sp1+ "Rebuild JVM custom property(ies) for a server or cluster ...\n"
        display += "\n"

        menuNum = 6
        display += sp1+ str(menuNum) + sp1+ "Rebuild web container custom property(ies) for a server or cluster ...\n"
        display += "\n"

        menuNum = 7
        display += sp1+ str(menuNum) + sp1+ "Rebuild MQ queue connection factory(ies) for a server or cluster ...\n"
        display += "\n"

        menuNum = 8
        display += sp1+ str(menuNum) + sp1+ "Rebuild MQ queue definition(s) for a server or cluster ...\n"
        display += "\n"
        
        menuNum = 9
        display += sp1+ str(menuNum) + sp1+ "Rebuild JMS Activation Spec(s) for a server or cluster ...\n"
        display += "\n"

        menuNum = 10
        display += sp1+ str(menuNum) + sp1+ "Rebuild shared library(ies) (& classloader(s)) for a server or cluster ...\n"
        display += "\n"

        menuNum = 11
        display += sp1+ str(menuNum) + sp1+ "Rebuild cell-scoped WebSphere variable(s) ...\n"
        display += "\n"

        menuNum = 12
        display += sp1+ str(menuNum) + sp1+ "Rebuild node-scoped WebSphere variable(s) ...\n"
        display += "\n"

        menuNum = 13
        display += sp1+ str(menuNum) + sp1+ "Rebuild cell-scoped JAAS authentication entry(ies) ...\n"
        display += "\n"

        menuNum = 14
        display += sp1+ str(menuNum) + sp1+ "Rebuild asynch bean work manager(s) for a server or cluster ...\n"
        display += "\n"
        
        menuNum = 99
        display += sp1+ str(menuNum) + sp1+ "Return to previous menu ...\n"
        display += "\n"
        
        print display
        menu_response = ""

        try:
            menu_response = raw_input(standard_prompt)
        except EOFError:
            print "\nExiting."
            sys.exit(0)
        if menu_response == "":
            print "Menu response was: empty string"
            menu_response = raw_input("\nReturn to previous menu? (y | n): ")
            if menu_response.lower() == "n":
                print "Response was: " + str(menu_response)
                menuToReplaceThings(config_file)
                return
            else:
                if menu_response == "":
                    print "Response was: empty string"
                else:
                    print "Response was: " + str(menu_response)
                print "\nReturning to previous menu."
                menuAddOrReplace(config_file)
                return
        
        danger_response = ""  
        warning_msg = ""
        try:
            warning_msg += "\nThis option will BLOW AWAY and REPLACE existing items in your WAS cell\n"
            warning_msg += "... but ONLY items that are in this config file. \n"
            warning_msg += "\nEnter 'y' to continue, any other key to abort. "
            danger_response = raw_input(warning_msg)
        except EOFError:
            print "\nExiting."
            sys.exit(0)
        print "Warning response was: " + str(danger_response) 
        if danger_response == "":
            print "Response was: empty string"
            menuToReplaceThings(config_file)
            return
        elif danger_response.lower() == 'y':
            print "Response was: " + str(danger_response)
            pass
        else:
            print "Response was: " + str(danger_response)
            menuToReplaceThings(config_file)
            return
            
        if menu_response.isnumeric():

            if menu_response == '1':
                try:
                    print "\nReplace all items in your WAS cell that are in this config file."
                    print "\n" + div1 
                    print "Removing all items that are in this config file ..."
                    print div1 + "\n"
                    if wsadminServer == "server1":
                        print "You are connected to a standalone server -- i.e., server name is server1."
                        print "Script cannot rebuild standalone server."
                        print "Continuing."
                    else:
                        Destroyer.blowAwayAllClustersServers(cfgDict)
                        Destroyer.blowAwayAllVirtualHosts(cfgDict)
                    Destroyer.blowAwayAllJaas(cfgDict)
                    Destroyer.blowAwayAllCellScopedWebsphereVariable(cellName, cfgDict)
                    Destroyer.zeroOutAllNodeScopedWebsphereVariable(cfgDict)
                    Destroyer.blowAwayAllRepDomains(cfgDict)
                    print "\n" + div1 
                    print "Recreating all items that are in this config file ..."
                    print div1 + "\n"
                    Configurator.doWebsphereVariables(cellName, cfgDict)
                    Configurator.doNodeLevelWebsphereVariables(cellName, cfgDict)
                    Configurator.doJaasEntries(cfgDict)
                    if wsadminServer == "server1":
                        pass                    
                    else:
                        Configurator.doServers(cfgDict)
                    readyReplaceMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToReplaceThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
                    
            elif menu_response == '2':
                try:
                    print "\nReplace a server ...\n"
                    if wsadminServer == "server1":
                        print "You are connected to a standalone server -- i.e., server name is server1."
                        print "\nScript cannot rebuild standalone server."
                        print "To rebuild server1:"
                        print
                        print "    1  Recreate the profile using 'application server' as profile type. "
                        print "       New profile will have a new server1 with all defaults."
                        print
                        print "    2  Rerun this script and use the individual 'modify' actions to add datasources, etc."
                    else: 
                        baseServerName = whatServerMenu(config_file)
                        if baseServerName is not None:
                            print "\n" + div1 
                            print "Removing cluster and/or server for: " + baseServerName + " ..."
                            print div1 + "\n"
                            getServerClusterConfigInfoDetail(baseServerName)
                            if serverIsClusteredInConfigFile == "true":
                                Destroyer.blowAwayCluster(clusterNameInConfigFile)
                            elif serverIsClusteredInConfigFile == "false":
                                Destroyer.blowAwayServer(nodeNameInConfigFile, baseServerName + '1')
                            print div1 
                            print "Recreating cluster and/or server for: " + baseServerName + " ..."
                            print div1 + "\n"
                            Configurator.doServer(cfgDict, baseServerName)
                        else:
                            print "\nNo server chosen."
                            menuToReplaceThings(config_file)
                    readyReplaceMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToReplaceThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '3':
                try:
                    print "\nRebuild virtual host for a server or cluster ...\n"
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\n" + div1 
                        print "Removing virtual host for: " + baseServerName + " ..."
                        print div1 + "\n"
                        Destroyer.blowAwayOneServersVirtualHost(cfgDict, baseServerName)
                        print "\n" + div1 
                        print "Recreating virtual host for: " + baseServerName + " ..."
                        print div1 + "\n"
                        Configurator.createOneVirtualHost(cfgDict, baseServerName)
                    else:
                        print "\nNo server chosen."
                        menuToReplaceThings(config_file)
                    readyReplaceMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToReplaceThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '4':
                try:
                    print "\nRebuild datasource(s) for a server or cluster ...\n"
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\n" + div1 
                        print "Removing a atasource(s) for: " + baseServerName + " ..."
                        print div1 + "\n"
                        try:
                            serversdataSourceInfoDict = wini.getPrefixedClauses(cfgDict,'dataSource:' + baseServerName + ':')
                            if serversdataSourceInfoDict:
                                for serversdataSourceInfoKey in serversdataSourceInfoDict.keys():
                                    sdi = serversdataSourceInfoDict[serversdataSourceInfoKey]
                                    dataSourceName = sdi['dataSourceName'].strip()
                                    dbType = sdi['db2OrOracle'].strip()
                                    for serverInfoKey in serverInfoDict.keys():
                                        si = serverInfoDict[serverInfoKey]
                                        if si['baseServerName'] == baseServerName:
                                            isClustered = si['isClustered'].strip()
                                            if isClustered == 'true':
                                                clusterName = si['clusterName']
                                                Destroyer.blowAwayOneClustersDatasource(clusterName, dbType, dataSourceName)
                                            else:
                                                nodeList = si['nodeList'].split()
                                                nodeNumber = 0
                                                for nodeName in nodeList:
                                                    nodeNumber += 1
                                                    #slap a number on the end of baseServerName whether it is clustered (on > 1 node) or not (1 node)
                                                    serverName = baseServerName + str(nodeNumber)
                                                    print "\nRemoving datasource: " + dataSourceName + " for server: " + serverName
                                                    Destroyer.blowAwayOneServersDatasource(cellName, nodeName, serverName, dbType, dataSourceName)
                        except:
                            print "\n\nException in menuToReplaceThings() when removing datasources()"
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            readyReplaceMenu(config_file, menu_response)
                        print "\n" + div1 
                        print "Recreating all datasource(s) for: " + baseServerName + " ..."
                        print div1 + "\n"
                        try:
                            Configurator.createOneServersDatasources(cfgDict, baseServerName)
                            Configurator.addOneServersDatasourcesCustomProps(cfgDict, baseServerName)
                        except:
                            print "\n\nException in menuToReplaceThings() when recreating datasources()"
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            readyReplaceMenu(config_file, menu_response)
                    else:
                        print "\nNo server chosen."
                        menuToReplaceThings(config_file)
                    readyReplaceMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToReplaceThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    
            elif menu_response == '5':
                try:
                    print "\nRebuild JVM custom property(ies) for a server or cluster ...\n"
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\n" + div1 
                        print "Removing JVM custom props for server: " + baseServerName + " ..."
                        print div1 + "\n"
                        try:
                            jvmCustomPropInfoDict = wini.getPrefixedClauses(cfgDict,'jvmCustomProperty:' + baseServerName + ':')
                            if jvmCustomPropInfoDict:
                                for jvmCustomPropInfoKey in jvmCustomPropInfoDict.keys():
                                    jcpi = jvmCustomPropInfoDict[jvmCustomPropInfoKey]
                                    jvmCustomPropName = jcpi['propertyName'].strip()
                                    for serverInfoKey in serverInfoDict.keys():
                                        si = serverInfoDict[serverInfoKey]
                                        if si['baseServerName'] == baseServerName:
                                            nodeList = si['nodeList'].split()
                                            nodeNumber = 0
                                            for nodeName in nodeList:
                                                nodeNumber += 1
                                                #slap a number on the end of baseServerName whether it is clustered (on > 1 node) or not (1 node)
                                                serverName = baseServerName + str(nodeNumber)
                                                print "\nRemoving JVM custom prop: " + jvmCustomPropName + " for server: " + serverName
                                                Destroyer.blowAwayOneServersJvmCustomProperty(nodeName, serverName, jvmCustomPropName)
                        except:
                            print "\n\nException in menuToReplaceThings() when removing JVM custom prop(s)"
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            readyReplaceMenu(config_file, menu_response)
                        print "\n" + div1 
                        print "Recreating JVM custom props for: " + baseServerName + " ..."
                        print div1 + "\n"
                        try:
                            Configurator.createJvmCustomProps(cfgDict, baseServerName)
                        except:
                            print "\n\nException in menuToReplaceThings() when recreating JVM custom prop(s)"
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            readyReplaceMenu(config_file, menu_response)
                    else:
                        print "\nNo server chosen."
                        menuToReplaceThings(config_file)
                    readyReplaceMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToReplaceThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyReplaceMenu(config_file, menu_response)

            elif menu_response == '6':
                try:
                    print "\nRebuild web container custom property(ies) for a server or cluster ...\n"
                    print "This feature is not implemented. Only option at the moment is to recreate the server."
                    readyReplaceMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToReplaceThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyReplaceMenu(config_file, menu_response)

            elif menu_response == '7':
                try:
                    print "\nRebuild MQ queue connection factory(ies) for a server or cluster ...\n"
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\n" + div1
                        print "Removing MQ queue connection factory(ies) for server: " + baseServerName + " ..."
                        print div1 + "\n"
                        try:
                            queueConnectionFactoryInfoDict = wini.getPrefixedClauses(cfgDict,'queueConnectionFactory:' + baseServerName + ':')
                            if queueConnectionFactoryInfoDict:
                                for queueConnectionFactoryInfoKey in queueConnectionFactoryInfoDict.keys():
                                    qcfi = queueConnectionFactoryInfoDict[queueConnectionFactoryInfoKey]
                                    factoryName = qcfi['name'].strip()
                                    for serverInfoKey in serverInfoDict.keys():
                                        si = serverInfoDict[serverInfoKey]
                                        if si['baseServerName'] == baseServerName:
                                            isClustered = si['isClustered'].strip()
                                            if isClustered == 'true':
                                                clusterName = si['clusterName']
                                                Destroyer.blowAwayOneClustersQueueConnectionFactory(cellName, clusterName, factoryName)
                                            else:
                                                nodeList = si['nodeList'].split()
                                                nodeNumber = 0
                                                for nodeName in nodeList:
                                                    nodeNumber += 1
                                                    #slap a number on the end of baseServerName whether it is clustered (on > 1 node) or not (1 node)
                                                    serverName = baseServerName + str(nodeNumber)
                                                    print "\nRemoving MQ queue connection factory: " + factoryName + " for server: " + serverName
                                                    Destroyer.blowAwayOneServersQueueConnectionFactory(cellName, nodeName, serverName, factoryName)
                        except:
                            print "\n\nException in menuToReplaceThings() when removing MQ queue connection factory(ies)"
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            readyReplaceMenu(config_file, menu_response)
                        print "\n" + div1 
                        print "Recreating MQ queue connection factory(ies) for server: " + baseServerName + " ..."
                        print div1 + "\n"
                        try:
                            Configurator.createOneServersQueueConnectionFactories(cfgDict, baseServerName)
                        except:
                            print "\n\nException in menuToReplaceThings() when recreating MQ queue connection factory(ies)"
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            readyReplaceMenu(config_file, menu_response)
                    else:
                        print "\nNo server chosen."
                        menuToReplaceThings(config_file)
                    readyReplaceMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToReplaceThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyReplaceMenu(config_file, menu_response)

            elif menu_response == '8':
                try:
                    print "\nRebuild MQ queue definition(s) for a server or cluster ...\n"
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\n" + div1 
                        print "Removing queue(s) for server: " + baseServerName + " ..."
                        print div1 + "\n"
                        try:
                            queueInfoDict = wini.getPrefixedClauses(cfgDict,'queue:' + baseServerName + ':')
                            if queueInfoDict:
                                for queueInfoKey in queueInfoDict.keys():
                                    qi = queueInfoDict[queueInfoKey]
                                    queueName = qi['name'].strip()
                                    for serverInfoKey in serverInfoDict.keys():
                                        si = serverInfoDict[serverInfoKey]
                                        if si['baseServerName'] == baseServerName:
                                            isClustered = si['isClustered'].strip()
                                            if isClustered == 'true':
                                                clusterName = si['clusterName']
                                                Destroyer.blowAwayOneClustersQueue(cellName, clusterName, queueName)
                                            else:
                                                nodeList = si['nodeList'].split()
                                                nodeNumber = 0
                                                for nodeName in nodeList:
                                                    nodeNumber += 1
                                                    #slap a number on the end of baseServerName whether it is clustered (on > 1 node) or not (1 node)
                                                    serverName = baseServerName + str(nodeNumber)
                                                    print "\nRemoving queue: " + queueName + " for server: " + serverName
                                                    Destroyer.blowAwayOneServersQueue(cellName, nodeName, serverName, queueName)

                        except:
                            print "\n\nException in menuToReplaceThings() when removing queue(s)"
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            readyReplaceMenu(config_file, menu_response)
                        print "\n" + div1 
                        print "Recreating queue(s) for: " + baseServerName + " ..."
                        print div1 + "\n"
                        try:
                            Configurator.createOneServersQueue(cfgDict, baseServerName)
                        except:
                            print "\n\nException in menuToReplaceThings() when recreating queue(s)"
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            readyReplaceMenu(config_file, menu_response)
                    else:
                        print "\nNo server chosen."
                        menuToReplaceThings(config_file)
                    readyReplaceMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToReplaceThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyReplaceMenu(config_file, menu_response)

            elif menu_response == '9':
                try:
                    print "\nRebuild JMS Activation Spec(s) for a server or cluster ...\n"
                    print "This feature is not implemented. Only option at the moment is to recreate the server."
                    readyReplaceMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToReplaceThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyReplaceMenu(config_file, menu_response)

            elif menu_response == '10':
                try:
                    print "\nRebuild shared library(ies) (& classloader(s)) for a server or cluster ...\n"
                    print "This feature is not implemented. Only option at the moment is to recreate the server."
                    readyReplaceMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToReplaceThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyReplaceMenu(config_file, menu_response)

            elif menu_response == '11':
                try:
                    print "\nRebuild cell-scoped WebSphere variable(s) ...\n"
                    print "\n" + div1 
                    print "Removing WAS vars ..."
                    print div1 + "\n"
                    Destroyer.blowAwayAllCellScopedWebsphereVariable(cellName, cfgDict)
                    print "\n" + div1 
                    print "Recreating WAS vars ..."
                    print div1 + "\n"
                    Configurator.doWebsphereVariables(cellName, cfgDict)
                    readyReplaceMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToReplaceThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyReplaceMenu(config_file, menu_response)

            elif menu_response == '12':
                try:
                    print "\nRebuild node-scoped WebSphere variable(s) ...\n"
                    print "\n" + div1 
                    print "Removing node-scoped WAS vars ..."
                    print div1 + "\n"
                    Destroyer.zeroOutAllNodeScopedWebsphereVariable(cfgDict)
                    print "\n" + div1 
                    print "Recreating node-scoped WAS vars ..."
                    print div1 + "\n"
                    Configurator.doNodeLevelWebsphereVariables(cellName, cfgDict)
                    readyReplaceMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToReplaceThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyReplaceMenu(config_file, menu_response)

            elif menu_response == '13':
                try:
                    print "\nRebuild cell-scoped JAAS authentication entry(ies) ...\n"
                    print "\n" + div1 
                    print "Removing JAAS entry(ies) ..."
                    print div1 + "\n"
                    Destroyer.blowAwayAllJaas(cfgDict)
                    print "\n" + div1 
                    print "Recreating JAAS entry(ies) ..."
                    print div1 + "\n"
                    Configurator.doJaasEntries(cfgDict)
                    readyReplaceMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToReplaceThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyReplaceMenu(config_file, menu_response)

            elif menu_response == '14':
                try:
                    print "\nRebuild asynch bean work manager definitions for a server or cluster ..."
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        try:
                            serversWorkManagerInfoDict = wini.getPrefixedClauses(cfgDict,'asynchBeanWorkManager:' + baseServerName + ':')
                            if serversWorkManagerInfoDict:
                                print "\n" + div1 
                                print "Removing all NON-DEFAULT asynch bean work manager definition(s) for: " + baseServerName + " ..."
                                print div1 + "\n"
                            
                                for serversWorkManagerInfoKey in serversWorkManagerInfoDict.keys():
                                    swm = serversWorkManagerInfoDict[serversWorkManagerInfoKey]
                                    jndiName = swm['jndiName'].strip()
                                    workManagerName = swm['name'].strip()
                                    if jndiName == 'wm/default':
                                        print "\n\n Warning:"
                                        print "     Cannot remove the default work manager (jndi name: " + jndiName + "). Only option at the moment is to rebuild the server, then modify work manager(s).\n"
                                        readyReplaceMenu(config_file, menu_response)
                                    else:
                                        for serverInfoKey in serverInfoDict.keys():
                                            si = serverInfoDict[serverInfoKey]
                                            if si['baseServerName'] == baseServerName:
                                                isClustered = si['isClustered'].strip()
                                                if isClustered == 'true':
                                                    clusterName = si['clusterName']
                                                    print "\nRemoving work manager: " + workManagerName + " for cluster: " + clusterName
                                                    Destroyer.blowAwayOneClustersAsynchBeanWorkManager(clusterName, workManagerName)
                                                else:
                                                    nodeList = si['nodeList'].split()
                                                    nodeNumber = 0
                                                    for nodeName in nodeList:
                                                        nodeNumber += 1
                                                        #slap a number on the end of baseServerName whether it is clustered (on > 1 node) or not (1 node)
                                                        serverName = baseServerName + str(nodeNumber)
                                                        print "\nRemoving work manager: " + workManagerName + " for server: " + serverName
                                                        Destroyer.blowAwayOneServersAsynchBeanWorkManager(nodeName, serverName, workManagerName)

                        except:
                            print "\n\nException in menuToReplaceThings() when removing work manager(s)"
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            readyReplaceMenu(config_file, menu_response)

                        try:
                            print "\n" + div1 
                            print "Recreating all NON-DEFAULT work manager(s) for: " + baseServerName + " ..."
                            print div1 + "\n"
                            Configurator.createAsynchBeanNonDefaultWorkManagers(cfgDict, baseServerName)
                        except:
                            print "\n\nException in menuToReplaceThings() when recreating work manager(s)"
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            readyReplaceMenu(config_file, menu_response)

                    else:
                        print "\nNo server chosen."
                        menuToReplaceThings(config_file)
                    readyReplaceMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToReplaceThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyReplaceMenu(config_file, menu_response)

            elif menu_response == '99':
                try:
                    menuAddOrReplace(config_file)
                except:
                    print "\n\nException in menuToReplaceThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    menuAddOrReplace(config_file)
            else:
                print "Response was not recognized."
                menuToReplaceThings(config_file)
        else:
            print "Response was non-numeric."
            print "Returning to previous menu."
            menuAddOrReplace(config_file)
    except SystemExit:
        pass
    except:
        print "\n\nException in menuToReplaceThings()\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def readyReplaceMenu(config_file, menu_response):
    """ Print out the menu option that was just done, and confirm that
     it completed, to make it show in case log of user session is desired: the Replace Menu """
    print "\nEnd of Replace Menu Option " + menu_response
    try:
        what_response = raw_input("\nPress any key to continue.  ")                    
    except EOFError:
        print "\nExiting."
        sys.exit(0)
    # go back to page one instead of re-displaying Replace menu
    reDisplaypageOne(config_file)
        

def menuToDeleteThings(config_file):
    """ The "Delete" Menu """
    try:
        display = "\n\n"
        display += div1 + "\n"
        display += "Options for DELETING items to your WAS cell \n\n"
        display += "These options will BLOW AWAY existing items in your WAS cell\n"
        display += sp3 + "... but ONLY items that are in this config file. \n"

        display += div1 + "\n\n"
        display += sp1 + "Config file: " + config_file + "\n"
        print display

        display = "\n\n"
        display += div1 + "\n"
        display += "Please choose action to perform \n"
        display += div1 + "\n"

        # get name of server we are connected to
        wsadminSvr = AdminControl.queryNames("node="+AdminControl.getNode( )+",type=Server,*" )
        wsadminServer = AdminControl.getAttribute(wsadminSvr, "name" )

        menuNum = 1
        display += sp1+ str(menuNum) + sp1+ "Delete all items in config file \n"
        if wsadminServer == "server1":
            display += sp3 + "\n"
            display += sp3 + "You are connected to a standalone server -- i.e., server name is server1.\n"
            display += sp3 + "Script will not delete standalone server.\n"
            display += sp3 + "Other items (if any) in your config will be deleted. \n"
        display += "\n"

        if wsadminServer == "dmgr":

            menuNum = 2
            display += sp1+ str(menuNum) + sp1+ "Delete a server ...\n"
            display += "\n"

            menuNum = 3
            display += sp1+ str(menuNum) + sp1+ "Delete virtual host for a server or cluster ...\n"
            display += "\n"

        menuNum = 4
        display += sp1+ str(menuNum) + sp1+ "Delete datasource(s) for a server or cluster ...\n"
        display += "\n"

        menuNum = 5
        display += sp1+ str(menuNum) + sp1+ "Delete JVM custom property(ies) for a server or cluster ...\n"
        display += "\n"

        menuNum = 6
        display += sp1+ str(menuNum) + sp1+ "Delete web container custom property(ies) for a server or cluster ...\n"
        display += "\n"

        menuNum = 7
        display += sp1+ str(menuNum) + sp1+ "Delete MQ queue connection factory(ies) for a server or cluster ...\n"
        display += "\n"

        menuNum = 8
        display += sp1+ str(menuNum) + sp1+ "Delete MQ queue definition(s) for a server or cluster ...\n"
        display += "\n"

        menuNum = 9
        display += sp1+ str(menuNum) + sp1+ "Delete JMS Activation Spec(s) for a server or cluster ...\n"
        display += "\n"

        menuNum = 10
        display += sp1+ str(menuNum) + sp1+ "Delete shared library(ies) (& classloader(s)) for a server or cluster ...\n"
        display += "\n"

        menuNum = 11
        display += sp1+ str(menuNum) + sp1+ "Delete cell-scoped WebSphere variable(s) ...\n"
        display += "\n"

        menuNum = 12
        display += sp1+ str(menuNum) + sp1+ "Delete node-scoped WebSphere variable(s) ...\n"
        display += "\n"

        menuNum = 13
        display += sp1+ str(menuNum) + sp1+ "Delete cell-scoped JAAS authentication entry(ies) ...\n"
        display += "\n"

        menuNum = 14
        display += sp1+ str(menuNum) + sp1+ "Delete asynch bean work manager(s) for a server or cluster ...\n"
        display += "\n"

        menuNum = 99
        display += sp1+ str(menuNum) + sp1+ "Return to previous menu ...\n"
        display += "\n"

        print display
        menu_response = ""

        try:
            menu_response = raw_input(standard_prompt)
        except EOFError:
            print "\nExiting."
            sys.exit(0)
        if menu_response == "":
            print "Menu response was: empty string"
            menu_response = raw_input("\nReturn to previous menu? (y | n): ")
            if menu_response.lower() == "n":
                print "Response was: " + str(menu_response)
                menuToDeleteThings(config_file)
                return
            else:
                if menu_response == "":
                    print "Response was: empty string"
                else:
                    print "Response was: " + str(menu_response)
                print "\nReturning to previous menu."
                menuAddOrReplace(config_file)
                return

        danger_response = ""
        warning_msg = ""
        try:
            warning_msg += "\nThis option will BLOW AWAY existing items in your WAS cell\n"
            warning_msg += "... but ONLY items that are in this config file. \n"
            warning_msg += "\nEnter 'y' to continue, any other key to abort. "
            danger_response = raw_input(warning_msg)
        except EOFError:
            print "\nExiting."
            sys.exit(0)
        print "Warning response was: " + str(danger_response)
        if danger_response == "":
            print "Response was: empty string"
            menuToDeleteThings(config_file)
            return
        elif danger_response.lower() == 'y':
            print "Response was: " + str(danger_response)
            pass
        else:
            print "Response was: " + str(danger_response)
            menuToDeleteThings(config_file)
            return

        if menu_response.isnumeric():

            if menu_response == '1':
                try:
                    print "\nDelete all items in your WAS cell that are in this config file."
                    print "\n" + div1
                    print "Removing all items that are in this config file ..."
                    print div1 + "\n"
                    if wsadminServer == "server1":
                        print "You are connected to a standalone server -- i.e., server name is server1."
                        print "Script will not remove standalone server."
                        print "Continuing."
                    else:
                        Destroyer.blowAwayAllClustersServers(cfgDict)
                        Destroyer.blowAwayAllVirtualHosts(cfgDict)
                    Destroyer.blowAwayAllJaas(cfgDict)
                    Destroyer.blowAwayAllCellScopedWebsphereVariable(cellName, cfgDict)
                    Destroyer.zeroOutAllNodeScopedWebsphereVariable(cfgDict)
                    Destroyer.blowAwayAllRepDomains(cfgDict)
                    readyDeleteMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToDeleteThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '2':
                try:
                    print "\Delete a server ...\n"
                    if wsadminServer == "server1":
                        print "You are connected to a standalone server -- i.e., server name is server1."
                        print "\nScript will not delete standalone server."
                    else:
                        baseServerName = whatServerMenu(config_file)
                        if baseServerName is not None:
                            print "\n" + div1
                            print "Removing cluster and/or server for: " + baseServerName + " ..."
                            print div1 + "\n"
                            getServerClusterConfigInfoDetail(baseServerName)
                            if serverIsClusteredInConfigFile == "true":
                                Destroyer.blowAwayCluster(clusterNameInConfigFile)
                            elif serverIsClusteredInConfigFile == "false":
                                Destroyer.blowAwayServer(nodeNameInConfigFile, baseServerName + '1')
                        else:
                            print "\nNo server chosen."
                            menuToDeleteThings(config_file)
                    readyDeleteMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToDeleteThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '3':
                try:
                    print "\nDelete virtual host for a server or cluster ...\n"
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\n" + div1
                        print "Removing virtual host for: " + baseServerName + " ..."
                    else:
                        print "\nNo server chosen."
                        menuToDeleteThings(config_file)
                    readyDeleteMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToDeleteThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '4':
                try:
                    print "\nDelete datasource(s) for a server or cluster ...\n"
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\n" + div1
                        print "Removing a atasource(s) for: " + baseServerName + " ..."
                        print div1 + "\n"
                        try:
                            serversdataSourceInfoDict = wini.getPrefixedClauses(cfgDict,'dataSource:' + baseServerName + ':')
                            if serversdataSourceInfoDict:
                                for serversdataSourceInfoKey in serversdataSourceInfoDict.keys():
                                    sdi = serversdataSourceInfoDict[serversdataSourceInfoKey]
                                    dataSourceName = sdi['dataSourceName'].strip()
                                    dbType = sdi['db2OrOracle'].strip()
                                    for serverInfoKey in serverInfoDict.keys():
                                        si = serverInfoDict[serverInfoKey]
                                        if si['baseServerName'] == baseServerName:
                                            isClustered = si['isClustered'].strip()
                                            if isClustered == 'true':
                                                clusterName = si['clusterName']
                                                Destroyer.blowAwayOneClustersDatasource(clusterName, dbType, dataSourceName)
                                            else:
                                                nodeList = si['nodeList'].split()
                                                nodeNumber = 0
                                                for nodeName in nodeList:
                                                    nodeNumber += 1
                                                    #slap a number on the end of baseServerName whether it is clustered (on > 1 node) or not (1 node)
                                                    serverName = baseServerName + str(nodeNumber)
                                                    print "\nRemoving datasource: " + dataSourceName + " for server: " + serverName
                                                    Destroyer.blowAwayOneServersDatasource(cellName, nodeName, serverName, dbType, dataSourceName)
                        except:
                            print "\n\nException in menuToDeleteThings() when removing datasources()"
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            readyDeleteMenu(config_file, menu_response)
                    else:
                        print "\nNo server chosen."
                        menuToDeleteThings(config_file)
                    readyDeleteMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToDeleteThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

            elif menu_response == '5':
                try:
                    print "\nDelete JVM custom property(ies) for a server or cluster ...\n"
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\n" + div1
                        print "Removing JVM custom props for server: " + baseServerName + " ..."
                        print div1 + "\n"
                        try:
                            jvmCustomPropInfoDict = wini.getPrefixedClauses(cfgDict,'jvmCustomProperty:' + baseServerName + ':')
                            if jvmCustomPropInfoDict:
                                for jvmCustomPropInfoKey in jvmCustomPropInfoDict.keys():
                                    jcpi = jvmCustomPropInfoDict[jvmCustomPropInfoKey]
                                    jvmCustomPropName = jcpi['propertyName'].strip()
                                    for serverInfoKey in serverInfoDict.keys():
                                        si = serverInfoDict[serverInfoKey]
                                        if si['baseServerName'] == baseServerName:
                                            nodeList = si['nodeList'].split()
                                            nodeNumber = 0
                                            for nodeName in nodeList:
                                                nodeNumber += 1
                                                #slap a number on the end of baseServerName whether it is clustered (on > 1 node) or not (1 node)
                                                serverName = baseServerName + str(nodeNumber)
                                                print "\nRemoving JVM custom prop: " + jvmCustomPropName + " for server: " + serverName
                                                Destroyer.blowAwayOneServersJvmCustomProperty(nodeName, serverName, jvmCustomPropName)
                        except:
                            print "\n\nException in menuToDeleteThings() when removing JVM custom prop(s)"
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            readyDeleteMenu(config_file, menu_response)
                    else:
                        print "\nNo server chosen."
                        menuToDeleteThings(config_file)
                    readyDeleteMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToDeleteThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyDeleteMenu(config_file, menu_response)

            elif menu_response == '6':
                try:
                    print "\nDelete web container custom property(ies) for a server or cluster ...\n"
                    print "This feature is not implemented. Only option at the moment is to recreate the server."
                    readyDeleteMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToDeleteThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyDeleteMenu(config_file, menu_response)

            elif menu_response == '7':
                try:
                    print "\nDelete MQ queue connection factory(ies) for a server or cluster ...\n"
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\n" + div1
                        print "Removing MQ queue connection factory(ies) for server: " + baseServerName + " ..."
                        print div1 + "\n"
                        try:
                            queueConnectionFactoryInfoDict = wini.getPrefixedClauses(cfgDict,'queueConnectionFactory:' + baseServerName + ':')
                            if queueConnectionFactoryInfoDict:
                                for queueConnectionFactoryInfoKey in queueConnectionFactoryInfoDict.keys():
                                    qcfi = queueConnectionFactoryInfoDict[queueConnectionFactoryInfoKey]
                                    factoryName = qcfi['name'].strip()
                                    for serverInfoKey in serverInfoDict.keys():
                                        si = serverInfoDict[serverInfoKey]
                                        if si['baseServerName'] == baseServerName:
                                            isClustered = si['isClustered'].strip()
                                            if isClustered == 'true':
                                                clusterName = si['clusterName']
                                                Destroyer.blowAwayOneClustersQueueConnectionFactory(cellName, clusterName, factoryName)
                                            else:
                                                nodeList = si['nodeList'].split()
                                                nodeNumber = 0
                                                for nodeName in nodeList:
                                                    nodeNumber += 1
                                                    #slap a number on the end of baseServerName whether it is clustered (on > 1 node) or not (1 node)
                                                    serverName = baseServerName + str(nodeNumber)
                                                    print "\nRemoving MQ queue connection factory: " + factoryName + " for server: " + serverName
                                                    Destroyer.blowAwayOneServersQueueConnectionFactory(cellName, nodeName, serverName, factoryName)
                        except:
                            print "\n\nException in menuToDeleteThings() when removing MQ queue connection factory(ies)"
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            readyDeleteMenu(config_file, menu_response)
                    else:
                        print "\nNo server chosen."
                        menuToDeleteThings(config_file)
                    readyDeleteMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToDeleteThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyDeleteMenu(config_file, menu_response)

            elif menu_response == '8':
                try:
                    print "\nDelete MQ queue definition(s) for a server or cluster ...\n"
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\n" + div1
                        print "Removing queue(s) for server: " + baseServerName + " ..."
                        print div1 + "\n"
                        try:
                            queueInfoDict = wini.getPrefixedClauses(cfgDict,'queue:' + baseServerName + ':')
                            if queueInfoDict:
                                for queueInfoKey in queueInfoDict.keys():
                                    qi = queueInfoDict[queueInfoKey]
                                    queueName = qi['name'].strip()
                                    for serverInfoKey in serverInfoDict.keys():
                                        si = serverInfoDict[serverInfoKey]
                                        if si['baseServerName'] == baseServerName:
                                            isClustered = si['isClustered'].strip()
                                            if isClustered == 'true':
                                                clusterName = si['clusterName']
                                                Destroyer.blowAwayOneClustersQueue(cellName, clusterName, queueName)
                                            else:
                                                nodeList = si['nodeList'].split()
                                                nodeNumber = 0
                                                for nodeName in nodeList:
                                                    nodeNumber += 1
                                                    #slap a number on the end of baseServerName whether it is clustered (on > 1 node) or not (1 node)
                                                    serverName = baseServerName + str(nodeNumber)
                                                    print "\nRemoving queue: " + queueName + " for server: " + serverName
                                                    Destroyer.blowAwayOneServersQueue(cellName, nodeName, serverName, queueName)

                        except:
                            print "\n\nException in menuToDeleteThings() when removing queue(s)"
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            readyDeleteMenu(config_file, menu_response)
                    else:
                        print "\nNo server chosen."
                        menuToDeleteThings(config_file)
                    readyDeleteMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToDeleteThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyDeleteMenu(config_file, menu_response)

            elif menu_response == '9':
                try:
                    print "\nDelete JMS Activation Spec(s) for a server or cluster ...\n"
                    print "This feature is not implemented. Only option at the moment is to recreate the server."
                    readyDeleteMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToDeleteThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyDeleteMenu(config_file, menu_response)

            elif menu_response == '10':
                try:
                    print "\nDelete shared library(ies) (& classloader(s)) for a server or cluster ...\n"
                    print "This feature is not implemented. Only option at the moment is to recreate the server."
                    readyDeleteMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToDeleteThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyDeleteMenu(config_file, menu_response)

            elif menu_response == '11':
                try:
                    print "\nDelete cell-scoped WebSphere variable(s) ...\n"
                    print "\n" + div1
                    print "Removing WAS vars ..."
                    print div1 + "\n"
                    Destroyer.blowAwayAllCellScopedWebsphereVariable(cellName, cfgDict)
                    readyDeleteMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToDeleteThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyDeleteMenu(config_file, menu_response)

            elif menu_response == '12':
                try:
                    print "\nDelete node-scoped WebSphere variable(s) ...\n"
                    print "\n" + div1
                    print "Removing node-scoped WAS vars ..."
                    print div1 + "\n"
                    Destroyer.zeroOutAllNodeScopedWebsphereVariable(cfgDict)
                    readyDeleteMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToDeleteThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyDeleteMenu(config_file, menu_response)

            elif menu_response == '13':
                try:
                    print "\nDelete cell-scoped JAAS authentication entry(ies) ...\n"
                    print "\n" + div1
                    print "Removing JAAS entry(ies) ..."
                    print div1 + "\n"
                    Destroyer.blowAwayAllJaas(cfgDict)
                    readyDeleteMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToDeleteThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyDeleteMenu(config_file, menu_response)

            elif menu_response == '14':
                try:
                    print "\nDelete asynch bean work manager definitions for a server or cluster ..."
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        try:
                            serversWorkManagerInfoDict = wini.getPrefixedClauses(cfgDict,'asynchBeanWorkManager:' + baseServerName + ':')
                            if serversWorkManagerInfoDict:
                                print "\n" + div1
                                print "Removing all NON-DEFAULT asynch bean work manager definition(s) for: " + baseServerName + " ..."
                                print div1 + "\n"

                                for serversWorkManagerInfoKey in serversWorkManagerInfoDict.keys():
                                    swm = serversWorkManagerInfoDict[serversWorkManagerInfoKey]
                                    jndiName = swm['jndiName'].strip()
                                    workManagerName = swm['name'].strip()
                                    if jndiName == 'wm/default':
                                        print "\n\n Warning:"
                                        print "     Cannot remove the default work manager (jndi name: " + jndiName + "). Only option at the moment is to rebuild the server, then modify work manager(s).\n"
                                        readyDeleteMenu(config_file, menu_response)
                                    else:
                                        for serverInfoKey in serverInfoDict.keys():
                                            si = serverInfoDict[serverInfoKey]
                                            if si['baseServerName'] == baseServerName:
                                                isClustered = si['isClustered'].strip()
                                                if isClustered == 'true':
                                                    clusterName = si['clusterName']
                                                    print "\nRemoving work manager: " + workManagerName + " for cluster: " + clusterName
                                                    Destroyer.blowAwayOneClustersAsynchBeanWorkManager(clusterName, workManagerName)
                                                else:
                                                    nodeList = si['nodeList'].split()
                                                    nodeNumber = 0
                                                    for nodeName in nodeList:
                                                        nodeNumber += 1
                                                        #slap a number on the end of baseServerName whether it is clustered (on > 1 node) or not (1 node)
                                                        serverName = baseServerName + str(nodeNumber)
                                                        print "\nRemoving work manager: " + workManagerName + " for server: " + serverName
                                                        Destroyer.blowAwayOneServersAsynchBeanWorkManager(nodeName, serverName, workManagerName)
                        except:
                            print "\n\nException in menuToDeleteThings() when removing work manager(s)"
                            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                            readyDeleteMenu(config_file, menu_response)
                    else:
                        print "\nNo server chosen."
                        menuToDeleteThings(config_file)
                    readyDeleteMenu(config_file, menu_response)
                except:
                    print "\n\nException in menuToDeleteThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    readyDeleteMenu(config_file, menu_response)

            elif menu_response == '99':
                try:
                    menuAddOrReplace(config_file)
                except:
                    print "\n\nException in menuToDeleteThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    menuAddOrReplace(config_file)
            else:
                print "Response was not recognized."
                menuToDeleteThings(config_file)
        else:
            print "Response was non-numeric."
            print "Returning to previous menu."
            menuAddOrReplace(config_file)
    except SystemExit:
        pass
    except:
        print "\n\nException in menuToDeleteThings()\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def readyDeleteMenu(config_file, menu_response):
    """ Print out the menu option that was just done, and confirm that
    it completed, to make it show in case log of user session is desired:
    the Delete Menu """
    print "\nEnd of Delete Menu Option " + menu_response
    try:
        what_response = raw_input("\nPress any key to continue.  ")
    except EOFError:
        print "\nExiting."
        sys.exit(0)
    # go back to page one instead of re-displaying Delete menu,
    #  to help avoid tragic mistakes, and to avoid having the "are you sure"
    #  confirmation triggered inappropriately, e.g., for "return to previous"
    reDisplaypageOne(config_file)


def menuToModifyThings(config_file):
    """ The "Modify" Menu. Doesn't support too much because generally we
    just delete and replace something to change it. """
    try:
        display = "\n\n"
        display += div1 + "\n"
        display += "Options for MODIFYING EXISTING things in your WAS cell \n"
        display += div1 + "\n\n"   
        
        display += sp1 + "Config file: " + config_file + "\n"
        display += "\n"
        
        display = "\n\n"
        display += div1 + "\n"
        display += "Please choose action to perform \n"
        display += div1 + "\n"   
        
        menuNum = 7
        display += sp1+ str(menuNum) + sp1+ "Modify one EXISTING queue connection factory ...\n"
        display += sp1+ ' ' + sp1+ "(currently only pool settings can be modified)\n"
        display += "\n"
        
        menuNum = 14
        display += sp1+ str(menuNum) + sp1+ "Modify EXISTING asynch bean work manager(s) for a server ...\n"
        display += "\n"
        
        menuNum = 20
        display += sp1+ str(menuNum) + sp1+ "Modify HTTP queue tuning params for a server ...\n"
        display += "\n"
        

        menuNum = 99
        display += sp1+ str(menuNum) + sp1+ "Return to previous menu ...\n"
        display += "\n"

        print display
        menu_response = ""
        try:
            menu_response = raw_input(standard_prompt)
        except EOFError:
            print "Exiting."
            sys.exit(0)
        print "Menu response was: " + str(menu_response)

        if menu_response.isnumeric():
            if menu_response == '7':
                try:
                    print "\nModify a server or cluster's EXISTING queue connection factory connection and/or session pools ..."
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\nModifying one EXISTING queue connection factory for: " + baseServerName + " ."
                        print "(currently only pool settings can be modified)"
                        factoryJNDIName = whatQueueConnectionFactoryMenu(config_file, baseServerName)
                        if factoryJNDIName is not None:
                            for queueConnectionFactoryKey in queueConnectionFactoryDict.keys():
                                qcf = queueConnectionFactoryDict[queueConnectionFactoryKey]
                                jndiName = qcf['jndiName'].strip()
                                if jndiName == factoryJNDIName:
                                    factoryName = qcf['name'].strip()
                                    Configurator.modifyOneQCFPool(cfgDict, baseServerName, factoryName)
                                    readyModifyMenu(menu_response)
                        else:
                            print "\n No qcf chosen."
                    else:
                        print "\n No server chosen."
                        menuToModifyThings(config_file)
                except:
                    print "\n\nException in menuToModifyThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            if menu_response == '14':
                try:
                    print "\nModify a server or cluster's EXISTING asynch bean work manager(s) ..."
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\nModifying EXISTING asynch bean work manager(s) for: " + baseServerName + " ."
                        Configurator.modifyAsynchBeanDefaultWorkManager(cfgDict, baseServerName)
                        readyModifyMenu(menu_response)
                    else:
                        print "\nNo server chosen."
                        menuToModifyThings(config_file)
                except:
                    print "\n\nException in menuToModifyThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            if menu_response == '20':
                try:
                    print "\nModify HTTP queue tuning params for a server ..."
                    baseServerName = whatServerMenu(config_file)
                    if baseServerName is not None:
                        print "\nModifying HTTP queue tuning params for: " + baseServerName + " ."
                        Configurator.modifyHttpQueueTuningParams(cfgDict, baseServerName, "WC_defaulthost")
                        Configurator.modifyHttpQueueTuningParams(cfgDict, baseServerName, "WC_defaulthost_secure")
                        readyModifyMenu(menu_response)
                    else:
                        print "\nNo server chosen."
                        menuToModifyThings(config_file)
                except:
                    print "\n\nException in menuToModifyThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
                    
            elif menu_response == '99':
                try:
                    menuAddOrReplace(config_file)
                except:
                    print "\n\nException in menuToModifyThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
            else:
                print "Response was not recognized."
                menuToModifyThings(config_file)
        else:
            print "Response was non-numeric."
            print "Returning to previous menu."
            menuAddOrReplace(config_file)
        
    except SystemExit:
        pass
    except:
        print "\n\nException in menuToModifyThings()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def readyModifyMenu(menu_response):
    """ Print out the menu option that was just done, and confirm that
    it completed, to make it show in case log of user session is
    desired: the Modify Menu """
    print "\nEnd of Modify Menu Option " + menu_response  
    try:
        what_response = raw_input("\nPress any key to continue.  ")                    
    except EOFError:
        print "\nExiting."
        sys.exit(0)
    #getWASinfo()    
    menuToModifyThings(config_file)

        
def menuToSwitchConfigFiles(config_file, keyword=""):
    """ Let user select a different config file without having to start
    a new script session. User can filter on cell or environment nickname. """
    try:
        display = "\n\n"
        display += div1 + "\n"
        display += "Switch to a different config file \n"
        display += div1 + "\n\n"   

        display += sp1 + "Current config filename: " + config_file + "\n"
        display += "\n"
        
        print display
        if keyword == "all":
            pass
        else:
            if WAScellName == "HappyCell":
                keyword = "happy"
            elif WAScellName == "LazyCell":
                keyword = "lazy"
            else:
                keyword = ""
            
        config_file = whatConfigFileMenu(keyword)
        if config_file is not None:
            getConfigInfo(config_file)
            pageOne(config_file)
        
    except SystemExit:
        pass
    except:
        print "\n\nException in menuToSwitchConfigFiles()\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def whatConfigFileMenu(keyword=""):
    """ Part of "menuToSwitchConfigFiles". """
    try:
        isFiltered = "true"
        theChosenConfigFileName = "theChosenConfigFileName not defined yet"
        count = 1
        display = "\n\n"
        display += ""
        display += div1 + "\n"    
        display += sp1 + "Contents of your config file directory: \n"
        display += div1 + "\n"
        
        print display
        display = ""
        configPath = get_config_dir_path()
        if keyword == "all":
            keyword = ""
            isFiltered = "false"
        searchPath = os.path.join(configPath, '*' + keyword + '*')
        dirList = glob.glob(searchPath)
        
        fileListing = []
        for listing in dirList:
            listingPath = os.path.join(configPath, listing)
            if os.path.isfile(listingPath):
                fileListing.append(listing)
                count = count + 1
        count = 1
        for file in fileListing:
            print str(count) + ".  " + file
            count = count + 1
        print ""
        if isFiltered == "true":
            print "List may be filtered based on your cell. Enter 'A' to see list of ALL config files.\n"
        else:
            print "List is unfiltered. Enter 'F' to attempt to narrow list config files based on your cell.\n"
        
        try:
            what_config_file_response = raw_input("\nPlease enter number of config file to switch to:  ")                    
        except EOFError:
            print "\nExiting."
            sys.exit(0)
        print "Menu response was: " + str(what_config_file_response)                
        if what_config_file_response is None:
            print "\nExiting."
            menuAddOrReplace
        if what_config_file_response.lower() == 'a':
            isFiltered = "false"
            keyword = "all"
            menuToSwitchConfigFiles(keyword)
        if what_config_file_response.lower() == 'f':
            isFiltered = "true"
            menuToSwitchConfigFiles(config_file)
            
        if what_config_file_response.isnumeric():
            what_config_file_response = int(what_config_file_response)
            try:
                theChosenConfigFileName = fileListing[what_config_file_response - 1]
            except IndexError:
                print "\nPlease enter a number that corresponds to a config file."
                menuToSwitchConfigFiles(config_file)
            except:
                print "\n\nException trying to look up file in whatConfigFileMenu()"
                sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                sys.exit(1)
            
            print "theChosenConfigFileName is: " + theChosenConfigFileName
            return theChosenConfigFileName
    except SystemExit:
        pass
    except:
        print "\n\nException in whatConfigFileMenu()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    

def menuToShowMoreDetail(config_file, baseServerName):
    """ Menu to let user choose what kind of extra server detail to
    show. Only choice currently is qcf connection and session pools."""
    try:
        display = "\n\n"
        display += div1 + "\n"
        display += "Show more detail for server: " + baseServerName + "\n"
        display += div1 + "\n\n"  

        display += sp1 + "Config file: " + config_file + "\n"
        display += "\n"
        
        
        print display

        display = "\n\n"
        display += div1 + "\n"
        display += "Please choose what type of item to show more detail for \n"
        display += div1 + "\n"   
        
        menuNum = 1
        display += sp1+ str(menuNum) + sp1+ "Queue connection factory connection and session pools ...\n"
        display += "\n"     

        menuNum = 99
        display += sp1+ str(menuNum) + sp1+ "Return to previous menu ...\n"
        display += "\n"

        print display
        menu_response = ""
        try:
            menu_response = raw_input(standard_prompt)
        except EOFError:
            print "Exiting."
            sys.exit(0)
        print "Menu response was: " + str(menu_response)

        if menu_response.isnumeric():
            if menu_response == '1':
                try:
                    print "\nShow more detail for queue connection factory connection and session pools ..."
                    queueConnectionFactory = whatQueueConnectionFactoryMenu(config_file, baseServerName)
                    if queueConnectionFactory is not None:
                        print "\nShowing more detail for: " + queueConnectionFactory + " ..."
                    else:
                        print "\nNo queue connection factory chosen."
                        menuToShowMoreDetail(config_file, baseServerName)
                except:
                    print "\n\nException in menuToModifyThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

                    
            elif menu_response == '99':
                try:
                    menuAddOrReplace(config_file)
                except:
                    print "\n\nException in menuToModifyThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
            else:
                print "Response was not recognized."
                menuToModifyThings(config_file)
        else:
            print "Response was non-numeric."
            print "Returning to previous menu."
            menuAddOrReplace(config_file)
        
    except SystemExit:
        pass
    except:
        print "\n\nException in menuToShowMoreDetail()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def whatQueueConnectionFactoryMenu(config_file, baseServerName):
    """ Menu to let user drill down to the specific qcf they want to see
    pool config for."""
    count = 1
    foundInWAS = "false"
    display = ""
    factoryName = "factoryName not defined yet"
    # getServerConfigInfoDetail() & getServerWASinfoDetail() might not have been called yet
    #   if user hasn't viewed server detail yet
    # need to call getServerConfigInfoDetail() to get queueConnectionFactoryDict populated
    getServerConfigInfoDetail(baseServerName)
    # need to call getServerWASinfoDetail() to get WASqueueConnectionFactoryList populated
    getServerWASinfoDetail(baseServerName)
    
    display += sp1 + "Config file: " + config_file + "\n"
    
    if queueConnectionFactoryDict:
        display = "\n\n"
        display += ""
        display += sp1 + "Queue connection factories in your config file for server: " + baseServerName + "\n"
        if len(queueConnectionFactoryDict) != 0:
            for queueConnectionFactoryKey in queueConnectionFactoryDict.keys():
                foundInWAS = "false"
                qcf = queueConnectionFactoryDict[queueConnectionFactoryKey]
                jndiName = qcf['jndiName'].strip()
                if jndiName in WASqueueConnectionFactoryList:
                    foundInWAS = "true"
                if foundInWAS == "true":
                    display += sp2star
                else:
                    display += sp2
                display += str(count) + getSpacer(count) + jndiName + "\n"
                count = count + 1

        else:
            try:
                menu_response = raw_input("\nNo queue connection factories found in your config file. Press any key to continue: ")
            except EOFError:
                print "\nExiting."
                sys.exit(0)
                
            pageOne(config_file)
    else:
        try:
            menu_response = raw_input("\nNo queue connection factories found in your config file. Press any key to continue: ")
        except EOFError:
            print "\nExiting."
            sys.exit(0)
        pageOne(config_file)
        
    display += "\n"
    display += "* means that the item in your config file is found in your WAS cell."
    print display        
    try:
        what_qcf_response = raw_input("\nPlease enter number of queue connection factory:  ")                    
    except EOFError:
        print "\nExiting."
        sys.exit(0)
    print "Menu response was: " + str(what_qcf_response)    
    if what_qcf_response is None:
        print "\nNo response made."
        
    #print "what_qcf_response is: " + what_qcf_response
    if what_qcf_response.isnumeric():
        what_qcf_response = int(what_qcf_response)
        theChosenQCF = queueConnectionFactoryList[what_qcf_response - 1]
        print "Queue connection factory chosen was: " + theChosenQCF
        return theChosenQCF


def menuForCellThings(config_file):
    """ Cell Menu. Lets user choose options that will apply to whole
    WAS cell. Currently, only supports several options for changing pool
    settings for qfcs """
    try:
        display = "\n\n"
        display += div1 + "\n"
        display += "Options that apply to your whole WAS cell \n"
        display += div1 + "\n\n"  

        display += sp1 + "Config file: " + config_file + "\n"
        display += "\n"
        
        
        print display

        display = "\n\n"
        display += div1 + "\n"
        display += "Please choose action to perform \n"
        display += div1 + "\n"   
        
        menuNum = 1
        display += sp1+ str(menuNum) + sp1+ "Compare existing pool settings for all MQ queue connection factories to admin console defaults \n"
        display += "\n"

        menuNum = 2
        display += sp1+ str(menuNum) + sp1+ "Set pool settings for all MQ queue connection factories to admin console DEFAULTS ... \n"
        display += "\n"
        
        menuNum = 3
        display += sp1+ str(menuNum) + sp1+ "Apply pool settings for all MQ queue connection factories using non-DEFAULT values from config file ... \n"
        display += "\n"
        
        menuNum = 99
        display += sp1+ str(menuNum) + sp1+ "Return to previous menu ...\n"
        display += "\n"

        print display
        menu_response = ""
        try:
            menu_response = raw_input(standard_prompt)
        except EOFError:
            print "Exiting."
            sys.exit(0)
        print "Menu response was: " + str(menu_response)

        if menu_response.isnumeric():
            if menu_response == '1':
                try:
                    PoolDefaultsFixerUpper.list()
                    readyCellMenu(menu_response)
                except:
                    print "\n\nException in menuForCellThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
                    
            elif menu_response == '2':
                try:
                    callQCFPoolDefaultsFixerUpper(menu_response)
                    readyCellMenu(menu_response)
                except:
                    print "\n\nException in menuForCellThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)

            elif menu_response == '3':
                try:
                    callModifyAllQCFPoolPropsInCell(config_file, menu_response)
                    readyCellMenu(menu_response)
                except:
                    print "\n\nException in menuForCellThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
                    
            elif menu_response == '99':
                try:
                    pageOne(config_file)
                except:
                    print "\n\nException in menuForCellThings() on menu response: " + menu_response + "\n\n"
                    sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                    sys.exit(1)
            else:
                print "Response was not recognized."
                menuForCellThings(config_file)
        else:
            print "Response was non-numeric."
            print "Returning to previous menu."
            pageOne(config_file)
        
    except SystemExit:
        pass
    except:
        print "\n\nException in menuForCellThings()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def readyCellMenu(menu_response):
    """ Print out the menu option that was just done, and confirm that
    it completed, to make it show in case log of user session is
    desired: the Cell Menu """
    print "\nEnd of menu for cell things option " + menu_response  
    try:
        what_response = raw_input("\nPress any key to continue.  ")                    
    except EOFError:
        print "\nExiting."
        sys.exit(0)
    #getWASinfo()    
    menuForCellThings(config_file)


def callQCFPoolDefaultsFixerUpper(menu_response):
    """ Let user fix up pool defaults for queue connection factories to
    match admin console defaults. Displays warning message and requires
    user to confirm before continuing."""
    danger_response = ""  
    warning_msg = ""
    try:
        warning_msg += "\nAction will set all values for connection and session pools for ALL qcf's to ADMIN CONSOLE DEFAULTS. "
        warning_msg += "\nWarning: this action may overwrite existing non-default pool settings in your cell. "        
        warning_msg += "\nEnter 'y' to continue, any other key to abort. "
        danger_response = raw_input(warning_msg)
    except EOFError:
        print "\nExiting."
        sys.exit(0)
    print "Warning response was: " + str(danger_response) 
    if danger_response == "":
        print "\nExiting."
        sys.exit(0)
    elif danger_response.lower() == 'y':
        PoolDefaultsFixerUpper.fixUp()
        readyCellMenu(menu_response)
    else:
        print "Response was not recognized."
        print "Returning to previous menu."
        menuForCellThings(config_file)
            

def callModifyAllQCFPoolPropsInCell(config_file, menu_response):
    """ Let user change pool settings for queue connection factories as
    specified in config file. Displays warning message and requires user to confirm before continuing."""
    danger_response = ""  
    warning_msg = ""
    display = ""
    display += sp1 + "Config file: " + config_file + "\n"
    print display
    try:
        warning_msg += "\nAction will set all values for connection and session pools for ALL qcf's as specified in file. "
        warning_msg += "\nWarning: this action may overwrite existing non-default pool settings in your cell. "        
        warning_msg += "\nEnter 'y' to continue, any other key to abort. "
        danger_response = raw_input(warning_msg)
    except EOFError:
        print "\nExiting."
        sys.exit(0)
    print "Warning response was: " + str(danger_response) 
    if danger_response == "":
        print "\nExiting."
        sys.exit(0)
    elif danger_response.lower() == 'y':
        Configurator.modifyAllQCFPoolPropsInCell(cfgDict)
        readyCellMenu(menu_response)
    else:
        print "Response was not recognized."
        print "Returning to previous menu."
        menuForCellThings(config_file)


def get_config_dir_path():
    """ Return the path we expect the config files to be in. We expect
    the config_files dir to be in a dir called 'config_files' which is
    a sister dir of pwd. Edit this method to change the name or specify
    a different location."""
    config_dir_name = 'config_files'
    current_working_dir = os.getcwd()
    parent_dir = os.path.split(current_working_dir)[0]
    config_dir = os.path.join(parent_dir, config_dir_name)
    return config_dir

#--------------------------------------------------------------------
# "main"
# when this module is being run as top-level, call the appropriate function
#--------------------------------------------------------------------
if __name__=="__main__":

    usage = "Usage: cd into dir containing the scripts, then execute \n"
    usage += " <wsadmin command> -f <this py script> <config file name> \n"
    usage = usage + " . . . and must have modified soap.client.props of target wsadmin profile if security is enabled\n\n\n"

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
        # I can't find any way to get wsadmin to display name & path
        #   of currently running script
        # and it's way too awkward to make scripts dir be an arg
        # so we require script must be run from scripts dir
        # e.g., home/hazel/websphere_v9/was_configurator/scripts
        pwd = os.getcwd()
        scripts_dir = pwd
        sys.path.append(scripts_dir)

        config_dir = get_config_dir_path()
        config_filename = sys.argv[0]
        config_file = os.path.join(config_dir, config_filename)

        # we expect these modules to be in the directory we just appended
        #   to search path
        import wini
        import ConfigFile
        import Utilities

        start(config_file)
    else:
        print usage
        sys.exit("wrong number of args")
