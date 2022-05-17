###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following procedures:
#   modifyAsynchBeanWorkManager
#   createAsynchBeanWorkManagerByProviderId
#   createServerLevelAsynchBeanWorkManager
#   createClusterLevelAsynchBeanWorkManager
#   displayNonDefaultExplicitlyCreatedWorkManagerSettingsByScopePath
#   displayNonDefaultExplicitlyCreatedWorkManagerSettingsByServer
#   displayNonDefaultExplicitlyCreatedWorkManagerSettingsByCluster
###############################################################################
# Notes


import sys
import AdminConfig
import AdminControl

# modules that are searched for in the same directory as this script
import ItemExists



''' Modify an existing asynch bean work manager '''
def modifyAsynchBeanWorkManager(workManagerId, name, jndiName, category, description, workTimeout, workReqQSize, workReqQFullAction, numAlarmThreads, minThreads, maxThreads, threadPriority, isGrowable, serviceNameString):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Modify an existing asynch bean work manager"
        print " workManagerId:        "+str(workManagerId)
        print " name:                 "+name
        print " jndiName:             "+jndiName
        print " category:             "+category        
        print " description:          "+description
        print " workTimeout:          "+str(workTimeout)
        print " workReqQSize:         "+str(workReqQSize)
        print " workReqQFullAction:   "+str(workReqQFullAction)
        print " numAlarmThreads:      "+str(numAlarmThreads)
        print " minThreads:           "+str(minThreads)
        print " maxThreads:           "+str(maxThreads)
        print " threadPriority:       "+str(threadPriority)
        print " isGrowable:           "+isGrowable
        print " serviceNameString:    "+serviceNameString        
        msg = " Executing: WorkManagers.modifyAsynchBeanWorkManager(\""+str(workManagerId)+"\", \""+name+"\", \""+jndiName+"\", \""+category+"\", \""+description+"\", \""+str(workTimeout)+"\", \""+str(workReqQSize)+"\", \""+str(workReqQFullAction)+"\", \""+str(numAlarmThreads)+"\", \""+str(minThreads)+"\", \""+str(maxThreads)+"\", \""+str(threadPriority)+"\", \""+isGrowable+"\", \""+serviceNameString+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        nameAttr = ["name", name]
        jndiNameAttr = ["jndiName", jndiName]
        categoryAttr = ["category", category]
        descriptionAttr = ["description", description]
        workTimeoutAttr = ["workTimeout", workTimeout]
        workReqQSizeAttr = ["workReqQSize", workReqQSize]
        workReqQFullActionAttr = ["workReqQFullAction", workReqQFullAction]
        numAlarmThreadsAttr = ["numAlarmThreads", numAlarmThreads]
        minThreadsAttr = ["minThreads", minThreads]
        maxThreadsAttr = ["maxThreads", maxThreads]
        threadPriorityAttr = ["threadPriority", threadPriority]
        isGrowableAttr = ["isGrowable", isGrowable]
        serviceNamesAttr = ["serviceNames", serviceNameString]

        attrs = [nameAttr, jndiNameAttr, categoryAttr, descriptionAttr, workTimeoutAttr, workReqQSizeAttr, workReqQFullActionAttr, numAlarmThreadsAttr, minThreadsAttr, maxThreadsAttr, threadPriorityAttr, isGrowableAttr, serviceNamesAttr ]

        print AdminConfig.modify(workManagerId, attrs)
        print "Modified work manager id:"
        print workManagerId
    except:
        print "Exception in modifyAsynchBeanWorkManager() when modifying config item"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        AdminConfig.save()
    except:
        print "Exception in modifyAsynchBeanWorkManager() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry


''' Create new  asynch bean work manager '''
def createAsynchBeanWorkManagerByProviderId(workManagerProviderId, attrs):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create new asynch bean work manager by passing in scoped provider id"
        print " workManagerProviderId:     "+workManagerProviderId
        print ""
        print " attrs:                     "+str(attrs)
        print ""
        msg = " Executing: WorkManagers.createAsynchBeanWorkManagerByProviderId(\""+workManagerProviderId+"\", \""+str(attrs)+"\")"
        print msg
        print "---------------------------------------------------------------"

        print AdminConfig.create("WorkManagerInfo", workManagerProviderId, attrs)
    except:
        print "Exception in createAsynchBeanWorkManagerByProviderId() when creating config item"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "Exception in createAsynchBeanWorkManagerByProviderId() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of createAsynchBeanWorkManagerByProviderId()"


''' Create new  asynch bean work manager at the server level '''
def createServerLevelAsynchBeanWorkManager(nodeName, serverName, name, jndiName, category, description, workTimeout, workReqQSize, workReqQFullAction, numAlarmThreads, minThreads, maxThreads, threadPriority, isGrowable, serviceNameString):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create new asynch bean work manager at server level"
        print " nodeName:                  "+nodeName
        print " serverName:                "+serverName
        print " name:                      "+name
        print " jndiName:                  "+jndiName
        print " category:                  "+category        
        print " description:               "+description
        print " workTimeout:               "+str(workTimeout)
        print " workReqQSize:              "+str(workReqQSize)
        print " workReqQFullAction:        "+str(workReqQFullAction)
        print " numAlarmThreads:           "+str(numAlarmThreads)
        print " minThreads:                "+str(minThreads)
        print " maxThreads:                "+str(maxThreads)
        print " threadPriority:            "+str(threadPriority)
        print " isGrowable:                "+isGrowable
        print " serviceNameString:         "+serviceNameString
        msg = " Executing: WorkManagers.createServerLevelAsynchBeanWorkManager(\""+nodeName+"\", \""+serverName+"\", \""+name+"\", \""+jndiName+"\", \""+category+"\", \""+description+"\", \""+str(workTimeout)+"\", \""+str(workReqQSize)+"\", \""+str(workReqQFullAction)+"\", \""+str(numAlarmThreads)+"\", \""+str(minThreads)+"\", \""+str(maxThreads)+"\", \""+str(threadPriority)+"\", \""+isGrowable+"\", \""+serviceNameString+"\")"
        print msg
        print "---------------------------------------------------------------"

        # checking if the parameter value exists
        nodeExist = AdminConfig.getid("/Node:"+nodeName+"/")
        if (len(nodeExist) == 0):
            print "\n Error: The specified node: " + nodeName + " does not exist.\n"
            sys.exit(1)
        serverId = AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
        if (serverId == ''):
            print "\n Error: The specified server: " + serverName + " does not exist.\n"
            sys.exit(1)
    except:
        print "Exception in createServerLevelAsynchBeanWorkManager() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:    

        
        #serviceNameString = "AppProfileService;com.ibm.ws.i18n;security;UserWorkArea"
        #serviceNameString = "AppProfileService;com.ibm.ws.i18n"
        
        nameAttr = ["name", name]
        jndiNameAttr = ["jndiName", jndiName]
        categoryAttr = ["category", category]
        descriptionAttr = ["description", description]
        workTimeoutAttr = ["workTimeout", workTimeout]
        workReqQSizeAttr = ["workReqQSize", workReqQSize]
        workReqQFullActionAttr = ["workReqQFullAction", workReqQFullAction]
        numAlarmThreadsAttr = ["numAlarmThreads", numAlarmThreads]
        minThreadsAttr = ["minThreads", minThreads]
        maxThreadsAttr = ["maxThreads", maxThreads]
        threadPriorityAttr = ["threadPriority", threadPriority]
        isGrowableAttr = ["isGrowable", isGrowable]
        serviceNamesAttr = ["serviceNames", serviceNameString]

        attrs = [nameAttr, jndiNameAttr, categoryAttr, descriptionAttr, workTimeoutAttr, workReqQSizeAttr, workReqQFullActionAttr, numAlarmThreadsAttr, minThreadsAttr, maxThreadsAttr, threadPriorityAttr, isGrowableAttr, serviceNamesAttr ]

        workManagerProviderId = ItemExists.serverScopedWorkManagerProviderExists(nodeName, serverName)
        createAsynchBeanWorkManagerByProviderId(workManagerProviderId, attrs)
        #print AdminConfig.create("WorkManagerInfo", workManagerProviderId, attrs)
    except:
        print "Exception in createServerLevelAsynchBeanWorkManager() when calling submethod"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        AdminConfig.save()
    except:
        print "Exception in createServerLevelAsynchBeanWorkManager() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of createServerLevelAsynchBeanWorkManager()"


''' Create new  asynch bean work manager at the cluster level '''
def createClusterLevelAsynchBeanWorkManager(clusterName, name, jndiName, category, description, workTimeout, workReqQSize, workReqQFullAction, numAlarmThreads, minThreads, maxThreads, threadPriority, isGrowable, serviceNameString):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create new asynch bean work manager at cluster level"
        print " clusterName:               "+clusterName
        print " name:                      "+name
        print " jndiName:                  "+jndiName
        print " category:                  "+category        
        print " description:               "+description
        print " workTimeout:               "+str(workTimeout)
        print " workReqQSize:              "+str(workReqQSize)
        print " workReqQFullAction:        "+str(workReqQFullAction)
        print " numAlarmThreads:           "+str(numAlarmThreads)
        print " minThreads:                "+str(minThreads)
        print " maxThreads:                "+str(maxThreads)
        print " threadPriority:            "+str(threadPriority)
        print " isGrowable:                "+isGrowable
        msg = " Executing: WorkManagers.createClusterLevelAsynchBeanWorkManager(\""+clusterName+"\", \""+name+"\", \""+jndiName+"\", \""+category+"\", \""+description+"\", \""+str(workTimeout)+"\", \""+str(workReqQSize)+"\", \""+str(workReqQFullAction)+"\", \""+str(numAlarmThreads)+"\", \""+str(minThreads)+"\", \""+str(maxThreads)+"\", \""+str(threadPriority)+"\", \""+isGrowable+"\")"
        print msg
        print "---------------------------------------------------------------"

        # checking if the parameter value exists
        clusterExist = AdminConfig.getid("/ServerCluster:"+clusterName+"/")
        if (len(clusterExist) == 0):
            print "\n Error: The specified cluster: " + clusterName + " does not exist.\n"
            sys.exit(1)
    except:
        print "Exception in createClusterLevelAsynchBeanWorkManager() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:    
        
        #serviceNameString = "AppProfileService;com.ibm.ws.i18n;security;UserWorkArea"
        
        nameAttr = ["name", name]
        jndiNameAttr = ["jndiName", jndiName]
        categoryAttr = ["category", category]
        descriptionAttr = ["description", description]
        workTimeoutAttr = ["workTimeout", workTimeout]
        workReqQSizeAttr = ["workReqQSize", workReqQSize]
        workReqQFullActionAttr = ["workReqQFullAction", workReqQFullAction]
        numAlarmThreadsAttr = ["numAlarmThreads", numAlarmThreads]
        minThreadsAttr = ["minThreads", minThreads]
        maxThreadsAttr = ["maxThreads", maxThreads]
        threadPriorityAttr = ["threadPriority", threadPriority]
        isGrowableAttr = ["isGrowable", isGrowable]
        serviceNamesAttr = ["serviceNames", serviceNameString]

        attrs = [nameAttr, jndiNameAttr, categoryAttr, descriptionAttr, workTimeoutAttr, workReqQSizeAttr, workReqQFullActionAttr, numAlarmThreadsAttr, minThreadsAttr, maxThreadsAttr, threadPriorityAttr, isGrowableAttr, serviceNamesAttr ]

        workManagerProviderId = ItemExists.clusterScopedWorkManagerProviderExists(clusterName)
        createAsynchBeanWorkManagerByProviderId(workManagerProviderId, attrs)
        #print AdminConfig.create("WorkManagerInfo", workManagerProviderId, attrs)
    except:
        print "Exception in createClusterLevelAsynchBeanWorkManager() when calling submethod"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        AdminConfig.save()
    except:
        print "Exception in createClusterLevelAsynchBeanWorkManager() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of createClusterLevelAsynchBeanWorkManager()"


def displayNonDefaultExplicitlyCreatedWorkManagerSettingsByScopePath(scopePath):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Display tuning properties for explicitly created workManager"
        print " scopePath:                      "+scopePath

        msg = " Executing: workManagers.displayNonDefaultExplicitlyCreatedWorkManagerSettingsByScopePath(\""+scopePath+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        print
        print " Note: Only non-default properties shown."
        print 
        print " workManagers that were ADMIN-CONSOLE-created have purge policy EntirePool"
        print "  vs WSADMIN-created ones prior to Oct 2013 - FailingConnectionOnly"
        print
    
        import ThreadPoolDefaults
        

        # checking if the parameter value exists
        #scopePath = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        path=scopePath
        objectId= AdminConfig.getid(path)
        if (len(objectId) == 0):
            print "\n\nNo object can be found at specified scope: " + scopePath 
            sys.exit(1)
        workManagerListString = AdminConfig.list('WorkManagerInfo', objectId)
        workManagerList = workManagerListString.splitlines()
        print workManagerList

        for workManagerId in workManagerList:
            name = AdminConfig.showAttribute(workManagerId, 'name')
            allDefaults = "true"
            if name != "AsyncRequestDispatcherWorkManager" and name != "DefaultWorkManager": 
                print
                print name
                workTimeout = str(AdminConfig.showAttribute(connectionPoolId, 'workTimeout'))
                workReqQSize = str(AdminConfig.showAttribute(connectionPoolId, 'workReqQSize'))
                workReqQFullAction = str(AdminConfig.showAttribute(connectionPoolId, 'workReqQFullAction'))
                numAlarmThreads = str(AdminConfig.showAttribute(connectionPoolId, 'numAlarmThreads'))
                minThreads = AdminConfig.showAttribute(connectionPoolId, 'minThreads')
                maxThreads = str(AdminConfig.showAttribute(connectionPoolId, 'maxThreads'))
                threadPriority = str(AdminConfig.showAttribute(connectionPoolId, 'threadPriority'))
                isGrowable = str(AdminConfig.showAttribute(connectionPoolId, 'isGrowable'))
                
                if workTimeout != str(ThreadPoolDefaults.getDefaultWorkManagerWorkTimeout()):
                    allDefaults = "false"
                    print "****************************************************************************************************"
                    print "workTimeout: " + workTimeout
                    print "****************************************************************************************************"
                
                if workReqQSize != str(ThreadPoolDefaults.getDefaultWorkManagerQueueSiz()):
                    allDefaults = "false"
                    print "****************************************************************************************************"
                    print "workReqQSize: " + workReqQSize
                    print "****************************************************************************************************"
                
                if workReqQFullAction != str(ThreadPoolDefaults.getDefaultWorkManagerQueueFullAction()):
                    allDefaults = "false"
                    print "****************************************************************************************************"
                    print "workReqQFullAction: " + workReqQFullAction
                    print "****************************************************************************************************"
                
                if numAlarmThreads != str(ThreadPoolDefaults.getDefaultWorkManagerNumAlarmThreads()):
                    allDefaults = "false"
                    print "****************************************************************************************************"
                    print "numAlarmThreads: " + numAlarmThreads
                    print "****************************************************************************************************"
                
                if minThreads != ThreadPoolDefaults.getDefaultWorkManagerMinimumSize():
                    allDefaults = "false"
                    print "****************************************************************************************************"
                    print "minThreads: " + minThreads
                    print "****************************************************************************************************"
                
                if maxThreads != str(ThreadPoolDefaults.getDefaultWorkManagerMaximumSize()):
                    allDefaults = "false"
                    print "****************************************************************************************************"
                    print "maxThreads: " + maxThreads
                    print "****************************************************************************************************"
                
                if threadPriority != str(ThreadPoolDefaults.getDefaultWorkManagerThreadPriority()):
                    allDefaults = "false"
                    print "****************************************************************************************************"
                    print "threadPriority: " + threadPriority
                    print "****************************************************************************************************"

                if isGrowable != str(ThreadPoolDefaults.getDefaultWorkManagerGrowable()):
                    allDefaults = "false"
                    print "****************************************************************************************************"
                    print "isGrowable: " + isGrowable
                    print "****************************************************************************************************"

                if allDefaults == "true":
                    print "all defaults"
                    print
        
            
    except:
        print "Exception in displayNonDefaultExplicitlyCreatedWorkManagerSettingsByScopePath() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

def displayNonDefaultExplicitlyCreatedWorkManagerSettingsByServer(nodeName, serverName):
    try:
        # checking if the parameter value exists
        cellName = AdminControl.getCell()
        scopePath = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        path=scopePath
        objectId= AdminConfig.getid(path)
        if (len(objectId) == 0):
            print "\n\nNo object can be found at specified scope: " + scopePath 
            sys.exit(1)
        displayNonDefaultExplicitlyCreatedWorkManagerSettingsByScopePath(scopePath)
            
    except:
        print "Exception in displayNonDefaultExplicitlyCreatedWorkManagerSettingsByServer() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]) 
        sys.exit(1)

def displayNonDefaultExplicitlyCreatedWorkManagerSettingsByCluster(clusterName):
    try:
        # checking if the parameter value exists
        scopePath = '/ServerCluster:'+clusterName+'/'
        path=scopePath
        objectId= AdminConfig.getid(path)
        if (len(objectId) == 0):
            print "\n\nNo object can be found at specified scope: " + scopePath 
            sys.exit(1)
        displayNonDefaultExplicitlyCreatedWorkManagerSettingsByScopePath(scopePath)
            
    except:
        print "Exception in displayNonDefaultExplicitlyCreatedWorkManagerSettingsByCluster() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]) 
        sys.exit(1)    
