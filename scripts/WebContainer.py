###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following procedures:
#   setServerDefaultVirtualHost
#   setWebContainerProperties
#   setWebContainerThreadPoolProperties
#   setTcpTransportChannelProperties
#   createOneTcpTransportChannelCustomProperty
#   modifyOneTcpTransportChannelCustomProperty
#   setHttpTransportChannelProperties
#   modifyHttpQueueTuningParams
#   displayServerComponentAttribute
#   displayHttpQueueTuningParamsByPortName
#   displayHttpQueueTuningParamsByPortNameByServerName
#   displayHttpQueueTuningParams
#   displayNonDefaultServerComponentAttribute
#   displayNonDefaultHttpQueueTuningParamsByPortName
#   displayNonDefaultHttpQueueTuningParamsByPortNameByServerName
#   displayNonDefaultHttpQueueTuningParams
#   setSessionManagementDefaultCookieSettings
#   setSessionCookieSettings
###############################################################################
# Notes

# windows commands - displayHttpQueueTuningParams
# wsadmin.bat -lang jython -f c:\qdr\ETP_dev/config_scripts/WebContainer.py displayHttpQueueTuningParams AUSYDHQ-WS0958Node02 t1_cheetah_server2

# aix commands for Dev1 - displayHttpQueueTuningParams
# ./wsadmin.sh -lang jython -f /etp/wasadmin/was_configurator/ETP_dev/config_scripts/WebContainer.py displayHttpQueueTuningParams servers2HappyNode t1_cheetah_server2
# aix commands for Dev0 - displayHttpQueueTuningParams
# ./wsadmin.sh -lang jython -f /etp/wasadmin/was_configurator/ETP_dev/config_scripts/WebContainer.py displayHttpQueueTuningParams servers2LazNode dev0_t1_cheetah_server2

# aix commands for Prod PPSR servers - displayHttpQueueTuningParams
# bilby
# ./wsadmin.sh -lang jython -f /etp/wasadmin/was_configurator/ETP_prod/config_scripts/WebContainer.py displayHttpQueueTuningParams servers2SnowwhiteNode t0_bilby_server1

# aix commands for Prod PPSR servers - displayHttpQueueTuningParams
# bilby
# ./wsadmin.sh -lang jython -f /etp/wasadmin/was_configurator/ETP_prod/config_scripts/WebContainer.py /etp/wasadmin/was_configurator/ETP_prod/ displayHttpQueueTuningParams servers2SnowwhiteNode t0_bilby_server1

# numbat
# ./wsadmin.sh -lang jython -f /etp/wasadmin/was_configurator/ETP_prod/config_scripts/WebContainer.py /etp/wasadmin/was_configurator/ETP_prod/ displayHttpQueueTuningParams servers2SnowwhiteNode t0_numbat_server1

# wallaby
# ./wsadmin.sh -lang jython -f /etp/wasadmin/was_configurator/ETP_prod/config_scripts/WebContainer.py /etp/wasadmin/was_configurator/ETP_prod/ displayHttpQueueTuningParams servers2SnowwhiteNode t0_wallaby_server1

# cougar
# ./wsadmin.sh -lang jython -f /etp/wasadmin/was_configurator/ETP_prod/config_scripts/WebContainer.py /etp/wasadmin/was_configurator/ETP_prod/ displayHttpQueueTuningParams servers2SnowwhiteNode t1_cougar_server1

import sys
import AdminConfig

import ServerComponent
import Utilities


#--------------------------------------------------------------------
# This is just a cross-reference to where the function is defined
# The setting in admin console is at: Application servers > tier1_be_server1 > Web container
# but I placed the function body in VirtualHosts.py because that is where I would probably look for it
#--------------------------------------------------------------------
def setServerDefaultVirtualHost(nodeName, serverName, virtualhostName):
    import Virtualhosts
    try:
        Virtualhosts.setServerDefaultVirtualHost(nodeName, serverName, virtualhostName)

    except:
        print "\n\nException in WebContainer.setServerDefaultVirtualHost() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])



#--------------------------------------------------------------------
# Set properties for a server's web container, e.g., servlet caching
# see config file for list of frequently used properties
# should support any other attributes of type 'WebContainer' not listed there, just add them on
#Using Jython string format for the arguments, as all the nested[ drive me mental otherwise
#'[[name1 val1] [name2 val2] [name3 val3]]'
# Calls a generic method in ServerComponent.py
#--------------------------------------------------------------------
def setWebContainerProperties(nodeName, serverName, propertyListString):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Set properties for a server's web container"
        print " nodeName:             "+nodeName
        print " serverName:           "+serverName
        print " propertyList:         "+str(propertyListString)
        msg = " Executing: WebContainer.setWebContainerProperties(\""+nodeName+"\", \""+serverName+"\", \""+str(propertyListString)+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        componentType = 'WebContainer'
        print " . . . calling generic method . . . ServerComponent.setProperties(nodeName, serverName, componentType, propertyListString)"
        ServerComponent.setProperties(nodeName, serverName, componentType, propertyListString)
    except:
        print "Exception in setWebContainerProperties()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setWebContainerProperties()"


#--------------------------------------------------------------------
# Set properties for a server's web container thread pool
# see config file for list of frequently used properties
# should support any other attributes of type 'ThreadPool' not listed there, just add them on
#Using Jython string format for the arguments, as all the nested[ drive me mental otherwise
#'[[name1 val1] [name2 val2] [name3 val3]]'
# Calls a generic method in ServerComponent.py
#--------------------------------------------------------------------
def setWebContainerThreadPoolProperties(nodeName, serverName, propertyListString):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Set properties for a web container's thread pool"
        print " nodeName:             "+nodeName
        print " serverName:           "+serverName
        print " propertyList:         "+str(propertyListString)
        msg = " Executing: WebContainer.setWebContainerThreadPoolProperties(\""+nodeName+"\", \""+serverName+"\", \""+str(propertyListString)+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        componentType = 'ThreadPool'
        componentName = 'WebContainer'
        nameName = 'name'
        print " . . . calling generic method . . . "
        ServerComponent.setPropertiesByComponentName(nodeName, serverName, componentType, componentName, nameName, propertyListString)

    except:
        print "Exception in setWebContainerThreadPoolProperties() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setWebContainerThreadPoolProperties()"


#--------------------------------------------------------------------
# Set non-custom properties for a server's transport channel by channel name
# should support any other attributes of type 'TCPInboundChannel', just add them on
# get list of allowable properties for a type, e.g., 'WebContainer' by AdminConfig.attributes('WebContainer')
#Using Jython string format for the arguments, as all the nested[ drive me mental otherwise
#'[[name1 val1] [name2 val2] [name3 val3]]'
# Calls a generic method in ServerComponent.py
# Underlying file is server.xml
#--------------------------------------------------------------------
def setTcpTransportChannelProperties(nodeName, serverName, channelName, propertyListString):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Set properties for TCP transport channel for port WC_defaulthost"
        print " nodeName:             "+nodeName
        print " serverName:           "+serverName
        print " channelName:          "+channelName
        print " propertyList:         "+str(propertyListString)
        msg = " Executing: WebContainer.setTcpTransportChannelProperties(\""+nodeName+"\", \""+serverName+"\", \""+channelName+"\", \""+str(propertyListString)+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        componentType = 'TCPInboundChannel'
        #componentName = 'TCP_2'
        componentName = channelName
        nameName = 'name'
        print " . . . calling generic method . . . "
        ServerComponent.setPropertiesByComponentName(nodeName, serverName, componentType, componentName, nameName, propertyListString)

    except:
        print "Exception in setTcpTransportChannelProperties() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setTcpTransportChannelProperties()"


#--------------------------------------------------------------------
# If it doesn't already exist, set one custom property for a server's transport channel by channel name
# should support any custom property attribute of type 'TCPInboundChannel'
# compare to Configurator.setWebContainerCustomProperties()
# Underlying file is server.xml
#--------------------------------------------------------------------
def createOneTcpTransportChannelCustomProperty(nodeName, serverName, channelName, propertyName, propertyValue, propertyIsRequired):
    try:
        import ItemExists
        
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Create a custom property for TCP transport channel for port WC_defaulthost"
        print " nodeName:             "+nodeName
        print " serverName:           "+serverName
        print " channelName:          "+channelName
        print " propertyName:         "+str(propertyName)
        print " propertyValue:        "+str(propertyValue)
        print " propertyIsRequired:   "+str(propertyIsRequired)
        msg = " Executing: WebContainer.createOneTcpTransportChannelCustomProperty(\""+nodeName+"\", \""+serverName+"\", \""+channelName+"\", \""+str(propertyName)+"\", \""+str(propertyValue)+"\", \""+str(propertyIsRequired)+"\")"
        print msg
        print "---------------------------------------------------------------"
        if nodeName != "" and serverName != "" and propertyName != "" and propertyValue != "" and propertyIsRequired != "":
            if ItemExists.tcpTransportChannelCustomPropExists(nodeName, serverName, channelName, propertyName):
                print "\n   . . . skipping a step:"                
                print "   TCP transport channel custom prop already exists: " + str(propertyName) + " for server: " + serverName
            else:
                #Using Jython string format for the arguments, as all the nested[ drive me mental otherwise
                #'[[name1 val1] [name2 val2] [name3 val3]]'
                # this is a wierd situation: 1 property which happens to be named "properties" & is nested, and of type collection, i.e., it has an extra set of [  around it
                propertyListString = '[[ properties [[[name "' + propertyName + '"] [value "' + str(propertyValue) + '"] [required "' + propertyIsRequired + '"]]]]]'
                #print "\n propertyListString: " + propertyListString
                #print ""
                print " . . . calling method for TCP channel non-custom props . . . "
                setTcpTransportChannelProperties(nodeName, serverName, channelName, propertyListString)
        else:
            print "\n\n One or more required parameters is empty string. Returning."
            return

    except:
        print "Exception in createOneTcpTransportChannelCustomProperty() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of createOneTcpTransportChannelCustomProperty()"


#--------------------------------------------------------------------
# If it already exists, modify one custom property for a server's transport channel by channel name
# should support any custom property attribute of type 'TCPInboundChannel'
# to get list  list of allowable properties for a type, e.g., 'TCPInboundChannel' by AdminConfig.attributes('TCPInboundChannel')
# compare to Configurator.setWebContainerCustomProperties()
# Underlying file is server.xml
#--------------------------------------------------------------------
def modifyOneTcpTransportChannelCustomProperty(nodeName, serverName, channelName, propertyName, propertyValue, propertyIsRequired):
    try:
        import ItemExists
        
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Modify a custom property for TCP transport channel for port WC_defaulthost"
        print " nodeName:             "+nodeName
        print " serverName:           "+serverName
        print " channelName:          "+channelName
        print " propertyName:         "+str(propertyName)
        print " propertyValue:        "+str(propertyValue)
        print " propertyIsRequired:   "+str(propertyIsRequired)
        msg = " Executing: WebContainer.modifyOneTcpTransportChannelCustomProperty(\""+nodeName+"\", \""+serverName+"\", \""+channelName+"\", \""+str(propertyName)+"\", \""+str(propertyValue)+"\", \""+str(propertyIsRequired)+"\")"
        print msg
        print "---------------------------------------------------------------"
        if nodeName != "" and serverName != "" and propertyName != "" and propertyValue != "" and propertyIsRequired != "":
            propertyId = ItemExists.tcpTransportChannelCustomPropExists(nodeName, serverName, channelName, propertyName)
            if propertyId != "":
                #Using Jython string format for the arguments, as all the nested[ drive me mental otherwise
                #'[[name1 val1] [name2 val2] [name3 val3]]'
                propertyListString = '[[name "' + propertyName + '"] [value "' + str(propertyValue) + '"] [required "' + propertyIsRequired + '"]]'
                #print "\n propertyListString: " + propertyListString
                #print ""
                print AdminConfig.modify(propertyId, propertyListString)               
            else:
                print "\n\n\n Could not find custom property to modify for channel: " + channelName + ". Returning."
                return
        else:
            print "\n\n\n One or more required parameters is empty string. Returning."
            return

    except:
        print "Exception in modifyOneTcpTransportChannelCustomProperty() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of modifyOneTcpTransportChannelCustomProperty()"


#--------------------------------------------------------------------
# Set properties for a server's transport channel by channel type & channel name
# should support any other attributes of type 'HTTPInboundChannel', just include them in list 
# get list of allowable properties for a type, e.g., 'WebContainer' by AdminConfig.attributes('WebContainer')
#Using Jython string format for the arguments, as all the nested[ drive me mental otherwise
#'[[name1 val1] [name2 val2] [name3 val3]]'
# Calls a generic method in ServerComponent.py
# Underlying file is server.xml
#--------------------------------------------------------------------
def setHttpTransportChannelProperties(nodeName, serverName, channelName, propertyListString):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Set properties for TCP transport channel for port WC_defaulthost"
        print " nodeName:             "+nodeName
        print " serverName:           "+serverName
        print " channelName:          "+channelName
        print " propertyList:         "+str(propertyListString)
        msg = " Executing: WebContainer.setHttpTransportChannelProperties(\""+nodeName+"\", \""+serverName+"\", \""+channelName+"\", \""+str(propertyListString)+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        componentType = 'HTTPInboundChannel'
        #componentName = 'HTTP_2'
        componentName = channelName
        nameName = 'name'
        print " . . . calling generic method . . . "
        ServerComponent.setPropertiesByComponentName(nodeName, serverName, componentType, componentName, nameName, propertyListString)

    except:
        print "Exception in setHttpTransportChannelProperties() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setHttpTransportChannelProperties()"


#--------------------------------------------------------------------
# Set properties relating to HTTP queue tuning for a server
# method provided for convenience - in turn calls other methods (in this same module file)
#    to do the individual transport channels, which in turn call a very generic method in ServerComponent.py
# Underlying file is server.xml
#--------------------------------------------------------------------
def modifyHttpQueueTuningParams(nodeName, serverName, portName, tcpMaxOpenConnections, tcpInactivityTimeout, tcpListenBacklog, httpKeepAlive, httpMaximumPersistentRequests, httpPersistentTimeout, httpReadTimeout, httpWriteTimeout):
    try:
        import ItemExists
        
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Set properties for HTTP queue tuning for a port"
        print " nodeName:                      "+nodeName
        print " serverName:                    "+serverName
        print " portName:                      "+portName
        print " tcpMaxOpenConnections:         "+str(tcpMaxOpenConnections)
        print " tcpInactivityTimeout:          "+str(tcpInactivityTimeout)
        print " tcpListenBacklog:              "+str(tcpListenBacklog)
        print " httpKeepAlive:                 "+httpKeepAlive
        print " httpMaximumPersistentRequests: "+str(httpMaximumPersistentRequests)
        print " httpPersistentTimeout:         "+str(httpPersistentTimeout)
        print " httpReadTimeout:               "+str(httpReadTimeout)
        print " httpWriteTimeout:              "+str(httpWriteTimeout)
        msg = " Executing: WebContainer.modifyHttpQueueTuningParams(\""+nodeName+"\", \""+serverName+"\", \""+portName+"\", \""+str(tcpMaxOpenConnections)+"\", \""+str(tcpInactivityTimeout)+"\", \""+str(tcpListenBacklog)+"\", \""+str(httpKeepAlive)+"\", \""+str(httpMaximumPersistentRequests)+"\", \""+str(httpPersistentTimeout)+"\", \""+str(httpReadTimeout)+"\", \""+str(httpWriteTimeout)+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        channelName = "channelName not defined yet"
        
        if (str(tcpMaxOpenConnections) != "" or str(tcpInactivityTimeout) != ""):
            if portName == "WC_defaulthost":
                channelName = "TCP_2"
            elif portName == "WC_defaulthost_secure":
                channelName = "TCP_4"
            else:
                print "\n\n portName: " + portName + " not recognized in modifyHttpQueueTuningParams()"
                print "Exiting."
                sys.exit(1)      
            
            print "\n\n . . . modifying TCP transport channel non-custom properties for portName: " + portName + " . . . "
            propertyListString = ''
            if str(tcpMaxOpenConnections) != "":
                propertyListString += '[maxOpenConnections ' + str(tcpMaxOpenConnections) + ']'
            if str(tcpInactivityTimeout) != "":
                propertyListString += '[inactivityTimeout ' + str(tcpInactivityTimeout) + ']'
            propertyListString = '[' + propertyListString + ']'
            setTcpTransportChannelProperties(nodeName, serverName, channelName, propertyListString)  
            
        if (str(tcpListenBacklog) != ""):
            if portName == "WC_defaulthost":
                channelName = "TCP_2"
            elif portName == "WC_defaulthost_secure":
                channelName = "TCP_4"
            else:
                print "\n\n portName: " + portName + " not recognized in modifyHttpQueueTuningParams()"
                print "Exiting."
                sys.exit(1)      
        
            print "\n\n . . . modifying (or creating) TCP transport channel custom properties for portName: " + portName + " . . . "
            propertyName = "listenBacklog"
            propertyValue = tcpListenBacklog
            #all custom properties are optional (I think)
            propertyIsRequired = "false"
            if ItemExists.tcpTransportChannelCustomPropExists(nodeName, serverName, channelName, propertyName):            
                modifyOneTcpTransportChannelCustomProperty(nodeName, serverName, channelName, propertyName, str(propertyValue), propertyIsRequired)
            else:
                createOneTcpTransportChannelCustomProperty(nodeName, serverName, channelName, propertyName, str(propertyValue), propertyIsRequired)
            
        if (httpKeepAlive != "" or str(httpMaximumPersistentRequests) != "" or str(httpPersistentTimeout) != "" or str(httpReadTimeout) != "" or str(httpWriteTimeout) != "" ):
            if portName == "WC_defaulthost":
                channelName = "HTTP_2"
            elif portName == "WC_defaulthost_secure":
                channelName = "HTTP_4"
            else:
                print "\n\n portName: " + portName + " not recognized in modifyHttpQueueTuningParams()"
                print "Exiting."
                sys.exit(1)      

            print "\n\n . . . modifying HTTP transport channel (non-custom) properties for portName: " + portName + " . . . "
            propertyListString = ''
            if str(httpKeepAlive) != "":
                propertyListString += '[keepAlive ' + str(httpKeepAlive) + ']'
            if str(httpMaximumPersistentRequests) != "":
                propertyListString += '[maximumPersistentRequests ' + str(httpMaximumPersistentRequests) + ']'
            if str(httpPersistentTimeout) != "":
                propertyListString += '[persistentTimeout ' + str(httpPersistentTimeout) + ']'
            if str(httpReadTimeout) != "":
                propertyListString += '[readTimeout ' + str(httpReadTimeout) + ']'
            if str(httpWriteTimeout) != "":
                propertyListString += '[writeTimeout ' + str(httpWriteTimeout) + ']'
            propertyListString = '[' + propertyListString + ']'
            setHttpTransportChannelProperties(nodeName, serverName, channelName, propertyListString)  

    except:
        print "Exception in modifyHttpQueueTuningParams() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of modifyHttpQueueTuningParams()"

def displayServerComponentAttribute(serverId, componentType, componentName, attributeName):
    import HttpQueueTuningDefaults
    try:
        componentIdListString = AdminConfig.list(componentType, serverId)
        componentIdList = Utilities.convertToList(componentIdListString)
        for componentId in componentIdList:
            if (AdminConfig.showAttribute(componentId, 'name') == componentName):
                #print "componentId: " + componentId
                #print "componentName: " + componentName
                attributeValue = AdminConfig.showAttribute(componentId, attributeName)
                
                defaultValue = HttpQueueTuningDefaults.getAttribute(attributeName)
                if str(attributeValue) != str(defaultValue):
                    print
                    print "****************************************************************************************************"
                    print "  " + attributeName + ": " + str(attributeValue)
                    print "   Attribute has been changed from admin console default."
                    print "   Admin console default for: " + attributeName + " is: " + str(defaultValue)
                    print "****************************************************************************************************"
                    print
                else:
                    print "   " + attributeName + ": " + str(attributeValue)

    except:
        print "Exception in displayServerComponentAttribute() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        
def displayNonDefaultServerComponentAttribute(serverId, componentType, componentName, attributeName):
    import HttpQueueTuningDefaults
    try:
        componentIdListString = AdminConfig.list(componentType, serverId)
        componentIdList = Utilities.convertToList(componentIdListString)
        for componentId in componentIdList:
            if (AdminConfig.showAttribute(componentId, 'name') == componentName):
                #print "componentId: " + componentId
                #print "componentName: " + componentName
                attributeValue = AdminConfig.showAttribute(componentId, attributeName)
                
                defaultValue = HttpQueueTuningDefaults.getAttribute(attributeName)
                if str(attributeValue) != str(defaultValue):
                    print
                    print "****************************************************************************************************"
                    print "  " + attributeName + ": " + str(attributeValue)
                    print "   vs admin console default for: " + attributeName + " is: " + str(defaultValue)
                    print "****************************************************************************************************"
                    print

                

    except:
        print "Exception in displayNonDefaultServerComponentAttribute() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])        

def displayHttpQueueTuningParamsByPortNameByServerName(nodeName, serverName, portName):
    serverId = ItemExists.serverExists(nodeName, serverName)
    return displayHttpQueueTuningParamsByPortName(serverId, portName)

def displayHttpQueueTuningParamsByPortName(serverId, portName):
    try:
        import ItemExists
        if portName == "WC_defaulthost":
            tcpChannelName = "TCP_2"
            httpChannelName = "HTTP_2"
        elif portName == "WC_defaulthost_secure":
            tcpChannelName = "TCP_4"
            httpChannelName = "HTTP_4"
        else:
            print "\n\n portName: " + portName + " not recognized in modifyHttpQueueTuningParams()"
            print "Exiting."
            sys.exit(1)      
        componentType = 'TCPInboundChannel'
        componentName = tcpChannelName
        print "\n\n TCP transport channel non-custom properties for portName: " + portName + " . . . "

        attributeName = "maxOpenConnections"
        displayServerComponentAttribute(serverId, componentType, componentName, attributeName)
        
        attributeName = "inactivityTimeout"
        displayServerComponentAttribute(serverId, componentType, componentName, attributeName)
        
        print "\n\n TCP transport channel custom properties for portName: " + portName + " . . . "
        attributeName = "listenBacklog"
        nodeName = serverId[serverId.find("/nodes/")+7:serverId.find("/servers/")]
        serverName = serverId[serverId.find("/servers/")+9:serverId.find("|server.xml")]
        propertyId = ItemExists.tcpTransportChannelCustomPropExists(nodeName, serverName, componentName, attributeName)
        if propertyId != None:
            print attributeName + " : " + AdminConfig.showAttribute(propertyId, 'value')
        else:
            print "   No value set for custom property: " + attributeName + " for portName: " + portName
        
        componentType = 'HTTPInboundChannel'
        componentName = httpChannelName
        print "\n\n HTTP transport channel (non-custom) properties for portName: " + portName + " . . . "     
        attributeName = "keepAlive"
        displayServerComponentAttribute(serverId, componentType, componentName, attributeName)

        attributeName = "maximumPersistentRequests"
        displayServerComponentAttribute(serverId, componentType, componentName, attributeName)

        attributeName = "persistentTimeout"
        displayServerComponentAttribute(serverId, componentType, componentName, attributeName)
        
        attributeName = "readTimeout"
        displayServerComponentAttribute(serverId, componentType, componentName, attributeName)

        attributeName = "writeTimeout"
        displayServerComponentAttribute(serverId, componentType, componentName, attributeName)
        
    except:
        print "Exception in displayHttpQueueTuningParamsByPortName() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

def displayNonDefaultHttpQueueTuningParamsByPortNameByServerName(nodeName, serverName, portName):
    serverId = ItemExists.serverExists(nodeName, serverName)
    return displayHttpQueueTuningParamsByPortName(serverId, portName)

def displayNonDefaultHttpQueueTuningParamsByPortName(serverId, portName):
    try:
        import ItemExists
        if portName == "WC_defaulthost":
            tcpChannelName = "TCP_2"
            httpChannelName = "HTTP_2"
        elif portName == "WC_defaulthost_secure":
            tcpChannelName = "TCP_4"
            httpChannelName = "HTTP_4"
        else:
            print "\n\n portName: " + portName + " not recognized in modifyHttpQueueTuningParams()"
            print "Exiting."
            sys.exit(1)      
        componentType = 'TCPInboundChannel'
        componentName = tcpChannelName
        #print "\n\n TCP transport channel non-custom properties for portName: " + portName + " . . . "

        attributeName = "maxOpenConnections"
        displayNonDefaultServerComponentAttribute(serverId, componentType, componentName, attributeName)
        
        attributeName = "inactivityTimeout"
        displayNonDefaultServerComponentAttribute(serverId, componentType, componentName, attributeName)
        
        #print "\n\n TCP transport channel custom properties for portName: " + portName + " . . . "
        attributeName = "listenBacklog"
        nodeName = serverId[serverId.find("/nodes/")+7:serverId.find("/servers/")]
        serverName = serverId[serverId.find("/servers/")+9:serverId.find("|server.xml")]
        propertyId = ItemExists.tcpTransportChannelCustomPropExists(nodeName, serverName, componentName, attributeName)
        if propertyId != None:
            print "****************************************************************************************************"
            print attributeName + " : " + AdminConfig.showAttribute(propertyId, 'value')
            print "****************************************************************************************************"
        #else:
            #print "   No value set for custom property: " + attributeName + " for portName: " + portName
        
        componentType = 'HTTPInboundChannel'
        componentName = httpChannelName
        #print "\n\n HTTP transport channel (non-custom) properties for portName: " + portName + " . . . "     
        attributeName = "keepAlive"
        displayNonDefaultServerComponentAttribute(serverId, componentType, componentName, attributeName)

        attributeName = "maximumPersistentRequests"
        displayNonDefaultServerComponentAttribute(serverId, componentType, componentName, attributeName)

        attributeName = "persistentTimeout"
        displayNonDefaultServerComponentAttribute(serverId, componentType, componentName, attributeName)
        
        attributeName = "readTimeout"
        displayNonDefaultServerComponentAttribute(serverId, componentType, componentName, attributeName)

        attributeName = "writeTimeout"
        displayNonDefaultServerComponentAttribute(serverId, componentType, componentName, attributeName)
        
    except:
        print "Exception in displayNonDefaultHttpQueueTuningParamsByPortName() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])


        
#--------------------------------------------------------------------
# Display properties relating to HTTP queue tuning for a server
# Underlying file is server.xml
#--------------------------------------------------------------------
def displayHttpQueueTuningParams(nodeName, serverName):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Display tuning properties for HTTP and HTTPS"
        print " nodeName:                      "+nodeName
        print " serverName:                    "+serverName

        msg = " Executing: WebContainer.displayHttpQueueTuningParams(\""+nodeName+"\", \""+serverName+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        print
        print " Note: Properties are admin console defaults unless otherwise specified."
        print
        serverId = AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
        
        portName = "WC_defaulthost"
        displayHttpQueueTuningParamsByPortName(serverId, portName)
                
        portName = "WC_defaulthost_secure"
        displayHttpQueueTuningParamsByPortName(serverId, portName)

    except:
        print "Exception in displayHttpQueueTuningParams() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of displayHttpQueueTuningParams()"  

def displayNonDefaultHttpQueueTuningParams(nodeName, serverName):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Display tuning properties for HTTP and HTTPS"
        print " nodeName:                      "+nodeName
        print " serverName:                    "+serverName

        msg = " Executing: WebContainer.displayNonDefaultHttpQueueTuningParams(\""+nodeName+"\", \""+serverName+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        print
        print " Note: Only non-default properties shown."
        print
        serverId = AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
        
        portName = "WC_defaulthost"
        displayNonDefaultHttpQueueTuningParamsByPortName(serverId, portName)
                
        portName = "WC_defaulthost_secure"
        displayNonDefaultHttpQueueTuningParamsByPortName(serverId, portName)

    except:
        print "Exception in displayNonDefaultHttpQueueTuningParams() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of displayNonDefaultHttpQueueTuningParams()"      


# H. Malloy Feb 2016
# see http://www-01.ibm.com/support/knowledgecenter/SSAW57_8.5.5/com.ibm.websphere.nd.doc/ae/txml_dbsessionpersist.html?lang=en  
#Using Jython string format for the arguments, as all the nested[ drive me mental otherwise
#'[[name1 val1] [name2 val2] [name3 val3]]'
# I am making these 3 cookie settings required
# b/c if you only set "secure" flag in admin console, other 2 get admin console defaults added to security.xml
# however, if you do same in wsadmin, other 2 do not get added to security.xml -- I don't know if that means they get the default from somewhere else or not
# useContextRootAsPath is new in WASv8 and this function omits it for WASv7
def setSessionCookieSettings(nodeName, serverName, wasVersion, defaultSessionCookieSettingsSecure, defaultSessionCookieSettingsHttpOnly, defaultSessionCookieSettingsUseContextRootAsPath):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Set cookie settings for a server"
        print " nodeName:              "+nodeName
        print " serverName:            "+serverName
        print " wasVersion:            "+str(wasVersion)
        print " secure:                "+defaultSessionCookieSettingsSecure
        print " httpOnly:              "+defaultSessionCookieSettingsHttpOnly
        print " useContextRootAsPath:  "+defaultSessionCookieSettingsUseContextRootAsPath        
        msg = " Executing: WebContainer.setSessionCookieSettings(\""+nodeName+"\", \""+serverName+"\", \""+str(wasVersion)+"\", \""+defaultSessionCookieSettingsSecure+"\", \""+defaultSessionCookieSettingsHttpOnly+"\", \""+defaultSessionCookieSettingsUseContextRootAsPath+"\")"
        print msg
        print "---------------------------------------------------------------"
        print ""
        cellId=AdminConfig.list('Cell')
        cellName=AdminConfig.showAttribute(cellId, 'name')

        scope = '/Cell:'+cellName+'/Node:'+nodeName+'/Server:'+serverName+'/'
        serverID = AdminConfig.getid(scope)
        sessionManagerID = AdminConfig.list('SessionManager', serverID)
        cookies = AdminConfig.list("Cookie", sessionManagerID)
        cookieList = Utilities.convertToList(cookies)
        sessionCookieID = cookieList[0]
        propertyListString = 'propertyListString not defined yet'
        # defaultSessionCookieSettingsSecure = "true"
        # defaultSessionCookieSettingsHttpOnly = "false"
        # defaultSessionCookieSettingsUseContextRootAsPath = "true"

        print "wasVersion: " + wasVersion
        #  WAS major version (e.g., "7" or "8")
        if (wasVersion == "7"):
            print "WAS version is 7; omitting useContextRootAsPath"
            propertyListString = '[[secure "' + defaultSessionCookieSettingsSecure + '"]]'
        elif (int(wasVersion) >= 8):
            print "WAS version is: " + str(wasVersion) + "; adding useContextRootAsPath"
            propertyListString = '[[secure "' + defaultSessionCookieSettingsSecure + '"] [httpOnly "' + defaultSessionCookieSettingsHttpOnly + '"] [useContextRootAsPath "' + defaultSessionCookieSettingsUseContextRootAsPath + '"]]'
            #propertyListString = '[[secure "' + defaultSessionCookieSettingsSecure + '"]]'
            print "propertyListString is : " + propertyListString

        print AdminConfig.modify(sessionCookieID, propertyListString)
        #print setSessionCookieSettings(sessionManagerID, propertyListString)
        print "Modified component: " + sessionCookieID
        print AdminConfig.showall(sessionCookieID)
    except:
        print "Exception in setSessionCookieSettings() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setSessionCookieSettings()"


    
#--------------------------------------------------------------------
# main
#--------------------------------------------------------------------
#when this module is being run as top-level, call the requested function
if __name__=="__main__":
    usage = " "
    usage = usage + " "
    usage = usage + "Usage: <wsadmin command> -p <profile script to run>] -f <this py script> <config dir e.g., c:/qdr/ETP_dev/> <action> <node name> <server name> "
    usage = usage + " . . . where <action> is one of:\n"
    usage = usage + " . . .   * displayHttpQueueTuningParams - display all http queue tuning params \n"
    usage = usage + " . . . and must have modified soap.client.props of target wsadmin profile if security is enabled\n"
    print "\n\n"
    #print '\n\nlen(sys.argv) is ' 
    #print len(sys.argv)
    if len(sys.argv) == 4:
        configDir=sys.argv[0]
        #print "configDir " + configDir
        # e.g., C:/qdr/ETP_dev/
        
        #sys.path.append('C:/qdr/ETP_dev/config_scripts')          
        sys.path.append(configDir + 'config_scripts')
        #print "sys.path:" 
        #print sys.path
        
        # modules are expected to be in the directory we just appended to search path
        import ItemExists
        import HttpQueueTuningDefaults
        import ServerComponent


        action=sys.argv[1]
        print "action: " + action

        nodeName=sys.argv[2]
        print "nodeName: " + nodeName

        serverName=sys.argv[3]
        print "serverName: " + serverName

    else:
        print ""
        print "wrong number of args"
        print ""
        print usage
        sys.exit(1)

    if action == "displayHttpQueueTuningParams":
        displayHttpQueueTuningParams(nodeName, serverName)
    else:
        print "Action: " + action + " not recognized. Exiting."
        sys.exit(1)        
