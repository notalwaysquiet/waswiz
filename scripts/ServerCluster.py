###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following server management procedures:
#   convertServerToCluster(nodeName, serverName, clusterName)
#   addAnotherServerToCluster(nodeName, serverName, clusterName)
###############################################################################
# Notes
# this script does not use script "library" as I didn't see any relevant method in scripts library 

# in was 7.0.0.0 clusters created by this script (even when save succeeds) do not show up in admin console unless you log out & back in
# this can create a lot of confusion!!! but you can use admin console to delete clusters if you can see them

#
#  'Commands for the AdminConfig object using wsadmin scripting: convertToCluster'
#   http://publib.boulder.ibm.com/infocenter/wasinfo/fep/topic/com.ibm.websphere.nd.multiplatform.doc/info/ae/ae/rxml_adminconfig1.html#rxml_adminconfig1__cmd3

#wsadmin.bat -lang jython -f c:\foo\ServerCluster.py ausydhq-lt0197Node01 pyapya burmese_cluster


import sys
import java
import AdminConfig

#--------------------------------------------------------------------
# Create cluster & add server to it
#--------------------------------------------------------------------
def convertServerToCluster(nodeName, serverName, clusterName):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create cluster & add server to it"
        print " nodeName:                       "+nodeName
        print " serverName:                     "+serverName
        print " clusterName:                    "+clusterName
        msg = " Executing: ServerCluster.convertServerToCluster(\""+nodeName+"\", \""+serverName+"\", \""+clusterName+"\")"
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
        if (len(clusterName) == 0):
            print usage
            sys.exit(1)

        # checking if the parameter value exists
        nodeId = AdminConfig.getid("/Node:"+nodeName+"/")
        if (len(nodeId) == 0):
            print "\nThe specified node: " + nodeName + " does not exist."
            sys.exit(1)

        #server to put in cluster must exist
        serverId = AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
        if (len(serverId) == 0):
            print "\nThe specified server: " + serverName + " does not exist."
            sys.exit(1)

        #cluster with name must NOT exist
        newClusterExist = AdminConfig.getid("/ServerCluster:"+clusterName+"/")
        if (len(newClusterExist) != 0):
            print "\nThe specified cluster: " + clusterName + " exists ALREADY."
            sys.exit(1)

    except:
        print "\n\nException in convertServerToCluster() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        print AdminConfig.convertToCluster(serverId, clusterName)
    except:
        print "\n\nException in convertServerToCluster() when executing underlying wsadmin command AdminConfig.convertToCluster(serverId, clusterName)"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "\n\nException in convertServerToCluster() when saving to master configuration"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of convertServerToCluster()"


#--------------------------------------------------------------------
# Add a server to existing cluster
#--------------------------------------------------------------------
def addAnotherServerToCluster(nodeName, serverName, clusterName):
    try:
        print "\n\n"        
        print "---------------------------------------------------------------"
        print " Add a server to existing cluster"
        print " nodeName:                       "+nodeName
        print " serverName:                     "+serverName
        print " clusterName:                    "+clusterName
        msg = " Executing: ServerCluster.addAnotherServerToCluster(\""+nodeName+"\", \""+serverName+"\", \""+clusterName+"\")"
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
        if (len(clusterName) == 0):
            print usage
            sys.exit(1)

        # checking if the parameter value exists
        nodeId = AdminConfig.getid("/Node:"+nodeName+"/")
        if (len(nodeId) == 0):
            print "\nThe specified node: " + nodeName + " does not exist."
            sys.exit(1)

        #server to put in cluster must NOT exist
        serverId = AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
        if (len(serverId) != 0):
            print "\nThe specified server: " + serverName + " exists ALREADY."
            sys.exit(1)

        #cluster with name must exist
        clusterId = AdminConfig.getid("/ServerCluster:"+clusterName+"/")
        if (len(clusterId) == 0):
            print "\nThe specified cluster: " + clusterName + " does not exist."
            sys.exit(1)

    except:
        print "\n\nException in addAnotherServerToCluster() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.createClusterMember(clusterId, nodeId, [['memberName', serverName]])
    except:
        print "\n\nException in addAnotherServerToCluster() when executing underlying wsadmin AdminConfig command"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "\n\nException in addAnotherServerToCluster() when saving to master configuration"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of addAnotherServerToCluster()"


#--------------------------------------------------------------------
# main
#--------------------------------------------------------------------
#when this module is being run as top-level, call the function
if __name__=="__main__":
  usage = " "
  usage = usage + " "
  usage = usage + "Usage: <wsadmin command> -p <target wsadmin.properties file> -f <this py script> <nodeName, serverName, clusterName>\n"
  usage = usage + " . . . and must have modified soap.client.props of target wsadmin profile if security is enabled\n"

  if len(sys.argv) == 3:
      nodeName=sys.argv[0]
      print "nodeName :" + nodeName
  
      serverName=sys.argv[1]
      print "serverName: " + serverName
    
      clusterName=sys.argv[2]
      print "clusterName: " + clusterName

      convertServerToCluster(nodeName, serverName, clusterName)
  else:
    print "wrong number of args"
    print usage
    sys.exit(1)

