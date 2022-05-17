###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
# Notes
#   This Jython script is meant to be called from another script (e.g.,, imported into it)
# It contains mostly just method definitions. The methods are grouped in this file
#  instead of in the scripts relating to the settings for jvm, datasources, etc. because these methods
#  generally have more in common with each other than with creation/modification methods.
# This script includes the following procedures:
#       thingoExists
#       cellExists
#       nodeExists
#       virtualHostExists
#       clusterExists
#       serverExists
#       jvmCustomPropExists
#		webContainerCustomPropExists
#       tcpTransportChannelCustomPropExists
#       jaasAliasExists
#       cellScopedVariableExists
#       nodeScopedVariableExists
#       clusterScopedJdbcProviderExists
#       serverScopedJdbcProviderExists
#       clusterScopedDataSourceExists
#       clusterScopedDataSourceCustomPropExists
#       clusterScopedDataSourceByJndiExists
#       serverScopedDataSourceExists
#       serverScopedDataSourceCustomPropExists
#       serverScopedDataSourceByJndiExists
#       datasourceByServerOrClusterNameSubstringExists
#       serverScopedThingoExists
#       clusterScopedThingoExists
#       serverScopedQueueConnectionFactoryExists
#       clusterScopedQueueConnectionFactoryExists
#       serverScopedQueueExists
#       clusterScopedQueueExists
#       serverScopedListenerPortExists
#       replicationDomainExists
#       serverScopedJMSActivationSpecExists
#       clusterScopedJMSActivationSpecExists
#       serverScopedClassLoaderExists
#       serverScopedAsynchBeanWorkManagerExists
#       clusterScopedAsynchBeanWorkManagerExists
#		stringNameSpaceBindingExists


import sys

# wsadmin objects
import AdminConfig
import AdminTask
import AdminControl

import Utilities


def thingoExists(path):
    try:
        id = AdminConfig.getid(path)
        if (len(id) == 0):
            return
        else:
            return id
    except:
        print "\n\nException in thingoExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
def cellExists(name):
    try:
        path = '/Cell:'+name+'/'
        return thingoExists(path)
    except:
        print "\n\nException in cellExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def nodeExists(name):      
    try:        
        path='/Node:'+name+'/'
        return thingoExists(path)
    except:
        print "\n\nException in nodeExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def virtualHostExists(name):
    try:        
        path='/VirtualHost:'+name+'/'
        return thingoExists(path)
    except:
        print "\n\nException in virtualHostExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def clusterExists(clusterName):
    try:        
        path="/ServerCluster:" +clusterName+"/"
        return thingoExists(path)
    except:
        print "\n\nException in clusterExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def serverExists(nodeName, serverName):
    try:        
        path='/Node:'+nodeName+'/Server:'+serverName+'/'
        return thingoExists(path)
    except:
        print "\n\nException in serverExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def jvmCustomPropExists(nodeName, serverName, jvmCustomPropName):
    try:        
        serverId=AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
        jvmId = AdminConfig.list('JavaVirtualMachine', serverId)
        #print 'jvmId is ' + jvmId
        #print AdminConfig.showAttribute(jvmId, 'systemProperties')
        propertyListString = AdminConfig.showAttribute(jvmId, 'systemProperties')
        propertyList = Utilities.convertToList(propertyListString)
        #print propertyList
        for propertyId in propertyList:
            if (AdminConfig.showAttribute(propertyId, 'name') == jvmCustomPropName):
                return propertyId
    except:
        print "\n\nException in jvmCustomPropExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def webContainerCustomPropExists(nodeName, serverName, webContainerCustomPropName):
    try:        
        serverId=AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
        #print 'serverId is: ' + serverId
        webContainerId = AdminConfig.list('WebContainer', serverId)
        #print 'webContainerId is ' + webContainerId
        propertyListString = AdminConfig.showAttribute(webContainerId, 'properties')
        #print 'propertyListString is: ' + propertyListString
        propertyList = propertyList = Utilities.convertToList(propertyListString)
        #print "propertyList is: "
        #print propertyList
        for propertyId in propertyList:
            if (AdminConfig.showAttribute(propertyId, 'name') == webContainerCustomPropName):
                return propertyId
    except:
        print "\n\nException in webContainerCustomPropExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def tcpTransportChannelCustomPropExists(nodeName, serverName, channelName, propertyName):
    try:        
        serverId=AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
        #print 'serverId is: ' + serverId
        transportChannelIdList = AdminConfig.list('TCPInboundChannel', serverId).splitlines()
        for transportChannelId in transportChannelIdList:
            name = AdminConfig.showAttribute(transportChannelId, 'name')
            if (name == channelName):
            #if (name == 'TCP_2'):
                #print 'transportChannelId is ' + transportChannelId
                propertyListString = AdminConfig.showAttribute(transportChannelId, 'properties')
                #print 'propertyListString is: ' + propertyListString
                propertyList = Utilities.convertToList(propertyListString)
                #print "propertyList is: "
                #print propertyList
                for propertyId in propertyList:
                    if (AdminConfig.showAttribute(propertyId, 'name') == propertyName):
                        return propertyId
    except:
        print "\n\nException in tcpTransportChannelCustomPropExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
def jaasAliasExists(aliasName):
    try:
        # get node name of process wsadmin is connected to, e.g., dmgr or server1
        thisNodeName = AdminControl.getNode()
        stupidPrefix = thisNodeName + "/"
        for entry in AdminConfig.list("JAASAuthData").splitlines():
            if stupidPrefix + aliasName.strip() == AdminConfig.showAttribute(entry, "alias"):
                return entry
        return
    except:
        print "\n\nException in jaasAliasExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def cellScopedVariableExists(cellName, variableName):
    try:
        path="/Cell:" + cellName +  "/VariableMap:/"
        variableMapId = thingoExists(path)
        if variableMapId:
            variableListString = AdminConfig.showAttribute(variableMapId, 'entries')
            variableList = Utilities.convertToList(variableListString)
            #print variableList
            for variableId in variableList:
                if (AdminConfig.showAttribute(variableId, 'symbolicName') == variableName):
                    return variableId
    except:
        print "\n\nException in cellScopedVariableExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def nodeScopedVariableExists(cellName, nodeName, variableName):
    try:
        path = "/Cell:" + cellName + "/Node:" + nodeName  + "/VariableMap:/"
        variableMapId = thingoExists(path)
        if variableMapId:
            variableListString = AdminConfig.showAttribute(variableMapId, 'entries')
            variableList = Utilities.convertToList(variableListString)
            #print variableList
            for variableId in variableList:
                if (AdminConfig.showAttribute(variableId, 'symbolicName') == variableName):
                    return variableId
    except:
        print "\n\nException in nodeScopedVariableExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
		
def clusterScopedJdbcProviderExists(clusterName, dbType):
    try:
        if clusterExists(clusterName):
			if (dbType.lower() == "db2"):
				jdbcProviderName='DB2 Universal JDBC Driver Provider (XA)'
			elif (dbType.lower() == "oracle"):
				#for some reason oracle provider template name lacks "Provider" at end, but I have added it
				jdbcProviderName='Oracle JDBC Driver Provider'
			elif (dbType.lower() == "sqlserver"):
				#for some reason sql server provider template name lacks "Provider" at end, but I have added it
				jdbcProviderName='Microsoft SQL Server JDBC Driver Provider (XA)'
			elif (dbType.lower() == 'mysql'):
				#this is from user-defined template
				jdbcProviderName='MySql JDBC Driver Provider'
			else:
				print 'jdbc provider type must be "db2", "mysql", "sqlserver" or "oracle" (caps insensitive)'
				sys.exit(1)
			serverPath='/ServerCluster:'+clusterName+'/'
			path=serverPath + 'JDBCProvider:'+jdbcProviderName+'/'
			return thingoExists(path)
        else:
            print "cluster not found: " + clusterName
            sys.exit(1)
    except:
        print "\n\nException in clusterScopedJdbcProviderExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
		
def serverScopedJdbcProviderExists(cellName, nodeName, serverName, dbType):
    try:
        if nodeExists(nodeName):
            if serverExists(nodeName, serverName):
                if (dbType.lower() == "db2"):
                    jdbcProviderName='DB2 Universal JDBC Driver Provider (XA)'
                elif (dbType.lower() == "oracle"):
                    #for some reason oracle provider template name lacks "Provider" at end, but I have added it
                    jdbcProviderName='Oracle JDBC Driver Provider'
                elif (dbType.lower() == "sqlserver"):
                    #for some reason sql server provider template name lacks "Provider" at end, but I have added it
                    jdbcProviderName='Microsoft SQL Server JDBC Driver Provider (XA)'
                elif (dbType.lower() == 'mysql'):
                    #this is from user-defined template
                    jdbcProviderName='MySql JDBC Driver Provider'
                else:
                    print 'jdbc provider type must be "db2", "mysql", "sqlserver" or "oracle" (caps insensitive)'
                    sys.exit(1)
                serverPath='/Cell:'+cellName+'/Node:'+nodeName+'/'+'Server:'+serverName+'/'
                path=serverPath + 'JDBCProvider:'+jdbcProviderName+'/'
                return thingoExists(path)
            else:
                print "server not found: " + serverName
                sys.exit(1)
        else:
            print "node not found: " + nodeName
            sys.exit(1)
    except:
        print "\n\nException in serverScopedJdbcProviderExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def clusterScopedDataSourceExists(clusterName, dbType, dataSourceName):
    try:
        if clusterExists(clusterName):
            if (dbType.lower() == 'db2'):
                jdbcProviderName='DB2 Universal JDBC Driver Provider (XA)'
            elif (dbType.lower() == 'oracle'):
                #for some reason oracle provider template name lacks "Provider" at end, but I have added it
                jdbcProviderName='Oracle JDBC Driver Provider'
            elif (dbType.lower() == "sqlserver"):
                #for some reason sql server provider template name lacks "Provider" at end, but I have added it
                jdbcProviderName='Microsoft SQL Server JDBC Driver Provider (XA)'
            elif (dbType.lower() == 'mysql'):
                #this is from user-defined template
                jdbcProviderName='MySql JDBC Driver Provider'
                
            else:
                print 'clusterScopedDataSourceExists: jdbc provider type must be "db2", "mysql", "sqlserver" or "oracle" (caps insensitive)'
                sys.exit(1)

            serverPath='/ServerCluster:'+clusterName+'/'
            providerPath=serverPath + 'JDBCProvider:'+jdbcProviderName+'/'
            path=providerPath + 'DataSource:' + dataSourceName
            return thingoExists(path)
        else:
            print "clusterScopedDataSourceExists: cluster not found: " + clusterName
            sys.exit(1)
    except:
        print "\n\nException in clusterScopedDataSourceExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
def clusterScopedDataSourceCustomPropExists(clusterName, dbType, dataSourceName, dataSourceCustomPropertyName):
    try:
        if clusterScopedDataSourceExists(clusterName, dbType, dataSourceName):
            if (dbType.lower() == 'db2'):
                jdbcProviderName='DB2 Universal JDBC Driver Provider (XA)'
            elif (dbType.lower() == 'oracle'):
                #for some reason oracle provider template name lacks "Provider" at end, but I have added it
                jdbcProviderName='Oracle JDBC Driver Provider'
            elif (dbType.lower() == 'sqlserver'):
                #for some reason sql server provider template name lacks "Provider" at end, but I have added it
                jdbcProviderName='Microsoft SQL Server JDBC Driver Provider (XA)'
            elif (dbType.lower() == 'mysql'):
                #this is from user-defined template
                jdbcProviderName='MySql JDBC Driver Provider'
            else:
                print 'serverScopedDataSourceExists: jdbc provider type must be "db2", "mysql", "sqlserver" or "oracle" (caps insensitive)'
                sys.exit(1)
            serverPath='/ServerCluster:'+clusterName+'/'
            providerPath=serverPath + 'JDBCProvider:'+jdbcProviderName+'/'
            path=providerPath + 'DataSource:' + dataSourceName
            dataSourceID = thingoExists(path)
            propertySetID = AdminConfig.showAttribute(dataSourceID, 'propertySet')
            propList =  Utilities.convertToList(AdminConfig.showAttribute(propertySetID, 'resourceProperties'))
            for id in propList:
                if AdminConfig.showAttribute(id, 'name') == dataSourceCustomPropertyName:
                    return id
        else:
            print "clusterScopedDataSource not found: " + dataSourceName
            sys.exit(1)
    except:
        print "\n\nException in clusterScopedDataSourceCustomPropExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])        
        
def clusterScopedDataSourceByJndiExists(clusterName, dbType, jndiName):
    try:
        if clusterExists(clusterName):
            if (dbType.lower() == 'db2'):
                jdbcProviderName='DB2 Universal JDBC Driver Provider (XA)'
            elif (dbType.lower() == 'oracle'):
                #for some reason oracle provider template name lacks "Provider" at end, but I have added it
                jdbcProviderName='Oracle JDBC Driver Provider'
            elif (dbType.lower() == "sqlserver"):
                #for some reason sql server provider template name lacks "Provider" at end, but I have added it
                jdbcProviderName='Microsoft SQL Server JDBC Driver Provider (XA)'
            elif (dbType.lower() == 'mysql'):
                #this is from user-defined template
                jdbcProviderName='MySql JDBC Driver Provider'
                
            else:
                print 'clusterScopedDataSourceByIdExists: jdbc provider type must be "db2", "mysql", "sqlserver" or "oracle" (caps insensitive)'
                sys.exit(1)
            dataSourceIdList = AdminTask.listDatasources('[-scope Cluster=' + clusterName + ']').splitlines()  
            for dataSourceId in dataSourceIdList:
                if (AdminConfig.showAttribute(dataSourceId, 'jndiName') == jndiName):
                    return dataSourceId
        else:
            print "clusterScopedDataSourceByJndiExists: cluster not found: " + clusterName
            sys.exit(1)
    except:
        print "\n\nException in clusterScopedDataSourceByJndiExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def serverScopedDataSourceExists(cellName, nodeName, serverName, dbType, dataSourceName):
    try:
        if nodeExists(nodeName):
            if serverExists(nodeName, serverName):
                if (dbType.lower() == 'db2'):
                    jdbcProviderName='DB2 Universal JDBC Driver Provider (XA)'
                elif (dbType.lower() == 'oracle'):
                    #for some reason oracle provider template name lacks "Provider" at end, but I have added it
                    jdbcProviderName='Oracle JDBC Driver Provider'
                elif (dbType.lower() == 'sqlserver'):
                    #for some reason sql server provider template name lacks "Provider" at end, but I have added it
                    jdbcProviderName='Microsoft SQL Server JDBC Driver Provider (XA)'
                elif (dbType.lower() == 'mysql'):
                    #this is from user-defined template
                    jdbcProviderName='MySql JDBC Driver Provider'

                else:
                    print 'serverScopedDataSourceExists: jdbc provider type must be "db2", "mysql", "sqlserver" or "oracle" (caps insensitive)'
                    sys.exit(1)
    
                serverPath='/Cell:'+cellName+'/Node:'+nodeName+'/'+'Server:'+serverName+'/'
                providerPath=serverPath + 'JDBCProvider:'+jdbcProviderName+'/'
                path=providerPath + 'DataSource:' + dataSourceName
                return thingoExists(path)
            else:
                print "serverScopedDataSourceExists: server not found: " + serverName
                sys.exit(1)
        else:
            print "serverScopedDataSourceExists: node not found: " + nodeName
            sys.exit(1)
    except:
        print "\n\nException in serverScopedDataSourceExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def serverScopedDataSourceCustomPropExists(cellName, nodeName, serverName, dbType, dataSourceName, dataSourceCustomPropertyName):
    try:
        if serverScopedDataSourceExists(cellName, nodeName, serverName, dbType, dataSourceName):
            if (dbType.lower() == 'db2'):
                jdbcProviderName='DB2 Universal JDBC Driver Provider (XA)'
            elif (dbType.lower() == 'oracle'):
                #for some reason oracle provider template name lacks "Provider" at end, but I have added it
                jdbcProviderName='Oracle JDBC Driver Provider'
            elif (dbType.lower() == 'sqlserver'):
                #for some reason sql server provider template name lacks "Provider" at end, but I have added it
                jdbcProviderName='Microsoft SQL Server JDBC Driver Provider (XA)'
            elif (dbType.lower() == 'mysql'):
                #this is from user-defined template
                jdbcProviderName='MySql JDBC Driver Provider'
            else:
                print 'serverScopedDataSourceExists: jdbc provider type must be "db2", "mysql", "sqlserver" or "oracle" (caps insensitive)'
                sys.exit(1)
            serverPath='/Cell:'+cellName+'/Node:'+nodeName+'/'+'Server:'+serverName+'/'
            providerPath=serverPath + 'JDBCProvider:'+jdbcProviderName+'/'
            path=providerPath + 'DataSource:' + dataSourceName
            dataSourceID = thingoExists(path)
            propertySetID = AdminConfig.showAttribute(dataSourceID, 'propertySet')
            propList =  Utilities.convertToList(AdminConfig.showAttribute(propertySetID, 'resourceProperties'))
            for id in propList:
                if AdminConfig.showAttribute(id, 'name') == dataSourceCustomPropertyName:
                    return id
        else:
            print "serverScopedDataSource not found: " + dataSourceName
            sys.exit(1)
    except:
        print "\n\nException in serverScopedDataSourceCustomPropExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
def serverScopedDataSourceByJndiExists(cellName, nodeName, serverName, dbType, jndiName):
    try:
        if nodeExists(nodeName):
            if serverExists(nodeName, serverName):
                if (dbType.lower() == 'db2'):
                    jdbcProviderName='DB2 Universal JDBC Driver Provider (XA)'
                elif (dbType.lower() == 'oracle'):
                    #for some reason oracle provider template name lacks "Provider" at end, but I have added it
                    jdbcProviderName='Oracle JDBC Driver Provider'
                elif (dbType.lower() == 'sqlserver'):
                    #for some reason sql server provider template name lacks "Provider" at end, but I have added it
                    jdbcProviderName='Microsoft SQL Server JDBC Driver Provider (XA)'
                elif (dbType.lower() == 'mysql'):
                    #this is from user-defined template
                    jdbcProviderName='MySql JDBC Driver Provider'

                else:
                    print 'serverScopedDataSourceByJndiExists: jdbc provider type must be "db2", "mysql", "sqlserver" or "oracle" (caps insensitive)'
                    sys.exit(1)
                dataSourceIdList = AdminTask.listDatasources('[-scope Node=' + nodeName + ',Server=' + serverName + ']').splitlines()
                for dataSourceId in dataSourceIdList:
                    if (AdminConfig.showAttribute(dataSourceId, 'jndiName') == jndiName):
                        return dataSourceId
            else:
                print "serverScopedDataSourceByJndiExists: server not found: " + serverName
                sys.exit(1)
        else:
            print "serverScopedDataSourceByJndiExists: node not found: " + nodeName
            sys.exit(1)
    except:
        print "\n\nException in serverScopedDataSourceByJndiExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
def datasourceByServerOrClusterNameSubstringExists(serverOrClusterNameSubstring, dataSourceName):
    # we return a single ds id because we expect that if server is clustered, the ds will exist at cluster level
    # so there can be only one ds
    try:
        datasourceIDList = AdminConfig.list('DataSource', '*' + serverOrClusterNameSubstring + '*').splitlines()
        for ds in datasourceIDList:
            name=AdminConfig.showAttribute(ds, 'name')
            if name == dataSourceName:
                return ds
    except:
        print "\n\nException in datasourceByServerOrClusterNameSubstringExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])



def serverScopedThingoExists(cellName, nodeName, serverName, thingoName, thingoType):
    try:
        if nodeExists(nodeName):
            if serverExists(nodeName, serverName):
                serverId = AdminConfig.getid('/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + serverName + '/')
                list = AdminConfig.list(thingoType, serverId).splitlines()
                if len(list) > 0:                                    
                    for id in list:
                        if (thingoName.strip() == AdminConfig.showAttribute(id, 'name').strip()):
                            return id
                else:
                    #print "no list of type: " + thingoType + " found for node " + nodeName + " & server: " + serverName
                    return
            else:
                print "server not found: " + serverName
                sys.exit(1)
        else:
            print "node not found: " + nodeName
            sys.exit(1)
    except:
        print "\n\nException in serverScopedThingoExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def clusterScopedThingoExists(cellName, clusterName, thingoName, thingoType):
    try:
        if clusterExists(clusterName):
            clusterId = AdminConfig.getid('/Cell:' + cellName + '/ServerCluster:' + clusterName + '/')
            list = AdminConfig.list(thingoType, clusterId).splitlines()
            if len(list) > 0:                                    
                for id in list:
                    if (thingoName.strip() == AdminConfig.showAttribute(id, 'name').strip()):
                        return id
            else:
                #print "no list of type: " + thingoType + " found for cluster " + clusterName 
                return
        else:
            print "cluster not found: " + serverName
            sys.exit(1)
    except:
        print "\n\nException in clusterScopedThingoExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
def serverScopedQueueConnectionFactoryExists(cellName, nodeName, serverName, factoryName):
    try:
        return serverScopedThingoExists(cellName, nodeName, serverName, factoryName, 'MQQueueConnectionFactory')
    except:
        print "\n\nException in serverScopedQueueConnectionFactoryExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def clusterScopedQueueConnectionFactoryExists(cellName, clusterName, factoryName):
    try:
        return clusterScopedThingoExists(cellName, clusterName, factoryName, 'MQQueueConnectionFactory')
    except:
        print "\n\nException in clusterScopedQueueConnectionFactoryExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def serverScopedQueueConnectionFactoryConnectionPoolExists(cellName, nodeName, serverName, factoryName):
    try:
        queueConnectionFactoryId = serverScopedQueueConnectionFactoryExists(cellName, nodeName, serverName, factoryName)
        return AdminConfig.showAttribute(queueConnectionFactoryId, 'connectionPool')
    except:
        print "\n\nException in serverScopedQueueConnectionFactoryConnectionPoolExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def clusterScopedQueueConnectionFactoryConnectionPoolExists(cellName, clusterName, factoryName):
    try:
        queueConnectionFactoryId = clusterScopedQueueConnectionFactoryExists(cellName, clusterName, factoryName)
        return AdminConfig.showAttribute(queueConnectionFactoryId, 'connectionPool')
    except:
        print "\n\nException in clusterScopedQueueConnectionConnectionPoolFactoryExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])


def serverScopedQueueExists(cellName, nodeName, serverName, queueName):
    try:
        return serverScopedThingoExists(cellName, nodeName, serverName, queueName, 'MQQueue')
        
    except:
        print "\n\nException in serverScopedQueueExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def clusterScopedQueueExists(cellName, clusterName, queueName):
    try:
        return clusterScopedThingoExists(cellName, clusterName, queueName, 'MQQueue')
        
    except:
        print "\n\nException in clusterScopedQueueExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def serverScopedListenerPortExists(cellName, nodeName, serverName, listenerName):
    try:
        return serverScopedThingoExists(cellName, nodeName, serverName, listenerName, 'ListenerPort')
    except:
        print "\n\nException in serverScopedListenerPortExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    
def replicationDomainExists(cellName, name):
    try:
        path = '/DataReplicationDomain:'+name+'/'
        return thingoExists(path)
    except:
        print "\n\nException in replicationDomainExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def serverScopedJMSActivationSpecExists(cellName, nodeName, serverName, activationSpecName):
    try:
        return serverScopedThingoExists(cellName, nodeName, serverName, activationSpecName, 'J2CActivationSpec')
    except:
        print "\n\nException in serverScopedJMSActivationSpecExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
def clusterScopedJMSActivationSpecExists(cellName, clusterName, activationSpecName):
    try:
        return clusterScopedThingoExists(cellName, clusterName, activationSpecName, 'J2CActivationSpec')
    except:
        print "\n\nException in clusterScopedJMSActivationSpecExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def serverScopedLibraryExists(nodeName, serverName, libaryName):
    try:
        serverId = serverExists(nodeName, serverName)
        libraryListString = AdminConfig.list('Library', serverId)
        if (len(libraryListString) == 0):
            return
        else:
            libraryList = libraryListString.split()
            for libraryId in libraryList:
                if AdminConfig.showAttribute(libraryId, 'name') == libaryName:
                    return libaryId
    except:
        print "\n\nException in serverScopedLibraryExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def clusterScopedLibraryExists(clusterName, libaryName):
    try:
        clusterId = clusterExists(clusterName)
        libraryListString = AdminConfig.list('Library', clusterId)
        if (len(libraryListString) == 0):
            return
        else:
            libraryList = libraryListString.split()
            for libraryId in libraryList:
                if AdminConfig.showAttribute(libraryId, 'name') == libaryName:
                    return libaryId
    except:
        print "\n\nException in clusterScopedLibraryExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
                                
def serverScopedClassLoaderExists(nodeName, serverName):
    try:
        serverId = serverExists(nodeName, serverName)
        classLoaderListString = AdminConfig.list('Classloader', serverId)
        if (len(classLoaderListString) == 0):
            #print "case a"
            return ""
        else:
            classLoaderList = classLoaderListString.split()
            #print "case b"
            return classLoaderList[0]
    except:
        print "\n\nException in serverScopedClassLoaderExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def virtualHostEntryExists(virtualhostName, hostname, port):
    
    #print "\n\n  entering virtualHostEntryExists with virtualhostName: " + virtualhostName + " hostname: " + hostname + " port: " + str(port) + "\n"
    
    try:
        virtualhostId = AdminConfig.getid('/VirtualHost:'+virtualhostName+'/')
        if virtualhostId == '':
            print "\n\nThe specified virtualhostName: " + virtualhostName + " does not exist."
            sys.exit(1)
        aliasIdList = Utilities.convertToList(AdminConfig.showAttribute(virtualhostId, 'aliases'))
        #print "aliasIdList:"
        #print aliasIdList
        #print ""
        if (aliasIdList == []):
            return ""
        for aliasId in aliasIdList:
            #print ""
            #print "aliasId:"
            #print aliasId
            #print AdminConfig.showall(aliasId)
            #print "hostname:" + AdminConfig.showAttribute(aliasId, 'hostname')
            if (AdminConfig.showAttribute(aliasId, 'hostname')  == hostname):
                #print "hostname matches: " + hostname
                thisPort = AdminConfig.showAttribute(aliasId, 'port').strip()
                #print "thisPort: " + str(thisPort)
                if (str(thisPort).strip()  == str(port).strip()):
                    #print "******************************port matches: " + str(port)
                    #print "returning aliasId: " + aliasId
                    return aliasId
                else:
                    #print "---------------------port doesn't match: " + str(port)
                    return ""
            else:
                return ""
    except:
        print "\n\nException in virtualHostEntryExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def serverScopedAsynchBeanWorkManagerExists(nodeName, serverName, workManagerName):
    try:
        serverId = serverExists(nodeName, serverName)
        workManagerList = Utilities.convertToList(AdminConfig.list('WorkManagerInfo', serverId))
        for workManagerId in workManagerList:
            name = AdminConfig.showAttribute(workManagerId, "name")
            if (name == workManagerName):
                return workManagerId
        return ""    
        
    except:
        print "\n\nException in serverScopedAsynchBeanWorkManagerExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])        

def clusterScopedAsynchBeanWorkManagerExists(clusterName, workManagerName):
    try:
        clusterId = clusterExists(clusterName)
        workManagerList = Utilities.convertToList(AdminConfig.list('WorkManagerInfo', clusterId))
        #print workManagerList
        for workManagerId in workManagerList:
            if (AdminConfig.showAttribute(workManagerId, "name") == workManagerName):
                #print workManagerId
                return workManagerId
        return ""    
        
    except:
        print "\n\nException in serverScopedAsynchBeanWorkManagerExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])                
        
def serverScopedWorkManagerProviderExists(nodeName, serverName):
    try:
        workManagerProviderId = AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/WorkManagerProvider:/")
        return workManagerProviderId
    except:
        print "\n\nException in serverScopedWorkManagerProviderExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def clusterScopedWorkManagerProviderExists(clusterName):
    try:
        workManagerProviderId = AdminConfig.getid("/ServerCluster:"+clusterName+"/WorkManagerProvider:/")
        return workManagerProviderId
    except:
        print "\n\nException in clusterScopedWorkManagerProviderExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def stringNameSpaceBindingExists(theNameInNameSpace):
    try:
        type = "StringNameSpaceBinding"
        namebindingList = AdminConfig.list(type).splitlines()
        for namebindingId in namebindingList:
            itsNameInNameSpace = AdminConfig.showAttribute(namebindingId,'nameInNameSpace')
            if itsNameInNameSpace == theNameInNameSpace:
                return namebindingId
        return
    except:
        print "\n\nException in stringNameSpaceBindingExists()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
      
