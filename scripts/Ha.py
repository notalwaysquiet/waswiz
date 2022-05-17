###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following High Availability -related procedures:
#       createReplicationDomain
#       addHTTPSessionManagerToDomain
#       enableM2MSessionReplication
###############################################################################
# Notes


import sys

import AdminConfig

#--------------------------------------------------------------------
# Create a replication domain for use by a session manager, dynamic caching service, or stateful session beans
# provides the same defaults as the admin console for values not supplied (other than name)
#--------------------------------------------------------------------
def createReplicationDomain(cellName, name, numberOfReplicas, requestTimeout, encryptionType, useSSL):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a replication domain for use by a session manager, dynamic caching service, or stateful session beans"
        print " name:                 "+name
        print " numberOfReplicas:     "+str(numberOfReplicas)
        print " requestTimeout:       "+str(requestTimeout)
        print " encryptionType:       "+encryptionType
        print " useSSL:               "+useSSL
        msg = " Executing: Ha.createReplicationDomain(\""+name+"\", \""+str(numberOfReplicas)+"\", \""+str(requestTimeout)+ "\", \"" + encryptionType + "\", \"" + useSSL + "\")"
        print msg
        print "---------------------------------------------------------------"

        if (len(name) < 1):
            print "\\n Must provide a name for replication domain\n\n"
            sys.exit(1)
        
        name = ['name', name]

        if (len(str(numberOfReplicas)) < 1):
            numberOfReplicas = 1

        numberOfReplicas = ['numberOfReplicas', numberOfReplicas]

        if (len(str(requestTimeout)) < 1):
            requestTimeout = 5  
          
        requestTimeout = ['requestTimeout', requestTimeout]

        if (len(str(encryptionType)) > 1):
            encryptionType = 'NONE'
          
        encryptionType = ['encryptionType', encryptionType]

        if (len(useSSL) > 1):
            useSSL = 'false'  
          
        useSSL = ['useSSL', useSSL]
        
        properties = ['defaultDataReplicationSettings', [numberOfReplicas, requestTimeout, encryptionType, useSSL]]
        #print properties

        properties = [name, properties]
        #print properties

    except:
        print "Exception in createReplicationDomain() when packing up parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry

    try:
        path='/Cell:'+cellName+'/'
        cellId= AdminConfig.getid(path)

        print AdminConfig.create('DataReplicationDomain', cellId, properties)
    except:
        print "Exception in createReplicationDomain() when creating rep domain"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry

    try:
        print AdminConfig.save()
    except:
        print "Exception in createReplicationDomain() when saving to config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry

    print "end of createReplicationDomain()"


#--------------------------------------------------------------------
# Add a server to specified replication domain for HTTP session replication
#--------------------------------------------------------------------
def addHTTPSessionManagerToDomain(nodeName, serverName, domainName):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Add server to specified replication domain for HTTP session replication."
        print " nodeName:           "+nodeName
        print " serverName:         "+serverName
        print " domainName:         "+domainName
        msg = " Executing: Ha.addHTTPSessionManagerToDomain(\""+nodeName+"\", \""+serverName+"\", \"" +domainName + "\")"
        print msg
        print "---------------------------------------------------------------"
        
        serverId=AdminConfig.getid('/Node:' + nodeName + '/Server:' + serverName)    

    except:
        print "\n Exception in addHTTPSessionManagerToDomain() when getting server id"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry

    try:
        sessionManagerId = AdminConfig.list('SessionManager', serverId)
    except:
        print "\n Exception in addHTTPSessionManagerToDomain() when getting session manager id"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry

    try:
        # NOTE: based on setting up ha in admin console, the sessionDRSPersistenceId does not get created unless session persistence is turned on
        # to do: check first if it exists instead of just creating it
        properties = [['messageBrokerDomainName', domainName]]
        #print properties
        
        # NOTE: the *type* of the thingo is DRSSettings, but the *attribute* name the object will get is sessionDRSPersistence
        print AdminConfig.create('DRSSettings', sessionManagerId, properties)

    except:
        print "\n Exception in addHTTPSessionManagerToDomain() when creating DRSSettings (that's the type) entry in server.sml"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry

    try:
        sessionDRSPersistenceId = AdminConfig.showAttribute(sessionManagerId, 'sessionDRSPersistence')
        print "sessionDRSPersistenceId is: " + sessionDRSPersistenceId
        messageBrokerDomainName = AdminConfig.showAttribute(sessionDRSPersistenceId, 'messageBrokerDomainName')
        print "\n Added server: " + serverName + " to replication domain: " + messageBrokerDomainName
    except:
        print "\n Exception in addHTTPSessionManagerToDomain() when display new rep domain for server"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry

    try:
        print AdminConfig.save()
    except:
        print "Exception in addHTTPSessionManagerToDomain() when saving to config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry

    print "end of addHTTPSessionManagerToDomain()"


#--------------------------------------------------------------------
# Turn on memory-to-memory HTTP session replication & set IBM-recommended properties
#--------------------------------------------------------------------
def enableM2MSessionReplication(nodeName, serverName):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Turn on memory-to-memory HTTP session replication"
        print " nodeName:           "+nodeName
        print " serverName:         "+serverName

        msg = " Executing: Ha.enableM2MSessionReplication(\""+nodeName+"\", \""+serverName + "\")"
        print msg
        print "---------------------------------------------------------------"
        
        serverId=AdminConfig.getid('/Node:' + nodeName + '/Server:' + serverName)    

    except:
        print "\n Exception in enableM2MSessionReplication() when getting server id"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry

    try:
        sessionManagerId = AdminConfig.list('SessionManager', serverId)
    except:
        print "\n Exception in enableM2MSessionReplication() when getting session manager id"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry

    try:
        AdminConfig.modify(sessionManagerId, '[[sessionPersistenceMode "DATA_REPLICATION"]]')
    except:
        print "\n Exception in enableM2MSessionReplication() when enabling memory-to-memory session replication"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    
    #AdminConfig.modify('(cells/SneezyCell/nodes/servers2SneezyNode/servers/t1_lion_server2|server.xml#TuningParams_1299652522699)', '[[writeContents "ALL_SESSION_ATTRIBUTES"] [writeFrequency "END_OF_SERVLET_SERVICE"] [scheduleInvalidation "false"]]') 
    try:
        TuningParamsId = AdminConfig.list('TuningParams', serverId)
        AdminConfig.modify(TuningParamsId, '[[writeContents "ALL_SESSION_ATTRIBUTES"] [writeFrequency "END_OF_SERVLET_SERVICE"] [scheduleInvalidation "false"]]') 
        #AdminConfig.show(TuningParamsId)

    except:
        print "\n Exception in enableM2MSessionReplication() when setting IBM-(Craig Oakley)-recommended session persistence tuning params"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry


    try:
        print AdminConfig.save()
    except:
        print "Exception in enableM2MSessionReplication() when saving to config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry

    print "end of enableM2MSessionReplication()"






