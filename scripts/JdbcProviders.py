###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following procedures:
#   createClusterScopedJdbcProvider
#   createServerScopedJdbcProvider
#   createJDBCProviderByObjectId
#   deleteRubbishDatasource
###############################################################################

#wsadmin.bat -lang jython =user builtin -password xxxxxx -f c:/qdr/ETP_dev/config_scripts/jdbcProviders.py servers1DevNode commercialclick_dev_be_server1 oracle
#wsadmin.bat -lang jython -f c:/qdr/ETP_dev/config_scripts/jdbcProviders.py nodeName serverName db2
#wsadmin.bat -lang jython -f c:/qdr/ETP_dev/config_scripts/jdbcProviders.py servers1DevNode tier1_be_server1 db2

#jdbc provider templates are in (for standalone) C:\was764\profiles\AppSrv01\config\templates\system\jdbc-resource-provider-templates.xml


import java
import sys
import time
import AdminConfig
import ItemExists

def getJdbcProviderName(dbType):
    try:
        if (dbType.lower() == "db2"):
            #for "DB2 connection pool data source, i.e., 1-phase"
            #jdbcProviderName='DB2 Universal JDBC Driver Provider'
            #jdbcProviderDescriptionAttribute=['description', "One-phase commit DB2 JCC provider that supports JDBC 3.0. Data sources that use this provider support only 1-phase commit processing."]
            #jdbcProviderXaAttribute=['xa', "false"]

            #for "DB2 XA data source, i.e., 2-phase"
            jdbcProviderName='DB2 Universal JDBC Driver Provider (XA)'
            jdbcProviderNameAttribute= ['name', jdbcProviderName]
            jdbcProviderDescriptionAttribute=['description', "Two-phase commit DB2 JCC provider that supports JDBC 3.0. Data sources that use this provider support the use of XA to perform 2-phase commit processing."]            
            jdbcProviderXaAttribute=['xa', "true"]

        elif (dbType.lower() == "mysql"):
            #jdbcProviderName here = providerType in resources.xml = database type in create jdbc provider wizard (admin console)
            jdbcProviderName='User-defined JDBC Provider'
            
        elif (dbType.lower() == "oracle"):
            #for some reason oracle provider *template* name lacks "Provider" at end
            jdbcProviderName='Oracle JDBC Driver'
            

        elif (dbType.lower() == "sqlserver"):
            #for some reason sqlserver provider *template* name lacks "Provider" at end
            jdbcProviderName="Microsoft SQL Server JDBC Driver (XA)"
        else:
            print "/n DB type not recognized: " + dbType
            sys.exit(1)
        return jdbcProviderName
			
    except:
        print "\n\nException in getJdbcProviderName() when getting the provider name"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
            
#--------------------------------------------------------------------
# Create a cluster-scoped JDBC Provider
#--------------------------------------------------------------------
def createClusterScopedJdbcProvider(clusterName, dbType):
    jdbcProviderName='not defined yet'
    try:
        print "\n"
        print "---------------------------------------------------------------"
        print " Create cluster-scoped JDBC Provider"
        print " clusterName:                    "+clusterName
        print " dbType:                         "+dbType        
        msg = " Executing: jdbcProviders.createClusterScopedJdbcProvider(\""+clusterName+"\", \""+dbType+"\")"
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
        if (len(dbType) == 0):
            print usage
            sys.exit(1)

        # checking if the parameter value exists
        clusterId = ItemExists.clusterExists(clusterName)
        if (len(clusterId) == 0):
            print "The specified cluster: " + clusterName + " does not exist."
            sys.exit(1)
        
        if (dbType.lower() != "db2") and (dbType.lower() != "oracle") and (dbType.lower() != "sqlserver") and (dbType.lower() != "mysql"):
            print 'Please specify "db2", "mysql", "sqlserver" or "oracle" for dbType (case insensitive)'
            sys.exit(1)
    except:
        print "\n\nException in createClusterScopedJdbcProvider() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
		createJDBCProviderByObjectId(clusterId, dbType)
    except:
        print "\n\nException when calling generic method to create the provider"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of createClusterScopedJdbcProvider()"


#--------------------------------------------------------------------
# Create a server-scoped JDBC Provider
#--------------------------------------------------------------------
def createServerScopedJdbcProvider(nodeName, serverName, dbType):
    jdbcProviderName='not defined yet'
    try:
        print "\n"
        print "---------------------------------------------------------------"
        print " Create server-scoped JDBC Provider"
        print " nodeName:                       "+nodeName
        print " serverName:                     "+serverName
        print " dbType:                         "+dbType        
        msg = " Executing: jdbcProviders.createServerScopedJdbcProvider(\""+nodeName+"\", \""+serverName+"\", \""+dbType+"\")"
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
        if (len(dbType) == 0):
            print usage
            sys.exit(1)

        # checking if the parameter value exists
        nodeId = ItemExists.nodeExists(nodeName)
        if (len(nodeId) == 0):
            print "The specified node: " + nodeName + " does not exist."
            sys.exit(1)

        #server must also exist
        serverId = ItemExists.serverExists(nodeName, serverName)
        if (len(serverId) == 0):
            print "The specified server: " + serverName + " does not exist."
            sys.exit(1)

        if (dbType.lower() != "db2") and (dbType.lower() != "oracle") and (dbType.lower() != "sqlserver") and (dbType.lower() != "mysql"):
            print 'Please specify "db2", "mysql", "sqlserver" or "oracle" for dbType (case insensitive)'
            sys.exit(1)
    except:
        print "\n\nException in createServerScopedJdbcProvider() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
		createJDBCProviderByObjectId(serverId, dbType)
    except:
        print "\n\nException when calling generic method to create the provider"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    #endTry
    print "end of createServerScopedJdbcProvider()"


#--------------------------------------------------------------------
# Create a JDBC Provider by passing in the  object id for the desired scope (e.g., serverId or clusterId)
# valid dbTypes are db2, oracle, mysql, sqlserver
#--------------------------------------------------------------------
def createJDBCProviderByObjectId(objectId, dbType):
    jdbcProviderName='not defined yet'
    try:
        print "\n"
        print "---------------------------------------------------------------"
        print " Create a JDBC Provider by passing in the wsadmin object id of the desired scope (e.g., serverId or clusterId)"
        print " objectId:                       "+objectId
        print " dbType:                         "+dbType        
        msg = " Executing: jdbcProviders.createJDBCProviderByObjectId(\""+objectId+"\", \""+dbType+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "

        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg
    
        # checking required parameters
        if (len(objectId) == 0):
            print usage
            sys.exit(1)
        if (len(dbType) == 0):
            print usage
            sys.exit(1)

        # checking if the parameter value exists
        objectName = AdminConfig.showAttribute(objectId, 'name')
        if (len(objectName) == 0):
            print ""
            print "Cannot find object with specified id: " + objectId
            print ""
            sys.exit(1)

        if (dbType.lower() != "db2") and (dbType.lower() != "sqlserver") and (dbType.lower() != "oracle") and (dbType.lower() != "mysql"):
            print 'Please specify "db2", "mysql", "sqlserver", or "oracle" for dbType (case insensitive)'
            sys.exit(1)
    except:
        print "\n\nException in createJDBCProviderByObjectId() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        if (dbType.lower() == "db2"):
            #for "DB2 connection pool data source, i.e., 1-phase"
            #jdbcProviderName='DB2 Universal JDBC Driver Provider'
            #jdbcProviderDescriptionAttribute=['description', "One-phase commit DB2 JCC provider that supports JDBC 3.0. Data sources that use this provider support only 1-phase commit processing."]
            #jdbcProviderXaAttribute=['xa', "false"]

            #for "DB2 XA data source, i.e., 2-phase"
            jdbcProviderName='DB2 Universal JDBC Driver Provider (XA)'
            jdbcProviderNameAttribute= ['name', jdbcProviderName]
            jdbcProviderDescriptionAttribute=['description', "Two-phase commit DB2 JCC provider that supports JDBC 3.0. Data sources that use this provider support the use of XA to perform 2-phase commit processing."]            
            jdbcProviderXaAttribute=['xa', "true"]

        elif (dbType.lower() == "mysql"):
            #jdbcProviderName here = providerType in resources.xml = database type in create jdbc provider wizard (admin console)
            jdbcProviderName='User-defined JDBC Provider'
            
        elif (dbType.lower() == "oracle"):
            #for some reason oracle provider *template* name lacks "Provider" at end
            jdbcProviderName='Oracle JDBC Driver'
            

        elif (dbType.lower() == "sqlserver"):
            #for some reason sqlserver provider *template* name lacks "Provider" at end
            jdbcProviderName="Microsoft SQL Server JDBC Driver (XA)"
			
        jdbcTemplateString=jdbcProviderName + '(templates/system'
        jdbcTemplateId = AdminConfig.listTemplates('JDBCProvider', jdbcTemplateString)
        print 'jdbcTemplateId is ' + jdbcTemplateId
    except:
        print "\n\nException in createJDBCProviderByObjectId() when getting the provider template"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        if (dbType.lower() == "db2"):
            jdbcAttrs = [jdbcProviderNameAttribute,jdbcProviderDescriptionAttribute, jdbcProviderXaAttribute]

        elif (dbType.lower() == "mysql"):
            jdbcProviderName = "MySql JDBC Driver Provider"
            jdbcProviderNameAttribute= ['name', jdbcProviderName]
            jdbcProviderDescriptionAttribute=['description', "MySql 5.1.20 Driver Provider"]
            jdbcProviderClasspath = "${MYSQL_JDBC_DRIVER_PATH}/mysql-connector-java-5.1.20-bin.jar"
            jdbcProviderClasspathAttribute = ['classpath', jdbcProviderClasspath]
            implementationClassName = "com.mysql.jdbc.jdbc2.optional.MysqlConnectionPoolDataSource"
            implementationClassNameAttribute = ['implementationClassName', implementationClassName]
            jdbcAttrs = [jdbcProviderNameAttribute,jdbcProviderDescriptionAttribute,jdbcProviderClasspathAttribute,implementationClassNameAttribute]
        
        elif (dbType.lower() == "oracle"):    
            #I am adding the "Provider" at the end, over what the default name/descr is when you create it in admin console			
            jdbcProviderName = jdbcProviderName + ' Provider'
            jdbcProviderNameAttribute= ['name', jdbcProviderName]
            jdbcProviderDescriptionAttribute=['description', "Oracle JDBC Driver Provider"]

            # override the default classpath that is in the template, which is objdbc6.jar (WRONG!) no such thing
            # per Stephen W 19/8/2011, we are also not using ojdbc14.jar whihc does exist but rather classes12.zip which is older
            jdbcProviderClasspath = "${ORACLE_JDBC_DRIVER_PATH}/classes12.zip"
            jdbcProviderClasspathAttribute = ['classpath', jdbcProviderClasspath]
            #per Stephen W 19/8/2011  override the default implementationClassName that is in the template, which is oracle.jdbc.pool.OracleConnectionPoolDataSource
            implementationClassName = "oracle.jdbc.xa.client.OracleXADataSource"
            implementationClassNameAttribute = ['implementationClassName', implementationClassName]
            jdbcAttrs = [jdbcProviderNameAttribute,jdbcProviderDescriptionAttribute,jdbcProviderClasspathAttribute,implementationClassNameAttribute]

     	elif (dbType.lower() == "sqlserver"):
            #I am adding the "Provider" at the end, over what the default name/descr is when you create it in admin console			
            jdbcProviderName = "Microsoft SQL Server JDBC Driver Provider (XA)"
            jdbcProviderNameAttribute= ['name', jdbcProviderName]
            jdbcProviderDescriptionAttribute=['description', "Microsoft SQL Server JDBC Driver Provider (XA)"]

            # classpath in the template is wrong jar, sqljdbc.jar - I think that's for older jdk
            jdbcProviderClasspath = "${MICROSOFT_JDBC_DRIVER_PATH}/sqljdbc4.jar"
            jdbcProviderClasspathAttribute = ['classpath', jdbcProviderClasspath]
            jdbcAttrs = [jdbcProviderNameAttribute, jdbcProviderDescriptionAttribute, jdbcProviderClasspathAttribute]
        
        jdbcProviderId = AdminConfig.createUsingTemplate('JDBCProvider', objectId, jdbcAttrs, jdbcTemplateId)
        print jdbcProviderId
        
        deleteRubbishDatasourceByJdbcProviderId(jdbcProviderId, dbType)
  
    except:
        print "\n\nException in createJDBCProviderByObjectId() when creating the provider"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "\n\nException in createJDBCProviderByObjectId() when saving to master configuration"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of createJDBCProviderByObjectId()"


# Delete the automatically created datasource for a new jdbc provider
# assumes we have just created the jdbc provider so we know there is only 1 for the scope
# getid should return a unique datasource, as the provider name specifies the scope, and we only just created it
def deleteRubbishDatasource(jdbcProviderScope, dbType):
    try:
        print "\n"
        print "---------------------------------------------------------------"
        print " Delete the automatically created datasource for a new jdbc provider"
        print " jdbcProviderScope:              "+jdbcProviderScope
        print " dbType:                         "+dbType        
        msg = " Executing: jdbcProviders.deleteRubbishDatasource(\""+jdbcProviderScope+"\", \""+dbType+"\")"
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
        if (len(dbType) == 0):
            print usage
            sys.exit(1)

        # checking if the parameter value exists
        path=jdbcProviderScope
        objectId= AdminConfig.getid(path)
        objectName = AdminConfig.showAttribute(objectId, 'name')
        if (len(objectName) == 0):
            print ""
            print "Cannot find object with specified id: " + jdbcProviderScope
            print ""
            sys.exit(1)
    except:
        print "\n\nException in deleteRubbishDatasource() when checking the parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        jdbcProviderContainmentPath = "jdbcProviderContainmentPath not defined yet"
		#jdbcProviderScope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
		
        if dbType == 'db2':
            #name if XA
            jdbcProviderName='DB2 Universal JDBC Driver Provider (XA)'
            #name if not XA
            #jdbcProviderName='DB2 Universal JDBC Driver Provider'
            #name if XA
            rubbishDatasourceName = 'DB2 Universal JDBC Driver XA DataSource'
            #name if not XA
            #rubbishDatasourceName = 'DB2 Universal JDBC Driver DataSource'
        elif dbType == 'mysql':
            jdbcProviderName='MySql JDBC Driver Provider'
            rubbishDatasourceName = 'User-defined DataSource'
        elif dbType == 'oracle':
            jdbcProviderName='Oracle JDBC Driver Provider'
            rubbishDatasourceName = 'Oracle JDBC Driver DataSource '
        elif dbType == 'sqlserver':
            jdbcProviderName='Microsoft SQL Server JDBC Driver Provider (XA)'
            rubbishDatasourceName = 'Microsoft SQL Server JDBC Driver - XA DataSource'

        jdbcProviderContainmentPath = jdbcProviderScope + 'JDBCProvider:'+jdbcProviderName+'/'
        dataSourcePath=jdbcProviderContainmentPath + 'DataSource:' + rubbishDatasourceName + '/'
        dataSourceId=AdminConfig.getid(dataSourcePath)
        #print "jdbcProviderName: " + jdbcProviderName
        #print "jdbcProviderContainmentPath: " + jdbcProviderContainmentPath
        #print "rubbishDatasourceName: " + rubbishDatasourceName
        #print "dataSourceId: " + dataSourceId
        if len(dataSourceId) > 0:
            AdminConfig.remove(dataSourceId)
            print "Rubbish automatically created datasource removed: \n" + dataSourceId
        else:
            print "\nRubbish automatically created datasource not found: " + jdbcProviderContainmentPath
    except:
        print "\n\nException in deleteRubbishDatasource() when removing rubbish automatically created datasource for DB type: " + dbType + " for scope: " + jdbcProviderScope
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "Exception in deleteRubbishDatasource() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


# Delete the automatically created datasource for a new jdbc provider
# assumes we have just created the jdbc provider so we know there is only 1 for the scope
# getid should return a unique datasource, as the provider name specifies the scope, and we only just created it
def deleteRubbishDatasourceByJdbcProviderId(jdbcProviderId, dbType):
    try:
        print "\n"
        print "---------------------------------------------------------------"
        print " Delete the automatically created datasource for a new jdbc provider"
        print " jdbcProviderId:                 "+jdbcProviderId
        print " dbType:                         "+dbType        
        msg = " Executing: jdbcProviders.deleteRubbishDatasourceByJdbcProviderId(\""+jdbcProviderId+"\", \""+dbType+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "

        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg
    
        # checking required parameters
        if (len(jdbcProviderId) == 0):
            print usage
            sys.exit(1)
        if (len(dbType) == 0):
            print usage
            sys.exit(1)

        # checking if the parameter value exists
        objectName = AdminConfig.showAttribute(jdbcProviderId, 'name')
        if (len(objectName) == 0):
            print ""
            print "Cannot find object with specified id: " + jdbcProviderId
            print ""
            sys.exit(1)
    except:
        print "\n\nException in deleteRubbishDatasourceByJdbcProviderId() when checking the parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        jdbcProviderContainmentPath = "jdbcProviderContainmentPath not defined yet"
		#jdbcProviderId = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
		
        if dbType == 'db2':
            #name if XA
            jdbcProviderName='DB2 Universal JDBC Driver Provider (XA)'
            #name if not XA
            #jdbcProviderName='DB2 Universal JDBC Driver Provider'
            #name if XA
            rubbishDatasourceName = 'DB2 Universal JDBC Driver XA DataSource'
            #name if not XA
            #rubbishDatasourceName = 'DB2 Universal JDBC Driver DataSource'
        elif dbType == 'mysql':
            jdbcProviderName='MySql JDBC Driver Provider'
            rubbishDatasourceName = 'User-defined DataSource'
        elif dbType == 'oracle':
            jdbcProviderName='Oracle JDBC Driver Provider'
            rubbishDatasourceName = 'Oracle JDBC Driver DataSource '
        elif dbType == 'sqlserver':
            jdbcProviderName='Microsoft SQL Server JDBC Driver Provider (XA)'
            rubbishDatasourceName = 'Microsoft SQL Server JDBC Driver - XA DataSource'

        jdbcProviderContainmentPath = '/JDBCProvider:'+jdbcProviderName
        dataSourcePath=jdbcProviderContainmentPath + '/DataSource:' + rubbishDatasourceName
        dataSourceId=AdminConfig.getid(dataSourcePath)
        #print "jdbcProviderName: " + jdbcProviderName
        #print "jdbcProviderContainmentPath: " + jdbcProviderContainmentPath
        #print "rubbishDatasourceName: " + rubbishDatasourceName
        #print "dataSourceId: " + dataSourceId
        if len(dataSourceId) > 0:
            AdminConfig.remove(dataSourceId)
            print "Rubbish automatically created datasource removed: \n" + dataSourceId
        else:
            print "\nRubbish automatically created datasource not found: " + jdbcProviderContainmentPath
    except:
        print "\n\nException in deleteRubbishDatasourceByJdbcProviderId() when removing rubbish automatically created datasource for DB type: " + dbType + " for scope: " + jdbcProviderId
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "Exception in deleteRubbishDatasourceByJdbcProviderId() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


#--------------------------------------------------------------------
# main
#--------------------------------------------------------------------
#when this module is being run as top-level, call the function
if __name__=="__main__":
    usage = " "
    usage = usage + " "
    usage = usage + "Usage: <wsadmin command> -p <target wsadmin.properties file> -f <this py script> <nodeName, serverName, dbType>\n"
    usage = usage + " . . . and must have modified soap.client.props of target wsadmin profile if security is enabled\n"

    if len(sys.argv) == 3:
        nodeName=sys.argv[0]
        print "nodeName :" + nodeName
  
        serverName=sys.argv[1]
        print "serverName: " + serverName
        
        dbType=sys.argv[2]
        print "dbType: " + dbType        


        print createServerScopedJdbcProvider(nodeName, serverName, dbType)
  
    else:
        print "\n\nwrong number of args"
        print usage
        sys.exit(1)

