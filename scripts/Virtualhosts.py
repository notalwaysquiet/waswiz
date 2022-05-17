###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following procedures:
#   createVirtualHost
#   setVirtualHostEntry
#   setServerDefaultVirtualHost
###############################################################################
# Notes
# This file doesn't care how many ports there are -- 
#   see Configurator.py to adjust which ports get put into virtual host.
#   see also ServerPorts.py

# this script does not use script "library" as didn't see any helpful method in scripts library

#caution: doesn't check if the alias name/port is already there or not, just adds them

#wsadmin.bat -lang jython -f c:/foo/qdr/Virtualhosts.py pyapya

#--------------------------------------------------------------------
# Set global constants
#--------------------------------------------------------------------
import sys
import java

# wsadmin objects
import AdminConfig

# modules that are searched for in the same directory as this script
import ItemExists
import Utilities

#--------------------------------------------------------------------
# Create virtual host 
#--------------------------------------------------------------------
def createVirtualHost(virtualhostName):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create virtual host"
        print " virtualhostName:              "+virtualhostName
        msg = " Executing: Virtualhosts.createVirtualHost(\""+virtualhostName+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(virtualhostName) == 0):
           print usage
           sys.exit(1)

        # checking if the parameter value exists already
        virtualhostId = AdminConfig.getid('/VirtualHost:'+virtualhostName+'/')
        if virtualhostId != '':
            print "\n\nThe specified virtualhostName: " + virtualhostName + " ALREADY exists.\n\n"
            print '    virtualhostId is ' + virtualhostId       
            sys.exit(1)
    except:
        print "\n\nException in createVirtualHost() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:    
        #assumes there is only 1 cell which is usually true
        cellId = AdminConfig.list('Cell')
        print ''
        #print 'cellId is ' + cellId
        #print 'virtualhostName is ' + virtualhostName
        #print 'virtualhostId before create is ' + virtualhostId
        virtualhostId = AdminConfig.create('VirtualHost', cellId, [['name', virtualhostName]])
        print 'created virtual host - \n virtualhostId is ' + virtualhostId

    except:
        print "\n\nException in createVirtualHost() when creating virtual host entry"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "\n\nException in createVirtualHost() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
        print "end of createVirtualHost()\n\n"


#--------------------------------------------------------------------
# Add additional entry to an existing virtual host for additional hostname/port pairs
#--------------------------------------------------------------------
def setVirtualHostEntry(virtualhostName, hostname, port):
    try:
        port=str(port)
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create hostname/pair entry for existing virtual host"
        print " virtualhostName:              "+virtualhostName
        print " hostname:                     "+hostname
        print " port:                         "+str(port)
        msg = " Executing: Virtualhosts.setVirtualHostEntry(\""+virtualhostName+"\", \""+hostname+"\", \""+str(port)+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(virtualhostName) == 0):
            print usage
            sys.exit(1)
        if (len(hostname) == 0):
            print usage
            sys.exit(1)
        if (len(port) == 0):
            print usage
            sys.exit(1)

        # checking if the parameter value exists already
        virtualhostId = AdminConfig.getid('/VirtualHost:'+virtualhostName+'/')
        if virtualhostId == '':
            print "\n\nThe specified virtualhostName: " + virtualhostName + " does not exist."
            sys.exit(1)
        try:
            # checking port is an int
            port=int(port)
        except:
            print "\n\nPort must be an integer."
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            sys.exit(1)
        try:
            virtualHostEntryId = ItemExists.virtualHostEntryExists(virtualhostName, hostname, port)
            #print "\n\nchecking if virtualHostEntry already exists -- virtualHostEntryId returned by ItemExists: " + virtualHostEntryId
            #print ""
            if virtualHostEntryId != "":
                print "\n\nThe specified virtualhostName, hostname, port already exists: " + virtualhostName + ", " + hostname + ", " + str(port)
                return
        except:
            print "\n\nException when checking if virtual host entry already exists."
            sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            sys.exit(1)
    except:
        print "\n\nException in setVirtualHostEntry() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        hostnamePair = ['hostname', hostname]
        portPair = ['port', port]
        hostPortPair = [hostnamePair, portPair]
        aliasList = [hostPortPair]
        virtualhostAliasesProperty = [['aliases', aliasList]]
    except:
        print "\n\nException in setVirtualHostEntry() when packaging aliases list" 
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        print AdminConfig.modify(virtualhostId, virtualhostAliasesProperty)
        AdminConfig.save()
        print "Created virtual host entry for: " + virtualhostName + ", " + hostname + ", " + str(port)
        #print ItemExists.virtualHostEntryExists(virtualhostName, hostname, port)
    except:
        print "\n\nException in setVirtualHostEntry() when adding alias entry to virtualhost" 
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "\n\nException in setVirtualHostEntry() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setVirtualHostEntry()"


#--------------------------------------------------------------------
# Set default virtual host for the specified server (this feature didn't work in WAS 6.1, not sure about WAS 7)
#--------------------------------------------------------------------
def setServerDefaultVirtualHost(nodeName, serverName, virtualhostName):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Set default virtual host for the specified server"
        print " nodeName:                           "+nodeName
        print " serverName:                         "+serverName
        print " virtualhostName:                    "+virtualhostName
        msg = " Executing: Virtualhosts.setServerDefaultVirtualHost(\""+nodeName+"\", \""+serverName+"\", \""+virtualhostName+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully.\n"
        usage = usage + msg

        # checking required parameters
        if (len(nodeName) == 0):
            print usage
            sys.exit(1)
        if (len(virtualhostName) == 0):
            print usage
            sys.exit(1)
        if (len(serverName) == 0):
            print usage
            sys.exit(1)

        # checking if the parameter value exists already
        nodeId = AdminConfig.getid('/Node:'+nodeName+'/')
        if nodeId  == '':
            print "\n\nThe specified nodeName: " + nodeName + " does not exist."
            sys.exit(1)
        serverId = AdminConfig.getid('/Node:'+nodeName+'/Server:'+serverName+'/')
        if serverId  == '':
            print "\n\nThe specified server: " + serverName + " does not exist."
            sys.exit(1)
        virtualhostId = AdminConfig.getid('/VirtualHost:'+virtualhostName+'/')
        if virtualhostId == '':
            print "\n\nThe specified virtualhostName: " + virtualhostName + " does not exist."
            sys.exit(1)
            
    except:
        print "\n\nException in setServerDefaultVirtualHost() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        serverComponentsListString = AdminConfig.showAttribute(serverId, '[[components]]')
        #print 'serverComponentsListString is: ' + serverComponentsListString
        
        serverComponentsList = Utilities.convertToList(serverComponentsListString)
        
        applicationServerComponentId = ''
        for component in serverComponentsList:
            if component.find('ApplicationServer') != -1:
                #print component
                applicationServerComponentId = component
                
        #print applicationServerComponentId 
    except:
        print "\n\nException in setServerDefaultVirtualHost() when getting app server component for server" 
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        appServerComponentsListString = AdminConfig.showAttribute(applicationServerComponentId, '[[components]]')
        #print "appServerComponentsListString: " + appServerComponentsListString

        appServerComponentsList = Utilities.convertToList(appServerComponentsListString)
        #print "appServerComponentsList: "
        #print appServerComponentsList

        for component in appServerComponentsList:
            if component.find('WebContainer') != -1:
                webContainerComponentId = component
    
        #print webContainerComponentId
    except:
        print "\n\nException in setServerDefaultVirtualHost() when getting web container component for server" 
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.modify(webContainerComponentId, [['defaultVirtualHostName', virtualhostName]])
        print "Modified web container id: " + webContainerComponentId
    except:
        print "\n\nException in setServerDefaultVirtualHost() when setting virtual host for server's web container" 
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        AdminConfig.save()
    except:
        print "\n\nException in setServerDefaultVirtualHost() when saving to master config"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setServerDefaultVirtualHost()"



#--------------------------------------------------------------------
# main
#--------------------------------------------------------------------
#when this module is being run as top-level, call the function
if __name__=="__main__":
  usage = " "
  usage = usage + " "
  usage = usage + "Usage: <wsadmin command> -p <target wsadmin.properties file> -f <this py script> <virtualhostName>\n"
  usage = usage + " . . . and must have modified soap.client.props of target wsadmin profile if security is enabled\n"
  print ""
  if len(sys.argv) == 1:
      virtualhostName=sys.argv[0]
      print "virtualhostName :" + virtualhostName
  
      createVirtualHost(virtualhostName)
      print ""
  else:
    print "wrong number of args"
    print usage
    sys.exit(1)



  


