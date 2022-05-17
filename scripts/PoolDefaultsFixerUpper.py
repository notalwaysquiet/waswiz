###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
# dev - list
#wsadmin.sh -f /etp/wasadmin/was_configurator/ETP_dev/config_scripts/PoolDefaultsFixerUpper.py list | tee /etp/wasadmin/was_configurator/config_audit/list_and_compare_qcf_pool_admin_console_defaults_log
# prod - list
#wsadmin.sh -f /etp/wasadmin/was_configurator/ETP_prod/config_scripts/PoolDefaultsFixerUpper.py list | tee /etp/wasadmin/was_configurator/config_audit/prod_list_and_compare_qcf_pool_all_defaults_log

# dev - fix
#wsadmin.sh -f /etp/wasadmin/was_configurator/ETP_dev/config_scripts/PoolDefaultsFixerUpper.py fix | tee ~/fix_up_qcf_pool_defaults_log_1

#   To call from dos shell in windows
# wsadmin.bat -f c:/qdr/ETP_dev/config_scripts/PoolDefaultsFixerUpper.py

#   To call from within wsadmin
#   Can call this script from within wsadmin 2 ways: 1) import 2) execfile

#   To call from within wsadmin by import (then call functions)
# slashes must be dos-style, back slash
#sys.path.append('C:\qdr\ETP_dev\config_scripts') 
#import gui

#   To call from within wsadmin by execfile (can't pass any args this way though)
#slashes can be forward
#execfile('C:/qdr/ETP_dev/config_scripts/UserInterface.py')
#       


import sys
import AdminConfig
import AdminTask

import Utilities


def fixUpPoolDefaults(poolId):
    try:
        adminConsoleDefaultConnectionPoolProperties = '[[connectionTimeout "180"] [maxConnections "10"] [unusedTimeout "1800"] [minConnections "1"] [purgePolicy "EntirePool"] [agedTimeout "0"] [reapTime "180"]]'
        print AdminConfig.modify(poolId, adminConsoleDefaultConnectionPoolProperties)
    except:
        print "\n\nException in fixUpPoolDefaults()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    
def fixUpMqcfPoolsForScopeId(scopeId):
    try:
        queueConnectionFactoryIdList = AdminTask.listWMQConnectionFactories(scopeId).splitlines()
        
        for queueConnectionFactoryId in queueConnectionFactoryIdList:
            factoryName = AdminConfig.showAttribute(queueConnectionFactoryId, 'name')
            print "\n Starting on factoryName: " + str(factoryName)
            connectionPoolId = AdminConfig.showAttribute(queueConnectionFactoryId, 'connectionPool')
            fixUpPoolDefaults(connectionPoolId)
            print "      connection pool is fixed up"
            sessionPoolId = AdminConfig.showAttribute(queueConnectionFactoryId, 'sessionPool')
            fixUpPoolDefaults(sessionPoolId)
            print "      session pool is fixed up"
    except:
        print "\n\nException in fixUpMqcfPoolsForAllClusters()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def fixUpMqcfPoolsForAllClusters():
    try:
        #print AdminConfig.list('Cell')
        clusterList = AdminConfig.list('ServerCluster', AdminConfig.list('Cell')).splitlines() 
        #print clusterList[0]
        if clusterList == []:
            print "\n\n No clusters found.\n\n"
        else:
            for scopeId in clusterList:
                print "\n\n++++Starting on " + AdminConfig.showAttribute(scopeId, 'name')
                print "scopeId: " + scopeId
                fixUpMqcfPoolsForScopeId(scopeId)
    except:
        print "\n\nException in fixUpMqcfPoolsForAllClusters()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

def fixUpMqcfPoolsForAllServers():
    try:
        serverList = AdminTask.listServers('[-serverType APPLICATION_SERVER ]').splitlines()
        #print serverList[0]
        if serverList == []:
            print "\n\n No servers found.\n\n"
        else:
            for scopeId in serverList:
                print "\n\n++++Starting on " + AdminConfig.showAttribute(scopeId, 'name')
                print "scopeId: " + scopeId
                fixUpMqcfPoolsForScopeId(scopeId)
    except:
        print "\n\nException in fixUpMqcfPoolsForAllServers()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

def fixUp():        
    fixUpMqcfPoolsForAllServers()
    fixUpMqcfPoolsForAllClusters()

def listPoolsForQCF(queueConnectionFactoryId):
    try:
            factoryName = AdminConfig.showAttribute(queueConnectionFactoryId, 'name')
            print "\n Starting on factoryName: " + str(factoryName) 
            print " ====== comparing to wsadmin defaults ======"
            connectionPoolId = AdminConfig.showAttribute(queueConnectionFactoryId, 'connectionPool')
            #print AdminConfig.show(connectionPoolId)
            wsadminDefaultConnectionPoolProperties = [["connectionTimeout", "1800"], ["maxConnections", "10"], ["unusedTimeout", "1800"], ["minConnections", "0"], ["purgePolicy", "EntirePool"], ["agedTimeout", "1800"], ["reapTime", "180"]]
            bothPoolsMatchWsadminDefaults = "true"
            print "------connection pool:"
            
            result = compareExistingPoolToDefault(connectionPoolId, wsadminDefaultConnectionPoolProperties)
            print
            print "result of compareExistingPoolToDefault: " + str(result)
            if result != "all match":
                bothPoolsMatchWsadminDefaults = "false"
            print "------session pool:"
            sessionPoolId = AdminConfig.showAttribute(queueConnectionFactoryId, 'sessionPool')
            #print AdminConfig.show(sessionPoolId)
            result = compareExistingPoolToDefault(connectionPoolId, wsadminDefaultConnectionPoolProperties)
            print
            print "result of compareExistingPoolToDefault: " + str(result)

            if result != "all match":
                bothPoolsMatchWsadminDefaults = "false"

            print " ====== comparing to admin console defaults ======"
            connectionPoolId = AdminConfig.showAttribute(queueConnectionFactoryId, 'connectionPool')
            bothPoolsMatchAdminConsoleDefaults = "true"

            print "------connection pool:"
            #print AdminConfig.show(connectionPoolId)
            adminConsoleDefaultPoolProperties = [["connectionTimeout", "180"], ["maxConnections", "10"], ["unusedTimeout", "1800"], ["minConnections", "1"], ["purgePolicy", "EntirePool"], ["agedTimeout", "0"], ["reapTime", "180"]]
            result = compareExistingPoolToDefault(connectionPoolId, adminConsoleDefaultPoolProperties)
            print
            print "result of compareExistingPoolToDefault: " + str(result)

            if result != "all match":
                bothPoolsMatchAdminConsoleDefaults = "false"
            
            print "------session pool:"
            sessionPoolId = AdminConfig.showAttribute(queueConnectionFactoryId, 'sessionPool')
            result = compareExistingPoolToDefault(connectionPoolId, adminConsoleDefaultPoolProperties)
            #print AdminConfig.show(sessionPoolId)
            print
            print "result of compareExistingPoolToDefault: " + str(result)

            if result != "all match":
                bothPoolsMatchAdminConsoleDefaults = "false"
            print
            print "bothPoolsMatchWsadminDefaults: " + bothPoolsMatchWsadminDefaults
            print "bothPoolsMatchAdminConsoleDefaults: " + bothPoolsMatchAdminConsoleDefaults
            if bothPoolsMatchWsadminDefaults == "true" or bothPoolsMatchAdminConsoleDefaults == "true":
                return "not manually modified"    
            else:
                return "qcf was modified"
    except:
        print "\n\nException in listPoolsForQCF()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    
    
def listMqcfPoolsForScopeId(scopeId):
    try:
        queueConnectionFactoryIdListString = AdminTask.listWMQConnectionFactories(scopeId)
        if queueConnectionFactoryIdListString == "":
            print  "no qcf found"
            return "no qcf found"
        queueConnectionFactoryIdList = queueConnectionFactoryIdListString.splitlines()
        serverHasAtLeastOneModifiedQcf = "false"
        for queueConnectionFactoryId in queueConnectionFactoryIdList:
            result = listPoolsForQCF(queueConnectionFactoryId)
            if result == "qcf was modified":
                serverHasAtLeastOneModifiedQcf = "true"
        if serverHasAtLeastOneModifiedQcf == "true":
            return "server has a modified qcf"
        else:
            return "not manually modified"
    except:
        print "\n\nException in listMqcfPoolsForScopeId()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


def listMqcfPoolsForAllClusters():
    try:
        #print AdminConfig.list('Cell')
        clusterList = AdminConfig.list('ServerCluster', AdminConfig.list('Cell')).splitlines() 
        #print clusterList[0]
        modifiedClusterList = []
        if clusterList == []:
            print "\n\n No clusters found.\n\n"
        else:
            for scopeId in clusterList:
                name = AdminConfig.showAttribute(scopeId, 'name')
                print "\n\n++++Starting on " + name
                print "scopeId: " + scopeId
                result = listMqcfPoolsForScopeId(scopeId)
                print "result in listMqcfPoolsForAllClusters is: " + str(result)
                if result != "no qcf found":
                    if result != "not manually modified":
                        modifiedClusterList.append(scopeId)
        return modifiedClusterList
    except:
        print "\n\nException in listMqcfPoolsForAllClusters()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

def listMqcfPoolsForAllServers():
    try:
        serverList = AdminTask.listServers('[-serverType APPLICATION_SERVER ]').splitlines()
        modifiedServerList = []
        #print serverList[0]
        if serverList == []:
            print "\n\n No servers found.\n\n"
        else:
            for scopeId in serverList:
                name = AdminConfig.showAttribute(scopeId, 'name')
                print "\n\n++++Starting on " + name
                print "scopeId: " + scopeId
                result = listMqcfPoolsForScopeId(scopeId)
                print "result in listMqcfPoolsForAllServers is: " + str(result)
                if result != "not manually modified":
                    modifiedServerList.append(scopeId)
                
    except:
        print "\n\nException in listMqcfPoolsForAllServers()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)    
    
def list():        
    modifiedServerList = listMqcfPoolsForAllServers()
    modifiedClusterList = listMqcfPoolsForAllClusters()
    print "\n\n SUMMARY"
    print "\n\n Modified servers:" 
    print "modifiedServerList: " 
    print modifiedServerList
    if modifiedServerList != [] and modifiedServerList != None:
        for scopeId in modifiedServerList:
            print "server: " + scopeId
            listMqcfPoolsForScopeId(scopeId)

    print "\n\n Modified clusters:" 
    print "modifiedClusterList: "
    print modifiedClusterList
    if modifiedClusterList != [] and modifiedClusterList != None:
        for scopeId in modifiedClusterList:
            print "cluster: " + scopeId
            listMqcfPoolsForScopeId(scopeId)
        
def compareExistingPoolToDefault(connectionPoolId, defaultProperties):
    try:
        #existingPropsList = AdminConfig.show("(cells/AUSYDHQ-WS0958Node01Cell/nodes/AUSYDHQ-WS0958Node01/servers/server1|resources.xml#ConnectionPool_1354263652094)").splitlines()
        existingPropsList = AdminConfig.show(connectionPoolId).splitlines()
        allMatch = "true"
        for existingProp in existingPropsList:
            existingProp = Utilities.convertToList(existingProp)
            #print "existingProp[0]: " + str(existingProp[0])
            for defaultProp in defaultProperties:
                # if names match
                if existingProp[0] == defaultProp[0]:
                    # if values match 
                    if existingProp[1] == defaultProp[1]:
                        # do nothing
                        #print "match: " + existingProp[0] + " = " + existingProp[1]
                        pass
                    else:
                        allMatch = "false"
                        print "found existing value that differs from default"
                        #print "     PoolId: " + str(connectionPoolId)
                        print "     " + str(existingProp[0]) + ": " + str(existingProp[1])
                        print "     vs default: " + str(defaultProp[1])
        if allMatch == "true":
            print "all props match default*************"
            return "all match"
        elif allMatch == "false":
            return "some diff"
    except:
        print "\n\nException in compareExistingPoolToDefault()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)    


#--------------------------------------------------------------------
# main
#--------------------------------------------------------------------
#when this module is being run as top-level, call the appropriate function
if __name__=="__main__":
    usage = " "
    usage = usage + " "
    usage = usage + "Usage: <wsadmin command> -f <this py script> <action: fix | list>"
    usage = usage + " . . . and must have modified soap.client.props of target wsadmin profile if security is enabled\n"
    print "\n\n"

    if len(sys.argv) == 1:
        if sys.argv[0] == 'fix':
            print "global fix up not enabled as some qcf's have been manually modified"
            #fixUp()
        if sys.argv[0] == 'list':
            list()
    else:
        print usage
        sys.exit(1)

  

