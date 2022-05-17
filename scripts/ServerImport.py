###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following server management procedures:
#   importServer
###############################################################################
# Notes
# this script does not use script "library" as I didn't see any relevant method in scripts library 
#
#  'ConfigArchiveOperations command group for the AdminTask object using wsadmin scripting'
#   http://publib.boulder.ibm.com/infocenter/wasinfo/fep/topic/com.ibm.websphere.nd.multiplatform.doc/info/ae/ae/rxml_atconfigarchive.html

# Makes an archive of an existing server & use archive to create a new server with the same configuration
#  for this script, new server must have a different name from existing server

# underlying wsadmin export function overwrites file if one alerady exist
# this script appends today's date to archive name to lessen the chance of overwriting a wanted archive
# optional environment label allows having all the car files in the same directory without overwriting each other

# can use ServerArchive.archiveServer to generate the car file to import the server from

#wsadmin.bat -lang jython -f c:\foo\ServerImport.py c:/foo/serverConfigArchive_base_server_2010_01_14.car servers1DevNode tintun


import java
import sys
import time

import AdminConfig
import AdminTask

#--------------------------------------------------------------------
# Create a server by importing a "configuration archive" made from an existing server
#   which could have been in a different WAS node, cell or installation
#--------------------------------------------------------------------
def importServer(serverConfigArchiveFilename, nodeName, newServerName):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create server from clone file of an existing unclustered app server"
        print " serverConfigArchiveFilename:    "+serverConfigArchiveFilename
        print " nodeName:                       "+nodeName
        print " newServerName:                  "+newServerName
        msg = " Executing: ServerClone.importServer(\""+serverConfigArchiveFilename +"\", \""+nodeName+"\", \""+newServerName+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "

        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg
    
        # checking required parameters
        if (len(serverConfigArchiveFilename) == 0):
            print usage
            sys.exit(1)
        if (len(nodeName) == 0):
            print usage
            sys.exit(1)
        if (len(newServerName) == 0):
            print usage
            sys.exit(1)

        # checking if the parameter value exists
        nodeId = AdminConfig.getid("/Node:"+nodeName+"/")
        if (len(nodeId) == 0):
            print "The specified node: " + nodeName + " does not exist."
            sys.exit(1)

        # to do:
        #serverConfigArchiveFilename must exist but skip that & look up syntax later

        #server with new server name must NOT exist
        newServerExist = AdminConfig.getid("/Node:"+nodeName+"/Server:"+newServerName+"/")
        if (len(newServerExist) != 0):
            print "The specified server: " + newServerName + " exists ALREADY."
            sys.exit(1)
        
    except:
        print "\n\nException in importServer() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        serverId=AdminTask.importServer(['-archive', serverConfigArchiveFilename, '-nodeName', nodeName, '-serverName', newServerName])
        print serverId

    except:
        print "\n\nException in importServer() when importing server archive: "+ serverConfigArchiveFilename + " as new server: " + newServerName
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "\n\nException in importServer() when saving to master configuration"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of importServer()\n\n"



#--------------------------------------------------------------------
# main
#--------------------------------------------------------------------
#when this module is being run as top-level, call the function
if __name__=="__main__":
    usage = " "
    usage = usage + " "
    usage = usage + "Usage: <wsadmin command> -p <target wsadmin.properties file> -f <this py script> <serverConfigArchiveFilename, nodeName, newServerName>\n"
    usage = usage + " . . . and must have modified soap.client.props of target wsadmin profile if security is enabled\n"

    if len(sys.argv) == 3:
        serverConfigArchiveFilename=sys.argv[0]
        print "serverConfigArchiveFilename: " + serverConfigArchiveFilename
     
        nodeName=sys.argv[1]
        print "nodeName :" + nodeName
  
        newServerName=sys.argv[2]
        print "newServerName: " + newServerName

        importServer(serverConfigArchiveFilename, nodeName, newServerName)
  
    else:
        print "wrong number of args"
        print usage
        sys.exit(1)

