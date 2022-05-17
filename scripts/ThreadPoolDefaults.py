###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following procedures:

###############################################################################
# Notes
# http://pic.dhe.ibm.com/infocenter/wasinfo/v7r0/topic/com.ibm.websphere.nd.doc/info/ae/ae/uejb_rthrd.html
# http://www.ibm.com/developerworks/websphere/techjournal/0909_blythe/0909_blythe.html
#--------------------------------------------------------------------
# Set global constants
#--------------------------------------------------------------------

#admin Console Default values 
#minimumSize specifies the minimum number of threads to allow in the pool. When an application server starts, no threads are initially assigned to the thread pool. Threads are added to the thread pool as the workload assigned to the application server requires them, until the number of threads in the pool equals the number specified in the Minimum size field. After this point in time, additional threads are added and removed as the workload changes. However, the number of threads in the pool never decreases below the number specified in the Minimum size field, even if some of the threads are idle.
#maximumSize specifies the maximum number of threads to maintain in the default thread pool.
#threadInactivityTimeout specifies the number of milliseconds of inactivity that should elapse before a thread is reclaimed. A value of 0 indicates not to wait and a negative value (less than 0) means to wait forever.
#growable specifies whether the number of threads can increase beyond the maximum size that is configured for the thread pool.
#The maximum number of threads that can be created is constrained only within the limits of the Java virtual machine and the operating system. When a thread pool that is allowed to grow expands beyond the maximum size, the additional threads are not reused and are discarded from the pool after required work items are completed.


# Web container: Used when requests come in over HT.
# Default: Used when requests come in for a message driven bean or if a particular transport chain has not been defined to a specific thread pool.
# ORB: Used when remote requests come in over RMI/IIOP for an enterprise bean from an EJB application client, remote EJB interface, or another application server.


webContainerMinimumSize = 50
#webContainerMaximumSize admin console default is 50, but we might want to set it to 100 as default
webContainerMaximumSize = 100
webContainerThreadInactivityTimeout = 60000
webContainerGrowable = "false"

defaultMinimumSize = 20
defaultMaximumSize = 20
defaultThreadInactivityTimeout = 5000
defaultGrowable = "false"

ORBMinimumSize = 10
ORBMaximumSize = 50
ORBThreadInactivityTimeout = 3500
ORBGrowable = "false"

DefaultWorkManagerMinimumSize = 1
DefaultWorkManagerMaximumSize = 10
# in milliseconds
DefaultWorkManagerWorkTimeout = 0
DefaultWorkManagerGrowable = "false"
#Work request queue size in numbers of objects
DefaultWorkManagerQueueSize = 0
# Work request queue full action - Block or Fail
DefaultWorkManagerQueueFullAction = "block"
DefaultWorkManagerNumAlarmThreads = 5
DefaultWorkManagerThreadPriority = 5



def getWebContainerMinimumSize():
    return webContainerMinimumSize
    
def getWebContainerMaximumSize():
    return webContainerMaximumSize

def getWebContainerThreadInactivityTimeout():
    return webContainerThreadInactivityTimeout
 
def getWebContainerGrowable():
    return webContainerGrowable

    
    
def getDefaultMinimumSize():
    return defaultMinimumSize
    
def getDefaultMaximumSize():
    return defaultMaximumSize

def getDefaultThreadInactivityTimeout():
    return defaultThreadInactivityTimeout
 
def getDefaultGrowable():
    return defaultGrowable

    

    
def getORBMinimumSize():
    return ORBMinimumSize
    
def getORBMaximumSize():
    return ORBMaximumSize

def getORBThreadInactivityTimeout():
    return ORBThreadInactivityTimeout
 
def getORBGrowable():
    return ORBGrowable

    
def getDefaultWorkManagerMinimumSize():
    return DefaultWorkManagerMinimumSize
    
def getDefaultWorkManagerMaximumSize():
    return DefaultWorkManagerMaximumSize

def getDefaultWorkManagerWorkTimeout():
    return DefaultWorkManagerWorkTimeout
 
def getDefaultWorkManagerGrowable():
    return DefaultWorkManagerGrowable    

def getDefaultWorkManagerQueueSiz():
    return DefaultWorkManagerQueueSize    

def getDefaultWorkManagerQueueFullAction():
    return DefaultWorkManagerQueueFullAction
    
def getDefaultWorkManagerNumAlarmThreads():
    return DefaultWorkManagerNumAlarmThreads

def getDefaultWorkManagerThreadPriority():
    return DefaultWorkManagerThreadPriority
