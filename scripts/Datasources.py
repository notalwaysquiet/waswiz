###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following procedures:
#   setClusterLevelDb2Datasource
#   setServerLevelDb2Datasource
#   setDb2DatasourceByScopePath
#   setServerLevelOracleDatasource
#   setClusterLevelOracleDatasource
#   setOracleDatasourceByScopePath
#   setClusterLevelSqlServerDatasource
#   setServerLevelSqlServerDatasource
#   setSqlServerDatasourceByScopePath

#	setClusterLevelMySqlDatasource
#	setServerLevelMySqlDatasource
#	setMySqlDatasourceByScopePath
#   addCustomPropToDb2Datasource
#
###############################################################################
# Notes
# this script does not use script "library" as the methods in scripts library did not help with 
#  all the nested attributes

#'Configuring new data sources using wsadmin'
#http://publib.boulder.ibm.com/infocenter/wasinfo/fep/topic/com.ibm.websphere.nd.multiplatform.doc/info/ae/ae/txml_configdatasource.html

#there is an AdminTask way to do this, but it is nearly as ugly as AdminConfig way
#AdminConfig gives you more configuration control than the AdminTask object. 
#Other properties that are required by your JDBC driver are assigned default values by Application Server. 
#You cannot use AdminTask commands to set or edit these properties; you must use AdminConfig commands.

#this script uses the first of the 2 methods for modifying heavily nested objects
#-->Modify one of the object parents and specify the location of the nested attribute(s) within the parent
#'Modifying nested attributes using the wsadmin scripting tool'
#http://publib.boulder.ibm.com/infocenter/wasinfo/fep/topic/com.ibm.websphere.nd.multiplatform.doc/info/ae/ae/txml_modifynest.html

#beware the underlying wsadmin command & this script will let you create datasources 
#   with same name & scope, as long as jndi name differs

#if you create a ds in admin consle & save, wsadmin won't pick it up unless you restart it

# if you create a ds in wsadmin, admin console will not pick it up unless you log out & back in
# --> this is still true in v7

#must create jdbc providers & jaas aliases first before calling this script
# be sure to create providers that match these names - db2 one defaults to this name but oracle one by default (in admin console) lacks the "Provider" on the end

#parent of a ds is jdbc provider, regardless of scope, & jdbc provider specifies the scope

#recommended to not create any datasources at cell level, only at server or cluster level - this is to avoid
# potential confusion with which datasource is operating, e.g., if new server is created without its own ds

#for this reason, jdbcProvider doesn't figure into the params, only the server name

#we also do not want any "default" params

#wsadmin.bat -lang jython -f c:\qdr\ETP_dev/config_scripts/Datasources.py servers1devNode tier1_fe_server ds1 databaseServerName jndiName authDataAlias description statementCacheSize maxConnections databaseName readOnly currentSchema retrieveMessagesFromServerOnGetMessage

import sys

import AdminConfig

#--------------------------------------------------------------------
# Modify connection pool of an existing datasource at cluster level
#--------------------------------------------------------------------
def modifyClusterLevelDatasourceConnectionPool(clusterName, dbType, dataSourceName, connectionTimeout, maxConnections, unusedTimeout, minConnections, purgePolicy, agedTimeout, reapTime):
    id = "id not created yet"
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Modify a datasource's connection pool at cluster level"
        print " clusterName:                            "+clusterName
        print " dbType:                                 "+dbType                
        print " dataSourceName:                         "+dataSourceName
        print " connectionTimeout:                      "+str(connectionTimeout)
        print " maxConnections:                         "+str(maxConnections)
        print " unusedTimeout:                          "+str(unusedTimeout)
        print " minConnections:                         "+str(minConnections)
        print " purgePolicy:                            "+purgePolicy
        print " agedTimeout:                            "+str(agedTimeout)
        print " reapTime:                               "+str(reapTime)
        msg = " Executing: Datasources.modifyClusterLevelDatasourceConnectionPool(\""+clusterName+"\", \""+dbType+"\", \""+dataSourceName+"\", \""+str(agedTimeout)+"\",  \""+str(connectionTimeout)+"\", \""+purgePolicy+"\", \""+str(unusedTimeout)+"\", \""+str(minConnections)+"\", \""+str(maxConnections)+"\", \""+str(reapTime)+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully."
        usage = usage + msg

        # checking required parameters
        if (len(clusterName) == 0):
            print usage
            sys.exit(1)
        if (len(dataSourceName) == 0):
           print usage
           sys.exit(1)
        if (len(dbType) == 0):
           print usage
           sys.exit(1)
        # checking if the parameter value exists
        path='/ServerCluster:'+clusterName+'/'
        clusterId= AdminConfig.getid(path)
        if (len(clusterId) == 0):
            print "The specified cluster at: " + clusterName + " does not exist."
            sys.exit(1)

    except:
        print "\n\nException in modifyClusterLevelDatasourceConnectionPool() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        jdbcProviderScope = '/ServerCluster:'+clusterName+'/'
        id = modifyDatasourceConnectionPoolByScopePath(jdbcProviderScope, dbType, dataSourceName, connectionTimeout, maxConnections, unusedTimeout, minConnections, purgePolicy, agedTimeout, reapTime)

    except:
        print "\n\nException in modifyClusterLevelDatasourceConnectionPool() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
        return id        
    except:
        print "\n\nException in modifyClusterLevelDatasourceConnectionPool() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of modifyClusterLevelDatasourceConnectionPool()\n\n"


#--------------------------------------------------------------------
# Modify connection pool of an existing datasource at server level
#--------------------------------------------------------------------
def modifyServerLevelDatasourceConnectionPool(nodeName, serverName, dbType, dataSourceName, connectionTimeout, maxConnections, unusedTimeout, minConnections, purgePolicy, agedTimeout, reapTime):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Modify a datasource's connection pool at server level"
        print " nodeName:                               "+nodeName
        print " serverName:                             "+serverName
        print " dbType:                                 "+dbType                
        print " dataSourceName:                         "+dataSourceName
        print " connectionTimeout:                      "+str(connectionTimeout)
        print " maxConnections:                         "+str(maxConnections)
        print " unusedTimeout:                          "+str(unusedTimeout)
        print " minConnections:                         "+str(minConnections)
        print " purgePolicy:                            "+purgePolicy
        print " agedTimeout:                            "+str(agedTimeout)
        print " reapTime:                               "+str(reapTime)
        msg = " Executing: Datasources.modifyServerLevelDatasourceConnectionPool(\""+nodeName+"\", \""+serverName+"\", \""+dbType+"\", \""+dataSourceName+"\", \""+str(agedTimeout)+"\",  \""+str(connectionTimeout)+"\", \""+purgePolicy+"\", \""+str(unusedTimeout)+"\", \""+str(minConnections)+"\", \""+str(maxConnections)+"\", \""+str(reapTime)+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully."
        usage = usage + msg

        # checking required parameters
        if (len(nodeName) == 0):
            print usage
            sys.exit(1)
        if (len(serverName) == 0):
            print usage
            sys.exit(1)
        if (len(dataSourceName) == 0):
           print usage
           sys.exit(1)
        if (len(dbType) == 0):
           print usage
           sys.exit(1)
           
        # checking if the parameter value exists
        path='/Node:'+nodeName+'/Server:'+serverName+'/'
        serverId= AdminConfig.getid(path)
        if (len(serverId) == 0):
            print "The specified server at: " + serverName + " does not exist."
            sys.exit(1)

    except:
        print "\n\nException in modifyServerLevelDatasourceConnectionPool() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        cellId=AdminConfig.list('Cell')
        cellName=AdminConfig.showAttribute(cellId, 'name')
        jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        id = modifyDatasourceConnectionPoolByScopePath(jdbcProviderScope, dbType, dataSourceName, connectionTimeout, maxConnections, unusedTimeout, minConnections, purgePolicy, agedTimeout, reapTime)
    except:
        print "\n\nException in modifyServerLevelDatasourceConnectionPool() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
        return id        
    except:
        print "\n\nException in modifyServerLevelDatasourceConnectionPool() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of modifyServerLevelDatasourceConnectionPool()\n\n"

    
#--------------------------------------------------------------------
# Modify connection pool of an existing datasource 
#--------------------------------------------------------------------
def modifyDatasourceConnectionPoolByScopePath(jdbcProviderScope, dbType, dataSourceName, connectionTimeout, maxConnections, unusedTimeout, minConnections, purgePolicy, agedTimeout, reapTime):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Modify a datasource's connection pool by passing in the scope path"
        print " jdbcProviderScope:                      "+jdbcProviderScope
        print " dbType:                                 "+dbType        
        print " dataSourceName:                         "+dataSourceName
        print " connectionTimeout:                      "+str(connectionTimeout)
        print " maxConnections:                         "+str(maxConnections)
        print " unusedTimeout:                          "+str(unusedTimeout)
        print " minConnections:                         "+str(minConnections)
        print " purgePolicy:                            "+purgePolicy
        print " agedTimeout:                            "+str(agedTimeout)
        print " reapTime:                               "+str(reapTime)
        msg = " Executing: Datasources.modifyDatasourceConnectionPoolByScopePath(\""+jdbcProviderScope+"\", \""+dbType+"\", \""+dataSourceName+"\", \""+str(agedTimeout)+"\",  \""+str(connectionTimeout)+"\", \""+purgePolicy+"\", \""+str(unusedTimeout)+"\", \""+str(minConnections)+"\", \""+str(maxConnections)+"\", \""+str(reapTime)+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully."
        usage = usage + msg

        # checking required parameters
        if (len(jdbcProviderScope) == 0):
            print usage
            sys.exit(1)
        if (len(dataSourceName) == 0):
           print usage
           sys.exit(1)
        if (len(dbType) == 0):
           print usage
           sys.exit(1)

        #dbTypeList=['db2', 'mysql', 'oracle', 'sqlserver'] 
        
        import JdbcProviders
        
        jdbcProviderName = JdbcProviders.getJdbcProviderName(dbType)
        #print "jdbcProviderName: " + str(jdbcProviderName)
        if jdbcProviderName != None and jdbcProviderName != "":
            jdbcProviderPath = jdbcProviderScope + 'JDBCProvider:'+jdbcProviderName+'/'
        else:
            print "No jdbc provider name found for dbType: " + dbType
            sys.exit(1)
        
        jdbcProviderId = AdminConfig.getid(jdbcProviderPath)
        if (len(jdbcProviderId) == 0):
            print "No jdbc provider found for scope: " + jdbcProviderScope + " for DB type: " + dbType + ".\nPlease create jdbc provider and datasource first before running this method."
            sys.exit(1)
        
        dataSourcePath = jdbcProviderPath + 'DataSource:' + dataSourceName + '/'
        dataSourceId = AdminConfig.getid(dataSourcePath)
        #print dataSourceId
        connectionPoolId = AdminConfig.showAttribute(dataSourceId, 'connectionPool')
        #print connectionPoolId
        
    except:
        print "\n\nException in modifyDatasourceConnectionPoolByScopePath() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        noPropsProvided = "true"
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
            print "No props provided for pool: " + connectionPoolId
            print "Exiting."
            sys.exit(1)

        #print "attributeList: " + str(attributeList)
        AdminConfig.modify(connectionPoolId, attributeList)

        print "Modified props for pool: " + connectionPoolId        
        for prop in attributeList:
            print "  " + str(prop[1])
        

    except:
        print "\n\nException in modifyDatasourceConnectionPoolByScopePath() when modifying pool\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "\n\nException in modifyDatasourceConnectionPoolByScopePath() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of modifyDatasourceConnectionPoolByScopePath()\n\n"


        
#--------------------------------------------------------------------
# Create a cluster-level DB2 datasource
# Jdbc provider must already exist
#--------------------------------------------------------------------
def setClusterLevelDb2Datasource(clusterName, dataSourceName, databaseServerName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, databaseName, readOnly, currentSchema, retrieveMessagesFromServerOnGetMessage):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a cluster-level DB2 datasource"
        print " clusterName:                              "+clusterName
        print " dataSourceName:                           "+dataSourceName
        print " jndiName:                                 "+jndiName        
        print " authDataAlias:                            "+authDataAlias        
        print " description (optional):                   "+description        
        print " statementCacheSize:                       "+str(statementCacheSize)
        print " maxConnections:                           "+str(maxConnections)
        print " databaseServerName:                       "+databaseServerName
        print " databaseName:                             "+databaseName        
        print " readOnly:                                 "+readOnly        
        print " currentSchema:                            "+currentSchema 
        print " retrieveMessagesFromServerOnGetMessage:   "+retrieveMessagesFromServerOnGetMessage         
        msg = " Executing: Datasources.setClusterLevelDb2Datasource(\""+clusterName+"\", \""+dataSourceName+"\", \""+databaseServerName+"\",  \""+jndiName+"\", \""+authDataAlias+"\", \""+description+"\", \""+str(statementCacheSize)+"\", \""+str(maxConnections)+"\", \""+databaseName+"\", \""+readOnly+"\", \""+currentSchema+"\", \""+retrieveMessagesFromServerOnGetMessage+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(clusterName) == 0):
            print usage
            sys.exit(1)
        if (len(dataSourceName) == 0):
           print usage
           sys.exit(1)
        if (len(jndiName) == 0):
           print usage
           sys.exit(1)
        if (len(authDataAlias) == 0):
           print usage
           sys.exit(1)
        if (len(str(statementCacheSize)) == 0):
           print usage
           sys.exit(1)
        if (len(str(maxConnections)) == 0):
           print usage
           sys.exit(1)

        #DB2-specific ones 
        if (len(databaseServerName) == 0):
           print usage
           sys.exit(1)
        if (len(databaseName) == 0):
           print usage
           sys.exit(1)
        if (len(readOnly) == 0):
           print usage
           sys.exit(1)
        if (len(currentSchema) == 0):
           #schema can be ''
           pass
        if (len(retrieveMessagesFromServerOnGetMessage) == 0):
           print usage
           sys.exit(1)
    
        # checking if the parameter value exists
        path='/ServerCluster:'+clusterName+'/'
        clusterId= AdminConfig.getid(path)
        if (len(clusterId) == 0):
            print "The specified cluster at: " + clusterName + " does not exist."
            sys.exit(1)
    except:
        print "\n\nException in setClusterLevelDb2Datasource() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        jdbcProviderScope = '/ServerCluster:'+clusterName+'/'
        id = setDb2DatasourceByScopePath(jdbcProviderScope, dataSourceName, databaseServerName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, databaseName, readOnly, currentSchema, retrieveMessagesFromServerOnGetMessage)
    except:
        print "\n\nException in setClusterLevelDb2Datasource() when creating the data source\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
        return id        
    except:
        print "\n\nException in setClusterLevelDb2Datasource() when saving to master config\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setClusterLevelDb2Datasource()\n\n"


#--------------------------------------------------------------------
# Create a server-level DB2 datasource
# Jdbc provider must already exist
#--------------------------------------------------------------------
def setServerLevelDb2Datasource(nodeName, serverName, dataSourceName, databaseServerName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, databaseName, readOnly, currentSchema, retrieveMessagesFromServerOnGetMessage):
    id = "id not created yet"
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a server-level DB2 datasource"
        print " nodeName:                                 "+nodeName
        print " serverName:                               "+serverName
        print " dataSourceName:                           "+dataSourceName
        print " jndiName:                                 "+jndiName        
        print " authDataAlias:                            "+authDataAlias        
        print " description (optional):                   "+description        
        print " statementCacheSize:                       "+str(statementCacheSize)
        print " maxConnections:                           "+str(maxConnections)
        print " databaseServerName:                       "+databaseServerName
        print " databaseName:                             "+databaseName        
        print " readOnly:                                 "+readOnly        
        print " currentSchema:                            "+currentSchema 
        print " retrieveMessagesFromServerOnGetMessage:   "+retrieveMessagesFromServerOnGetMessage         
        msg = " Executing: Datasources.setServerLevelDb2Datasource(\""+nodeName+"\", \""+serverName+"\", \""+dataSourceName+"\", \""+databaseServerName+"\",  \""+jndiName+"\", \""+authDataAlias+"\", \""+description+"\", \""+str(statementCacheSize)+"\", \""+str(maxConnections)+"\", \""+databaseName+"\", \""+readOnly+"\", \""+currentSchema+"\", \""+retrieveMessagesFromServerOnGetMessage+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully."
        usage = usage + msg

        # checking required parameters
        if (len(serverName) == 0):
            print usage
            sys.exit(1)
        if (len(dataSourceName) == 0):
           print usage
           sys.exit(1)
        if (len(jndiName) == 0):
           print usage
           sys.exit(1)
        if (len(authDataAlias) == 0):
           print usage
           sys.exit(1)
        if (len(str(statementCacheSize)) == 0):
           print usage
           sys.exit(1)
        if (len(str(maxConnections)) == 0):
           print usage
           sys.exit(1)

        #DB2-specific ones 
        if (len(databaseServerName) == 0):
           print usage
           sys.exit(1)
        if (len(databaseName) == 0):
           print usage
           sys.exit(1)
        if (len(readOnly) == 0):
           print usage
           sys.exit(1)
        if (len(currentSchema) == 0):
           #schema can be ''
           pass
        if (len(retrieveMessagesFromServerOnGetMessage) == 0):
           print usage
           sys.exit(1)
        
        # checking if the parameter value exists
        path='/Node:'+nodeName+'/'
        nodeId= AdminConfig.getid(path)
        if (len(nodeId) == 0):
            print "\n\nThe specified node at: " + nodeName + " does not exist.\n\n"
            sys.exit(1)

        # checking if the parameter value exists
        path='/Node:'+nodeName+'/Server:'+serverName+'/'
        serverId= AdminConfig.getid(path)
        if (len(serverId) == 0):
            print "\n\nThe specified server at: " + serverName + " does not exist.\n\n"
            sys.exit(1)
    except:
        print "\n\nException in setServerLevelDb2Datasource() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        cellId=AdminConfig.list('Cell')
        cellName=AdminConfig.showAttribute(cellId, 'name')
        jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        id = setDb2DatasourceByScopePath(jdbcProviderScope, dataSourceName, databaseServerName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, databaseName, readOnly, currentSchema, retrieveMessagesFromServerOnGetMessage)
    except:
        print "\n\nException in setServerLevelDb2Datasource() when creating the data source\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
        return id
    except:
        print "\n\nException in setServerLevelDb2Datasource() when saving to master config\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setServerLevelDb2Datasource()"


#--------------------------------------------------------------------
# Create a DB2 datasource by passing in the scope path
# Jdbc provider must already exist
# e.g., jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
#--------------------------------------------------------------------
def setDb2DatasourceByScopePath(jdbcProviderScope, dataSourceName, databaseServerName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, databaseName, readOnly, currentSchema, retrieveMessagesFromServerOnGetMessage):
    id = "id not created yet"
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a DB2 datasource by passing in the scope path"
        print " jdbcProviderScope:                        "+jdbcProviderScope
        print " dataSourceName:                           "+dataSourceName
        print " jndiName:                                 "+jndiName        
        print " authDataAlias:                            "+authDataAlias        
        print " description (optional):                   "+description        
        print " statementCacheSize:                       "+str(statementCacheSize)
        print " maxConnections:                           "+str(maxConnections)
        print " databaseServerName:                       "+databaseServerName
        print " databaseName:                             "+databaseName        
        print " readOnly:                                 "+readOnly        
        print " currentSchema:                            "+currentSchema 
        print " retrieveMessagesFromServerOnGetMessage:   "+retrieveMessagesFromServerOnGetMessage         
        msg = " Executing: Datasources.setDb2DatasourceByScopePath(\""+jdbcProviderScope+"\", \""+dataSourceName+"\", \""+databaseServerName+"\",  \""+jndiName+"\", \""+authDataAlias+"\", \""+description+"\", \""+str(statementCacheSize)+"\", \""+str(maxConnections)+"\", \""+databaseName+"\", \""+readOnly+"\", \""+currentSchema+"\", \""+retrieveMessagesFromServerOnGetMessage+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully."
        usage = usage + msg

        # checking required parameters
        if (len(jdbcProviderScope) == 0):
            print usage
            sys.exit(1)
        if (len(dataSourceName) == 0):
           print usage
           sys.exit(1)
        if (len(jndiName) == 0):
           print usage
           sys.exit(1)
        if (len(authDataAlias) == 0):
           print usage
           sys.exit(1)
        if (len(str(statementCacheSize)) == 0):
           print usage
           sys.exit(1)
        if (len(str(maxConnections)) == 0):
           print usage
           sys.exit(1)

        #DB2-specific ones 
        if (len(databaseServerName) == 0):
           print usage
           sys.exit(1)
        if (len(databaseName) == 0):
           print usage
           sys.exit(1)
        if (len(readOnly) == 0):
           print usage
           sys.exit(1)
        if (len(currentSchema) == 0):
           #schema can be ''
           pass
        if (len(retrieveMessagesFromServerOnGetMessage) == 0):
           print usage
           sys.exit(1)

        # checking if the parameter value exists
        #jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        path=jdbcProviderScope
        objectId= AdminConfig.getid(path)
        if (len(objectId) == 0):
            print "\n\nNo object can be found at specified scope: " + jdbcProviderScope 
            sys.exit(1)
    except:
        print "\n\nException in setDb2DatasourceByScopePath() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        #cellId=AdminConfig.list('Cell')
        #cellName=AdminConfig.showAttribute(cellId, 'name')
        #jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        jdbcProviderName='DB2 Universal JDBC Driver Provider (XA)'
        jdbcProviderPath = jdbcProviderScope + 'JDBCProvider:'+jdbcProviderName+'/'
        jdbcProviderId= AdminConfig.getid(jdbcProviderPath)
        if (len(jdbcProviderId) == 0):
            print "No jdbc provider found for scope: " + jdbcProviderScope + ".\nPlease create jdbc provider first before running this method."
            sys.exit(1)
    except:
        print "\n\nException in setDb2DatasourceByScopePath() when getting jdbcProviderId\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        dataSourceTemplateName='DB2 Universal JDBC Driver DataSource'
        dataSourceTemplateId= AdminConfig.listTemplates('DataSource', dataSourceTemplateName)
    except:
        print "\n\nException in setDb2DatasourceByScopePath() when getting dataSourceTemplateId"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        connectionPool=[['maxConnections', maxConnections]]

        #DB2-specific ones 
        resourcePropertyName='databaseName'
        resourcePropertyValue=databaseName
        customProperty=[['name', resourcePropertyName], ['value', resourcePropertyValue]]
        resourceProperties=[customProperty]

        #driverType 4 is default in admin console
        resourcePropertyName='driverType'
        resourcePropertyValue=4
        customProperty=[['name', resourcePropertyName], ['value', resourcePropertyValue]]
        resourceProperties.append(customProperty)

        #portNumber 50000 is default in admin console
        resourcePropertyName='portNumber'
        resourcePropertyValue=50000
        customProperty=[['name', resourcePropertyName], ['value', resourcePropertyValue]]
        resourceProperties.append(customProperty)

        resourcePropertyName='serverName'
        resourcePropertyValue=databaseServerName
        customProperty=[['name', resourcePropertyName], ['value', resourcePropertyValue]]
        resourceProperties.append(customProperty)

        resourcePropertyName='readOnly'
        resourcePropertyValue=readOnly
        customProperty=[['name', resourcePropertyName], ['value', resourcePropertyValue]]
        resourceProperties.append(customProperty)

        resourcePropertyName='currentSchema'
        resourcePropertyValue=currentSchema
        customProperty=[['name', resourcePropertyName], ['value', resourcePropertyValue]]
        resourceProperties.append(customProperty)

        resourcePropertyName='retrieveMessagesFromServerOnGetMessage'
        resourcePropertyValue=retrieveMessagesFromServerOnGetMessage
        customProperty=[['name', resourcePropertyName], ['value', resourcePropertyValue]]
        resourceProperties.append(customProperty)

        propertySet=[['resourceProperties', resourceProperties]]
        #print "propertySet is: " 
        #print propertySet

    except:
        print "\n\nException in setDb2DatasourceByScopePath() when packing up the param lists"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        id = AdminConfig.createUsingTemplate('DataSource', jdbcProviderId, [['name', dataSourceName], ['jndiName', jndiName], ['description', description], ['authDataAlias', authDataAlias], ['statementCacheSize', statementCacheSize], ['connectionPool', connectionPool], ['propertySet', propertySet] ], dataSourceTemplateId)
        print id
    except:
        print "\n\nException in setDb2DatasourceByScopePath() when creating the data source"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
        return id        
    except:
        print "\n\nException in setDb2DatasourceByScopePath() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setDb2DatasourceByScopePath()"


def addCustomPropToClusterLevelDb2Datasource(clusterName, jndiName, dataSourceCustomPropertyName, dataSourceCustomPropertyType, dataSourceCustomPropertyValue, dataSourceCustomPropertyDescription):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Modify a cluster-level DB2 datasource by adding a custom prop"
        print " clusterName:                              "+clusterName
        print " jndiName:                                 "+jndiName        
        print " dataSourceCustomPropertyName:             "+dataSourceCustomPropertyName
        print " dataSourceCustomPropertyType:             "+dataSourceCustomPropertyType        
        print " dataSourceCustomPropertyValue:            "+str(dataSourceCustomPropertyValue)
        print " dataSourceCustomPropertyDescription:      "+dataSourceCustomPropertyDescription
        msg = " Executing: Datasources.addCustomPropToClusterLevelDb2Datasource(\""+clusterName+"\", \""+jndiName+"\", \""+dataSourceCustomPropertyName+"\", \""+dataSourceCustomPropertyType+"\", \""+str(dataSourceCustomPropertyValue)+"\", \""+dataSourceCustomPropertyDescription+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully."
        usage = usage + msg

        # checking required parameters
        if (len(clusterName) == 0):
            print usage
            sys.exit(1)
        if (len(jndiName) == 0):
           print usage
           sys.exit(1)

        if (len(dataSourceCustomPropertyName) == 0):
           print usage
           sys.exit(1)
        if (len(dataSourceCustomPropertyType) == 0):
           print usage
           sys.exit(1)
        if (len(str(dataSourceCustomPropertyValue)) == 0):
           print usage
           sys.exit(1)
        if (len(dataSourceCustomPropertyDescription) == 0):
           print usage
           sys.exit(1)
        # checking if the parameter value exists
        path='/ServerCluster:'+clusterName+'/'
        clusterId= AdminConfig.getid(path)
        if (len(clusterId) == 0):
            print "The specified cluster at: " + clusterName + " does not exist."
            sys.exit(1)

    except:
        print "\n\nException in addCustomPropToClusterLevelDb2Datasource() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        jdbcProviderScope = '/ServerCluster:'+clusterName+'/'
        id = addCustomPropToDb2Datasource(jdbcProviderScope,  jndiName, dataSourceCustomPropertyName, dataSourceCustomPropertyType, str(dataSourceCustomPropertyValue), dataSourceCustomPropertyDescription)

    except:
        print "\n\nException in addCustomPropToClusterLevelDb2Datasource() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
        return id        
    except:
        print "\n\nException in addCustomPropToClusterLevelDb2Datasource() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of addCustomPropToClusterLevelDb2Datasource()\n\n"


def addCustomPropToServerLevelDb2Datasource(nodeName, serverName, jndiName, dataSourceCustomPropertyName, dataSourceCustomPropertyType, dataSourceCustomPropertyValue, dataSourceCustomPropertyDescription):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Modify a server-level DB2 datasource by adding a custom prop"
        print " nodeName:                                 "+nodeName
        print " serverName:                               "+serverName
        print " jndiName:                                 "+jndiName        
        print " dataSourceCustomPropertyName:             "+dataSourceCustomPropertyName
        print " dataSourceCustomPropertyType:             "+dataSourceCustomPropertyType        
        print " dataSourceCustomPropertyValue:            "+str(dataSourceCustomPropertyValue)
        print " dataSourceCustomPropertyDescription:      "+dataSourceCustomPropertyDescription
        msg = " Executing: Datasources.addCustomPropToServerLevelDb2Datasource(\""+nodeName+"\", \""+serverName+"\", \""+jndiName+"\", \""+dataSourceCustomPropertyName+"\", \""+dataSourceCustomPropertyType+"\", \""+str(dataSourceCustomPropertyValue)+"\", \""+dataSourceCustomPropertyDescription+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully."
        usage = usage + msg

        # checking required parameters
        if (len(nodeName) == 0):
            print usage
            sys.exit(1)
        if (len(serverName) == 0):
            print usage
            sys.exit(1)
        if (len(jndiName) == 0):
           print usage
           sys.exit(1)

        if (len(dataSourceCustomPropertyName) == 0):
           print usage
           sys.exit(1)
        if (len(dataSourceCustomPropertyType) == 0):
           print usage
           sys.exit(1)
        if (len(str(dataSourceCustomPropertyValue)) == 0):
           print usage
           sys.exit(1)
        if (len(dataSourceCustomPropertyDescription) == 0):
           print usage
           sys.exit(1)
        # checking if the parameter value exists
        path='/Node:'+nodeName+'/Server:'+serverName+'/'
        serverId= AdminConfig.getid(path)
        if (len(serverId) == 0):
            print "The specified server at: " + serverName + " does not exist."
            sys.exit(1)

    except:
        print "\n\nException in addCustomPropToServerLevelDb2Datasource() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        cellId=AdminConfig.list('Cell')
        cellName=AdminConfig.showAttribute(cellId, 'name')
        jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        id = addCustomPropToDb2Datasource(jdbcProviderScope,  jndiName, dataSourceCustomPropertyName, dataSourceCustomPropertyType, str(dataSourceCustomPropertyValue), dataSourceCustomPropertyDescription)

    except:
        print "\n\nException in addCustomPropToServerLevelDb2Datasource() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
        return id        
    except:
        print "\n\nException in addCustomPropToServerLevelDb2Datasource() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of addCustomPropToServerLevelDb2Datasource()\n\n"



def addCustomPropToDb2Datasource(jdbcProviderScope, jndiName, dataSourceCustomPropertyName, dataSourceCustomPropertyType, dataSourceCustomPropertyValue, dataSourceCustomPropertyDescription):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Modify a DB2 datasource by adding a custom prop"
        print " jdbcProviderScope:                        "+jdbcProviderScope
        print " jndiName:                                 "+jndiName        
        print " dataSourceCustomPropertyName:             "+dataSourceCustomPropertyName
        print " dataSourceCustomPropertyType:             "+dataSourceCustomPropertyType        
        print " dataSourceCustomPropertyValue:            "+str(dataSourceCustomPropertyValue)
        print " dataSourceCustomPropertyDescription:      "+dataSourceCustomPropertyDescription
        msg = " Executing: Datasources.addCustomPropToDb2Datasource(\""+jdbcProviderScope+"\", \""+jndiName+"\", \""+dataSourceCustomPropertyName+"\", \""+dataSourceCustomPropertyType+"\", \""+str(dataSourceCustomPropertyValue)+"\", \""+dataSourceCustomPropertyDescription+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully."
        usage = usage + msg

        # checking required parameters
        if (len(jdbcProviderScope) == 0):
            print usage
            sys.exit(1)
        if (len(jndiName) == 0):
           print usage
           sys.exit(1)

        if (len(dataSourceCustomPropertyName) == 0):
           print usage
           sys.exit(1)
        if (len(dataSourceCustomPropertyType) == 0):
           print usage
           sys.exit(1)
        if (len(str(dataSourceCustomPropertyValue)) == 0):
           print usage
           sys.exit(1)
        if (len(dataSourceCustomPropertyDescription) == 0):
           print usage
           sys.exit(1)

    except:
        print "\n\nException in addCustomPropToDb2Datasource() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        #cellId=AdminConfig.list('Cell')
        #cellName=AdminConfig.showAttribute(cellId, 'name')
        #jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        jdbcProviderName='DB2 Universal JDBC Driver Provider (XA)'
        jdbcProviderPath = jdbcProviderScope + 'JDBCProvider:'+jdbcProviderName+'/'
        jdbcProviderId= AdminConfig.getid(jdbcProviderPath)
        if (len(jdbcProviderId) == 0):
            print "No jdbc provider found for scope: " + jdbcProviderScope + ".\nPlease create jdbc provider first before running this method."
            sys.exit(1)
    except:
        print "\n\nException in addCustomPropToDb2Datasource() when getting jdbcProviderId\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        dataSourcePath = jdbcProviderPath + 'DataSource:' + '/' 
        dataSourceIDList = AdminConfig.getid(dataSourcePath).splitlines()
        print "dataSourceIDList:"
        print dataSourceIDList
        print
        dataSourceID = "dataSourceID not defined yet"
        for id in dataSourceIDList:
            if (AdminConfig.showAttribute(id, 'jndiName') == jndiName):
                dataSourceID = id
                print "dataSourceID to add custom prop to is: " + dataSourceID
        print
        print
        #see http://www-01.ibm.com/support/knowledgecenter/SSAW57_8.5.5/com.ibm.websphere.nd.doc/ae/txml_configcustom.html?lang=en
        propertySetID = AdminConfig.showAttribute(dataSourceID, 'propertySet')
        print
        print "propertySetID:"
        print propertySetID
        print
    except:
        print "\n\nException in addCustomPropToDb2Datasource() when getting ID of propertySet \n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        #dataSourceCustomPropertyName='deferPrepares'
        #dataSourceCustomPropertyType = 'java.lang.Boolean'
        #dataSourceCustomPropertyValue = 'false'
        #dataSourceCustomPropertyDescription = 'blablablah'
        customProperty=[['name', dataSourceCustomPropertyName], ['value', str(dataSourceCustomPropertyValue)], ['type', dataSourceCustomPropertyType], ['description', dataSourceCustomPropertyDescription]]

        id = AdminConfig.create('J2EEResourceProperty', propertySetID, customProperty)
        print id

    except:
        print "\n\nException in addCustomPropToDb2Datasource() when creating custom prop\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    

    try:
        AdminConfig.save()
        return id        
    except:
        print "\n\nException in addCustomPropToDb2Datasource() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of addCustomPropToDb2Datasource()"
  



#--------------------------------------------------------------------
# Create a cluster-level Oracle datasource
#--------------------------------------------------------------------
def setClusterLevelOracleDatasource(clusterName, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, url):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a cluster-level Oracle datasource"
        print " clusterName:                              "+clusterName
        print " dataSourceName:                           "+dataSourceName
        print " jndiName:                                 "+jndiName        
        print " authDataAlias:                            "+authDataAlias        
        print " description:                              "+description        
        print " statementCacheSize:                       "+str(statementCacheSize)
        print " maxConnections:                           "+str(maxConnections)
        print " url:                                      "+url        
        msg = " Executing: Datasources.setClusterLevelOracleDatasource(\""+clusterName+"\", \""+dataSourceName+"\", \""+jndiName+"\", \""+authDataAlias+"\", \""+description+"\", \""+str(statementCacheSize)+"\", \""+str(maxConnections)+"\", \""+url+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(clusterName) == 0):
            print usage
            sys.exit(1)
        if (len(dataSourceName) == 0):
           print usage
           sys.exit(1)
        if (len(jndiName) == 0):
           print usage
           sys.exit(1)
        if (len(authDataAlias) == 0):
           print usage
           sys.exit(1)
        if (len(str(statementCacheSize)) == 0):
           print usage
           sys.exit(1)
        if (len(str(maxConnections)) == 0):
           print usage
           sys.exit(1)

        #Oracle-specific
        if (len(url) == 0):
           print usage
           sys.exit(1)
    
        # checking if the parameter value exists
        path='/ServerCluster:'+clusterName+'/'
        clusterId= AdminConfig.getid(path)
        if (len(clusterId) == 0):
            print "The specified cluster at: " + clusterName + " does not exist."
            sys.exit(1)
    except:
        print "\n\nException in setClusterLevelOracleDatasource() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        jdbcProviderScope = '/ServerCluster:'+clusterName+'/'
        id = setOracleDatasourceByScopePath(jdbcProviderScope, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, url)
    except:
        print "\n\nException in setClusterLevelOracleDatasource() when creating the data source"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
        return id        
    except:
        print "\n\nException in setClusterLevelOracleDatasource() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setClusterLevelOracleDatasource()\n\n"


#--------------------------------------------------------------------
# Create a server-level Oracle datasource
#--------------------------------------------------------------------
def setServerLevelOracleDatasource(nodeName, serverName, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, url):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create an Oracle datasource"
        print " nodeName:                                 "+nodeName
        print " serverName:                               "+serverName
        print " dataSourceName:                           "+dataSourceName
        print " jndiName:                                 "+jndiName        
        print " authDataAlias:                            "+authDataAlias        
        print " description:                              "+description        
        print " statementCacheSize:                       "+str(statementCacheSize)
        print " maxConnections:                           "+str(maxConnections)
        print " url:                                      "+url        
        msg = " Executing: Datasources.setServerLevelOracleDatasource(\""+nodeName+"\", \""+serverName+"\", \""+dataSourceName+"\", \""+jndiName+"\", \""+authDataAlias+"\", \""+description+"\", \""+str(statementCacheSize)+"\", \""+str(maxConnections)+"\", \""+url+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(nodeName) == 0):
            print usage
            sys.exit(1)
        if (len(serverName) == 0):
            print usage
            sys.exit(1)
        if (len(dataSourceName) == 0):
           print usage
           sys.exit(1)
        if (len(jndiName) == 0):
           print usage
           sys.exit(1)
        if (len(authDataAlias) == 0):
           print usage
           sys.exit(1)
        if (len(str(statementCacheSize)) == 0):
           print usage
           sys.exit(1)
        if (len(str(maxConnections)) == 0):
           print usage
           sys.exit(1)

        #Oracle-specific
        if (len(url) == 0):
           print usage
           sys.exit(1)
    
        # checking if the parameter value exists
        path='/Node:'+nodeName+'/'
        nodeId= AdminConfig.getid(path)
        if (len(nodeId) == 0):
            print "The specified node at: " + nodeName + " does not exist."
            sys.exit(1)

        # checking if the parameter value exists
        path='/Node:'+nodeName+'/Server:'+serverName+'/'
        serverId= AdminConfig.getid(path)
        if (len(serverId) == 0):
            print "The specified server at: " + serverName + " does not exist."
            sys.exit(1)
    except:
        print "\n\nException in setServerLevelOracleDatasource() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        #assuming only 1 cell per installation
        cellId=AdminConfig.list('Cell')
        cellName=AdminConfig.showAttribute(cellId, 'name')
        jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        id = setOracleDatasourceByScopePath(jdbcProviderScope, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, url)
    except:
        print "\n\nException in setServerLevelOracleDatasource() when creating the data source"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
        return id        
    except:
        print "\n\nException in setServerLevelOracleDatasource() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setServerLevelOracleDatasource()\n\n"


#--------------------------------------------------------------------
# Create a Oracle datasource by passing in the scope path
# e.g., jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
#--------------------------------------------------------------------
def setOracleDatasourceByScopePath(jdbcProviderScope, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, url):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create an Oracle datasource by passing in the scope path"
        print " jdbcProviderScope:                        "+jdbcProviderScope        
        print " dataSourceName:                           "+dataSourceName
        print " jndiName:                                 "+jndiName        
        print " authDataAlias:                            "+authDataAlias        
        print " description:                              "+description        
        print " statementCacheSize:                       "+str(statementCacheSize)
        print " maxConnections:                           "+str(maxConnections)
        print " url:                                      "+url        
        msg = " Executing: Datasources.setOracleDatasourceByScopePath(\""+jdbcProviderScope+"\", \""+dataSourceName+"\", \""+jndiName+"\", \""+authDataAlias+"\", \""+description+"\", \""+str(statementCacheSize)+"\", \""+str(maxConnections)+"\", \""+url+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(jdbcProviderScope) == 0):
            print usage
            sys.exit(1)
        if (len(dataSourceName) == 0):
           print usage
           sys.exit(1)
        if (len(jndiName) == 0):
           print usage
           sys.exit(1)
        if (len(authDataAlias) == 0):
           print usage
           sys.exit(1)
        if (len(str(statementCacheSize)) == 0):
           print usage
           sys.exit(1)
        if (len(str(maxConnections)) == 0):
           print usage
           sys.exit(1)

        #Oracle-specific
        if (len(url) == 0):
           print usage
           sys.exit(1)
    
        # checking if the parameter value exists
        #jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        path=jdbcProviderScope
        objectId= AdminConfig.getid(path)
        if (len(objectId) == 0):
            print "\n\nNo object can be found at specified scope: " + jdbcProviderScope 
            print ""
            sys.exit(1)
    except:
        print "\n\nException in setOracleDatasourceByScopePath() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        #assuming only 1 cell
        #cellId=AdminConfig.list('Cell')
        #cellName=AdminConfig.showAttribute(cellId, 'name')
        #jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        #if you create the provider in admin console, note it does not add the "Provider" on end for you
        jdbcProviderName='Oracle JDBC Driver Provider'
        jdbcProviderPath = jdbcProviderScope + 'JDBCProvider:'+jdbcProviderName+'/'
        jdbcProviderId= AdminConfig.getid(jdbcProviderPath)
        if (len(jdbcProviderId) == 0):
            print "No jdbc provider found for scope path: " + jdbcProviderScope + ".\nPlease create jdbc provider first before running this script."
            sys.exit(1)
    except:
        print "\n\nException in setOracleDatasourceByScopePath() when getting jdbcProviderId"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        dataSourceTemplateName='Oracle JDBC Driver DataSource'
        dataSourceTemplateId= AdminConfig.listTemplates('DataSource', dataSourceTemplateName)
    except:
        print "\n\nException in setOracleDatasourceByScopePath() when getting dataSourceTemplateId"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        datasourceHelperClassname = 'com.ibm.websphere.rsadapter.Oracle10gDataStoreHelper'
        
        connectionPool=[['maxConnections', maxConnections]]

        resourcePropertyName='URL'
        resourcePropertyValue=url
        customProperty=[['name', resourcePropertyName], ['value', resourcePropertyValue], ['required', 'true']]
        resourceProperties=[customProperty]

        propertySet=[['resourceProperties', resourceProperties]]
        #print "propertySet is: " 
        #print propertySet
        
        resourcePropertyName='description'
        resourcePropertyValue='created by python script'
        customProperty=[['name', resourcePropertyName], ['value', resourcePropertyValue]]
        resourceProperties.append(customProperty)
    except:
        print "\n\nException in setOracleDatasourceByScopePath() when packing up the param lists"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        id = AdminConfig.createUsingTemplate('DataSource', jdbcProviderId, [['name', dataSourceName], ['jndiName', jndiName], ['description', description], ['authDataAlias', authDataAlias], ['statementCacheSize', statementCacheSize], ['connectionPool', connectionPool], ['datasourceHelperClassname', datasourceHelperClassname], ['propertySet', propertySet] ], dataSourceTemplateId)
        print id
    except:
        print "\n\nException in setOracleDatasourceByScopePath() when creating the data source"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
        return id        
    except:
        print "\n\nException in setOracleDatasourceByScopePath() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setOracleDatasourceByScopePath()\n\n"


#--------------------------------------------------------------------
# Create a cluster-level MySql datasource
#--------------------------------------------------------------------
def setClusterLevelMySqlDatasource(clusterName, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, url):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create cluster-level MySql datasource"
        print " clusterName:                              "+clusterName
        print " dataSourceName:                           "+dataSourceName
        print " jndiName:                                 "+jndiName        
        print " authDataAlias:                            "+authDataAlias        
        print " description:                              "+description        
        print " statementCacheSize:                       "+str(statementCacheSize)
        print " maxConnections:                           "+str(maxConnections)
        print " url:                                      "+url        
        msg = " Executing: Datasources.setClusterLevelMySqlDatasource(\""+clusterName+"\", \""+dataSourceName+"\", \""+jndiName+"\", \""+authDataAlias+"\", \""+description+"\", \""+str(statementCacheSize)+"\", \""+str(maxConnections)+"\", \""+url+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(clusterName) == 0):
            print usage
            sys.exit(1)
        if (len(dataSourceName) == 0):
           print usage
           sys.exit(1)
        if (len(jndiName) == 0):
           print usage
           sys.exit(1)
        if (len(authDataAlias) == 0):
           print usage
           sys.exit(1)
        if (len(str(statementCacheSize)) == 0):
           print usage
           sys.exit(1)
        if (len(str(maxConnections)) == 0):
           print usage
           sys.exit(1)

        #MySql-specific
        if (len(url) == 0):
           print usage
           sys.exit(1)
    
        # checking if the parameter value exists
        path='/ServerCluster:'+clusterName+'/'
        clusterId= AdminConfig.getid(path)
        if (len(clusterId) == 0):
            print "The specified cluster at: " + clusterName + " does not exist."
            sys.exit(1)
    except:
        print "\n\nException in setClusterLevelMySqlDatasource() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        jdbcProviderScope = '/ServerCluster:'+clusterName+'/'
        id = setMySqlDatasourceByScopePath(jdbcProviderScope, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, url)
    except:
        print "\n\nException in setClusterLevelMySqlDatasource() when creating the data source"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
        return id        
    except:
        print "\n\nException in setClusterLevelMySqlDatasource() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setClusterLevelMySqlDatasource()\n\n"


#--------------------------------------------------------------------
# Create a server-level MySql datasource
#--------------------------------------------------------------------
def setServerLevelMySqlDatasource(nodeName, serverName, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, url):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create server-level MySql datasource"
        print " nodeName:                                 "+nodeName
        print " serverName:                               "+serverName
        print " dataSourceName:                           "+dataSourceName
        print " jndiName:                                 "+jndiName        
        print " authDataAlias:                            "+authDataAlias        
        print " description:                              "+description        
        print " statementCacheSize:                       "+str(statementCacheSize)
        print " maxConnections:                           "+str(maxConnections)
        print " url:                                      "+url        
        msg = " Executing: Datasources.setServerLevelMySqlDatasource(\""+nodeName+"\", \""+serverName+"\", \""+dataSourceName+"\", \""+jndiName+"\", \""+authDataAlias+"\", \""+description+"\", \""+str(statementCacheSize)+"\", \""+str(maxConnections)+"\", \""+url+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(nodeName) == 0):
            print usage
            sys.exit(1)
        if (len(serverName) == 0):
            print usage
            sys.exit(1)
        if (len(dataSourceName) == 0):
           print usage
           sys.exit(1)
        if (len(jndiName) == 0):
           print usage
           sys.exit(1)
        if (len(authDataAlias) == 0):
           print usage
           sys.exit(1)
        if (len(str(statementCacheSize)) == 0):
           print usage
           sys.exit(1)
        if (len(str(maxConnections)) == 0):
           print usage
           sys.exit(1)

        #MySql-specific
        if (len(url) == 0):
           print usage
           sys.exit(1)
    
        # checking if the parameter value exists
        path='/Node:'+nodeName+'/'
        nodeId= AdminConfig.getid(path)
        if (len(nodeId) == 0):
            print "The specified node at: " + nodeName + " does not exist."
            sys.exit(1)

        # checking if the parameter value exists
        path='/Node:'+nodeName+'/Server:'+serverName+'/'
        serverId= AdminConfig.getid(path)
        if (len(serverId) == 0):
            print "The specified server at: " + serverName + " does not exist."
            sys.exit(1)
    except:
        print "\n\nException in setServerLevelMySqlDatasource() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        #assuming only 1 cell
        cellId=AdminConfig.list('Cell')
        cellName=AdminConfig.showAttribute(cellId, 'name')
        jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        id = setMySqlDatasourceByScopePath(jdbcProviderScope, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, url)
    except:
        print "\n\nException in setServerLevelMySqlDatasource() when creating the data source"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
        return id        
    except:
        print "\n\nException in setServerLevelMySqlDatasource() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setServerLevelMySqlDatasource()\n\n"


#--------------------------------------------------------------------
# Create a MySql datasource by passing in the scope path
# e.g., jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
#--------------------------------------------------------------------
def setMySqlDatasourceByScopePath(jdbcProviderScope, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, url):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create MySql datasource by passing in the scope path"
        print " jdbcProviderScope:                        "+jdbcProviderScope        
        print " dataSourceName:                           "+dataSourceName
        print " jndiName:                                 "+jndiName        
        print " authDataAlias:                            "+authDataAlias        
        print " description:                              "+description        
        print " statementCacheSize:                       "+str(statementCacheSize)
        print " maxConnections:                           "+str(maxConnections)
        print " url:                                      "+url        
        msg = " Executing: Datasources.setMySqlDatasourceByScopePath(\""+jdbcProviderScope+"\", \""+dataSourceName+"\", \""+jndiName+"\", \""+authDataAlias+"\", \""+description+"\", \""+str(statementCacheSize)+"\", \""+str(maxConnections)+"\", \""+url+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(jdbcProviderScope) == 0):
            print usage
            sys.exit(1)
        if (len(dataSourceName) == 0):
           print usage
           sys.exit(1)
        if (len(jndiName) == 0):
           print usage
           sys.exit(1)
        if (len(authDataAlias) == 0):
           print usage
           sys.exit(1)
        if (len(str(statementCacheSize)) == 0):
           print usage
           sys.exit(1)
        if (len(str(maxConnections)) == 0):
           print usage
           sys.exit(1)

        #MySql-specific
        if (len(url) == 0):
           print usage
           sys.exit(1)
    
        # checking if the parameter value exists
        #jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        path=jdbcProviderScope
        objectId= AdminConfig.getid(path)
        if (len(objectId) == 0):
            print "\n\nNo object can be found at specified scope: " + jdbcProviderScope 
            print ""
            sys.exit(1)
    except:
        print "\n\nException in setMySqlDatasourceByScopePath() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        #assuming only 1 cell
        #cellId=AdminConfig.list('Cell')
        #cellName=AdminConfig.showAttribute(cellId, 'name')
        #jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        jdbcProviderName='MySql JDBC Driver Provider'
        jdbcProviderPath = jdbcProviderScope + 'JDBCProvider:'+jdbcProviderName+'/'
        jdbcProviderId= AdminConfig.getid(jdbcProviderPath)
        if (len(jdbcProviderId) == 0):
            print "No jdbc provider found for scope path: " + jdbcProviderScope + ".\nPlease create jdbc provider first before running this script."
            sys.exit(1)
    except:
        print "\n\nException in setMySqlDatasourceByScopePath() when getting jdbcProviderId"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        dataSourceTemplateName='User-defined DataSource'
        dataSourceTemplateId= AdminConfig.listTemplates('DataSource', dataSourceTemplateName)
    except:
        print "\n\nException in setMySqlDatasourceByScopePath() when getting dataSourceTemplateId"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        datasourceHelperClassname = 'com.ibm.websphere.rsadapter.GenericDataStoreHelper'
        
        connectionPool=[['maxConnections', maxConnections]]

        resourcePropertyName='URL'
        resourcePropertyValue=url
        customProperty=[['name', resourcePropertyName], ['value', resourcePropertyValue], ['required', 'true']]
        resourceProperties=[customProperty]

        propertySet=[['resourceProperties', resourceProperties]]
        #print "propertySet is: " 
        #print propertySet
        
        resourcePropertyName='description'
        resourcePropertyValue='created by python script'
        customProperty=[['name', resourcePropertyName], ['value', resourcePropertyValue]]
        resourceProperties.append(customProperty)
    except:
        print "\n\nException in setMySqlDatasourceByScopePath() when packing up the param lists"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        id = AdminConfig.createUsingTemplate('DataSource', jdbcProviderId, [['name', dataSourceName], ['jndiName', jndiName], ['description', description], ['authDataAlias', authDataAlias], ['statementCacheSize', statementCacheSize], ['connectionPool', connectionPool], ['datasourceHelperClassname', datasourceHelperClassname], ['propertySet', propertySet] ], dataSourceTemplateId)
        print id
    except:
        print "\n\nException in setMySqlDatasourceByScopePath() when creating the data source"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
        return id
    except:
        print "\n\nException in setMySqlDatasourceByScopePath() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setMySqlDatasourceByScopePath()\n\n"


#--------------------------------------------------------------------
# Create a cluster-level SQL server datasource
#--------------------------------------------------------------------
def setClusterLevelSqlServerDatasource(clusterName, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, databaseName, databaseServerName):
                                
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a cluster-level SQL Server datasource"
        print " clusterName:                              "+clusterName
        print " dataSourceName:                           "+dataSourceName
        print " jndiName:                                 "+jndiName        
        print " authDataAlias:                            "+authDataAlias        
        print " description:                              "+description        
        print " statementCacheSize:                       "+str(statementCacheSize)
        print " maxConnections:                           "+str(maxConnections)
        print " databaseName:                             "+databaseName        
        print " databaseServerName:                       "+databaseServerName        
        msg = " Executing: Datasources.setClusterLevelSqlServerDatasource(\""+clusterName+"\", \""+dataSourceName+"\", \""+jndiName+"\", \""+authDataAlias+"\", \""+description+"\", \""+str(statementCacheSize)+"\", \""+str(maxConnections)+"\", \""+databaseName+"\", \""+databaseServerName+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(clusterName) == 0):
            print usage
            sys.exit(1)
        if (len(dataSourceName) == 0):
           print usage
           sys.exit(1)
        if (len(jndiName) == 0):
           print usage
           sys.exit(1)
        if (len(authDataAlias) == 0):
           print usage
           sys.exit(1)
        if (len(str(statementCacheSize)) == 0):
           print usage
           sys.exit(1)
        if (len(str(maxConnections)) == 0):
           print usage
           sys.exit(1)

        #SQL-server-specific
        if (len(databaseName) == 0):
           print usage
           sys.exit(1)
        if (len(databaseServerName) == 0):
           print usage
           sys.exit(1)
    
        # checking if the parameter value exists
        path='/ServerCluster:'+clusterName+'/'
        clusterId= AdminConfig.getid(path)
        if (len(clusterId) == 0):
            print "The specified cluster at: " + clusterName + " does not exist."
            sys.exit(1)
    except:
        print "\n\nException in setClusterLevelSqlServerDatasource() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        jdbcProviderScope = '/ServerCluster:'+clusterName+'/'
        id = setSqlServerDatasourceByScopePath(jdbcProviderScope, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, databaseName, databaseServerName)
    except:
        print "\n\nException in setClusterLevelSqlServerDatasource() when creating the data source"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
        return id        
    except:
        print "\n\nException in setClusterLevelSqlServerDatasource() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setClusterLevelSqlServerDatasource()\n\n"


#--------------------------------------------------------------------
# Create a server-level SQL server datasource
#--------------------------------------------------------------------
def setServerLevelSqlServerDatasource(nodeName, serverName, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, databaseName, databaseServerName):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create an SQL Server datasource"
        print " nodeName:                                 "+nodeName
        print " serverName:                               "+serverName
        print " dataSourceName:                           "+dataSourceName
        print " jndiName:                                 "+jndiName        
        print " authDataAlias:                            "+authDataAlias        
        print " description:                              "+description        
        print " statementCacheSize:                       "+str(statementCacheSize)
        print " maxConnections:                           "+str(maxConnections)
        print " databaseName:                             "+databaseName        
        print " databaseServerName:                       "+databaseServerName        
        msg = " Executing: Datasources.setServerLevelSqlServerDatasource(\""+nodeName+"\", \""+serverName+"\", \""+dataSourceName+"\", \""+jndiName+"\", \""+authDataAlias+"\", \""+description+"\", \""+str(statementCacheSize)+"\", \""+str(maxConnections)+"\", \""+databaseName+"\", \""+databaseServerName+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(nodeName) == 0):
            print usage
            sys.exit(1)
        if (len(serverName) == 0):
            print usage
            sys.exit(1)
        if (len(dataSourceName) == 0):
           print usage
           sys.exit(1)
        if (len(jndiName) == 0):
           print usage
           sys.exit(1)
        if (len(authDataAlias) == 0):
           print usage
           sys.exit(1)
        if (len(str(statementCacheSize)) == 0):
           print usage
           sys.exit(1)
        if (len(str(maxConnections)) == 0):
           print usage
           sys.exit(1)

        #SQL-server-specific
        if (len(databaseName) == 0):
           print usage
           sys.exit(1)
        if (len(databaseServerName) == 0):
           print usage
           sys.exit(1)
    
        # checking if the parameter value exists
        path='/Node:'+nodeName+'/'
        nodeId= AdminConfig.getid(path)
        if (len(nodeId) == 0):
            print "The specified node at: " + nodeName + " does not exist."
            sys.exit(1)

        # checking if the parameter value exists
        path='/Node:'+nodeName+'/Server:'+serverName+'/'
        serverId= AdminConfig.getid(path)
        if (len(serverId) == 0):
            print "The specified server at: " + serverName + " does not exist."
            sys.exit(1)
    except:
        print "\n\nException in setServerLevelSqlServerDatasource() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        #assuming only 1 cell
        cellId=AdminConfig.list('Cell')
        cellName=AdminConfig.showAttribute(cellId, 'name')
        jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        id = setSqlServerDatasourceByScopePath(jdbcProviderScope, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, databaseName, databaseServerName)
    except:
        print "\n\nException in setServerLevelSqlServerDatasource() when creating the data source"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
        return id        
    except:
        print "\n\nException in setServerLevelSqlServerDatasource() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setServerLevelSqlServerDatasource()\n\n"


#--------------------------------------------------------------------
# Create a SQL server datasource by passing in the scope path
#--------------------------------------------------------------------
def setSqlServerDatasourceByScopePath(jdbcProviderScope, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, databaseName, databaseServerName):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a SQL server datasource by passing in the scope path"
        print " jdbcProviderScope:                        "+jdbcProviderScope        
        print " dataSourceName:                           "+dataSourceName
        print " jndiName:                                 "+jndiName        
        print " authDataAlias:                            "+authDataAlias        
        print " description:                              "+description        
        print " statementCacheSize:                       "+str(statementCacheSize)
        print " maxConnections:                           "+str(maxConnections)
        print " databaseName:                             "+databaseName        
        print " databaseServerName:                       "+databaseServerName        
        msg = " Executing: Datasources.setSqlServerDatasourceByScopePath(\""+jdbcProviderScope+"\", \""+dataSourceName+"\", \""+jndiName+"\", \""+authDataAlias+"\", \""+description+"\", \""+str(statementCacheSize)+"\", \""+str(maxConnections)+"\", \""+databaseName+"\", \""+databaseServerName+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(jdbcProviderScope) == 0):
            print usage
            sys.exit(1)
        if (len(dataSourceName) == 0):
           print usage
           sys.exit(1)
        if (len(jndiName) == 0):
           print usage
           sys.exit(1)
        if (len(authDataAlias) == 0):
           print usage
           sys.exit(1)
        if (len(str(statementCacheSize)) == 0):
           print usage
           sys.exit(1)
        if (len(str(maxConnections)) == 0):
           print usage
           sys.exit(1)

        #SQL-server-specific
        if (len(databaseName) == 0):
           print usage
           sys.exit(1)
        if (len(databaseServerName) == 0):
           print usage
           sys.exit(1)
    
        # checking if the parameter value exists
        #jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        path=jdbcProviderScope
        objectId= AdminConfig.getid(path)
        if (len(objectId) == 0):
            print "\n\nNo object can be found at specified scope: " + jdbcProviderScope 
            print ""
            sys.exit(1)
    except:
        print "\n\nException in setSqlServerDatasourceByScopePath() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        #assuming only 1 cell
        #cellId=AdminConfig.list('Cell')
        #cellName=AdminConfig.showAttribute(cellId, 'name')
        #jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        #if you created the provider in admin console, note it does not add the "Provider" on end for you
        jdbcProviderName='Microsoft SQL Server JDBC Driver Provider (XA)'
        jdbcProviderPath = jdbcProviderScope + 'JDBCProvider:'+jdbcProviderName+'/'
        jdbcProviderId= AdminConfig.getid(jdbcProviderPath)
        if (len(jdbcProviderId) == 0):
            print "No jdbc provider found for scope path: " + jdbcProviderScope + ".\nPlease create jdbc provider first before running this script."
            sys.exit(1)
    except:
        print "\n\nException in setSqlServerDatasourceByScopePath() when getting jdbcProviderId"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        dataSourceTemplateName='Microsoft SQL Server JDBC Driver - XA DataSource'
        dataSourceTemplateId= AdminConfig.listTemplates('DataSource', dataSourceTemplateName)
    except:
        print "\n\nException in setSqlServerDatasourceByScopePath() when getting dataSourceTemplateId"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        connectionPool=[['maxConnections', maxConnections]]
		
		#Sql server-specific ones 
        resourcePropertyName='databaseName'
        resourcePropertyValue=databaseName
        customProperty=[['name', resourcePropertyName], ['value', resourcePropertyValue], ['required', 'true']]
        resourceProperties=[customProperty]

        #portNumber 1433 is default in admin console
        resourcePropertyName='portNumber'
        resourcePropertyValue=1433
        customProperty=[['name', resourcePropertyName], ['value', resourcePropertyValue], ['required', 'true']]
        resourceProperties.append(customProperty)

        resourcePropertyName='serverName'
        resourcePropertyValue=databaseServerName
        customProperty=[['name', resourcePropertyName], ['value', resourcePropertyValue], ['required', 'true']]
        resourceProperties.append(customProperty)		

        resourcePropertyName='description'
        resourcePropertyValue='created by python script'
        customProperty=[['name', resourcePropertyName], ['value', resourcePropertyValue]]
        resourceProperties.append(customProperty)

        propertySet=[['resourceProperties', resourceProperties]]
        #print "propertySet is: " 
        #print propertySet
		
    except:
        print "\n\nException in setSqlServerDatasourceByScopePath() when packing up the param lists"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        id = AdminConfig.createUsingTemplate('DataSource', jdbcProviderId, [['name', dataSourceName], ['jndiName', jndiName], ['description', description], ['authDataAlias', authDataAlias], ['statementCacheSize', statementCacheSize], ['connectionPool', connectionPool], ['propertySet', propertySet] ], dataSourceTemplateId)		
        print id
    except:
        print "\n\nException in setSqlServerDatasourceByScopePath() when creating the data source"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
        return id
        
    except:
        print "\n\nException in setSqlServerDatasourceByScopePath() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setSqlServerDatasourceByScopePath()\n\n"



def displayNonDefaultDatasourceConnectionPoolSettingsByScopePath(jdbcProviderScope):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Display tuning properties for datasource connection pools"
        print " jdbcProviderScope:                      "+jdbcProviderScope

        msg = " Executing: Datasources.displayNonDefaultDatasourceConnectionPoolSettingsByScopePath(\""+jdbcProviderScope+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        print
        print " Note: Only non-default properties shown."
        print 
        print " Datasources that were MANUALLY created have purge policy EntirePool, vs wsadmin-created ones - FailingConnectionOnly"
        print
    
        import DatasourceDefaults
        

        # checking if the parameter value exists
        #jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        path=jdbcProviderScope
        objectId= AdminConfig.getid(path)
        if (len(objectId) == 0):
            print "\n\nNo object can be found at specified scope: " + jdbcProviderScope 
            sys.exit(1)
        datasourceListString = AdminConfig.list('DataSource', objectId)
        datasourceList = datasourceListString.splitlines()
        #print datasourceList

        for datasource in datasourceList:
            name = AdminConfig.showAttribute(datasource, 'name')
            allDefaults = "true"
            if name != "DefaultEJBTimerDataSource" and name != "Default Datasource": 
                print
                print name
                connectionPoolId = AdminConfig.showAttribute(datasource, 'connectionPool')
                #print AdminConfig.show(connectionPoolId)
                #print
                connectionTimeout = str(AdminConfig.showAttribute(connectionPoolId, 'connectionTimeout'))
                maxConnections = str(AdminConfig.showAttribute(connectionPoolId, 'maxConnections'))
                unusedTimeout = str(AdminConfig.showAttribute(connectionPoolId, 'unusedTimeout'))
                minConnections = str(AdminConfig.showAttribute(connectionPoolId, 'minConnections'))
                purgePolicy = AdminConfig.showAttribute(connectionPoolId, 'purgePolicy')
                agedTimeout = str(AdminConfig.showAttribute(connectionPoolId, 'agedTimeout'))
                reapTime = str(AdminConfig.showAttribute(connectionPoolId, 'reapTime'))
                
                if connectionTimeout != str(DatasourceDefaults.getConnectionTimeout()):
                    allDefaults = "false"
                    print "****************************************************************************************************"
                    print "connectionTimeout: " + connectionTimeout
                    print "****************************************************************************************************"
                
                if maxConnections != str(DatasourceDefaults.getMaxConnections()):
                    allDefaults = "false"
                    print "****************************************************************************************************"
                    print "maxConnections: " + maxConnections
                    print "****************************************************************************************************"
                
                if unusedTimeout != str(DatasourceDefaults.getUnusedTimeout()):
                    allDefaults = "false"
                    print "****************************************************************************************************"
                    print "unusedTimeout: " + unusedTimeout
                    print "****************************************************************************************************"
                
                if minConnections != str(DatasourceDefaults.getMinConnections()):
                    allDefaults = "false"
                    print "****************************************************************************************************"
                    print "minConnections: " + minConnections
                    print "****************************************************************************************************"
                
                if purgePolicy != DatasourceDefaults.getPurgePolicy():
                    allDefaults = "false"
                    print "****************************************************************************************************"
                    print "purgePolicy: " + purgePolicy
                    print "****************************************************************************************************"
                
                if agedTimeout != str(DatasourceDefaults.getAgedTimeout()):
                    allDefaults = "false"
                    print "****************************************************************************************************"
                    print "agedTimeout: " + agedTimeout
                    print "****************************************************************************************************"
                
                if reapTime != str(DatasourceDefaults.getReapTime()):
                    allDefaults = "false"
                    print "****************************************************************************************************"
                    print "reapTime: " + reapTime
                    print "****************************************************************************************************"

                if allDefaults == "true":
                    print "all defaults"
                    print
        
            
    except:
        print "Exception in displayNonDefaultConnectionPoolSettings() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

def displayNonDefaultDatasourceConnectionPoolSettingsByServer(nodeName, serverName):
    try:
        # checking if the parameter value exists
        cellName = AdminControl.getCell()
        jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        path=jdbcProviderScope
        objectId= AdminConfig.getid(path)
        if (len(objectId) == 0):
            print "\n\nNo object can be found at specified scope: " + jdbcProviderScope 
            sys.exit(1)
        displayNonDefaultDatasourceConnectionPoolSettingsByScopePath(jdbcProviderScope)
            
    except:
        print "Exception in displayNonDefaultDatasourceConnectionPoolSettingsByServer() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]) 
        sys.exit(1)

def displayNonDefaultDatasourceConnectionPoolSettingsByCluster(clusterName):
    try:
        # checking if the parameter value exists
        jdbcProviderScope = '/ServerCluster:'+clusterName+'/'
        path=jdbcProviderScope
        objectId= AdminConfig.getid(path)
        if (len(objectId) == 0):
            print "\n\nNo object can be found at specified scope: " + jdbcProviderScope 
            sys.exit(1)
        displayNonDefaultDatasourceConnectionPoolSettingsByScopePath(jdbcProviderScope)
            
    except:
        print "Exception in displayNonDefaultDatasourceConnectionPoolSettingsByCluster() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]) 
        sys.exit(1) 

#--------------------------------------------------------------------
# Modify existing DB2 datasource so it uses Cyberark (or other credential mapper) to get credential instead of normal auth alias
# serverOrClusterNameSubstring is a unique string that occurs in the datasource id, e.g., cluster name or server name (if ds is at unclustered server level)
# Suggest to use this method on a clone of existin datasource, not on the only original
#--------------------------------------------------------------------
def modifyDatasourceCredMappingByDatasourceId(dataSourceId, dataSourceName, mappingConfigAlias, mappingAuthDataAlias):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Add or modify a datasource's credential mapping by passing in the cluster or server nickname (unique substring)"
        print " dataSourceId:                           "+str(dataSourceId)
        print " dataSourceName:                         "+str(dataSourceName)
        print " mappingConfigAlias:                     "+str(mappingConfigAlias)
        print " mappingAuthDataAlias:                   "+str(mappingAuthDataAlias)
        msg = " Executing: Datasources.modifyDatasourceCredMappingByDatasourceId(\""+str(dataSourceId)+"\", \""+str(dataSourceName)+"\", \""+str(mappingConfigAlias)+"\",  \""+str(mappingAuthDataAlias)+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully."
        usage = usage + msg

        # checking required parameters
        if (len(dataSourceId) == 0):
            print usage
            sys.exit(1)
        if (len(dataSourceName) == 0):
           print usage
           sys.exit(1)
        if (len(mappingConfigAlias) == 0):
           print usage
           sys.exit(1)
        if (len(mappingAuthDataAlias) == 0):
           print usage
           sys.exit(1)

        dbType='db2'

        # by default, a prefix gets added to all jaas entries
        # this can be turned off in fixpack over (?) 7.0.0.5 (7?), but it doesn't seem to work right
        stupidNodePrefix = AdminControl.getNode()
        mappingAuthDataAlias = stupidNodePrefix + '/' + mappingAuthDataAlias
        props=[['mappingConfigAlias', mappingConfigAlias],['authDataAlias', mappingAuthDataAlias]]
        
        mappingModuleId = AdminConfig.showAttribute(dataSourceId, 'mapping')
        if mappingModuleId != None:
            print "mappingModuleId already exists; modifying it"
            AdminConfig.modify(mappingModuleId, props)
        else:
            print "mapping module id does not already exist; creating it"
            type="MappingModule"
            print AdminConfig.create(type, dataSourceId, props)
        print "Removing the value for non-mapping (normal) auth alias."
        props=[['authDataAlias', ""]]
        print AdminConfig.modify(dataSourceId, props)
    except:
        print "\n\nException in modifyDatasourceCredMappingByDatasourceId() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
        return
    except:
        print "\n\nException in modifyDatasourceCredMappingByDatasourceId() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of modifyDatasourceCredMappingByDatasourceId()\n\n"

		
def modifyDatasourceByDatasourceId(dataSourceId, props):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Modify a datasource by ds id and passing in props as a list of lists"
        print " dataSourceId:                           "+str(dataSourceId)
        print " props:                                  "+str(props)
        msg = " Executing: Datasources.modifyDatasourceByDatasourceId(\""+str(dataSourceId)+"\", \""+str(props)+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully."
        usage = usage + msg

        # checking required parameters
        if (len(dataSourceId) == 0):
            print usage
            sys.exit(1)
        if props == None:
           print usage
           sys.exit(1)

    except:
        print "\n\nException in modifyDatasourceByDatasourceId() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.modify(dataSourceId, props)
        print "Datasource is modified.\n"
        
    except:
        print "\n\nException in modifyDatasourceByDatasourceId() when modifying datasource"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    try:
        AdminConfig.save()
        return
    except:
        print "\n\nException in modifyDatasourceByDatasourceId() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of modifyDatasourceByDatasourceId()\n\n"



#--------------------------------------------------------------------
# main
#--------------------------------------------------------------------
#when this module is being run as top-level, call the db2 function
if __name__=="__main__":
  usage = " "
  usage = usage + " "
  usage = usage + "Usage: <wsadmin command> -p <target wsadmin.properties file> -f <this py script> \n   <nodeName> <serverName> <dataSourceName> <jndiName>\n    <authDataAlias> <description> <statementCacheSize> <maxConnections> <databaseServerName> <databaseName>\n    [<readOnly>] [<currentSchema>] [<retrieveMessagesFromServerOnGetMessage>])"
  usage = usage + " . . . and must have modified soap.client.props of target wsadmin profile if security is enabled\n"
  print "\n\n"
  #print '\n\nlen(sys.argv) is ' 
  #print len(sys.argv)
  if len(sys.argv) == 13:
    nodeName=sys.argv[0]
    print "nodeName :" + nodeName

    serverName=sys.argv[1]
    print "serverName :" + serverName

    dataSourceName=sys.argv[2]
    print "dataSourceName: " + dataSourceName

    jndiName=sys.argv[3]
    print "jndiName: " + jndiName

    authDataAlias=sys.argv[4]
    print "authDataAlias: " + authDataAlias

    description=sys.argv[5]
    print "description: " + description

    statementCacheSize=sys.argv[6]
    print "statementCacheSize: " + statementCacheSize

    maxConnections=sys.argv[7]
    print "maxConnections: " + maxConnections

    databaseServerName=sys.argv[8]
    print "databaseServerName: " + databaseServerName

    databaseName=sys.argv[9]
    print "databaseName: " + databaseName

    readOnly=sys.argv[10]
    print "readOnly: " + readOnly

    currentSchema=sys.argv[11]
    print "currentSchema: " + currentSchema

    retrieveMessagesFromServerOnGetMessage=sys.argv[12]
    print "retrieveMessagesFromServerOnGetMessage: " + retrieveMessagesFromServerOnGetMessage

    setServerLevelDb2Datasource(nodeName, serverName, dataSourceName, jndiName, authDataAlias, description, statementCacheSize, maxConnections, databaseServerName, databaseName, readOnly, currentSchema, retrieveMessagesFromServerOnGetMessage)
  elif len(sys.argv) == 3:
    configDir=sys.argv[0]
    #print "configDir " + configDir
    # e.g., C:/qdr/ETP_dev/

    #sys.path.append('C:/qdr/ETP_dev/config_scripts')          
    sys.path.append(configDir + 'config_scripts')
    #print "sys.path:" 
    #print sys.path


    nodeName=sys.argv[1]
    print "nodeName :" + nodeName

    serverName=sys.argv[2]
    print "serverName :" + serverName

    displayNonDefaultDatasourceConnectionPoolSettingsByServer(nodeName, serverName)

  elif len(sys.argv) == 2:
    configDir=sys.argv[0]
    sys.path.append(configDir + 'config_scripts')


    clusterName=sys.argv[1]
    print "clusterName :" + clusterName

    displayNonDefaultDatasourceConnectionPoolSettingsByCluster(clusterName)
  
  elif len(sys.argv) == 5:
    configDir=sys.argv[0]
    sys.path.append(configDir + 'config_scripts')
    serverOrClusterNameSubstring=sys.argv[1]
    dataSourceName=sys.argv[2]
    mappingConfigAlias=sys.argv[3]
    mappingAuthDataAlias=sys.argv[4]
    modifyDatasourceCredMappingByDatasourceId(serverOrClusterNameSubstring, dataSourceName, mappingConfigAlias, mappingAuthDataAlias)
  else:
    print ""
    print "wrong number of args"
    print ""
    print usage
    sys.exit(1)


