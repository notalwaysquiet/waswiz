###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following server management procedures:
#   setEndPointsStartPort
###############################################################################
# Notes
# was8 has 20 automatically created ports per server
#  new in was8: OVERLAY_TCP_LISTENER_ADDRESS & OVERLAY_UDP_LISTENER_ADDRESS 
# was7 has 18 automatically created ports per server (vs 17 for was61 - ipc one is new)
# wc_defaulthost ports are 17th & 18th respectively (e.g., 6016, 6017 if start range is 6000)

# this script does not use script "library" as didn't see any method in scripts library to change ports
# to change hostname only, could use AdminServerManagement.configureEndPointsHost(nodeName, serverName, hostName)
# 
# can change ports with either AdminConfig or AdminTask but task is much much easier
# host is an optional param for AdminTask.modifyServerPort() 


# general ports info
# http://publib.boulder.ibm.com/infocenter/wasinfo/v7r0/index.jsp?topic=/com.ibm.websphere.base.doc/info/aes/ae/txml_portnumber.html
# http://publib.boulder.ibm.com/infocenter/wasinfo/v7r0/index.jsp?topic=/com.ibm.websphere.migration.express.doc/info/exp/ae/rmig_portnumber.html

# some ports are "shared" and must pass additional param for them
# this does not refer to sharing among xml files so it is not necessary to take any additional steps other than that param
# per IBM support 11/1/10, This parameter need to be set to "true" if the port you are trying to update is shared between multiple transport channel chains.
# you can see which ports have multiple transport chains by clicking on link 'View associated transports' in ports list in admin console
# note that more ports have that link than actually have multiple chains
# http://www-01.ibm.com/support/docview.wss?uid=swg21256533 

# ./wsadmin.bat -lang jython -javaoption "-Dwsadmin.script.libraries=c:/foo/qdr/" -f c:/foo/qdr/ServerPorts.py servers1DevNode tier1_fe_server1 4060
# ./wsadmin.bat -lang jython -f c:/foo/qdr/ServerPorts.py servers1DevNode tier1_fe_server1 4080
# ./wsadmin.bat -lang jython -f C:\was_configurator/config_scripts/ServerPorts.py servers1HappyNode server1 4040

# ./wsadmin.sh -lang jython -f /opt/was/scripts/wasconfig/ServerPorts.py EVSDevNode EVSDev 3060
# ./wsadmin.sh -lang jython -f /opt/was/scripts/wasconfig/ServerPorts.py EVSTestNode EVSTest 3080
# ./wsadmin.sh -lang jython -f /opt/was/scripts/wasconfig/ServerPorts.py EVSTestNode idm_prd0_imat_server1 3100
# ./wsadmin.sh -lang jython -f /opt/was/scripts/wasconfig/ServerPorts.py EVSTestNode idm_qa0_logging_server1 3200

# ./wsadmin.sh -lang jython -f /opt/was/scripts/wasconfig/ServerPorts.py  	EVSClientTestNode  idm_cta_imat_server1 3080

# ./wsadmin.sh -lang jython -profile "/etp/wasadmin/was_configurator/ETP_dev/config_scripts/profile_scripts/WAuJ.py" -f /etp/wasadmin/was_configurator/ETP_dev/config_scripts/ServerPorts.py servers1AwkwardNode  t0_grizzly_server1 14320 8
# ./wsadmin.sh -lang jython -profile "/etp/wasadmin/was_configurator/ETP_dev/config_scripts/profile_scripts/WAuJ.py" -f /etp/wasadmin/was_configurator/ETP_dev/config_scripts/ServerPorts.py servers2AwkwardNode  t0_grizzly_server2 15320 8


import sys
import AdminConfig
import AdminTask

#--------------------------------------------------------------------
# Configure end points start port
#--------------------------------------------------------------------
def setEndPointsStartPort(nodeName, serverName, startPort, wasVersion):
    endPointName="endPointName not set yet"
    startPort = str(startPort)
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Configure server end points start port"
        print " nodeName:                       "+nodeName
        print " serverName:                     "+serverName
        print " startPort:                      "+str(startPort)
        print " wasVersion:                     "+str(wasVersion)
        msg = " Executing: ServerPorts.setEndPointsStartPort(\""+nodeName+"\", \""+serverName+"\", \""+str(startPort)+"\", \""+str(wasVersion)+"\")"
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
        if (len(str(startPort)) == 0):
           print usage
           print 'len(str(startPort)):'
           print len(str(startPort))
           sys.exit(1)
    except:
        print "Exception in setEndPointsStartPort() when checking parameters"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:

        # checking if the parameter value exists
        nodeExist = AdminConfig.getid("/Node:"+nodeName+"/")
        if (len(nodeExist) == 0):
            print "The specified node: " + nodeName + " does not exist."
            sys.exit(1)
        serverExist = AdminConfig.getid("/Node:"+nodeName+"/Server:"+serverName+"/")
        if (serverExist == ''):
            print "The specified server: " + serverName + " does not exist."
            sys.exit(1)
    except:
        print "Exception in setEndPointsStartPort() when checking if node & server exist"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        portNumber = int(startPort)
    except:
        print "startPort must be an integer and should be in the custom-assigned port range for this WAS install."
    
    try:
        ''' not putting the port calls in a loop because the calls are not all the same --  some have a shared channel business. E.g., DCS Port has 2 channel transport chains (http & SSL) which both use ("share") the same instance of TCP channel. DCS TCP channel is dedicated for use by DCS, and likewise the SSL chain uses a dedicated SSL channel. The SSL chain "shares" the same TCP channel with http chain. Nothing is being "shared" from DCS port with any other ports or in any other sense, and this is not at all the same as "port sharing".
        For these ones, need extra param '-modifyShared', 'true'
        CWPMC0016E: Endpoint 'DCS_UNICAST_ADDRESS' is shared and cannot be modified if the modifyShared parameter is not specified.
        '''
        
        endPointName='BOOTSTRAP_ADDRESS'
        AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber])

        # 1
        portNumber=portNumber+1

        # CSIV2 Client Authentication Listener Port
        endPointName='CSIV2_SSL_MUTUALAUTH_LISTENER_ADDRESS'
        AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber])

        # 2
        portNumber=portNumber+1
        # CSIV2 Server Authentication Port
        endPointName='CSIV2_SSL_SERVERAUTH_LISTENER_ADDRESS'
        AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber])

        # 3
        # Inbound messages for DCS (Distribution and Consistency Services aka High Availability Manager Communication Port)
        portNumber=portNumber+1
        endPointName='DCS_UNICAST_ADDRESS'
        AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber, '-modifyShared', 'true'])
        print "wasVersion is: " + wasVersion + "."
        
        if (int(wasVersion) >= 7):
            # 4
            portNumber=portNumber+1
            ''' new in WAS7
            # IPC Connector Port (Inter-Process Communications connector, uses JMX, is default option used for connections between process on same physical machine, rather than soap) '''
            endPointName='IPC_CONNECTOR_ADDRESS'
            AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber])

        # 5
        portNumber=portNumber+1
        endPointName='ORB_LISTENER_ADDRESS'
        AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber])

        # 6
        if (int(wasVersion) >= 8):
            portNumber=portNumber+1
            ''' new in WAS8
            # Used for peer-to-peer (P2P) communication.The ODC (On Demand Configuration) and asynchronous PMI components use P2P as their transport. This port is required by every WebSphere Extended Deployment process. '''
            endPointName='OVERLAY_TCP_LISTENER_ADDRESS'
            AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber])

        # 7
        if (int(wasVersion) >= 8):
            portNumber=portNumber+1
            ''' new in WAS8
            # As for previous, but UDP. '''
            endPointName='OVERLAY_UDP_LISTENER_ADDRESS '
            AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber])

        # 8
        portNumber=portNumber+1
        endPointName='SAS_SSL_SERVERAUTH_LISTENER_ADDRESS'
        AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber])

        # 9
        portNumber=portNumber+1
        endPointName='SIB_ENDPOINT_ADDRESS'
        AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber])

        # 10
        portNumber=portNumber+1
        endPointName='SIB_ENDPOINT_SECURE_ADDRESS'
        AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber])

        # 11
        portNumber=portNumber+1
        endPointName='SIB_MQ_ENDPOINT_ADDRESS'
        AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber])

        # 12
        portNumber=portNumber+1
        endPointName='SIB_MQ_ENDPOINT_SECURE_ADDRESS'
        AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber])

        # 13
        # port has multiple channel thingos, need extra param '-modifyShared', 'true'
        portNumber=portNumber+1
        #SIP Container Port (Session Initiation Protocol) The SIP container will not listen on a port without a SIP application installed. 
        #The Session Initiation Protocol (SIP) proxy server initiates communication and data sessions between users.
        endPointName='SIP_DEFAULTHOST' # com.ibm.websphere.management.cmdframework.CommandException: CWPMC0016E: Endpoint 'SIP_DEFAULTHOST' is shared and cannot be modified if the modifyShared parameter is not specified.
        AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber, '-modifyShared', 'true'])

        # 14
        # port has multiple channel thingos, need extra param '-modifyShared', 'true'
        portNumber=portNumber+1
        #SIP Container Secure Port 
        endPointName='SIP_DEFAULTHOST_SECURE'#CWPMC0016E: Endpoint 'SIP_DEFAULTHOST_SECURE' is shared and cannot be modified if the modifyShared parameter is not specified.
        AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber, '-modifyShared', 'true'])

        # 15
        portNumber=portNumber+1
        endPointName='SOAP_CONNECTOR_ADDRESS'
        AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber])

        # 16
        portNumber=portNumber+1
        endPointName='WC_adminhost'
        AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber])

        # 17
        portNumber=portNumber+1
        endPointName='WC_adminhost_secure'
        AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber])

        # 18
        # port has multiple channel thingos, need extra param '-modifyShared', 'true'
        portNumber=portNumber+1
        endPointName='WC_defaulthost' #CWPMC0016E: Endpoint 'WC_defaulthost' is shared and cannot be modified if the modifyShared parameter is not specified.
        AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber, '-modifyShared', 'true'])

        # 19
        # port has multiple channel thingos, need extra param '-modifyShared', 'true'
        portNumber=portNumber+1
        endPointName='WC_defaulthost_secure' ##CWPMC0016E: Endpoint 'WC_defaulthost_secure' is shared and cannot be modified if the modifyShared parameter is not specified.
        AdminTask.modifyServerPort (serverName, ['-nodeName', nodeName, '-endPointName', endPointName, '-port', portNumber, '-modifyShared', 'true'])
        
    except:
        print "Exception in setEndPointsStartPort() when modifying " + endPointName
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    try:
        AdminConfig.save()
    except:
        print "Exception in setEndPointsStartPort() when saving aliases list property"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])

    print "end of setEndPointsStartPort()"


#--------------------------------------------------------------------
# main
#--------------------------------------------------------------------
#when this module is being run as top-level, call the function
if __name__=="__main__":
  usage = " "
  usage = usage + " "
  usage = usage + "Usage: <wsadmin command> -p <target wsadmin.properties file> -f <this py script> <nodeName, serverName, startPort, wasVersion>\n"
  usage = usage + " . . . and must have modified soap.client.props of target wsadmin profile if security is enabled\n"

  if len(sys.argv) == 4:
      nodeName=sys.argv[0]
      print "nodeName :" + nodeName
  
      serverName=sys.argv[1]
      print "serverName: " + serverName
    
      startPort=sys.argv[2]
      print "startPort: " + startPort

      wasVersion=sys.argv[3]
      print "wasVersion: " + wasVersion
      
      setEndPointsStartPort(nodeName, serverName, startPort, wasVersion)
  else:
    print "wrong number of args"
    print usage
    sys.exit(1)



  


