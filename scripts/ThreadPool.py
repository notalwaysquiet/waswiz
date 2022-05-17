###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following procedures:
#   displaySettingsForThreadPool
###############################################################################
# Notes

# placing these methods here to bring thread pool info together
# thread pool settings for most thread pools are in server.xml (as a threadPools element) 
# but settings for work manager thread pools are in resources-pme.xml (as a factories element)
# see also WebContainer.setWebContainerThreadPoolProperties() and webContainerThreadPool clause in a WAS configurator config file

# windows commands - displayNonDefaultMqConnectionPoolForNamedAnimals
# wsadmin.bat -lang jython -f c:\qdr\ETP_dev/config_scripts/AuditConfig.py c:/qdr/ETP_dev/ displayNonDefaultMqConnectionPoolForNamedAnimals

import sys
import AdminConfig

import Utilities


# convenience method in case you don't have the serverId
def displayNonDefaultSettingsForThreadPools(nodeName, serverName):
    try:
        serverId = AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
        result = displayNonDefaultSettingsForThreadPools(serverId)
        return result
        
    except:
        print "Exception in displayNonDefaultSettingsForServerThreadPool() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])    
        sys.exit(1)

# all thread pools incl default work manager one 
# still to do: work managers other than default one
def displayNonDefaultSettingsForAllThreadPools(serverId):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Display properties for all thread pools (incl. default work manager)"
        print " serverId:                      "+serverId

        msg = " Executing: ThreadPool.displayNonDefaultSettingsForAllThreadPools(\""+serverId+"\")"
        print msg
        print "---------------------------------------------------------------"

        serverHasAllDefaults = "true"
        result = displayNonDefaultSettingsForServerThreadPools(serverId)
        if result == "server has modified server thread pool(s)":
            serverHasAllDefaults = "false"
        elif result == "server has no modified server thread pools":
            pass
        else:
            print "result from displayNonDefaultSettingsForServerThreadPools(serverId) not recognized"
            print "in displayNonDefaultSettingsForAllThreadPools(serverId)"
            sys.exit(1)
        
        result = displayNonDefaultSettingsForDefaultWorkManagerThreadPools(serverId)
        if result == "server has modified default work manager thread pool":
            serverHasAllDefaults = "false"
        elif result == "server has unmodified default work manager thread pool":
            pass
        else:
            print "result from displayNonDefaultSettingsForServerThreadPools(serverId) not recognized"
            print "in displayNonDefaultSettingsForAllThreadPools(serverId)"
            sys.exit(1)
            
        if serverHasAllDefaults == "true":
            print "server has all defaults"
            return "server has all defaults"
        else:
            print "server has modified pool(s)"
            return "server has modified pool(s)"
        
            
    except:
        print "Exception in displayNonDefaultSettingsForAllThreadPools()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

        
# "ServerThreadPool" includes the ones in server.xml (vs work manager ones)
# this kind of thread pool cannot be at cluster level, only server level
def displayNonDefaultSettingsForServerThreadPools(serverId):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Display properties for SERVER thread pools only (not incl. work managers)"
        print " serverId:                      "+serverId

        msg = " Executing: ThreadPool.displayNonDefaultSettingsForServerThreadPools(\""+serverId+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        serverHasAllDefaults = "true"
        serverName = serverId[serverId.find("/servers/")+9:serverId.find("|server.xml")]
        
        threadPoolName = "WebContainer"
        result = displayNonDefaultSettingsForServerThreadPool(serverId, threadPoolName)
        #print "result of displayNonDefaultSettingsForServerThreadPool is: " + str(result)
        if result != "pool has defaults":
            serverHasAllDefaults = "false"

        threadPoolName = "Default"
        result = displayNonDefaultSettingsForServerThreadPool(serverId, threadPoolName)
        #print "result of displayNonDefaultSettingsForServerThreadPool is: " + str(result)
        if result != "pool has defaults":
            serverHasAllDefaults = "false"
        
        threadPoolName = "ORB.thread.pool"
        result = displayNonDefaultSettingsForServerThreadPool(serverId, threadPoolName)
        #print "result of displayNonDefaultSettingsForServerThreadPool is: " + str(result)
        if result != "pool has defaults":
            serverHasAllDefaults = "false"

        if serverHasAllDefaults == "false":
            print
            print "server: " + serverName + " has at least one modified server thread pool(s)"
            return "server has modified server thread pool(s)"
        else:
            print "server: " + serverName + " has no modified server thread pool(s)"
            return "server has no modified server thread pools"
        
    except:
        print "Exception in displayNonDefaultSettingsForServerThreadPools() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])    
        sys.exit(1)

# does one thread pool at a time        
def displayNonDefaultSettingsForServerThreadPool(serverId, threadPoolName):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Display properties for SPECIFIED server thread pool only"
        print " serverId:                      "+serverId
        print " threadPoolName:                "+threadPoolName

        msg = " Executing: ThreadPool.displayNonDefaultSettingsForServerThreadPool(\""+serverId+", \""+threadPoolName+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        print
        print " Note: Only non-default properties shown."
        print
    
        import ThreadPoolDefaults 
        
        hasAllDefaults = "true"
        threadPoolList = AdminConfig.list('ThreadPool', serverId).splitlines()
        #print threadPoolList
        for poolId in threadPoolList:
            name = AdminConfig.showAttribute(poolId, 'name')
            if name == threadPoolName:
                #print AdminConfig.show(poolId)
                maximumSize = str(AdminConfig.showAttribute(poolId, 'maximumSize'))
                minimumSize = str(AdminConfig.showAttribute(poolId, 'minimumSize'))
                inactivityTimeout = str(AdminConfig.showAttribute(poolId, 'inactivityTimeout'))
                isGrowable = str(AdminConfig.showAttribute(poolId, 'isGrowable'))
                if threadPoolName == "WebContainer":
                    defaultMaximumSize = str(ThreadPoolDefaults.getWebContainerMaximumSize())
                    if maximumSize != defaultMaximumSize:
                        hasAllDefaults = "false"
                        print "****************************************************************************************************"
                        print "WebContainer maximumSize: " + maximumSize
                        print " vs default: " + defaultMaximumSize
                        print "****************************************************************************************************"
                    defaultMinimumSize = str(ThreadPoolDefaults.getWebContainerMinimumSize())
                    if minimumSize != defaultMinimumSize:
                        hasAllDefaults = "false"
                        print "****************************************************************************************************"
                        print "WebContainer minimumSize: " + minimumSize
                        print " vs default: " + defaultMinimumSize
                        print "****************************************************************************************************"
                    defaultInactivityTimeout = str(ThreadPoolDefaults.getWebContainerThreadInactivityTimeout())
                    if inactivityTimeout != defaultInactivityTimeout:
                        hasAllDefaults = "false"
                        print "****************************************************************************************************"
                        print "WebContainer inactivityTimeout: " + inactivityTimeout
                        print " vs default: " + defaultInactivityTimeout
                        print "****************************************************************************************************"
                    defaultIsGrowable = str(ThreadPoolDefaults.getWebContainerGrowable())
                    if isGrowable != defaultIsGrowable:
                        hasAllDefaults = "false"
                        print "****************************************************************************************************"
                        print "WebContainer isGrowable: " + isGrowable
                        print " vs default: " + defaultIsGrowable
                        print "****************************************************************************************************"
                        
                elif threadPoolName == "Default":
                    defaultMaximumSize = str(ThreadPoolDefaults.getDefaultMaximumSize())
                    if maximumSize != defaultMaximumSize:
                        hasAllDefaults = "false"
                        print "****************************************************************************************************"
                        print "Default maximumSize: " + maximumSize
                        print " vs default: " + defaultMaximumSize
                        print "****************************************************************************************************"
                    defaultMinimumSize = str(ThreadPoolDefaults.getDefaultMinimumSize())
                    if minimumSize != defaultMinimumSize:
                        hasAllDefaults = "false"
                        print "****************************************************************************************************"
                        print "Default minimumSize: " + minimumSize
                        print " vs default: " + defaultMinimumSize
                        print "****************************************************************************************************"
                    defaultInactivityTimeout = str(ThreadPoolDefaults.getDefaultThreadInactivityTimeout())
                    if inactivityTimeout != defaultInactivityTimeout:
                        hasAllDefaults = "false"
                        print "****************************************************************************************************"
                        print "Default inactivityTimeout: " + inactivityTimeout
                        print " vs default: " + defaultInactivityTimeout
                        print "****************************************************************************************************"
                    defaultIsGrowable = str(ThreadPoolDefaults.getDefaultGrowable())
                    if isGrowable != defaultIsGrowable:
                        hasAllDefaults = "false"
                        print "****************************************************************************************************"
                        print "Default isGrowable: " + isGrowable
                        print " vs default: " + defaultIsGrowable
                        print "****************************************************************************************************"


                                            
                elif threadPoolName == "ORB.thread.pool":
                    defaultMaximumSize = str(ThreadPoolDefaults.getORBMaximumSize())
                    if maximumSize != defaultMaximumSize:
                        hasAllDefaults = "false"
                        print "****************************************************************************************************"
                        print "ORB.thread.pool maximumSize: " + maximumSize
                        print " vs default: " + defaultMaximumSize
                        print "****************************************************************************************************"
                    defaultMinimumSize = str(ThreadPoolDefaults.getORBMinimumSize())
                    if minimumSize != defaultMinimumSize:
                        hasAllDefaults = "false"
                        print "****************************************************************************************************"
                        print "ORB.thread.pool minimumSize: " + minimumSize
                        print " vs default: " + defaultMinimumSize
                        print "****************************************************************************************************"
                    defaultInactivityTimeout = str(ThreadPoolDefaults.getORBThreadInactivityTimeout())
                    if inactivityTimeout != defaultInactivityTimeout:
                        hasAllDefaults = "false"
                        print "****************************************************************************************************"
                        print "ORB.thread.pool inactivityTimeout: " + inactivityTimeout
                        print " vs default: " + defaultInactivityTimeout
                        print "****************************************************************************************************"
                    defaultIsGrowable = str(ThreadPoolDefaults.getORBGrowable())
                    if isGrowable != defaultIsGrowable:
                        hasAllDefaults = "false"
                        print "****************************************************************************************************"
                        print "ORB.thread.pool isGrowable: " + isGrowable
                        print " vs default: " + defaultIsGrowable
                        print "****************************************************************************************************"

                else:
                    print "thread pool name: " + threadPoolName + " not supported"
                    sys.exit(1) 
                
                if hasAllDefaults == "false":
                    print "pool modified"
                    return "pool modified"
                else:
                    print "pool has defaults"
                    return "pool has defaults"
    except:
        print "Exception in displayNonDefaultSettingsForServerThreadPool() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])    
        sys.exit(1)


# this kind of thread pool can be at any level, e.g., cluster, server, node, cell
# this method only looks at default work manager, not explicitly created work managers
#   note that admin console default for Default work manager is not growable but for a new work manager, is growable
#   I am using same defaults for both as it seems like a bad idea to make work manager pool be growable
def displayNonDefaultSettingsForDefaultWorkManagerThreadPool(scopeId):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Display properties for default work manager at specified scope"
        print " scopeId:                      "+scopeId

        msg = " Executing: ThreadPool.displayNonDefaultSettingsForDefaultWorkManagerThreadPool(\""+scopeId+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        print
        print " Notes: "
        print "   1. Only non-default properties shown."
        print "   2. Method only looking at Default work manager. "
        print
    
        import ThreadPoolDefaults 

        hasAllDefaults = "true"
        
        workManagerName = "DefaultWorkManager"
        workManagerList = Utilities.convertToList(AdminConfig.list('WorkManagerInfo', scopeId))
        for workManagerId in workManagerList:
            name = AdminConfig.showAttribute(workManagerId, "name")
            if (name == workManagerName):
                maximumSize = str(AdminConfig.showAttribute(workManagerId, 'maxThreads'))
                defaultMaximumSize = str(ThreadPoolDefaults.getDefaultWorkManagerMaximumSize())
                if maximumSize != defaultMaximumSize:
                    hasAllDefaults = "false"
                    print "****************************************************************************************************"
                    print "DefaultWorkManager maximumSize: " + maximumSize
                    print " vs default: " + defaultMaximumSize
                    print "****************************************************************************************************"
                
                minimumSize = str(AdminConfig.showAttribute(workManagerId, 'minThreads'))
                defaultMinimumSize = str(ThreadPoolDefaults.getDefaultWorkManagerMinimumSize())
                if minimumSize != defaultMinimumSize:
                    hasAllDefaults = "false"
                    print "****************************************************************************************************"
                    print "DefaultWorkManager minimumSize: " + minimumSize
                    print " vs default: " + defaultMinimumSize
                    print "****************************************************************************************************"
                
                workTimeout = str(AdminConfig.showAttribute(workManagerId, 'workTimeout'))
                defaultworkTimeout = str(ThreadPoolDefaults.getDefaultWorkManagerWorkTimeout())
                if workTimeout != defaultworkTimeout:
                    hasAllDefaults = "false"
                    print "****************************************************************************************************"
                    print "DefaultWorkManager workTimeout: " + workTimeout
                    print " vs default: " + defaultworkTimeout
                    print "****************************************************************************************************"
                
                isGrowable = AdminConfig.showAttribute(workManagerId, 'isGrowable')
                defaultIsGrowable = ThreadPoolDefaults.getDefaultWorkManagerGrowable()
                if isGrowable != defaultIsGrowable:
                    hasAllDefaults = "false"
                    print "****************************************************************************************************"
                    print "DefaultWorkManager isGrowable: " + isGrowable
                    print " vs default: " + defaultIsGrowable
                    print "****************************************************************************************************"
                
                workReqQSize = str(AdminConfig.showAttribute(workManagerId, 'workReqQSize'))
                defaultWorkReqQSize = str(ThreadPoolDefaults.getDefaultWorkManagerQueueSiz())
                if workReqQSize != defaultWorkReqQSize:
                    hasAllDefaults = "false"
                    print "****************************************************************************************************"
                    print "DefaultWorkManager workReqQSize: " + workReqQSize
                    print " vs default: " + defaultWorkReqQSize
                    print "****************************************************************************************************"
                
                workReqQFullAction = str(AdminConfig.showAttribute(workManagerId, 'workReqQFullAction'))
                if workReqQFullAction == "0" or workReqQFullAction == 0:
                    workReqQFullAction = "block"
                elif workReqQFullAction == "1" or workReqQFullAction == 1:
                    workReqQFullAction = "fail"
                defaultWorkReqQFullAction = str(ThreadPoolDefaults.getDefaultWorkManagerQueueFullAction()).lower()
                if workReqQFullAction != defaultWorkReqQFullAction:
                    hasAllDefaults = "false"
                    print "****************************************************************************************************"
                    print "DefaultWorkManager workReqQFullAction: " + workReqQFullAction
                    print " vs default: " + defaultWorkReqQFullAction
                    print "****************************************************************************************************"

                numAlarmThreads = str(AdminConfig.showAttribute(workManagerId, 'numAlarmThreads'))
                defaultNumAlarmThreads = str(ThreadPoolDefaults.getDefaultWorkManagerNumAlarmThreads())
                if numAlarmThreads != defaultNumAlarmThreads:
                    hasAllDefaults = "false"
                    print "****************************************************************************************************"
                    print "DefaultWorkManager numAlarmThreads: " + numAlarmThreads
                    print " vs default: " + defaultNumAlarmThreads
                    print "****************************************************************************************************"

                threadPriority = str(AdminConfig.showAttribute(workManagerId, 'threadPriority'))
                defaultThreadPriority = str(ThreadPoolDefaults.getDefaultWorkManagerThreadPriority())
                if threadPriority != defaultThreadPriority:
                    hasAllDefaults = "false"
                    print "****************************************************************************************************"
                    print "DefaultWorkManager threadPriority: " + threadPriority
                    print " vs default: " + defaultThreadPriority
                    print "****************************************************************************************************"
                    
                break
        
        if hasAllDefaults == "false":
            print "pool modified"
            return "pool modified"
        else:
            print "pool has defaults"
            return "pool has defaults"
            
    except:
        print "Exception in displayNonDefaultSettingsForDefaultWorkManagerThreadPool() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])    
        sys.exit(1)        

        
# this kind of thread pool can be at any level, e.g., cluster, server, node, cell
# this method only compares to default settings, not to server config file
# for explicitly created work managers, we really should compare them 
#   to the WAS configurator config file, not to defaults for a new work manager
def displayNonDefaultSettingsForExplicitlyCreatedWorkManagerThreadPool(scopeId):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Display non-default properties for explicitly created work manager(s) at specified scope"
        print " scopeId:                      "+scopeId

        msg = " Executing: ThreadPool.displayNonDefaultSettingsForExplicitlyCreatedWorkManagerThreadPool(\""+scopeId+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        print
        print " Notes: "
        print "   1. Only non-default properties shown."
        print "   2. Method only looking at non-default props for explicitly created work manager(s). Not comparing to configurator file."
        print "   3. The admin console defaults for Default work manager and a new explicitly created work manager are slightly different:"
        print "      newly created work managers are growable by default (probably not a good idea)."
        print "      This method uses the same defaults as for Default work manager, not for newly created work manager (i.e., NOT growable)."
        print
    
        import ThreadPoolDefaults 

        hasNoExplicitlyCreatedWorkManagers = "true"
        hasAllDefaults = "true"
        
        workManagerList = Utilities.convertToList(AdminConfig.list('WorkManagerInfo', scopeId))
        for workManagerId in workManagerList:
            name = AdminConfig.showAttribute(workManagerId, "name")
            if name != "DefaultWorkManager" and name != "AsyncRequestDispatcherWorkManager":
                hasNoExplicitlyCreatedWorkManagers = "false"
                print
                print "****************************************************************************************************"
                print "****************************************************************************************************"
                print "Work manager name: " + name
                print "****************************************************************************************************"
                print "****************************************************************************************************"            
                print
                maximumSize = str(AdminConfig.showAttribute(workManagerId, 'maxThreads'))
                defaultMaximumSize = str(ThreadPoolDefaults.getDefaultWorkManagerMaximumSize())
                if maximumSize != defaultMaximumSize:
                    hasAllDefaults = "false"
                    print "****************************************************************************************************"
                    print "Work manager name: " + name
                    print " maximumSize: " + maximumSize
                    print " vs default: " + defaultMaximumSize
                    print "****************************************************************************************************"
                
                minimumSize = str(AdminConfig.showAttribute(workManagerId, 'minThreads'))
                defaultMinimumSize = str(ThreadPoolDefaults.getDefaultWorkManagerMinimumSize())
                if minimumSize != defaultMinimumSize:
                    hasAllDefaults = "false"
                    print "****************************************************************************************************"
                    print "Work manager name: " + name                
                    print " minimumSize: " + minimumSize
                    print " vs default: " + defaultMinimumSize
                    print "****************************************************************************************************"
                
                workTimeout = str(AdminConfig.showAttribute(workManagerId, 'workTimeout'))
                defaultworkTimeout = str(ThreadPoolDefaults.getDefaultWorkManagerWorkTimeout())
                if workTimeout != defaultworkTimeout:
                    hasAllDefaults = "false"
                    print "****************************************************************************************************"
                    print "Work manager name: " + name                
                    print " workTimeout: " + workTimeout
                    print " vs default: " + defaultworkTimeout
                    print "****************************************************************************************************"
                
                isGrowable = AdminConfig.showAttribute(workManagerId, 'isGrowable')
                defaultIsGrowable = ThreadPoolDefaults.getDefaultWorkManagerGrowable()
                if isGrowable != defaultIsGrowable:
                    hasAllDefaults = "false"
                    print "****************************************************************************************************"
                    print "Work manager name: " + name
                    print " isGrowable: " + isGrowable
                    print " vs default: " + defaultIsGrowable
                    print "****************************************************************************************************"
                
                workReqQSize = str(AdminConfig.showAttribute(workManagerId, 'workReqQSize'))
                defaultWorkReqQSize = str(ThreadPoolDefaults.getDefaultWorkManagerQueueSiz())
                if workReqQSize != defaultWorkReqQSize:
                    hasAllDefaults = "false"
                    print "****************************************************************************************************"
                    print " workReqQSize: " + workReqQSize
                    print " vs default: " + defaultWorkReqQSize
                    print "****************************************************************************************************"
                
                workReqQFullAction = str(AdminConfig.showAttribute(workManagerId, 'workReqQFullAction'))
                if workReqQFullAction == "0" or workReqQFullAction == 0:
                    workReqQFullAction = "block"
                elif workReqQFullAction == "1" or workReqQFullAction == 1:
                    workReqQFullAction = "fail"
                defaultWorkReqQFullAction = str(ThreadPoolDefaults.getDefaultWorkManagerQueueFullAction()).lower()
                if workReqQFullAction != defaultWorkReqQFullAction:
                    hasAllDefaults = "false"
                    print "****************************************************************************************************"
                    print "Work manager name: " + name
                    print " workReqQFullAction: " + workReqQFullAction
                    print " vs default: " + defaultWorkReqQFullAction
                    print "****************************************************************************************************"

                numAlarmThreads = str(AdminConfig.showAttribute(workManagerId, 'numAlarmThreads'))
                defaultNumAlarmThreads = str(ThreadPoolDefaults.getDefaultWorkManagerNumAlarmThreads())
                if numAlarmThreads != defaultNumAlarmThreads:
                    hasAllDefaults = "false"
                    print "****************************************************************************************************"
                    print "Work manager name: " + name
                    print " numAlarmThreads: " + numAlarmThreads
                    print " vs default: " + defaultNumAlarmThreads
                    print "****************************************************************************************************"

                threadPriority = str(AdminConfig.showAttribute(workManagerId, 'threadPriority'))
                defaultThreadPriority = str(ThreadPoolDefaults.getDefaultWorkManagerThreadPriority())
                if threadPriority != defaultThreadPriority:
                    hasAllDefaults = "false"
                    print "****************************************************************************************************"
                    print "Work manager name: " + name
                    print " threadPriority: " + threadPriority
                    print " vs default: " + defaultThreadPriority
                    print "****************************************************************************************************"
        
        if hasNoExplicitlyCreatedWorkManagers == "true":
            return "no work managers"
        else:
            if hasAllDefaults == "false":
                print "pool modified"
                return "pool modified"
            else:
                print "pool has defaults"
                return "pool has defaults"
            
    except:
        print "Exception in displayNonDefaultSettingsForExplicitlyCreatedWorkManagerThreadPool() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])    
        sys.exit(1)        

                
