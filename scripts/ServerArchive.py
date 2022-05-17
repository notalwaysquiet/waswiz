###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following server management procedures:
#   archiveServer
###############################################################################
# Notes
# this script does not use script "library" as I didn't see any relevant method in scripts library 
#
#  'ConfigArchiveOperations command group for the AdminTask object using wsadmin scripting'
#   http://publib.boulder.ibm.com/infocenter/wasinfo/fep/topic/com.ibm.websphere.nd.multiplatform.doc/info/ae/ae/rxml_atconfigarchive.html

# underlying wsadmin export function overwrites file if one alerady exist
# this script appends today's date to archive name to lessen the chance of overwriting a wanted archive
# optional environment label allows having all the car files in the same directory without overwriting each other
# e.g., to make another archive of the same server on the same date, use "a" for label, or use environment name, e.g., qa1

#desktop
#wsadmin.bat -lang jython -f C:/was_configurator\config_scripts\ServerArchive.py servers1QaNode all_defaults_server C:/was_configurator/server_archives/all_defaults_server_7_0_0_0.car

# wsadmin.bat -lang jython -f C:/was_configurator/config_scripts/ServerArchive.py servers1HappyNode all_defaults_8_5_5_7 C:/was_configurator/server_archives/all_defaults_server_8_5_5_7.car

#/opt/IBM/wasv9/profiles/dmgrPlum/bin/wsadmin.sh -f ServerArchive.py servers1PlumNode server1 all_defaults_server_v9_0_5_6

import sys
import time

#--------------------------------------------------------------------
#
# Make an archive of an existing server
#  Archive can then be used to create a new server in this or a different cell or WAS installation
#--------------------------------------------------------------------
def archiveServer(nodeName, serverName, serverConfigArchiveFilename):
    
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Archive an existing app server to a car file (config archive)"
        print " nodeName:                       "+nodeName
        print " serverName:                     "+serverName
        print " serverConfigArchiveFilename:    "+serverConfigArchiveFilename        
        msg = " Executing: ServerArchive.archiveServer(\""+nodeName+"\", \""+serverName+"\", \""+serverConfigArchiveFilename+"\")"
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

        # checking if the parameter value exists
        nodeId = AdminConfig.getid("/Node:"+nodeName+"/")
        if (len(nodeId) == 0):
            print "The specified node: " + nodeName + " does not exist."
            sys.exit(1)

        #server to clone must exist
        serverID = AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
        if (len(serverID) == 0):
            print "The specified server: " + serverName + " does not exist."
            sys.exit(1)
    
    except:
        print "Exception in archiveServer() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminTask.exportServer(['-archive', serverConfigArchiveFilename, '-nodeName', nodeName, '-serverName', serverName])           
        print "serverConfigArchiveFilename: " + serverConfigArchiveFilename
    except:
        print "Exception in archiveServer() when exporting server archive: " + serverConfigArchiveFilename
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of archiveServer()"


#--------------------------------------------------------------------
# main
#--------------------------------------------------------------------
#when this module is being run as top-level, call the function
if __name__=="__main__":

    print "dir: "
    dir()

    usage = " "
    usage = usage + " "
    usage = usage + "Usage: <wsadmin command> -p <target wsadmin.properties file> -f <this py script> <nodeName> <serverName> <path + filename>\n"
    usage = usage + " . . . and must have modified soap.client.props of target wsadmin profile if security is enabled\n"

    if len(sys.argv) == 3:
        nodeName=sys.argv[0]
        print "nodeName :" + nodeName

        serverName=sys.argv[1]
        print "serverName: " + serverName

        fileName=sys.argv[2]
        print "fileName: " + fileName

        archiveServer(nodeName, serverName, fileName)
    else:
        print ""
        print "wrong number of args"
        print ""
        print usage
        sys.exit(1)
else:
    import AdminConfig
    import AdminTask
