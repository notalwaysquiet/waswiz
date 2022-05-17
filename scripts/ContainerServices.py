###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following procedures:
#   setTransactionServiceProperties
#
###############################################################################
# Notes


#--------------------------------------------------------------------
# Set global constants
#--------------------------------------------------------------------
import sys

# modules that are searched for in the same directory as this script
import ServerComponent


#--------------------------------------------------------------------
# Set properties for a server's transaction service
# Application servers > tier1_fe_server1 > Container Services (under Container Settings) > Transaction service 
# see config file for list of frequently used properties
# should support any other attributes of type 'TransactionService' not listed there, just add them on
#--------------------------------------------------------------------
def setTransactionServiceProperties(nodeName, serverName, propertyListString):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Set properties for a server's web container"
        print " nodeName:             "+nodeName
        print " serverName:           "+serverName
        print " propertyList:         "+str(propertyListString)
        msg = " Executing: ContainerServices.setTransactionServiceProperties(\""+nodeName+"\", \""+serverName+"\", \""+str(propertyListString)+"\")"
        print msg
        print "---------------------------------------------------------------"
        
        componentType = 'TransactionService'
        print " . . . calling generic method . . . "
        ServerComponent.setProperties(nodeName, serverName, componentType, propertyListString)
    except:
        print "Exception in setTransactionServiceProperties()"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of setTransactionServiceProperties()"


