###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following server management procedures:
#   setJvmProcessDefinition
#   setJvmCustomProperty
#   setJvmLogRolling
###############################################################################
# Notes

import sys
import AdminConfig
import ItemExists
import ServerComponent


#--------------------------------------------------------------------
# Set process definition for a server's jvm, e.g., heap size
# see config file for list of frequently used properties
# should support any other attributes of type 'JavaVirtualMachine' not listed there, just add them on
# Calls a generic method in ServerComponent.py
#--------------------------------------------------------------------
def setJvmProcessDefinition(nodeName, serverName, propertyListString):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Set process definition for a server's jvm"
        print " nodeName:             "+nodeName
        print " serverName:           "+serverName
        print " propertyList:         "+str(propertyListString)
        msg = " Executing: Jvm.setJvmProcessDefinition(\""+nodeName+"\", \""+serverName+"\", \""+str(propertyListString)+"\")"
        print msg
        print "---------------------------------------------------------------"

        componentType = 'JavaVirtualMachine'
        print " . . . calling generic method . . . "
        ServerComponent.setProperties(nodeName, serverName, componentType, propertyListString)
    except:
        print "Exception in setJvmProcessDefinition()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setJvmProcessDefinition()"




#--------------------------------------------------------------------
# Set up log rolling for a server's jvm
# see config file for list of frequently used properties
# should support any other attributes of type 'StreamRedirect' not listed there, just add them on
# Calls a generic method in ServerComponent.py
#--------------------------------------------------------------------
def setJvmLogRolling(nodeName, serverName, propertyListString):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Set log rolling for a server's jvm"
        print " nodeName:             "+nodeName
        print " serverName:           "+serverName
        print " propertyList:         "+str(propertyListString)
        msg = " Executing: Jvm.setJvmLogRolling(\""+nodeName+"\", \""+serverName+"\", \""+str(propertyListString)+"\")"
        print msg
        print "---------------------------------------------------------------"

        componentType = 'StreamRedirect'
        componentName = '${SERVER_LOG_ROOT}/SystemOut.log'
        nameName = 'fileName'
        print " . . . calling generic method. . . "
        ServerComponent.setPropertiesByComponentName(nodeName, serverName, componentType, componentName, nameName, propertyListString)

        componentName = '${SERVER_LOG_ROOT}/SystemErr.log'
        print "\n\n"
        print " . . . calling generic method. . . "
        ServerComponent.setPropertiesByComponentName(nodeName, serverName, componentType, componentName, nameName, propertyListString)
        
        
        
    except:
        print "Exception in setJvmLogRolling() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setJvmLogRolling()"




#--------------------------------------------------------------------
# Create a custom property for a server's jvm
#--------------------------------------------------------------------
def setJvmCustomProperty(nodeName, serverName, propertyName, propertyValue, propertyDescription):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a custom property for a server's jvm"
        print " nodeName:             "+nodeName
        print " serverName:           "+serverName
        print " propertyName:         "+str(propertyName)
        print " propertyValue:        "+str(propertyValue)
        print " propertyDescription:  "+str(propertyDescription)
        msg = " Executing: Jvm.setJvmCustomProperty(\""+nodeName+"\", \""+serverName+"\", \""+str(propertyName)+"\", \""+str(propertyValue)+"\", \""+str(propertyDescription)+"\")"
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
        if (len(str(propertyName)) == 0):
            print usage
            sys.exit(1)
        if (len(str(propertyValue)) == 0):
            print usage
            sys.exit(1)

        # checking if the parameter value exists
        nodeExist = AdminConfig.getid("/Node:"+nodeName+"/")
        if (len(nodeExist) == 0):
            print "The specified node: " + nodeName + " does not exist."
            sys.exit(1)
        serverExist = AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
        if (serverExist == ''):
            print "The specified server: " + serverName + " does not exist."
            sys.exit(1)

    except:
        print "\n\nException in setJvmCustomProperty() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    try:    
        serverID=AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
        jvmId = AdminConfig.list('JavaVirtualMachine', serverID)
        #print 'jvmId is ' + jvmId
    
    except:
        print "\n\nException in setJvmCustomProperty() when getting object IDs"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    try:
        #method using AdminConfig
        #caution - justs adds the prop, doesn't check if its already there!!!
        AdminConfig.modify(jvmId, [['systemProperties', [[['description', propertyDescription],['name', propertyName],['required', 'false'],['value', propertyValue]]]]])
    except:
        print "\n\nException in setJvmCustomProperty() when creating jvm custom property"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    try:
        AdminConfig.save()
    except:
        print "\n\nException in setJvmCustomProperty() when saving to master configuration"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setJvmCustomProperty()"




#--------------------------------------------------------------------
# Modify a custom property for a server's jvm
#--------------------------------------------------------------------
def modifyJvmCustomProperty(nodeName, serverName, propertyName, propertyValue, propertyDescription):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Modify an existing custom property for a server's jvm"
        print " nodeName:             "+nodeName
        print " serverName:           "+serverName
        print " propertyName:         "+str(propertyName)
        print " propertyValue:        "+str(propertyValue)
        print " propertyDescription:  "+str(propertyDescription)
        msg = " Executing: Jvm.modifyJvmCustomProperty(\""+nodeName+"\", \""+serverName+"\", \""+str(propertyName)+"\", \""+str(propertyValue)+"\", \""+str(propertyDescription)+"\")"
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
        if (len(str(propertyName)) == 0):
            print usage
            sys.exit(1)
        if (len(str(propertyValue)) == 0):
            print usage
            sys.exit(1)

        # checking if the parameter value exists
        nodeExist = AdminConfig.getid("/Node:"+nodeName+"/")
        if (len(nodeExist) == 0):
            print "The specified node: " + nodeName + " does not exist."
            sys.exit(1)
        serverID = AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
        if (serverID == ''):
            print "The specified server: " + serverName + " does not exist."
            sys.exit(1)
        propertyId = ItemExists.jvmCustomPropExists(nodeName, serverName, propertyName)
        if (propertyId == ''):
            print "The specified property to be modified: " + propertyName + " does not exist."

    except:
        print "\n\nException in modifyJvmCustomProperty() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    try:    
        serverID=AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
        jvmId = AdminConfig.list('JavaVirtualMachine', serverID)
        #print 'jvmId is ' + jvmId
    
    except:
        print "\n\nException in modifyJvmCustomProperty() when getting object IDs"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    try:
        params = [['value', propertyValue]]
        if (len(str(propertyDescription)) != 0):
            params.append(['description', propertyDescription])
        print AdminConfig.modify(propertyId, params)

    except:
        print "\n\nException in modifyJvmCustomProperty() when creating jvm custom property"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    try:
        AdminConfig.save()
    except:
        print "\n\nException in modifyJvmCustomProperty() when saving to master configuration"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of modifyJvmCustomProperty()"


#--------------------------------------------------------------------
# main
#--------------------------------------------------------------------
#when this module is being run as top-level, call the function
if __name__=="__main__":
  usage = " "
  usage = usage + " "
  usage = usage + "Usage: <wsadmin command> -p <target wsadmin.properties file> -f <this py script>  \n"
  usage = usage + " . . . and must have modified soap.client.props of target wsadmin profile if security is enabled\n"
  print "\n\n"
  #print '\n\nlen(sys.argv) is ' 
  #print len(sys.argv)
  if len(sys.argv) == 6:
    configDir=sys.argv[0]
    #print "configDir " + configDir
    # e.g., C:/qdr/ETP_dev/

    #sys.path.append('C:/qdr/ETP_dev/config_scripts')          
    sys.path.append(configDir + 'config_scripts')
    #print "sys.path:" 
    #print sys.path
    # modules are expected to be in the directory we just appended to search path
    import ItemExists
    import ServerComponent

    nodeName=sys.argv[1]
    print "nodeName: " + nodeName
    
    serverName=sys.argv[2]
    print "serverName: " + serverName
    
    propertyName=sys.argv[3]
    print "propertyName: " + propertyName

    propertyValue=sys.argv[3]
    print "propertyValue: " + propertyValue

    propertyDescription=sys.argv[3]
    print "propertyDescription: " + propertyDescription
    
    setJvmCustomProperty(nodeName, serverName, propertyName, propertyValue, propertyDescription)
  else:
    print ""
    print "wrong number of args"
    print ""
    print usage
    sys.exit(1)

	
		
