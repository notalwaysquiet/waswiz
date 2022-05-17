###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following procedures:
#   setBlankNodeLevelWebsphereVariableEntry
#   setGlobalWebsphereVariableEntry
#   createStringNameSpaceBinding
###############################################################################

#not intended to be called as a top-level script

import sys
import AdminConfig
import ItemExists 

#--------------------------------------------------------------------
# Add a value for an existing item in the node's existing list of Websphere variables
# for standard JDBC drivers, the items are automatically created when the node is created, but with blank values.
# No point making it at cell level, as the blank node-level ones will override cell level scope.
# So we must overwrite the node var's blank value with the real value.
# This method throws exception (exits) if var has non-blank values.
#--------------------------------------------------------------------
def setBlankNodeLevelWebsphereVariableEntry(nodeName, symbolicName, newVarValue):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Modify a value for an existing BLANK item in the node's existing list of Websphere variables"
        print " nodeName:                               "+nodeName
        print " symbolicName:                           "+symbolicName
        print " newVarValue:                            "+newVarValue
        msg = " Executing: WebsphereVariables.setBlankNodeLevelWebsphereVariableEntry(\""+symbolicName+"\", \""+newVarValue+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(symbolicName) == 0):
            print usage
            sys.exit(1)
        if (len(newVarValue) == 0):
            print usage
            sys.exit(1)
    except:
        print "Exception in setBlankNodeLevelWebsphereVariableEntry() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        nodeId = AdminConfig.getid("/Node:" + nodeName + "/")
        varSubstitutions = AdminConfig.list("VariableSubstitutionEntry", nodeId).splitlines()

    except:
        print "Exception in setBlankNodeLevelWebsphereVariableEntry() when getting var substitutions list"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        foundVar = "false"
        for varSubst in varSubstitutions:
           getVarName = AdminConfig.showAttribute(varSubst, "symbolicName")
           if getVarName == symbolicName:
                foundVar = "true"
                # check to make sure value is blank
                getVarValue = AdminConfig.showAttribute(varSubst, "value")
                if getVarValue == "" or getVarValue == None:
                # value is "" for built-in vars that have never been modified
                # value is None for existing vars that have had value deleted & saved to config
                    print "Variable: " + getVarName + ": Old value: " + str(getVarValue)
                    AdminConfig.modify(varSubst,[["value", newVarValue]])
                    print "Variable: " + getVarName + ": New value: " + str(AdminConfig.showAttribute(varSubst, "value"))                            
                else:
                    print "Variable: " + getVarName + " is not blank. "
                    print "Value is: " + str(getVarValue) + "\n"
                    print "Cannot modify non-blank var in method WebsphereVariables.setBlankNodeLevelWebsphereVariableEntry()." 
                    print "Exiting.\n\n"
                break
        if foundVar == "false":
            print "Variable: " + getVarName + " not found."
            print "Exiting.\n\n"
            sys.exit(1)
            
    except:
        print "Exception in setBlankNodeLevelWebsphereVariableEntry() when changing var subst entry"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "Exception in setBlankNodeLevelWebsphereVariableEntry() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setBlankNodeLevelWebsphereVariableEntry()"


'''Add a value for an new item in the node's existing list of Websphere variables. For user-defined JDBC drivers, e.g, mysql, item will not exist yet. In variables.xml'''
def createNodeLevelWebsphereVariableEntry(nodeName, symbolicName, value, description):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Add a new item to the node's existing list of Websphere variables"
        print " nodeName:                               "+nodeName
        print " symbolicName:                           "+symbolicName
        print " value:                                  "+value
        print " description:                            "+description
        msg = " Executing: WebsphereVariables.createNodeLevelWebsphereVariableEntry(\""+symbolicName+"\", \""+value+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(symbolicName) == 0):
            print usage
            sys.exit(1)
        if (len(value) == 0):
            print usage
            sys.exit(1)
        if (len(description) == 0):
            description = ""
    except:
        print "Exception in createNodeLevelWebsphereVariableEntry() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        variableMapId = AdminConfig.getid("/Node:" + nodeName +  "/VariableMap:/")
    except:
        print "Exception in createNodeLevelWebsphereVariableEntry() when getting var map id"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        VariableMapEntry = [['symbolicName', symbolicName],
                            ['value', value],
                            ['description', description]]
        #print VariableMapEntry
        entryId = AdminConfig.create("VariableSubstitutionEntry", variableMapId, VariableMapEntry)
        print entryId
    except:
        print "Exception in setGlobalWebsphereVariableEntry() when creating var map entry"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "Exception in createNodeLevelWebsphereVariableEntry() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of createNodeLevelWebsphereVariableEntry()"


#--------------------------------------------------------------------
# Add an entry to the cell's existing list of Websphere variables
#--------------------------------------------------------------------
def setGlobalWebsphereVariableEntry(symbolicName, value):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Add an entry to the cell's existing cell-level list of Websphere variables"
        print " symbolicName:                           "+symbolicName
        print " value:                                  "+value
        msg = " Executing: WebsphereVariables.setGlobalWebsphereVariableEntry(\""+symbolicName+"\", \""+value+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(symbolicName) == 0):
            print usage
            sys.exit(1)
        if (len(value) == 0):
            print usage
            sys.exit(1)
    except:
        print "Exception in setGlobalWebsphereVariableEntry() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        cellName = AdminConfig.showAttribute(AdminConfig.list('Cell'), 'name')
        print cellName
        variableMapId = AdminConfig.getid("/Cell:" + cellName +  "/VariableMap:/")
    except:
        print "Exception in setGlobalWebsphereVariableEntry() when getting var map id"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        VariableMapEntry = [['symbolicName', symbolicName],['value', value]]
        #print VariableMapEntry
    
        print AdminConfig.create("VariableSubstitutionEntry", variableMapId, VariableMapEntry)
    except:
        print "Exception in setGlobalWebsphereVariableEntry() when creating var map entry"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "Exception in setGlobalWebsphereVariableEntry() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setGlobalWebsphereVariableEntry()"


def createStringNameSpaceBinding(name, nameInNameSpace, stringToBind):
# method needed for Cyberark but there is nothing cyberark-specific about it, only the values used
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Add a cell-level string name space binding"
        print " binding name:                           "+str(name)
        print " name in name space:                     "+str(nameInNameSpace)
        print " string to bind:                         "+str(stringToBind)
        msg = " Executing: WebsphereVariables.setGlobalWebsphereVariableEntry(\""+str(name)+"\", \""+str(nameInNameSpace)+"\", \""+str(stringToBind)+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "

        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(str(name)) == 0):
            print usage
            sys.exit(1)
        if (len(str(nameInNameSpace)) == 0):
            print usage
            sys.exit(1)
        if (len(str(stringToBind)) == 0):
            print usage
            sys.exit(1)
            
    except:
        print "Exception in setGlobalWebsphereVariableEntry() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        if ItemExists.stringNameSpaceBindingExists(nameInNameSpace):
            print "string name space binding for name in name space: " + nameInNameSpace + " already exists"
            return
        else:
            type = "StringNameSpaceBinding"
            cellId = AdminConfig.list('Cell')
            nameProp=['name', name]
            nameInNameSpaceProp=['nameInNameSpace', nameInNameSpace]
            stringToBindProp=['stringToBind', stringToBind]
            props=[nameProp, nameInNameSpaceProp, stringToBindProp]
            id = AdminConfig.create(type, cellId, props)
            print "created name space binding for name in name space: " + nameInNameSpace
    except:
        print "\n\nException in createStringNameSpaceBinding"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    try:
        AdminConfig.save()
    except:
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        print "Exception in createStringNameSpaceBinding() when saving to master config"
        
def modifyStringNameSpaceBinding(name, nameInNameSpace, stringToBind):
# method needed for Cyberark but there is nothing cyberark-specific about it, only the values used
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Add a cell-level string name space binding"
        print " binding name:                           "+str(name)
        print " name in name space:                     "+str(nameInNameSpace)
        print " string to bind:                         "+str(stringToBind)
        msg = " Executing: WebsphereVariables.setGlobalWebsphereVariableEntry(\""+str(name)+"\", \""+str(nameInNameSpace)+"\", \""+str(stringToBind)+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "

        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(str(name)) == 0):
            print usage
            sys.exit(1)
        if (len(str(nameInNameSpace)) == 0):
            print usage
            sys.exit(1)
        if (len(str(stringToBind)) == 0):
            print usage
            sys.exit(1)
            
    except:
        print "Exception in setGlobalWebsphereVariableEntry() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        id = ItemExists.stringNameSpaceBindingExists(nameInNameSpace)
        if id:
            type = "StringNameSpaceBinding"
            cellId = AdminConfig.list('Cell')
            nameProp=['name', name]
            nameInNameSpaceProp=['nameInNameSpace', nameInNameSpace]
            stringToBindProp=['stringToBind', stringToBind]
            props=[nameProp, nameInNameSpaceProp, stringToBindProp]
            
            print AdminConfig.modify(id, props)
            print "modified name space binding for name in name space: " + nameInNameSpace
        
        else:
            print "string name space binding for name in name space: " + nameInNameSpace + " doesn't already exist."
            return
        
    except:
        print "\n\nException in modifyStringNameSpaceBinding"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    try:
        AdminConfig.save()
    except:
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        print "Exception in modifyStringNameSpaceBinding() when saving to master config"        
        
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
  if len(sys.argv) == 0:
    setRemoveNodeNameGlobal('true')
    print "called setRemoveNodeNameGlobal('true')"
    print ""
  elif len(sys.argv) == 4:
    configDir=sys.argv[0]
    #print "configDir " + configDir
    # e.g., C:/qdr/ETP_dev/

    #sys.path.append('C:/qdr/ETP_dev/config_scripts')          
    sys.path.append(configDir + 'config_scripts')
    #print "sys.path:" 
    #print sys.path
    # modules are expected to be in the directory we just appended to search path
    import ItemExists 

    bindingName=sys.argv[1]
    print "bindingName: " + bindingName
    nameInNameSpace=sys.argv[2]
    print "nameInNameSpace: " + nameInNameSpace
    stringToBind=sys.argv[3]
    print "stringToBind: " + stringToBind
    createStringNameSpaceBinding(bindingName, nameInNameSpace, stringToBind)
  else:
    print ""
    print "wrong number of args"
    print ""
    print usage
    sys.exit(1)


	
		
