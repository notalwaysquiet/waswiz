###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following procedures:
#getConnectionTimeout
#getMaxConnections
#getUnusedTimeout
#getMinConnections
#getConnectionPurgePolicy
#getSessionPurgePolicy
#getAgedTimeout
#getReapTime
#getTempModel
#getCCSID
#getUseNativeEncoding
#getSendAsync
#getReadAhead
#fixUpPoolDefaultsClusterLevel
#fixUpPoolDefaultsServerLevel
###############################################################################
# Notes
# The connection & session pool properties (in config file) are optional. For each connection pool prop, 
#  if it is set to "" then the admin console default is used 
#  (as specified in py).
# For the diff between connection pool and session pool see 
#   http://www-01.ibm.com/support/docview.wss?uid=swg21201242
# WAS to MQ product connectivity info center
#    http://publib.boulder.ibm.com/infocenter/prodconn/v1r0m0/topic/com.ibm.scenarios.wmqwasusing.doc/topics/tcpipconnuse_jmsconfactory.htm
# Note that WASv7.0.0.21 does not set the wsadmin default to match admin console default for pool props.
# As of Feb 2013, my script sets pool props to admin console defaults if not specified differently in config file.
# WASv7.0.0.21 admin console defaults for connection and session pool props are the same.

import sys
import AdminConfig
import Mq

#admin Console Default values for QCF Connection & session Pool Properties. Time is in seconds.
connectionTimeout = 180
maxConnections = 10
minConnections = 1
reapTime = 180
unusedTimeout = 1800
agedTimeout = 0
connectionPurgePolicy = "EntirePool"
sessionPurgePolicy = "FailingConnectionOnly"

CCSID = '1208'
useNativeEncoding = 'true'
sendAsync = 'QUEUE_DEFINED'
readAhead = 'QUEUE_DEFINED'

# tempModel. In admin console at [qcf] > Advanced properties > WebSphere MQ model queue name 
# tempModel. The model queue that is used as a basis for temporary queue definitions.
# Default is suppsed to be: SYSTEM.DEFAULT.MODEL.QUEUE but script-created qcf's do not get this set unless they explicitly set it
# if we didn't do this, actual wsadmin default is ''
tempModel = 'SYSTEM.DEFAULT.MODEL.QUEUE'

def getConnectionTimeout():
    return connectionTimeout
 
def getMaxConnections():
    return maxConnections

def getUnusedTimeout():
    return unusedTimeout

def getMinConnections():
    return minConnections

def getConnectionPurgePolicy():
    return connectionPurgePolicy

def getSessionPurgePolicy():
    return sessionPurgePolicy
    
def getAgedTimeout():
    return agedTimeout

def getReapTime():
    return reapTime
    
def getTempModel():
    return tempModel

def getCCSID():
    return CCSID

def getUseNativeEncoding():
    return useNativeEncoding

def getSendAsync():
    return sendAsync

def getReadAhead():
    return readAhead
    
def fixUpPoolDefaultsClusterLevel(clusterName, poolType, factoryName):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Fix up pool defaults for cluster-level MQ queue connection factory"
        print " clusterName:             "+clusterName
        print " poolType:                "+poolType
        print " factoryName:             "+factoryName
        msg = " Executing: MqDefaults.fixUpPoolDefaultsClusterLevel(\""+clusterName+"\", \""+poolType+"\", \""+factoryName+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        cellName = AdminConfig.showAttribute(AdminConfig.list('Cell'), 'name')
        #print cellName

        jmsProviderScopePath = '/Cell:' + cellName + '/ServerCluster:' + clusterName
        fixUpPoolDefaultsByScope(poolType, jmsProviderScopePath, factoryName)
    except:
        print "\n\n Exception in fixUpPoolDefaultsClusterLevel()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of fixUpPoolDefaultsClusterLevel()"
    
def fixUpPoolDefaultsServerLevel(nodeName, serverName, poolType, factoryName):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Fix up pool defaults for server-level MQ queue connection factory"
        print " nodeName:                "+nodeName
        print " serverName:              "+serverName
        print " poolType:                "+poolType
        print " factoryName:             "+factoryName
        msg = " Executing: MqDefaults.fixUpPoolDefaultsServerLevel(\""+nodeName+"\", \""+serverName+"\", \""+poolType+"\", \""+factoryName+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        cellName = AdminConfig.showAttribute(AdminConfig.list('Cell'), 'name')
        #print cellName

        #path = '/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + serverName + '/JMSProvider:' + JMSProviderName
        jmsProviderScopePath = '/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + serverName
        fixUpPoolDefaultsByScope(poolType, jmsProviderScopePath, factoryName)
    except:
        print "\n\n Exception in fixUpPoolDefaultsServerLevel()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of fixUpPoolDefaultsServerLevel()"
        
#--------------------------------------------------------------------
# Fix up connection pool defaults for MQ queue connection factory by passing in the scope path
# connection pool properties are in resources.xml
# note that admin-console-created qcf's gets connection pool element created in resources.xml 
# but only 1 prop (purgePolicy) vs. wsadmin-created qcf's which get full list of regular connection 
# pool props BUT ... defaults for connection pool properties for wsadmin-created qcf's do not match 
# admin-console-created ones (but note that defaults for connection pool properties for 
# wsadmin-created **datasources** DO match admin-console-created ones) -- in fact, connection pool 
# properties for wsadmin-created qcf do not even get put into resources.xml unless they are non-default, 
# in contrast to admin-console-created datasources, which get full set of pool props including advanced ones
# advanced properties are only for when connection pool > 500
# the below note applies to qcfs, not sure if it also applies to datasources
# note that AdminConfig.show(connectionPoolId) will show "advanced" as well as "regular" connection pool properties
#   but the "advanced" properties do not actually get put in resources.xml or any other file until you modify one of them
#   then all of the advanced properties are added to attributes for that connection pool element in resources.xml with default values for any you did not modify
#--------------------------------------------------------------------
def fixUpPoolDefaultsByScope(poolType, jmsProviderScopePath, factoryName):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Fix up pool defaults for MQ queue connection factory by passing in scope path"
        print " poolType:                "+poolType
        print " jmsProviderScopePath:    "+jmsProviderScopePath
        print " factoryName:             "+factoryName
        msg = " Executing: MqDefaults.fixUpPoolDefaultsByScope(\""+poolType+"\", \""+jmsProviderScopePath+"\", \""+factoryName+"\")"
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

        connectionTimeout = getConnectionTimeout()
        maxConnections = getMaxConnections()
        unusedTimeout = getUnusedTimeout()
        minConnections = getMinConnections()
        if poolType.lower() == 'connection':
            purgePolicy = getConnectionPurgePolicy()
        if poolType.lower() == 'session':
            purgePolicy = getSessionPurgePolicy()
        agedTimeout = getAgedTimeout()
        reapTime = getReapTime()
        
        Mq.modifyQueueConnectionFactoryPoolByScope(poolType, jmsProviderScopePath, factoryName, connectionTimeout, maxConnections, unusedTimeout, minConnections, purgePolicy, agedTimeout, reapTime)
    
    except:
        print "\n\n Exception in fixUpPoolDefaultsByScope()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "fixUpPoolDefaultsByScope()"
    

