###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following procedures:
#   createServerClassLoader
#   modifyServerClassLoaderSettings
###############################################################################

#not intended to be called as a top-level script

#--------------------------------------------------------------------
# Set global constants
#--------------------------------------------------------------------
import sys
import AdminConfig
import ItemExists

#--------------------------------------------------------------------
# Create server class loader
#--------------------------------------------------------------------
def createServerClassLoader(nodeName, serverName, mode):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create Create server class loader"
        print " nodeName:                           "+nodeName
        print " serverName:                         "+serverName        
        print " class loader mode:                  "+mode
        msg = " Executing: ClassLoader.createServerClassLoader(\""+nodeName+"\", \""+serverName+"\", \""+mode+"\")"
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
        if (len(mode) == 0):
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
            
    except:
        print "Exception in createServerClassLoader() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        applicationServerId = AdminConfig.list('ApplicationServer', serverId)  
        #print applicationServerId
        #print ""
        if (len(applicationServerId) == 0):
            print "\n\n The specified server: " + serverName + " does not have an application server object"
            sys.exit(1)
    except:
        print "Exception in createServerClassLoader() when getting application server component id"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        classLoaderId = ItemExists.serverScopedClassLoaderExists(nodeName, serverName)
        #print ""
        #print classLoaderId
        #print ""
        
        if (len(classLoaderId) != 0):
            print "\n\n The specified server: " + serverName + " already has at least one classloader explicitly defined:"
            print classLoaderId
            print ""
            sys.exit(1)
    except:
        print "Exception in createServerClassLoader() when checking if class loader is already defined"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        print AdminConfig.create('Classloader', applicationServerId, '[[mode ' + mode + ']]')
    except:
        print "\n\n  Exception in createServerClassLoader() when creating server class loader for server:" + serverName
        print ""
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "Exception in createServerClassLoader() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of createServerClassLoader()"


#--------------------------------------------------------------------
# Modify server class loader
#--------------------------------------------------------------------
def modifyServerClassLoaderSettings(nodeName, serverName, policy, mode):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Modify server class loader settings"
        print " nodeName:                           "+nodeName
        print " serverName:                         "+serverName        
        print " class loader mode:                  "+policy
        print " class loader mode:                  "+mode
        msg = " Executing: ClassLoader.modifyServerClassLoaderSettings(\""+nodeName+"\", \""+serverName+"\", \""+policy+"\", \""+mode+"\")"
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
        if (len(policy) == 0):
            print usage
            sys.exit(1)
        if (len(mode) == 0):
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
            
    except:
        print "Exception in modifyServerClassLoaderSettings() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        applicationServerId = AdminConfig.list('ApplicationServer', serverId)  
        #print applicationServerId
        #print ""
        if (len(applicationServerId) == 0):
            print "\n\n The specified server: " + serverName + " does not have an application server object"
            sys.exit(1)
    except:
        print "Exception in modifyServerClassLoaderSettings() when getting application server component id"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        policyProp = ['applicationClassLoaderPolicy', policy]
        modeProp = ['applicationClassLoadingMode', mode]
        props = [policyProp, modeProp]
    except:
        print "Exception in modifyServerClassLoaderSettings() when packaging props"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.modify(applicationServerId, props)  
    except:
        print "Exception in modifyServerClassLoaderSettings() when modifying settings"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

    try:
        AdminConfig.save()
    except:
        print "Exception in modifyServerClassLoaderSettings() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of modifyServerClassLoaderSettings()"

