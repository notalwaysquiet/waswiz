###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following procedures:
#   createQueueConnectionFactoryServerLevel
#   createQueueConnectionFactoryClusterLevel
#   createQueueConnectionFactoryByScope
#   createQueueServerLevel
#   createQueueClusterLevel
#   createQueueByScopePath
#   createListenerPort
#   createJMSActivationSpecServerLevel
#   createJMSActivationSpecClusterLevel
#   createJMSActivationSpecByScope
#   modifyQueueConnectionFactoryPoolByScope
#   modifyQueueConnectionFactoryPoolClusterLevel
#   modifyQueueConnectionFactoryPoolServerLevel
###############################################################################
# Notes


import sys
import AdminConfig
import AdminControl
import AdminTask
# modules that are searched for in the same directory as this script
import ServerComponent
import MqDefaults

#--------------------------------------------------------------------
# Create a cluster-level MQ queue connection factory
#--------------------------------------------------------------------
def createQueueConnectionFactoryClusterLevel(clusterName, factoryName, description, jndiName, queueManager, host, port, channel, XAEnabled, transportType, tempModel):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a cluster-level MQ queue connection factory"
        print " clusterName:             "+clusterName
        print " qcfName:                 "+factoryName
        print " description:             "+description
        print " jndiName:                "+jndiName
        print " queueManager:            "+queueManager
        print " host:                    "+host
        print " port:                    "+str(port)
        print " channel:                 "+channel
        print " XAEnabled:               "+XAEnabled  
        print " transportType:           "+transportType  
        print " tempModel:               "+tempModel  
        
        msg = " Executing: Mq.createQueueConnectionFactoryClusterLevel(\""+clusterName+"\", \""+factoryName+"\", \""+description+"\", \""+jndiName+"\", \""+queueManager+"\", \""+host+"\", \""+str(port)+"\", \""+channel+"\", \""+XAEnabled+"\", \""+transportType+"\", \""+tempModel+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        cellName = AdminConfig.showAttribute(AdminConfig.list('Cell'), 'name')
        #print cellName

        jmsProviderScopePath = '/Cell:' + cellName + '/ServerCluster:' + clusterName
        createQueueConnectionFactoryByScope(jmsProviderScopePath, factoryName, description, jndiName, queueManager, host, port, channel, XAEnabled, transportType, tempModel)

    except:
        print "\n\nException in createQueueConnectionFactoryClusterLevel()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of createQueueConnectionFactoryClusterLevel()"


#--------------------------------------------------------------------
# Create a server-level MQ queue connection factory
#--------------------------------------------------------------------
def createQueueConnectionFactoryServerLevel(nodeName, serverName, factoryName, description, jndiName, queueManager, host, port, channel, XAEnabled, transportType, tempModel):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a server-level MQ queue connection factory"
        print " nodeName:                "+nodeName
        print " serverName:              "+serverName
        print " qcfName:                 "+factoryName
        print " description:             "+description
        print " jndiName:                "+jndiName
        print " queueManager:            "+queueManager
        print " host:                    "+host
        print " port:                    "+str(port)
        print " channel:                 "+channel
        print " XAEnabled:               "+XAEnabled  
        print " transportType:           "+transportType  
        print " tempModel:               "+tempModel  
        
        msg = " Executing: Mq.createQueueConnectionFactoryServerLevel(\""+nodeName+"\", \""+serverName+"\", \""+factoryName+"\", \""+description+"\", \""+jndiName+"\", \""+queueManager+"\", \""+host+"\", \""+str(port)+"\", \""+channel+"\", \""+XAEnabled+"\", \""+transportType+"\", \""+tempModel+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        cellName = AdminConfig.showAttribute(AdminConfig.list('Cell'), 'name')
        #print cellName

        #path = '/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + serverName + '/JMSProvider:' + JMSProviderName
        jmsProviderScopePath = '/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + serverName
        createQueueConnectionFactoryByScope(jmsProviderScopePath, factoryName, description, jndiName, queueManager, host, port, channel, XAEnabled, transportType, tempModel)

    except:
        print "\n\n Exception in createQueueConnectionFactoryServerLevel()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of createQueueConnectionFactoryServerLevel()"


#--------------------------------------------------------------------
# Create MQ queue connection factory by passing in the scope path
# unlike JDBC providers, JMS providers are automatically created by WAS at all levels
# so it is not necessary to create them ourselves
# tempModel. In admin console at [qcf] > Advanced properties > WebSphere MQ model queue name 
# tempModel. The model queue that is used as a basis for temporary queue definitions.
# Default is suppsed to be: SYSTEM.DEFAULT.MODEL.QUEUE but script-created qcf's do not get this set unless they explicitly set it
#--------------------------------------------------------------------
def createQueueConnectionFactoryByScope(jmsProviderScopePath, factoryName, description, jndiName, queueManager, host, port, channel, XAEnabled, transportType, tempModel):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a MQ queue connection factory by passing in scope path"
        print " jmsProviderScopePath:   "+jmsProviderScopePath
        print " qcfName:                "+factoryName
        print " description:            "+description
        print " jndiName:               "+jndiName
        print " queueManager:           "+queueManager
        print " host:                   "+host
        print " port:                   "+str(port)
        print " channel:                "+channel
        print " XAEnabled:              "+XAEnabled  
        print " transportType:          "+transportType  
        print " tempModel:              "+tempModel  
        msg = " Executing: Mq.createQueueConnectionFactoryByScope(\""+jmsProviderScopePath+"\", \""+factoryName+"\", \""+description+"\", \""+jndiName+"\", \""+queueManager+"\", \""+host+"\", \""+str(port)+"\", \""+channel+"\", \""+XAEnabled+"\", \""+transportType+"\", \""+tempModel+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        cellName = AdminConfig.showAttribute(AdminConfig.list('Cell'), 'name')
        #print cellName

        JMSProviderName = "WebSphere MQ JMS Provider"
        #path = '/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + serverName + '/JMSProvider:' + JMSProviderName
        path = jmsProviderScopePath + '/JMSProvider:' + JMSProviderName
        JMSProviderId = AdminConfig.getid(path)
        #print "\n JMSProviderId: " + JMSProviderId

        templateList = AdminConfig.listTemplates('MQQueueConnectionFactory').splitlines()
        #take the 2nd one, which should be "First Example WMQ QueueConnectionFactory(templates/system|JMS-resource-provider-templates.xml#MQQueueConnectionFactory_1)"
        template = templateList[1]
        #print template
        
        #set up attribute lists for the wsadmin command
        name = ['name', factoryName]
        jndiName = ['jndiName', jndiName]
        description = ['description', description]
        queueManager = ['queueManager', queueManager]
        host = ['host', host]
        port = ['port', str(port)]
        channel = ['channel', channel]
        XAEnabled = ['XAEnabled', XAEnabled]
        transportType = ['transportType', transportType]
        tempModel = ['tempModel', tempModel]
        
        attributeList = [name, jndiName, description, queueManager, host, port, channel, XAEnabled, transportType, tempModel]
        #print attributeList

        print AdminConfig.createUsingTemplate('MQQueueConnectionFactory', JMSProviderId, attributeList, template)
        
        print "\n\n   . . . fixing up pool defaults for queue connection factory: " + factoryName
        print "\n   . . . connection pool . . . "
        poolType = "connection"
        MqDefaults.fixUpPoolDefaultsByScope(poolType, jmsProviderScopePath, factoryName)
        print "\n\n   . . . session pool . . . "
        poolType = "session"
        MqDefaults.fixUpPoolDefaultsByScope(poolType, jmsProviderScopePath, factoryName)
            
        print AdminConfig.save()


    except:
        print "\n\n Exception in createQueueConnectionFactoryByScope()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of createQueueConnectionFactoryByScope()"


#--------------------------------------------------------------------
# Modify pool for a cluster-level MQ queue connection factory
#--------------------------------------------------------------------
def modifyQueueConnectionFactoryPoolClusterLevel(clusterName, poolType, factoryName, connectionTimeout, maxConnections, unusedTimeout, minConnections, purgePolicy, agedTimeout, reapTime):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Modify pool for a cluster-level MQ queue connection factory"
        print " clusterName:             "+clusterName
        print " poolType:                "+poolType
        print " qcfName:                 "+factoryName
        print " connectionTimeout:       "+str(connectionTimeout)
        print " maxConnections:          "+str(maxConnections)
        print " unusedTimeout:           "+str(unusedTimeout)
        print " minConnections:          "+str(minConnections)
        print " purgePolicy:             "+purgePolicy  
        print " agedTimeout:             "+str(agedTimeout)
        print " reapTime:                "+str(reapTime)
        msg = " Executing: Mq.modifyQueueConnectionFactoryPoolClusterLevel(\""+clusterName+"\", \""+poolType+"\", \""+factoryName+"\", \""+str(connectionTimeout)+"\", \""+str(maxConnections)+"\", \""+str(unusedTimeout)+"\", \""+str(minConnections)+"\", \""+purgePolicy+"\", \""+str(agedTimeout)+"\", \""+str(reapTime)+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        cellName = AdminConfig.showAttribute(AdminConfig.list('Cell'), 'name')
        #print cellName

        jmsProviderScopePath = '/Cell:' + cellName + '/ServerCluster:' + clusterName
        modifyQueueConnectionFactoryPoolByScope(poolType, jmsProviderScopePath, factoryName, connectionTimeout, maxConnections, unusedTimeout, minConnections, purgePolicy, agedTimeout, reapTime)

    except:
        print "\n\nException in modifyQueueConnectionFactoryPoolClusterLevel()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of modifyQueueConnectionFactoryPoolClusterLevel()"


#--------------------------------------------------------------------
# Modify pool for a server-level MQ queue connection factory
#--------------------------------------------------------------------
def modifyQueueConnectionFactoryPoolServerLevel(nodeName, serverName, poolType, factoryName, connectionTimeout, maxConnections, unusedTimeout, minConnections, purgePolicy, agedTimeout, reapTime):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Modify pool for a server-level MQ queue connection factory"
        print " nodeName:                "+nodeName
        print " serverName:              "+serverName
        print " poolType:                "+poolType
        print " qcfName:                 "+factoryName
        print " connectionTimeout:       "+str(connectionTimeout)
        print " maxConnections:          "+str(maxConnections)
        print " unusedTimeout:           "+str(unusedTimeout)
        print " minConnections:          "+str(minConnections)
        print " purgePolicy:             "+purgePolicy  
        print " agedTimeout:             "+str(agedTimeout)
        print " reapTime:                "+str(reapTime)
        msg = " Executing: Mq.modifyQueueConnectionFactoryPoolServerLevel(\""+nodeName+"\", \""+serverName+"\", \""+poolType+"\", \""+factoryName+"\", \""+str(connectionTimeout)+"\", \""+str(maxConnections)+"\", \""+str(unusedTimeout)+"\", \""+str(minConnections)+"\", \""+purgePolicy+"\", \""+str(agedTimeout)+"\", \""+str(reapTime)+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        cellName = AdminConfig.showAttribute(AdminConfig.list('Cell'), 'name')
        #print cellName

        jmsProviderScopePath = '/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + serverName
        modifyQueueConnectionFactoryPoolByScope(poolType, jmsProviderScopePath, factoryName, connectionTimeout, maxConnections, unusedTimeout, minConnections, purgePolicy, agedTimeout, reapTime)

    except:
        print "\n\nException in modifyQueueConnectionFactoryPoolServerLevel()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of modifyQueueConnectionFactoryPoolServerLevel()"


#--------------------------------------------------------------------
# Modify connection or session pool properties for MQ queue connection factory by passing in the scope path
# connection pool properties are in resources.xml
# All parameters are optional except poolType, jmsProviderScopePath and factoryName
# For the diff between connection pool and session pool see 
#   http://www-01.ibm.com/support/docview.wss?uid=swg21201242
# mq v7 allows multiple "conversations" i.e., sessions per tcp/ip connection
# WAS to MQ product connectivity info center
#    http://publib.boulder.ibm.com/infocenter/prodconn/v1r0m0/topic/com.ibm.scenarios.wmqwasusing.doc/topics/tcpipconnuse_jmsconfactory.htm
#--------------------------------------------------------------------
def modifyQueueConnectionFactoryPoolByScope(poolType, jmsProviderScopePath, factoryName, connectionTimeout, maxConnections, unusedTimeout, minConnections, purgePolicy, agedTimeout, reapTime):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Modify a MQ queue connection factory pool by passing in scope path"
        print " pooltype:               "+poolType
        print " jmsProviderScopePath:   "+jmsProviderScopePath
        print " factoryName:            "+factoryName
        print " connectionTimeout:      "+str(connectionTimeout)
        print " maxConnections:         "+str(maxConnections)
        print " unusedTimeout:          "+str(unusedTimeout)
        print " minConnections:         "+str(minConnections)
        print " purgePolicy:            "+purgePolicy
        print " agedTimeout:            "+str(agedTimeout)
        print " reapTime:               "+str(reapTime)
        msg = " Executing: Mq.modifyQueueConnectionFactoryPoolByScope(\""+poolType+"\", \""+jmsProviderScopePath+"\", \""+factoryName+"\", \""+str(connectionTimeout)+"\", \""+str(maxConnections)+"\", \""+str(unusedTimeout)+"\", \""+str(minConnections)+"\", \""+purgePolicy+"\", \""+str(agedTimeout)+"\", \""+str(reapTime)+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(poolType) == 0):
            print usage
            sys.exit(1)
        if (len(jmsProviderScopePath) == 0):
            print usage
            sys.exit(1)
        if (len(factoryName) == 0):
            print usage
            sys.exit(1)
        noPropsProvided = 'true'
        JMSProviderName = "WebSphere MQ JMS Provider"
        #print "jmsProviderScopePath: " + jmsProviderScopePath
        #print AdminConfig.getid(jmsProviderScopePath)
        path = jmsProviderScopePath + '/JMSProvider:' + JMSProviderName + '/' + 'MQQueueConnectionFactory:' + factoryName + '/'
        #print "path: " + path
        queueConnectionFactoryId = AdminConfig.getid(path)
        #print "queueConnectionFactoryId: " + queueConnectionFactoryId
        poolId = ""
        if poolType.lower() == 'connection':
            poolId = AdminConfig.showAttribute(queueConnectionFactoryId, 'connectionPool')
        if poolType.lower() == 'session':
            poolId = AdminConfig.showAttribute(queueConnectionFactoryId, 'sessionPool')
        
        #print "poolId: " + poolId
        if (poolId == ""):
            print "\n\nCould not modify pool for following reason:"
            print "Could not find pool id for "
            print "  pool type: " + poolType 
            print "  factoryName: " + factoryName 
            print "  scope: " + jmsProviderScopePath
            print "Exiting."
            sys.exit(1)

        #set up attribute list
        attributeList = []
        if connectionTimeout != "":
            connectionTimeout = ['connectionTimeout', str(connectionTimeout)]
            noPropsProvided = 'false'
            attributeList.append(connectionTimeout)
            
        if maxConnections != "":
            maxConnections = ['maxConnections', str(maxConnections)]
            noPropsProvided = 'false'
            attributeList.append(maxConnections)
        
        if unusedTimeout != "":
            unusedTimeout = ['unusedTimeout', str(unusedTimeout)]
            noPropsProvided = 'false'
            attributeList.append(unusedTimeout)
            
        if minConnections != "":
            minConnections = ['minConnections', str(minConnections)]
            noPropsProvided = 'false'
            attributeList.append(minConnections)
            
        if purgePolicy != "":
            purgePolicy = ['purgePolicy', purgePolicy]
            noPropsProvided = 'false'
            attributeList.append(purgePolicy)
            
        if agedTimeout != "":
            agedTimeout = ['agedTimeout', str(agedTimeout)]
            noPropsProvided = 'false'
            attributeList.append(agedTimeout)
        
        if reapTime != "":
            reapTime = ['reapTime', reapTime]
            noPropsProvided = 'false'
            attributeList.append(reapTime)
        
        if (noPropsProvided == 'true'):
            print "\n\nCould not modify pool for following reason:"
            print "No props provided for "
            print "  pool type: " + poolType 
            print "  factoryName: " + factoryName 
            print "  scope: " + jmsProviderScopePath
            print "Exiting."
            sys.exit(1)

        #print "attributeList: " + str(attributeList)
        print AdminConfig.modify(poolId, attributeList)
        print AdminConfig.save()
        print "Modified non-advanced props for pool: " + poolId

    except:
        print "\n\n Exception in modifyQueueConnectionFactoryPoolByScope()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of modifyQueueConnectionFactoryPoolByScope()"


#--------------------------------------------------------------------
# Create a cluster-level MQ queue 
# unlike JDBC providers, JMS providers are automatically created by WAS at all levels
# so it is not necessary to create them ourselves
#--------------------------------------------------------------------
def createQueueClusterLevel(clusterName, queueName, description, jndiName, baseQueueName, baseQueueManagerName, queueManagerHost, queueManagerPort, serverConnectionChannelName, CCSID, useNativeEncoding, sendAsync, readAhead):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a cluster-level MQ queue "
        print " clusterName:                 "+clusterName
        print " queueName:                   "+queueName
        print " description:                 "+description
        print " jndiName:                    "+jndiName
        print " baseQueueName:               "+baseQueueName
        print " baseQueueManagerName:        "+baseQueueManagerName
        print " queueManagerHost:            "+queueManagerHost
        print " queueManagerPort:            "+str(queueManagerPort)
        print " serverConnectionChannelName: "+serverConnectionChannelName
        print " CCSID:                       "+str(CCSID)
        print " useNativeEncoding:           "+useNativeEncoding
        print " sendAsync:                   "+sendAsync
        print " readAhead:                   "+readAhead
        
        msg = " Executing: Mq.createQueueClusterLevel(\""+clusterName+"\", \""+queueName+"\", \""+description+"\", \""+jndiName+"\", \""+baseQueueName+"\", \""+baseQueueManagerName+"\", \""+queueManagerHost+"\", \""+str(queueManagerPort)+"\", \""+serverConnectionChannelName+"\", \""+str(CCSID)+"\", \""+useNativeEncoding+"\", \""+sendAsync+"\", \""+readAhead+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        cellName = AdminConfig.showAttribute(AdminConfig.list('Cell'), 'name')
        #print cellName

        #path = '/Cell:' + cellName + '/ServerCluster:' + clusterName  + '/JMSProvider:' + JMSProviderName
        jmsProviderScopePath = '/Cell:' + cellName + '/ServerCluster:' + clusterName

        name = ['name', queueName]
        description = ['description', description]
        jndiName = ['jndiName', jndiName]
        baseQueueName = ['baseQueueName', baseQueueName]
        baseQueueManagerName = ['baseQueueManagerName', baseQueueManagerName]
        queueManagerHost = ['queueManagerHost', queueManagerHost]
        queueManagerPort = ['queueManagerPort', str(queueManagerPort)]
        serverConnectionChannelName = ['serverConnectionChannelName', serverConnectionChannelName]
        CCSID = ['CCSID', CCSID]
        useNativeEncoding = ['useNativeEncoding', useNativeEncoding]
        sendAsync = ['sendAsync', sendAsync]
        readAhead = ['readAhead', readAhead]
        
        attributeList = [name, description, jndiName, baseQueueName, baseQueueManagerName, queueManagerHost, queueManagerPort, serverConnectionChannelName, CCSID, useNativeEncoding, sendAsync, readAhead]
        #print attributeList
        
        createQueueByScopePath(jmsProviderScopePath, attributeList)
        
    except:
        print "\n\n Exception in createQueueClusterLevel()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of createQueueClusterLevel()"


#--------------------------------------------------------------------
# Create a server-level MQ queue 
# unlike JDBC providers, JMS providers are automatically created by WAS at all levels
# so it is not necessary to create them ourselves
#--------------------------------------------------------------------
def createQueueServerLevel(nodeName, serverName, queueName, description, jndiName, baseQueueName, baseQueueManagerName, queueManagerHost, queueManagerPort, serverConnectionChannelName, CCSID, useNativeEncoding, sendAsync, readAhead):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a server-level MQ queue "
        print " nodeName:             "+nodeName
        print " serverName:           "+serverName
        print " queueName:            "+queueName
        print " description:          "+description
        print " jndiName:             "+jndiName
        print " baseQueueName:        "+baseQueueName
        print " baseQueueManagerName: "+baseQueueManagerName
        print " queueManagerHost:            "+queueManagerHost
        print " queueManagerPort:            "+str(queueManagerPort)
        print " serverConnectionChannelName: "+serverConnectionChannelName        
        print " CCSID:                       "+str(CCSID)
        print " useNativeEncoding:           "+useNativeEncoding
        print " sendAsync:                   "+sendAsync
        print " readAhead:                   "+readAhead
        
        msg = " Executing: Mq.createQueueServerLevel(\""+nodeName+"\", \""+serverName+"\", \""+queueName+"\", \""+description+"\", \""+jndiName+"\", \""+baseQueueName+"\", \""+baseQueueManagerName+"\", \""+queueManagerHost+"\", \""+str(queueManagerPort)+"\", \""+serverConnectionChannelName+"\", \""+str(CCSID)+"\", \""+useNativeEncoding+"\", \""+sendAsync+"\", \""+readAhead+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        cellName = AdminConfig.showAttribute(AdminConfig.list('Cell'), 'name')
        #print cellName

        #path = '/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + serverName + '/JMSProvider:' + JMSProviderName
        jmsProviderScopePath = '/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + serverName

        name = ['name', queueName]
        description = ['description', description]
        jndiName = ['jndiName', jndiName]
        baseQueueName = ['baseQueueName', baseQueueName]
        baseQueueManagerName = ['baseQueueManagerName', baseQueueManagerName]
        queueManagerHost = ['queueManagerHost', queueManagerHost]
        queueManagerPort = ['queueManagerPort', str(queueManagerPort)]
        serverConnectionChannelName = ['serverConnectionChannelName', serverConnectionChannelName]
        CCSID = ['CCSID', CCSID]
        useNativeEncoding = ['useNativeEncoding', useNativeEncoding]
        sendAsync = ['sendAsync', sendAsync]
        readAhead = ['readAhead', readAhead]
        
        attributeList = [name, description, jndiName, baseQueueName, baseQueueManagerName, queueManagerHost, queueManagerPort, serverConnectionChannelName, CCSID, useNativeEncoding, sendAsync, readAhead]
        #print attributeList
        
        createQueueByScopePath(jmsProviderScopePath, attributeList)
        
    except:
        print "\n\n Exception in createQueueServerLevel()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of createQueueServerLevel()"


#--------------------------------------------------------------------
# Create a MQ queue  by passing in the scope path
# unlike JDBC providers, JMS providers are automatically created by WAS at all levels
# so it is not necessary to create them ourselves
#--------------------------------------------------------------------
def createQueueByScopePath(jmsProviderScopePath, attributeList):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a MQ queue by passing in scoped JMS provider id"
        print " jmsProviderScopePath:  "+jmsProviderScopePath
        msg = " Executing: Mq.createQueueByScopePath(\""+jmsProviderScopePath+"\", \""+str(attributeList)+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        cellName = AdminConfig.showAttribute(AdminConfig.list('Cell'), 'name')
        #print cellName

        JMSProviderName = "WebSphere MQ JMS Provider"
        #path = '/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + serverName + '/JMSProvider:' + JMSProviderName
        path = jmsProviderScopePath + '/JMSProvider:' + JMSProviderName
        JMSProviderId = AdminConfig.getid(path)
        #print JMSProviderId

        templateList = AdminConfig.listTemplates('MQQueue').splitlines()
        #just take the first one; should be the default one'
        #print templateList
        template = templateList[0]
        #print template
        
        #attributeList = [name, description, jndiName, baseQueueName, baseQueueManagerName]
        #print attributeList
        
        print AdminConfig.createUsingTemplate('MQQueue', JMSProviderId, attributeList, template)
        print AdminConfig.save()

    except:
        print "\n\n Exception in createQueueByScopePath()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of createQueueByScopePath()"


#--------------------------------------------------------------------
# Create a server's message-driven bean listener port
#  Note: Listener ports do NOT work in a cluster
#  The preferred way to hook up MDBs is now JMS Activation Specification
#--------------------------------------------------------------------
def createListenerPort(nodeName, serverName, portName, description, connectionFactoryJNDIName, destinationJNDIName, maxSessions, maxRetries, maxMessages):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a server's message-driven bean listener port"
        print " nodeName:                     "+nodeName
        print " serverName:                   "+serverName
        print " portName:                     "+portName
        print " description:                  "+description
        print " connectionFactoryJNDIName:    "+connectionFactoryJNDIName
        print " destinationJNDIName:          "+destinationJNDIName
        print " maxSessions:                  "+str(maxSessions)
        print " maxRetries:                   "+str(maxRetries)
        print " maxMessages:                  "+str(maxMessages)
        msg = " Executing: Mq.createListenerPort(\""+nodeName+"\", \""+serverName+"\", \""+portName+"\", \""+description+"\", \""+connectionFactoryJNDIName+"\", \""+destinationJNDIName+"\", \""+str(maxSessions)+"\", \""+str(maxRetries)+"\", \""+str(maxMessages)+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        cellName = AdminConfig.showAttribute(AdminConfig.list('Cell'), 'name')
        #print cellName

        serverId = AdminConfig.getid('/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + serverName + '/')
        #print serverId

        messageListenerServiceId = AdminConfig.list('MessageListenerService', serverId)
        #print messageListenerServiceId

        name = ['name', portName]
        description = ['description', description]
        connectionFactoryJNDIName = ['connectionFactoryJNDIName', connectionFactoryJNDIName]
        destinationJNDIName = ['destinationJNDIName', destinationJNDIName]
        maxSessions = ['maxSessions', str(maxSessions)]
        maxRetries = ['maxRetries', str(maxRetries)]
        maxMessages = ['maxMessages', str(maxMessages)]
        
        attributeList = [name, description, connectionFactoryJNDIName, destinationJNDIName, maxSessions, maxRetries, maxMessages]
        #print attributeList
        
        print AdminConfig.create('ListenerPort', messageListenerServiceId, attributeList)
        print AdminConfig.save()

    except:
        print "\n\n Exception in createListenerPort()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of createListenerPort()"


def createPropertiesString(activationSpecName, jndiName, description, destinationJndiName, destinationType, qmgrName, qmgrHostname, qmgrPortNumber, qmgrSvrconnChannel, wmqTransportType):
    # method is not currently being called
    propertiesString = '[-name ' + activationSpecName + ' -jndiName ' + jndiName + ' -description "' + description + '" -destinationJndiName ' + destinationJndiName + ' -destinationType ' +  destinationType + ' -qmgrName ' + qmgrName + ' -wmqTransportType ' + wmqTransportType + ' -qmgrHostname ' + qmgrHostname + ' -qmgrPortNumber ' + str(qmgrPortNumber) + ' -qmgrSvrconnChannel ' + qmgrSvrconnChannel + ']'
    print "returning propertiesString: " + propertiesString
    print ""
    return propertiesString
    
def createActSpecPropertiesStringPlusDontStopIfDeliveryFails(activationSpecName, jndiName, description, destinationJndiName, destinationType, qmgrName, qmgrHostname, qmgrPortNumber, qmgrSvrconnChannel, wmqTransportType):
    # method tacks on the "-stopEndpointIfDeliveryFails" option at the end which is needed to prevent the problem where server will not start if there are messages on the queue
    propertiesString = '[-name ' + activationSpecName + ' -jndiName ' + jndiName + ' -description "' + description + '" -destinationJndiName ' + destinationJndiName + ' -destinationType ' +  destinationType + ' -qmgrName ' + qmgrName + ' -wmqTransportType ' + wmqTransportType + ' -qmgrHostname ' + qmgrHostname + ' -qmgrPortNumber ' + str(qmgrPortNumber) + ' -qmgrSvrconnChannel ' + qmgrSvrconnChannel + ' -stopEndpointIfDeliveryFails false ]'
    print "returning propertiesString: " + propertiesString
    print ""
    return propertiesString
    
    
#--------------------------------------------------------------------
# Create a cluster-level JMS activation specification
#--------------------------------------------------------------------
def createJMSActivationSpecClusterLevel(clusterName, activationSpecName, jndiName, description, destinationJndiName, destinationType, qmgrName, qmgrHostname, qmgrPortNumber, qmgrSvrconnChannel, wmqTransportType):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a cluster-level JMS activation specification"
        print " clusterName:            "+clusterName
        print " activation spec name:   "+activationSpecName
        print " jndiName:               "+jndiName
        print " description:            "+description
        print " destinationJndiName:    "+destinationJndiName
        print " destinationType:        "+destinationType
        print " qmgrName:               "+qmgrName
        print " qmgrHostname:           "+qmgrHostname
        print " qmgrPortNumber:         "+str(qmgrPortNumber)
        print " qmgrSvrconnChannel:     "+qmgrSvrconnChannel
        print " wmqTransportType:       "+wmqTransportType  
        msg = " Executing: Mq.createJMSActivationSpecClusterLevel(\""+clusterName+"\", \""+activationSpecName+"\", \""+jndiName+"\", \""+description+"\", \""+destinationJndiName+"\", \""+destinationType+"\", \""+qmgrName+"\", \""+qmgrHostname+"\", \""+str(qmgrPortNumber)+"\", \""+qmgrSvrconnChannel+"\", \""+wmqTransportType+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        cellName = AdminConfig.showAttribute(AdminConfig.list('Cell'), 'name')
        #print cellName

        JMSProviderName = "WebSphere MQ JMS Provider"
        path = '/Cell:' + cellName + '/ServerCluster:' + clusterName + '/JMSProvider:' + JMSProviderName
        JMSProviderId = AdminConfig.getid(path)
        #print JMSProviderId

        #propertiesString = '[-name ' + activationSpecName + ' -jndiName ' + jndiName + ' -description "' + description + '" -destinationJndiName ' + destinationJndiName + ' -destinationType ' +  destinationType + ' -qmgrName ' + qmgrName + ' -wmqTransportType ' + wmqTransportType + ' -qmgrHostname ' + qmgrHostname + ' -qmgrPortNumber ' + str(qmgrPortNumber) + ' -qmgrSvrconnChannel ' + qmgrSvrconnChannel + ']'
        propertiesString = createActSpecPropertiesStringPlusDontStopIfDeliveryFails(activationSpecName, jndiName, description, destinationJndiName, destinationType, qmgrName, qmgrHostname, qmgrPortNumber, qmgrSvrconnChannel, wmqTransportType)
        #print "propertiesString: " + propertiesString
        #print ""

        createJMSActivationSpecByScope(JMSProviderId, propertiesString)
    except:
        print "\n\n Exception in createJMSActivationSpecClusterLevel()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of createJMSActivationSpecClusterLevel()"


#--------------------------------------------------------------------
# Create a server-level JMS activation specification
#--------------------------------------------------------------------
def createJMSActivationSpecServerLevel(nodeName, serverName, activationSpecName, jndiName, description, destinationJndiName, destinationType, qmgrName, qmgrHostname, qmgrPortNumber, qmgrSvrconnChannel, wmqTransportType):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a server-level JMS activation specification"
        print " nodeName:               "+nodeName
        print " serverName:             "+serverName
        print " activation spec name:   "+activationSpecName
        print " jndiName:               "+jndiName        
        print " description:            "+description
        print " destinationJndiName:    "+destinationJndiName
        print " destinationType:        "+destinationType
        print " qmgrName:               "+qmgrName
        print " qmgrHostname:           "+qmgrHostname
        print " qmgrPortNumber:         "+str(qmgrPortNumber)
        print " qmgrSvrconnChannel:     "+qmgrSvrconnChannel
        print " wmqTransportType:       "+wmqTransportType  
        msg = " Executing: Mq.createJMSActivationSpecServerLevel(\""+nodeName+"\", \""+serverName+"\", \""+activationSpecName+"\", \""+jndiName+"\", \""+description+"\", \""+destinationJndiName+"\", \""+destinationType+"\", \""+qmgrName+"\", \""+qmgrHostname+"\", \""+str(qmgrPortNumber)+"\", \""+qmgrSvrconnChannel+"\", \""+wmqTransportType+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        cellName = AdminConfig.showAttribute(AdminConfig.list('Cell'), 'name')
        #print cellName

        JMSProviderName = "WebSphere MQ JMS Provider"
        path = '/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + serverName + '/JMSProvider:' + JMSProviderName
        JMSProviderId = AdminConfig.getid(path)
        #print JMSProviderId

        #propertiesString = '[-name ' + activationSpecName + ' -jndiName ' + jndiName + ' -description "' + description + '" -destinationJndiName ' + destinationJndiName + ' -destinationType ' +  destinationType + ' -qmgrName ' + qmgrName + ' -wmqTransportType ' + wmqTransportType + ' -qmgrHostname ' + qmgrHostname + ' -qmgrPortNumber ' + str(qmgrPortNumber) + ' -qmgrSvrconnChannel ' + qmgrSvrconnChannel + ']'
        propertiesString = createActSpecPropertiesStringPlusDontStopIfDeliveryFails(activationSpecName, jndiName, description, destinationJndiName, destinationType, qmgrName, qmgrHostname, qmgrPortNumber, qmgrSvrconnChannel, wmqTransportType)

        print "propertiesString: " + propertiesString
        print ""

        createJMSActivationSpecByScope(JMSProviderId, propertiesString)
    except:
        print "\n\n Exception in createJMSActivationSpecServerLevel()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of createJMSActivationSpecServerLevel()"


#--------------------------------------------------------------------
# Create a JMS activation specification by passing in scoped JMS provider id & properties string
#--------------------------------------------------------------------
def createJMSActivationSpecByScope(JMSProviderId, propertiesString):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a JMS activation specification by passing in scoped JMS provider id"
        #print " propertiesString:               "+propertiesString
        msg = " Executing: Mq.createJMSActivationSpecByScope("+JMSProviderId+", \""+propertiesString+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        #print "propertiesString: " + propertiesString
        #print ""

        print AdminTask.createWMQActivationSpec(JMSProviderId, propertiesString) 

        print AdminConfig.save()


    except:
        print "\n\n Exception in createJMSActivationSpecByScope()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of createJMSActivationSpecByScope()"


def displayNonDefaultJmsPoolByConnectionPoolId(connectionPoolId, poolType):
    print "connectionPoolId: " + connectionPoolId
    allDefaults = "true"    
    connectionTimeout = str(AdminConfig.showAttribute(connectionPoolId, 'connectionTimeout'))
    maxConnections = str(AdminConfig.showAttribute(connectionPoolId, 'maxConnections'))
    unusedTimeout = str(AdminConfig.showAttribute(connectionPoolId, 'unusedTimeout'))
    minConnections = str(AdminConfig.showAttribute(connectionPoolId, 'minConnections'))
    purgePolicy = AdminConfig.showAttribute(connectionPoolId, 'purgePolicy')
    agedTimeout = str(AdminConfig.showAttribute(connectionPoolId, 'agedTimeout'))
    reapTime = str(AdminConfig.showAttribute(connectionPoolId, 'reapTime'))
    
    defaultConnectionTimeout = str(MqDefaults.getConnectionTimeout())
    if connectionTimeout != defaultConnectionTimeout:
        allDefaults = "false"
        print "****************************************************************************************************"
        print "connectionTimeout: " + connectionTimeout
        #print " vs. default: " + defaultConnectionTimeout
        print "****************************************************************************************************"

    defaultMaxConnections = str(MqDefaults.getMaxConnections())
    if maxConnections != defaultMaxConnections:
        allDefaults = "false"
        print "****************************************************************************************************"
        print "maxConnections: " + maxConnections
        #print " vs. default: " + defaultMaxConnections
        print "****************************************************************************************************"

    defaultMinConnections = str(MqDefaults.getMinConnections())
    if minConnections != defaultMinConnections:
        allDefaults = "false"
        print "****************************************************************************************************"
        print "minConnections: " + minConnections
        #print " vs. default: " + defaultMinConnections
        print "****************************************************************************************************"
    
    defaultReapTime = str(MqDefaults.getReapTime())
    if reapTime != defaultReapTime:
        allDefaults = "false"
        print "****************************************************************************************************"
        print "reapTime: " + reapTime
        #print " vs. default: " + defaultReapTime
        print "****************************************************************************************************"

    defaultUnusedTimeout = str(MqDefaults.getUnusedTimeout())
    if unusedTimeout != defaultUnusedTimeout:
        allDefaults = "false"
        print "****************************************************************************************************"
        print "unusedTimeout: " + unusedTimeout
        #print " vs. default: " + defaultUnusedTimeout
        print "****************************************************************************************************"

    defaultAgedTimeout = str(MqDefaults.getAgedTimeout())
    if agedTimeout != defaultAgedTimeout:
        allDefaults = "false"
        print "****************************************************************************************************"
        print "agedTimeout: " + agedTimeout
        #print " vs. default: " + defaultAgedTimeout
        print "****************************************************************************************************"
    
    if poolType == 'connectionPool':
        defaultPurgePolicy = MqDefaults.getConnectionPurgePolicy()
    elif poolType == 'sessionPool':
        defaultPurgePolicy = MqDefaults.getSessionPurgePolicy()
    if purgePolicy != defaultPurgePolicy:
        allDefaults = "false"
        print "****************************************************************************************************"
        print "purgePolicy: " + purgePolicy
        #print " vs. default: " + defaultPurgePolicy
        print "****************************************************************************************************"
    
    if allDefaults == "true":
        print "all defaults"
        print

def displayNonDefaultJmsConnectionPoolSettingsByScopePath(jmsProviderScope):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Display tuning properties for MQ connection factory connection and session pools"
        print " jmsProviderScope:                      "+jmsProviderScope

        msg = " Executing: Mq.displayNonDefaultJmsConnectionPoolSettingsByScopePath(\""+jmsProviderScope+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        print
        print " Note: Only non-ADMIN CONSOLE default properties shown."
        print
    
        import MqDefaults
        

        # checking if the parameter value exists
        #jmsProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        path=jmsProviderScope
        objectId= AdminConfig.getid(path)
        if (len(objectId) == 0):
            print "\n\nNo object can be found at specified scope: " + jmsProviderScope 
            sys.exit(1)
        connectionFactoryListString = AdminConfig.list('MQQueueConnectionFactory', objectId)
        connectionFactoryList = connectionFactoryListString.splitlines()
        #print connectionFactoryList

        for connectionFactoryId in connectionFactoryList:
            name = AdminConfig.showAttribute(connectionFactoryId, 'name')
            print name + "----CONNECTION POOL-----" + jmsProviderScope 
            #print AdminConfig.show(connectionFactoryId)
            #print
            connectionPoolId = AdminConfig.showAttribute(connectionFactoryId, 'connectionPool')
            #print AdminConfig.show(connectionPoolId)
            #print
            displayNonDefaultJmsPoolByConnectionPoolId(connectionPoolId, 'connectionPool')
            print
            print
            print name + "----SESSION POOL-----" + jmsProviderScope 
            #print AdminConfig.show(connectionFactoryId)
            #print
            connectionPoolId = AdminConfig.showAttribute(connectionFactoryId, 'sessionPool')
            #print AdminConfig.show(connectionPoolId)
            #print
            displayNonDefaultJmsPoolByConnectionPoolId(connectionPoolId, 'sessionPool')
            print
            print
            print
            
    except:
        print "Exception in displayNonDefaultConnectionPoolSettings() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

def displayNonDefaultJmsConnectionPoolSettingsByServer(nodeName, serverName):
    try:
        # checking if the parameter value exists
        cellName = AdminControl.getCell()
        jmsProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        path=jmsProviderScope
        objectId= AdminConfig.getid(path)
        if (len(objectId) == 0):
            print "\n\nNo object can be found at specified scope: " + jmsProviderScope 
            sys.exit(1)
        displayNonDefaultJmsConnectionPoolSettingsByScopePath(jmsProviderScope)
            
    except:
        print "Exception in displayNonDefaultJmsConnectionPoolSettingsByServer() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])   
        sys.exit(1)

def displayNonDefaultJmsConnectionPoolSettingsByCluster(clusterName):
    try:
        # checking if the parameter value exists
        jmsProviderScope = '/ServerCluster:'+clusterName+'/'
        path=jmsProviderScope
        objectId= AdminConfig.getid(path)
        if (len(objectId) == 0):
            print "\n\nNo object can be found at specified scope: " + jmsProviderScope 
            sys.exit(1)
        displayNonDefaultJmsConnectionPoolSettingsByScopePath(jmsProviderScope)
            
    except:
        print "Exception in displayNonDefaultJmsConnectionPoolSettingsByCluster() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])    
        sys.exit(1)

#--------------------------------------------------------------------
# main
#--------------------------------------------------------------------
#when this module is being run as top-level, call the fixUpPoolDefaultsByScope function
if __name__=="__main__":
  usage = " "
  usage = usage + " "
  usage = usage + "Usage: <wsadmin command> -f <this py script> <poolType - session or connection> <jmsProviderScopePath> <factoryName> \n   "
  usage = usage + " . . . and must have modified soap.client.props of target wsadmin profile if security is enabled\n"
  print "\n\n"
  #print '\n\nlen(sys.argv) is ' 
  #print len(sys.argv)
  if len(sys.argv) == 3:
      poolType=sys.argv[0]
      print "poolType :" + poolType

      jmsProviderScopePath=sys.argv[1]
      print "jmsProviderScopePath :" + jmsProviderScopePath
  
      factoryName=sys.argv[2]
      print "factoryName: " + factoryName
      
      fixUpPoolDefaultsByScope(poolType, jmsProviderScopePath, factoryName)
  else:
    print ""
    print "wrong number of args"
    print sys.argv
    print ""
    print usage
    sys.exit(1)

