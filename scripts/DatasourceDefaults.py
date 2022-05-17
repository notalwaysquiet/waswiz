###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following procedures:
#getConnectionTimeout
#getMaxConnections
#getUnusedTimeout
#getMinConnections
#getPurgePolicy
#getAgedTimeout
#getReapTime

###############################################################################
# Notes
# http://pic.dhe.ibm.com/infocenter/wasinfo/v7r0/topic/com.ibm.websphere.nd.doc/info/ae/ae/udat_conpoolset.html

#--------------------------------------------------------------------
# Set global constants
#--------------------------------------------------------------------
#admin Console Default values for Datasource Connection Pool Properties
# timeouts re in seconds
connectionTimeout = 180
maxConnections = 10
unusedTimeout = 1800
minConnections = 1
# wsadmin default is FailingConnectionOnly: not the same as admin console default, which is "EntirePool"
# despite the fact that I created them with AdminConfig.createUsingTemplate using built-in jdbc templates (in Datasources.py)
# this is not what the info center says http://pic.dhe.ibm.com/infocenter/wasinfo/v7r0/topic/com.ibm.websphere.nd.doc/info/ae/ae/udat_conpoolset.html
# set this to the wsadmin default, when running script to audit prod to see which datasources have been manually changed
# set this to admin console default "EntirePool" to make datasource creation script use that setting, which is IBM's recommendation
#purgePolicy = "FailingConnectionOnly"
purgePolicy = "EntirePool"
agedTimeout = 0
reapTime = 180



def getConnectionTimeout():
    return connectionTimeout
 
def getMaxConnections():
    return maxConnections

def getUnusedTimeout():
    return unusedTimeout

def getMinConnections():
    return minConnections

def getPurgePolicy():
    return purgePolicy

def getAgedTimeout():
    return agedTimeout

def getReapTime():
    return reapTime
    
