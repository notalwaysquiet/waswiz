###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following procedures:
#       disableAio
#       enableAio
#
# see http://www-01.ibm.com/support/docview.wss?rs=180&context=SSEQTP&q1=disabling+AIO&uid=swg21366862&loc=en_US&cs=utf-8&lang=en
# "Disabling AIO (Asynchronous Input/Output) native transport in WebSphere Application Server"
#
# windows commands
# wsadmin.bat -lang jython -f c:\qdr\ETP_dev/config_scripts/TransportChannelService.py getCommClassSetting AUSYDHQ-WS0958Node02 t1_cheetah_server2
# wsadmin.bat -lang jython -f c:\qdr\ETP_dev/config_scripts/TransportChannelService.py disableAio AUSYDHQ-WS0958Node02 t1_cheetah_server2
# wsadmin.bat -lang jython -f c:\qdr\ETP_dev/config_scripts/TransportChannelService.py enableAio AUSYDHQ-WS0958Node02 t1_cheetah_server2

# aix commands for Dev1 
# ./wsadmin.sh -lang jython -f /etp/wasadmin/was_configurator/ETP_dev/config_scripts/TransportChannelService.py getCommClassSetting servers2HappyNode t1_cheetah_server2
# ./wsadmin.sh -lang jython -f /etp/wasadmin/was_configurator/ETP_dev/config_scripts/TransportChannelService.py disableAio servers2HappyNode t1_cheetah_server2
# ./wsadmin.sh -lang jython -f /etp/wasadmin/was_configurator/ETP_dev/config_scripts/TransportChannelService.py enableAio servers2HappyNode t1_cheetah_server2


import AdminConfig

# Utilities - needed for convertToList()
import Utilities

# find out if server has already had async I/O libraries disabled
def getServerID(nodeName, serverName):
    try:
        # checking required parameters
        if (len(serverName) == 0):
            print usage
            sys.exit(1)

        # checking if the parameter value exists
        path='/Node:'+nodeName+'/'
        nodeId= AdminConfig.getid(path)
        if (len(nodeId) == 0):
            print "\n\nThe specified node at: " + nodeName + " does not exist.\n\n"
            sys.exit(1)

        # checking if the parameter value exists
        path='/Node:'+nodeName+'/Server:'+serverName+'/'
        serverID= AdminConfig.getid(path)
        if (len(serverID) == 0):
            print "\n\nThe specified server at: " + serverName + " does not exist.\n\n"
            sys.exit(1)
        return serverID
    except:
        print "\n\nException in getServerID() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

def commClassIsSet(serverID):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Check which I/O libraries server is set to use -- async (IBM) or sync (Sun)"
        print " nodeName:                                "+nodeName        
        print " serverName:                              "+serverName
        msg = " Executing: TransportChannelService.commClassIsSet(\""+nodeName+"\", \""+serverName+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "

        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg
        
        # checking required parameters
        if (len(serverName) == 0):
            print usage
            sys.exit(1)

        # checking if the parameter value exists
        path='/Node:'+nodeName+'/'
        nodeId= AdminConfig.getid(path)
        if (len(nodeId) == 0):
            print "\n\nThe specified node at: " + nodeName + " does not exist.\n\n"
            sys.exit(1)

        # checking if the parameter value exists
        path='/Node:'+nodeName+'/Server:'+serverName+'/'
        serverID= AdminConfig.getid(path)
        if (len(serverID) == 0):
            print "\n\nThe specified server at: " + serverName + " does not exist.\n\n"
            sys.exit(1)
    except:
        print "\n\nException in commClassIsSet() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        #transportChannelService doesn't show in admin console - it includes all channels - e.g., tcp, http, ssl, web container
        transportChannelServiceID = AdminConfig.list('TransportChannelService', serverID)
        print "transportChannelServiceID: " + transportChannelServiceID
        tcpFactoryID = AdminConfig.list('TCPFactory', transportChannelServiceID)
        
        if tcpFactoryID == "":
            print "\nDefault server I/O setting."
            print "Server: " + serverName + " on node: " + nodeName + " is set to use 'aio' libraries (IBM async I/O)"
            return "false"
        else:
            print "tcpFactoryID: " + tcpFactoryID
            print "TCP properties for all transport chains:"
            propertyList = AUtilities.convertToList(AdminConfig.showAttribute(tcpFactoryID, 'properties'))
            for property in propertyList:
                print AdminConfig.showAttribute(property, 'name')
                print AdminConfig.showAttribute(property, 'value')
                print

            print "Non-default server I/O setting. Dodgy aio libraries disabled."
            print "Server: " + serverName + " on node: " + nodeName + " is set to use 'nio' libraries (new Sun sync I/O)"
            return "true"
    except:
        print "\n\nException in commClassIsSet()  \n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)


# disable AIO libraries
def disableAio(nodeName, serverName):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Disable the IBM async I/O libraries for one server"
        print " nodeName:                                "+nodeName        
        print " serverName:                              "+serverName
        msg = " Executing: TransportChannelService.disableAio(\""+nodeName+"\", \""+serverName+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "

        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg
        
        # checking required parameters
        if (len(serverName) == 0):
            print usage
            sys.exit(1)

        # checking if the parameter value exists
        path='/Node:'+nodeName+'/'
        nodeId= AdminConfig.getid(path)
        if (len(nodeId) == 0):
            print "\n\nThe specified node at: " + nodeName + " does not exist.\n\n"
            sys.exit(1)

        # checking if the parameter value exists
        path='/Node:'+nodeName+'/Server:'+serverName+'/'
        serverID= AdminConfig.getid(path)
        if (len(serverID) == 0):
            print "\n\nThe specified server at: " + serverName + " does not exist.\n\n"
            sys.exit(1)
    except:
        print "\n\nException in disableAio() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        if commClassIsSet(serverID) == "true":
            print "\n\nAIO libraries already disabled for server: " + serverName + " on node: " + nodeName
            print "No action taken."
            return
        else:
            #transportChannelService doesn't show in admin console - it includes all channels - e.g., tcp, http, ssl, web container
            transportChannelServiceID = AdminConfig.list('TransportChannelService', serverID)
            #print transportChannelServiceID
            tcpFactoryID = AdminConfig.create('TCPFactory', transportChannelServiceID, [])
            #print tcpFactoryID
            property = AdminConfig.create('Property', tcpFactoryID, [['name', 'commClass'], ['value', 'com.ibm.ws.tcp.channel.impl.NioTCPChannel']])
            print property
            print AdminConfig.showAttribute(transportChannelServiceID, 'factories')
            print "\nFinished disabling aio libraries for server: " + serverName + " on node: " + nodeName
            commClassIsSet(serverID)
    except:
        print "\n\nException in disableAio() when creating the property \n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "\n\nException in disableAio() when saving to master config \n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
        

# enable AIO libraries (WAS default)
def enableAio(nodeName, serverName):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Enable the IBM async I/O libraries for one server (WAS default)"
        print " nodeName:                                "+nodeName        
        print " serverName:                              "+serverName
        msg = " Executing: TransportChannelService.enableAio(\""+nodeName+"\", \""+serverName+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "

        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg
        
        # checking required parameters
        if (len(serverName) == 0):
            print usage
            sys.exit(1)

        # checking if the parameter value exists
        path='/Node:'+nodeName+'/'
        nodeId= AdminConfig.getid(path)
        if (len(nodeId) == 0):
            print "\n\nThe specified node at: " + nodeName + " does not exist.\n\n"
            sys.exit(1)

        # checking if the parameter value exists
        path='/Node:'+nodeName+'/Server:'+serverName+'/'
        serverID= AdminConfig.getid(path)
        if (len(serverID) == 0):
            print "\n\nThe specified server at: " + serverName + " does not exist.\n\n"
            sys.exit(1)
    except:
        print "\n\nException in enableAio() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        if commClassIsSet(serverID) == "true":
            #transportChannelService doesn't show in admin console - it includes all channels - e.g., tcp, http, ssl, web container
            transportChannelServiceID = AdminConfig.list('TransportChannelService', serverID)
            #print transportChannelServiceID-
            tcpFactoryID = AdminConfig.list('TCPFactory', transportChannelServiceID)
            #print tcpFactoryID
            print AdminConfig.remove(tcpFactoryID)
            print AdminConfig.showAttribute(transportChannelServiceID, 'factories')
            print "\nFinished enabling aio libraries for server: " + serverName + " on node: " + nodeName
            commClassIsSet(serverID)
        else:
            print "\n\nAIO libraries already enabled for server: " + serverName + " on node: " + nodeName
            print "No action taken."
            return
    except:
        print "\n\nException in enableAio() when removing the property \n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "\n\nException in enableAio() when saving to master config \n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)        
        

        
        
        
#--------------------------------------------------------------------
# main
#--------------------------------------------------------------------
#when this module is being run as top-level, call the requested function
if __name__=="__main__":
    usage = " "
    usage = usage + " "
    usage = usage + "Usage: <wsadmin command> -f <this py script> <action> <node name> <server name> "
    usage = usage + " . . . where <action> is one of:\n"
    usage = usage + " . . .   * disableAio - this tells the server to use the synchronous I/O libraries built into Java instead of the IBM async libraries \n"
    usage = usage + " . . .   * enableAio - (WAS v7 default) this tells the server to use the IBM async I/O libraries instead of the synchronous I/O libraries built into Java\n"
    usage = usage + " . . .   * getCommClassSetting  - check whether server is using 'new' I/O built into Java or IBM async I/O libraries \n"
    usage = usage + " . . . and must have modified soap.client.props of target wsadmin profile if security is enabled\n"
    print "\n\n"
    #print '\n\nlen(sys.argv) is ' 
    #print len(sys.argv)
    if len(sys.argv) == 3:

        action=sys.argv[0]
        print "action: " + action

        nodeName=sys.argv[1]
        print "nodeName: " + nodeName

        serverName=sys.argv[2]
        print "serverName: " + serverName

    else:
        print ""
        print "wrong number of args"
        print ""
        print usage
        sys.exit(1)

    if action == "disableAio":
        disableAio(nodeName, serverName)
    elif action == "enableAio":
        enableAio(nodeName, serverName)
    elif action == "getCommClassSetting":
        serverID = getServerID(nodeName, serverName)
        print "serverID: " + serverID
        commClassIsSet(serverID)
        
    else:
        print "Action: " + action + " not recognized. Exiting."
        sys.exit(1)        
