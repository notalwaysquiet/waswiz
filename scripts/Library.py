###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following procedures:
#   createClusterScopedSharedLibrary
#   createServerScopedSharedLibrary
#   createScopedSharedLibrary
#   bindLibraryToServer
###############################################################################

#not intended to be called as a top-level script

import sys
import AdminConfig
import ItemExists

#--------------------------------------------------------------------
# Generic method to create shared library at scope of object id passed as param
#--------------------------------------------------------------------
def createScopedSharedLibrary(objectId, libraryName, description, classPath, useIsolatedClassLoader):
    props = "props not defined yet"
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create shared library at scope of object id passed as first param"
        print " objectId:                           "+objectId
        print " libraryName:                        "+libraryName
        print " description:                        "+description
        print " classPath:                          "+classPath
        print " useIsolatedClassLoader:             "+useIsolatedClassLoader
        msg = " Executing: Library.createScopedSharedLibrary(\""+objectId+"\", \""+libraryName+"\", \""+description+"\", \""+classPath+"\", \""+useIsolatedClassLoader+"\")"
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
        if (len(libraryName) == 0):
            print usage
            sys.exit(1)
        if (len(classPath) == 0):
            print usage
            sys.exit(1)
        if (len(useIsolatedClassLoader) == 0):
            print usage
            sys.exit(1)
            
            
    except:
        print "Exception in createScopedSharedLibrary() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        nameProp = ['name', libraryName]
        # If you associate the shared library with a server, the product ignores 
        #  the isolatedClassLoader=true setting and still adds files in the shared library 
        #  to the application server class loader. The product does not use an isolated 
        #  shared library when you associate the shared library with a server.
        # To have it really use isolated classloader, must attach library to application not server
        isolatedClassLoaderProp = ['isolatedClassLoader', useIsolatedClassLoader]
        # nativePath: platform-specific library files for shared library support; for example, .dll, .so, or *SRVPGM objects.
        nativePath = ""
        nativePathProp = ['nativePath', nativePath]
        descriptionProp = ['description', description]
        # classPath = "${WAS_INSTALL_ROOT}/lib/ext/netbeans/5.5"
        # classPath = "${WAS_INSTALL_ROOT}/lib/ext/netbeans/5.5 ${WAS_INSTALL_ROOT}/lib/ext/somethingElse"
        classPathProp = ['classPath', classPath]
        props = [nameProp, isolatedClassLoaderProp, nativePathProp, descriptionProp, classPathProp]
    except:
        print "Exception in createScopedSharedLibrary() when packaging params"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        print AdminConfig.create('Library', objectId, props)
    except:
        print "\n\n  Exception in createScopedSharedLibrary() when creating shared lib for object id:"
        print ""
        print objectId
        print ""
        print "props list: "
        print props
        print ""
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "Exception in createScopedSharedLibrary() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of createScopedSharedLibrary()"


#--------------------------------------------------------------------
# Create shared library at cluster scope 
#--------------------------------------------------------------------
def createClusterScopedSharedLibrary(clusterName, libraryName, description, classPath, useIsolatedClassLoader):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create shared library at cluster scope"
        print " clusterName:                        "+clusterName        
        print " libraryName:                        "+libraryName
        print " description:                        "+description
        print " classPath:                          "+classPath
        print " useIsolatedClassLoader:             "+useIsolatedClassLoader        
        msg = " Executing: Library.createClusterScopedSharedLibrary(\""+clusterName+"\", \""+libraryName+"\", \""+description+"\", \""+classPath+"\", \""+useIsolatedClassLoader+"\")"
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
        if (len(libraryName) == 0):
            print usage
            sys.exit(1)
        if (len(classPath) == 0):
            print usage
            sys.exit(1)
        if (len(useIsolatedClassLoader) == 0):
            print usage
            sys.exit(1)
            
            
    except:
        print "Exception in createClusterScopedSharedLibrary() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        cellName = AdminConfig.showAttribute(AdminConfig.list('Cell'), 'name')
        #print cellName
        clusterId = AdminConfig.getid( '/Cell:' + cellName + '/ServerCluster:' + clusterName + '/')
        #print clusterId
        # print ""
    except:
        print "Exception in createClusterScopedSharedLibrary() when getting cluster id"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        createScopedSharedLibrary(clusterId, libraryName, description, classPath, useIsolatedClassLoader)
    except:
        print "\n\n  Exception in createClusterScopedSharedLibrary() when calling generic method to create shared lib"
        print ""
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "Exception in createClusterScopedSharedLibrary() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of createClusterScopedSharedLibrary()"


#--------------------------------------------------------------------
# Create shared library at server scope 
#--------------------------------------------------------------------
def createServerScopedSharedLibrary(nodeName, serverName, libraryName, description, classPath, useIsolatedClassLoader):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create shared library at server scope"
        print " nodeName:                           "+nodeName
        print " serverName:                         "+serverName        
        print " libraryName:                        "+libraryName
        print " description:                        "+description
        print " classPath:                          "+classPath
        print " useIsolatedClassLoader:             "+useIsolatedClassLoader
        
        msg = " Executing: Library.createServerScopedSharedLibrary(\""+nodeName+"\", \""+serverName+"\", \""+libraryName+"\", \""+description+"\", \""+classPath+"\", \""+useIsolatedClassLoader+"\")"
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
        if (len(libraryName) == 0):
            print usage
            sys.exit(1)
        if (len(classPath) == 0):
            print usage
            sys.exit(1)
        if (len(useIsolatedClassLoader) == 0):
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
        print "Exception in createServerScopedSharedLibrary() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        cellName = AdminConfig.showAttribute(AdminConfig.list('Cell'), 'name')
        #print cellName
        serverId = AdminConfig.getid( '/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + serverName + '/')
        #print serverId
        #print ""
    except:
        print "Exception in createServerScopedSharedLibrary() when getting server id"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        createScopedSharedLibrary(serverId, libraryName, description, classPath, useIsolatedClassLoader)
    except:
        print "\n\n  Exception in createServerScopedSharedLibrary() when calling generic method to create shared lib"
        print ""
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "Exception in createServerScopedSharedLibrary() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of createServerScopedSharedLibrary()"


#--------------------------------------------------------------------
# Bind shared library to classloader of server 
#--------------------------------------------------------------------
def bindLibraryToServer(nodeName, serverName, libraryName):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Bind shared library to classloader of server "
        print " nodeName:                           "+nodeName
        print " serverName:                         "+serverName        
        print " libraryName:                        "+libraryName
        msg = " Executing: Library.bindLibraryToServer(\""+nodeName+"\", \""+serverName+"\", \""+libraryName+"\")"
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
        if (len(libraryName) == 0):
            print usage
            sys.exit(1)
        
        # checking if the parameter value exists
        nodeId = ItemExists.nodeExists(nodeName)
        if (len(nodeId) == 0):
            print "The specified node: " + nodeName + " does not exist."
            sys.exit(1)

        # server must also exist
        serverId = ItemExists.serverExists(nodeName, serverName)
        if (len(serverId) == 0):
            print "The specified server: " + serverName + " does not exist."
            sys.exit(1)
        
        # server must already have a class loader explicitly defined for it
        classLoaderId = ItemExists.serverScopedClassLoaderExists(nodeName, serverName)
        if (len(classLoaderId) == 0):
            print "\n\n The specified server: " + serverName + " must have a classloader explicitly defined prior to calling this method"
            print ""
            sys.exit(1)
            
    except:
        print "Exception in bindLibraryToServer() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        print AdminConfig.create('LibraryRef', classLoaderId, '[[libraryName ' + libraryName + ']]')
        print ""
    except:
        print "Exception in bindLibraryToServer() when binding library to server's classloader"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "Exception in bindLibraryToServer() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of bindLibraryToServer()"

