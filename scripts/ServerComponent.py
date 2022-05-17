###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following server management procedures:
#       setProperties
#       setPropertiesByComponentName
#   Gets called by various methods:
#       Jvm.setJvmProcessDefinition
#       WebContainer.setWebContainerProperties
#       WebContainer.setWebContainerThreadPoolProperties
###############################################################################
# Notes


import sys
import AdminConfig

import Utilities

#--------------------------------------------------------------------
# Generic method to set properties for a component of a server, e.g., jvm, web container
# This makes the most sense where the properties are all simple data types, and 
#   we do not know in advance how many or which ones we will want to set
# Gets called by a handful of more specific methods that pass in name of the component type
# componentType must be one of AdminConfig.types()
# Can probably use a list instead of a string for the bunch of properties but a string is easier to construct (fewer commas)
# get list of allowable properties for a type, e.g., 'WebContainer' by AdminConfig.attributes('WebContainer')
# example of how to call: ServerComponent.setProperties("servers1DevNode", "tier1_fe_server1", "JavaVirtualMachine", "[[verboseModeGarbageCollection 'true'] [maximumHeapSize 512] [initialHeapSize 512] ]")
#--------------------------------------------------------------------
def setProperties(nodeName, serverName, componentType, propertyListString):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Set properties for a server component"
        print " nodeName:             "+nodeName
        print " serverName:           "+serverName
        print " componentType:        "+componentType
        print " propertyList:         "+str(propertyListString)
        msg = " Executing: ServerComponent.setProperties(\""+nodeName+"\", \""+serverName+"\", \""+componentType+"\", \""+str(propertyListString)+"\")"
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
        if (len(componentType) == 0):
            print usage
            sys.exit(1)
        if (len(propertyListString) == 0):
            print usage
            sys.exit(1)

        # checking if the parameter value exists
        nodeExist = AdminConfig.getid("/Node:"+nodeName+"/")
        if (len(nodeExist) == 0):
            print "The specified node: " + nodeName + " does not exist."
            sys.exit(1)
        serverId = AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
        if (serverId == ''):
            print "The specified server: " + serverName + " does not exist."
            sys.exit(1)
                    

    except:
        print "Exception in setProperties() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    try:    
        componentId = AdminConfig.list(componentType, serverId)
        #print 'componentId is ' + componentId
    
    except:
        print "Exception in setProperties() when getting object IDs"
        print "componentType must be one of AdminConfig.types()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    try:

        AdminConfig.modify(componentId, propertyListString)
        print "modified component: " + componentId
    except:
        print "Exception in setProperties() when setting property or properties"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    try:
        AdminConfig.save()
    except:
        print "Exception in setProperties() when saving to master configuration"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setProperties()"


#--------------------------------------------------------------------
# Generic method to set properties for a component of a server, 
#  where there is more than one component of the given type
#  so we need to further specify the name, e.g., jvm log (error or out), thread pools (a whole bunch)
# Otherwise very very similar to setProperties()
#--------------------------------------------------------------------
def setPropertiesByComponentName(nodeName, serverName, componentType, componentName, nameName, propertyListString):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Set properties for a server component"
        print " nodeName:             "+nodeName
        print " serverName:           "+serverName
        print " componentType:        "+componentType
        print " componentName:        "+componentName
        print " nameName:             "+nameName
        print " propertyList:         "+str(propertyListString)
        msg = " Executing: ServerComponent.setPropertiesByComponentName(\""+nodeName+"\", \""+serverName+"\", \""+componentType+"\", \""+componentName+"\", \""+nameName+"\", \""+str(propertyListString)+"\")"
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
        if (len(componentType) == 0):
            print usage
            sys.exit(1)
        if (len(componentName) == 0):
            print usage
            sys.exit(1)
        if (len(nameName) == 0):
            print usage
            sys.exit(1)
        if (len(propertyListString) == 0):
            print usage
            sys.exit(1)

        # checking if the parameter value exists
        nodeExist = AdminConfig.getid("/Node:"+nodeName+"/")
        if (len(nodeExist) == 0):
            print "The specified node: " + nodeName + " does not exist."
            sys.exit(1)
        serverId = AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
        if (serverId == ''):
            print "The specified server: " + serverName + " does not exist."
            sys.exit(1)
                    

    except:
        print "Exception in setPropertiesByComponentName() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    try:    
        componentIdListString = AdminConfig.list(componentType, serverId)
        componentIdList = Utilities.convertToList(componentIdListString)
        #print "componentIdList: "
        #print componentIdList
        componentIdToChange = 'componentIdToChange not defined yet'
        for componentId in componentIdList:
            if (AdminConfig.showAttribute(componentId, nameName) == componentName):
                componentIdToChange = componentId
    
    except:
        print "Exception in setPropertiesByComponentName() when getting object IDs"
        print "componentType must be one of AdminConfig.types()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    try:

        AdminConfig.modify(componentIdToChange, propertyListString)
        print "modified component: " + componentIdToChange
    except:
        print "Exception in setPropertiesByComponentName() when setting property or properties"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    try:
        AdminConfig.save()
    except:
        print "Exception in setPropertiesByComponentName() when saving to master configuration"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setPropertiesByComponentName()"


