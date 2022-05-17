###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following procedures:
#   setRemoveNodeNameGlobal
#   setJaasAuthEntry
###############################################################################

#infocenter under Reference:
#'SecurityConfigurationCommands command group for the AdminTask object'
#http://127.0.0.1:65426/help/topic/com.ibm.websphere.nd.doc/info/ae/ae/rxml_7securityconfig.html


#wsadmin.bat -lang jython -f c:/qdr/ETP_dev/config_scripts/Jaas.py 


import sys
import java

import AdminConfig
import AdminTask

import Utilities

#--------------------------------------------------------------------
# Suppress dmgr node name from being prefixed to new JAAS/J2C authentication entries
#
# # to do the same thing in admin console:
#    Security > Global security > (Authentication) > Java Authentication and Authorization Service > 
#     J2C authentication data 
#    uncheck "Prefix new aliasName names with the node name of the cell (for compatibility with earlier releases)"
#
# #  this will make it easier to assign them to the datasources - will be the same across was installations
# #  applies to jaas created either way, both with admin console & scripted
#--------------------------------------------------------------------
def setRemoveNodeNameGlobal(trueOrFalse):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " JAAS/J2C:\n Suppress dmgr node name from being prefixed to new JAAS/J2C authentication entries"
        print "     'true' means prefixing is suppressed."
        print "     'false' means prefixing is done."        
        print " trueOrFalse:                   "+trueOrFalse
        msg = " Executing: Jaas.setRemoveNodeNameGlobal(\""+trueOrFalse+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully."
        usage = usage + msg

        # checking required parameters
        if (len(trueOrFalse) == 0):
            usage = usage + "\nNo parameters."
            print usage
            sys.exit(1)
        if (trueOrFalse != 'true') and (trueOrFalse != 'false'):
            usage = usage + "trueOrFalse must be either 'true' or 'false'"
            print usage
            sys.exit(1)
    except:
        print "Exception in setRemoveNodeNameGlobal() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        securityId = AdminConfig.getid('/Security:/')
        #print securityId
    except:
        print "Exception in setRemoveNodeNameGlobal() when getting securityId"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        securityPropertiesBigString = AdminConfig.showAttribute(securityId, 'properties')
        #print securityPropertiesBigString
        securityPropertiesList = Utilities.convertToList(securityPropertiesBigString)
        propNameExists = 'false'
        jaasPropName = 'com.ibm.websphere.security.JAASAuthData.removealiasNameGlobal'
        for propId in securityPropertiesList:
            #print propId
            propName = AdminConfig.showAttribute(propId, 'name')
            #print 'propName is: ' + propName
            if propName == jaasPropName:
                propNameExists = 'true'
                print "found it: " + propName
                jaasPrefixPropertyId = propId
    except:
        print "Exception in setRemoveNodeNameGlobal() when looking for jaasPrefixPropertyId"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        if (propNameExists == 'true'):
            print AdminConfig.modify(jaasPrefixPropertyId, [['value', trueOrFalse]])
            print "modified prop: " + jaasPrefixPropertyId
        else: 
            jaasPrefixPropertyId = AdminConfig.create('Property', securityId, [['name', jaasPropName], ['value','true']])
            # e.g., 'com.ibm.websphere.security.JAASAuthData.removealiasNameGlobal(cells/DevCell|security.xml#Property_1264060215942)'
            print "created prop" 
    except:
        print "Exception in setRemoveNodeNameGlobal() when modifying or creating jaasPrefixProperty"
        print "propNameExists is: " + propNameExists
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    
    try:
        print AdminConfig.showall(jaasPrefixPropertyId)
        # e.g., 'com.ibm.websphere.security.JAASAuthData.removealiasNameGlobal(cells/DevCell|security.xml#Property_1264060215942)'
    except:
        print "Exception in setRemoveNodeNameGlobal() when displaying jaasPrefixProperty"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        print "\n    Continuing . . . \n"
    try:
        AdminConfig.save()
    except:
        print "Exception in setRemoveNodeNameGlobal() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setRemoveNodeNameGlobal()"

#--------------------------------------------------------------------
# Create a JAAS/J2C authentication entry
#--------------------------------------------------------------------
def setJaasAuthEntry(aliasName, userId, password):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a JAAS/J2C authentication entry"
        print " aliasName:                               "+aliasName
        print " userId:                                  "+userId
        print " password:                                "+password
        msg = " Executing: Jaas.setJaasAuthEntry(\""+aliasName+"\", \""+userId+"\", \""+password+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(aliasName) == 0):
            print usage
            sys.exit(1)
        if (len(userId) == 0):
            print usage
            sys.exit(1)
        if (len(password) == 0):
           print usage
           sys.exit(1)
    except:
        print "\nException in setJaasAuthEntry() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        print AdminTask.createAuthDataEntry(['-alias', aliasName, '-user', userId, '-password', password]) 
        print "created jaas entry for " + aliasName

    except:
        print "\nException in setJaasAuthEntry() when creating jaas/j2c alias entry"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "Exception in setJaasAuthEntry() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setJaasAuthEntry()"



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
	

    aliasName=sys.argv[1]
    print "aliasName: " + aliasName
    userId=sys.argv[2]
    print "userId: " + userId
    password=sys.argv[3]
    print "password: " + password
    setJaasAuthEntry(aliasName, userId, password)
  else:
    print ""
    print "wrong number of args"
    print ""
    print usage
    sys.exit(1)


	
