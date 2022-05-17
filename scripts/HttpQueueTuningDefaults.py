###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following procedures:
#getAttribute()
###############################################################################
# Notes
# Purpose of this is for WebContainer.displayHttpQueueTuningParamsByPortName() to be able
#  to flag which attributes have been changed from the admin console defaults

import sys

#--------------------------------------------------------------------
# Set global constants
#--------------------------------------------------------------------

# TCP transport channel non-custom properties 
maxOpenConnections = 20000
inactivityTimeout = 60

# TCP transport channel custom properties
listenBacklog = 511


# HTTP transport channel (non-custom) properties
keepAlive = "true"
maximumPersistentRequests = 100
persistentTimeout = 30
readTimeout = 60
writeTimeout = 60

def getAttribute(attribute):
    if attribute == "maxOpenConnections": return maxOpenConnections
    elif attribute == "inactivityTimeout": return inactivityTimeout
    elif attribute == "listenBacklog": return listenBacklog
    elif attribute == "keepAlive": return keepAlive
    elif attribute == "maximumPersistentRequests": return maximumPersistentRequests
    elif attribute == "persistentTimeout": return persistentTimeout
    elif attribute == "readTimeout": return readTimeout
    elif attribute == "writeTimeout": return writeTimeout
    else:
        print "\n\nAttribute not recognized: " + attribute
        print "  in HttpQueueTuningDefaults.getAttribute()"
        print "Exiting."
        sys.exit(1)      

    
