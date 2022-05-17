###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
# Looks into the Websphere cell we are connected to & makes a list of all the servers
# For each unclustered server, extracts the plain-text property file.
# For each clustered server, extracts the file for one of the servers in the cluster.
# For ease of use, place inside the same file structure as the "WAS configurator" scripts, e.g., at /etp/wasadmin/was_configurator/ETP_dev/config_script

# profile_script_name takes care of adding the wsadmin objects (AdminConfig etc.) to the python system path so the modules can find them
# ok to omit the absolute path as long as the top-level script is called from its directory
# the file custom.properties specifies to call this profile script, so if you call custom.properties instead of wsadmin.properties you can omit the -profile arg
#profile_script_name="profile_scripts/WAuJ.py"

# script_file_name is the top-level python script to call (i.e., this script)
# ok to omit the absolute path as long as the top-level script is called from its directory
#script_file_name="WASPropertyFiles.py"

# environmentNickname="happy"

# there are 2 or 4 parameter the script takes: 
#   parent dir of script dir (needed to know where to place props files)
#   environment nickname (used to construct filenames)
#   nodeName & serverName - optional. If omitted, extracts props files for all servers in cell

# the property files will be created in the server_archives directory 

# IN ADDITION, in order to not have to pass in the wsadmin password in the commandline, 3 items in the soap.client.props file must be edited (securityEnabled, loginUserid, loginPassword)

#./wsadmin.sh  -lang jython -p $properties_file_name -profile $profile_script_name -f $script_file_name $environmentNickname 2>&1 | tee extract_${environmentNickname}_property_files.log 

#   To call from dos shell in windows
#wsadmin.bat -f c:/qdr/ETP_dev/config_scripts/WASPropertyFiles.py C:/qdr/ETP_dev/ dev servers1DevNode t1_puma_server1
# omit last 2 args to get it to dump all servers' props files
#wsadmin.bat -f c:/qdr/ETP_dev/config_scripts/WASPropertyFiles.py C:/qdr/ETP_dev/ desktop




# happy
#/usr/WebSphere/v7.0/dev1/profiles/dmgrHappy/bin/wsadmin.sh  -lang jython -profile profile_scripts/WAuJ.py -f WASPropertyFiles.py /etp/wasadmin/was_configurator/ETP_dev/ happy 2>&1 | tee extract_happy_property_files.log 

#./wsadmin.sh  -lang jython -profile $profile_script_name -f $script_file_name /etp/wasadmin/was_configurator/ETP_dev/ happy 2>&1 | tee extract_happy_property_files.log 
#./wsadmin.sh  -lang jython -p $properties_file_name -profile $profile_script_name -f $script_file_name /etp/wasadmin/was_configurator/ETP_dev/ happy 2>&1 | tee extract_happy_property_files.log 


# qa0
# ./wsadmin.sh  -lang jython -profile $profile_script_name -f $script_file_name /etp/wasadmin/was_configurator/ETP_dev/ qa0 2>&1 | tee extract_qa0_property_files.log 

# qa1
# ./wsadmin.sh  -lang jython -profile $profile_script_name -f $script_file_name /etp/wasadmin/was_configurator/ETP_dev/ qa1 2>&1 | tee extract_qa1_property_files.log 


# qa2
# ./wsadmin.sh  -lang jython -profile $profile_script_name -f $script_file_name /etp/wasadmin/was_configurator/ETP_dev/ qa2 2>&1 | tee extract_qa2_property_files.log 


# prod
# ./wsadmin.sh -f /etp/wasadmin/was_configurator/ETP_prod/config_scripts/WASPropertyFiles.py /etp/wasadmin/was_configurator/ETP_prod/ prod 2>&1 | tee extract_prod_property_files.log 


# sandbox1
# ./wsadmin.sh -user malloyh -password xxxxxx -p /etp/wasadmin/was_configurator/ETP_dev/config_scripts/wsadmin_properties_files/custom.properties -f /etp/wasadmin/was_configurator/ETP_dev/config_scripts/WASPropertyFiles.py /etp/wasadmin/was_configurator/ETP_dev/ sandbox1 2>&1 | tee extract_sandbox1_property_files.log

#   To call from dos shell in windows
# wsadmin.bat -lang jython -f c:/qdr/ETP_dev/config_scripts/WASPropertyFiles.py c:/qdr/ETP_dev/ desktop 

# C:\was7\profiles\dmgrDev\bin\wsadmin.bat -lang jython -f c:/qdr/ETP_dev/config_scripts/WASPropertyFiles.py c:/qdr/ETP_dev/ desktop 
# C:\was7\profiles\dmgrDev\bin\wsadmin.bat -lang jython -profile profile_scripts\WAuJ.py -f WASPropertyFiles.py c:/qdr/ETP_dev/ desktop 

#wsadmin.bat -p C:\qdr\ETP_dev\config_scripts\wsadmin_properties_files\custom.properties -f c:/qdr/ETP_dev/config_scripts/UserInterface.py c:/qdr/ETP_dev/ aa_win_grizzly_happy7.ini

# ./wsadmin.sh -user malloyh -password xxxxxx -p /etp/wasadmin/was_configurator/ETP_dev/config_scripts/wsadmin_properties_files/custom.properties -f /etp/wasadmin/was_configurator/ETP_dev/config_scripts/WASPropertyFiles.py /etp/wasadmin/was_configurator/ETP_dev/ sandbox1 2>&1 | tee extract_sandbox1_property_files.log
###############################################################################
# IBM doco on on the config properties files feature (introduced in v7)
#
# overly enthusiastic & error-filled IBM article 
# http://www.ibm.com/developerworks/websphere/techjournal/0904_chang/0904_chang.html
# beware that the article is misleading, e.g., "Your WebSphere Application Server configuration can be extracted into a single file and any configuration attribute can be located in that file in the form of name/value pair properties."
# It seems that when they say "WebSphere Application Server", they mean just one app server at a time, not a whole cell.
# It is not practical to extract properties for a whole cell, as the command seems to timeout on Donald's linux when the cell is the least bit complicated, e.g., has 2 servers. I did get it to do a whole cell on my desktop, when there are no servers, and it is windows.
# This is also misleading: " For further ease of use, you can apply a working configuration to another system quickly with one command that applies the configuration attributes specified in the properties file, as opposed to other tools, such as wsadmin, that require you to invoke multiple commands to achieve similar results."
# You CANNOT extract the file for a server in 1 cell & then apply it to a different cell (validation step fails). However, you can apply it to a cell that is an exact replica of the first cell, e.g., made using config archive feature.
# Also note that "-reportFile" arg should be "-reportFileName" - the infocenter has it correct & is a much better resource

# The infocenter is more realistic - at "PropertiesBasedConfiguration command group for the AdminTask object using wsadmin scripting"
# http://pic.dhe.ibm.com/infocenter/wasinfo/v7r0/index.jsp?topic=/com.ibm.websphere.base.doc/info/aes/ae/rxml_7propbasedconfig.html
# Avoid trouble:  Use properties files to customize, not replicate or merge environments. Do not extract an entire Cell, Node, Server, or ServerCluster to apply to a different environment. Only a subset of WCCM types are applied, and the extracted information is not merged with the new environment in a meaningful way.
# There is an explicit table of objects that can be configured this way on page at above link. 
# See Table 1. Supported WCCM types. You can use properties files to configure the WCCM types that are listed in this table
# There are also samples for some but not all of the supported types at "Managing specific configuration objects using properties files":
# http://pic.dhe.ibm.com/infocenter/wasinfo/v7r0/index.jsp?topic=%2Fcom.ibm.websphere.base.doc%2Finfo%2Faes%2Fae%2Ftxml_config_prop.html 


import time
import os
import sys

import AdminConfig
import AdminTask

import Utilities


def extractAllServersPropsFiles(filesPath, environmentNickname):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Extract props files for all servers in cell (1 per cluster for clustered servers)"
        print " archiveDir:                                "+filesPath
        print " environmentNickname:                       "+environmentNickname
        msg = " Executing: WASPropertyFiles.extractAllServersPropsFiles(\""+filesPath+"\", \""+environmentNickname+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully."
        usage = usage + msg

        # checking required parameters
        if (len(filesPath) == 0):
            print usage
            sys.exit(1)
        if (len(environmentNickname) == 0):
           print usage
           sys.exit(1)
        
        # checking if the parameter value exists
        
        if (os.path.exists(filesPath) != 1):
            print "\n\nThe specified directory: " + filesPath + " does not exist.\n\n"
            sys.exit(1)

    except:
        print "\n\nException in extractAllServersPropsFiles() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:

        #environmentNickname = 'happy'
        environmentDatetimeLabel = time.strftime('%Y'+'_'+'%m'+'_'+'%d',time.localtime())
        if environmentNickname != '':
            environmentDatetimeLabel = environmentNickname + '_' + environmentDatetimeLabel

        WASserverList = []
        WASserverIdList = AdminTask.listServers('[-serverType APPLICATION_SERVER ]').splitlines()
        if WASserverIdList:
            for id in WASserverIdList:
                serverName = id[0:id.find("(")]
                isClustered = "false"
                clusterName = AdminConfig.showAttribute(id, 'clusterName')
                if clusterName == None:
                    WASserverList.append(serverName)
                else:
                    isClustered = "true"
                    #we just take the first server in the list of cluster members
                    path="/ServerCluster:" +clusterName+"/"
                    clusterId = AdminConfig.getid(path)
                    #clusterId = 't1_lion_cluster(cells/HappyCell/clusters/t1_lion_cluster|cluster.xml#ServerCluster_1314951336231)'
                    #serverId = 't1_lion_server1(cells/HappyCell/clusters/t1_lion_cluster|cluster.xml#ClusterMember_1314951336271)'
                    #print AdminConfig.show(serverId)
                    #print AdminConfig.show(clusterId)
                    memberIdList = AdminConfig.showAttribute(clusterId, 'members')
                    #print memberIdList
                    memberIdList = Utilities.convertToList(memberIdList)
                    #print memberIdList	
                    serverName = AdminConfig.showAttribute(memberIdList[0], 'memberName')
                    WASserverList.append(serverName)
                
            for serverName in WASserverList:
                propertiesFileName = filesPath + '/serverConfigProps_' + serverName + '_' + environmentDatetimeLabel + '.props'
                print 'propertiesFileName: ' + propertiesFileName
                print ""
                AdminTask.extractConfigProperties('-configData Server=' + serverName + ' -propertiesFileName ' + propertiesFileName)
    except:
        print "\n\nException in extractAllServersPropsFiles() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)

def extractOneServersPropsFile(filesPath, environmentNickname, nodeName, serverName):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Extract props files for a server"
        print " archiveDir:                                "+filesPath
        print " environmentNickname:                       "+environmentNickname
        print " nodeName:                                  "+nodeName
        print " serverName:                                "+serverName
        
        msg = " Executing: WASPropertyFiles.extractOneServersPropsFiles(\""+filesPath+"\", \""+environmentNickname+"\", \""+nodeName+"\", \""+serverName+"\")"
        print msg
        print "---------------------------------------------------------------"
        print " "
        print " "
    
        usage = "\n\n"
        usage = usage + "Please check arguments carefully."
        usage = usage + msg

        # checking required parameters
        if (len(filesPath) == 0):
            print usage
            sys.exit(1)
        if (len(environmentNickname) == 0):
           print usage
           sys.exit(1)
        
        # checking if the parameter value exists
        if (os.path.exists(filesPath) != 1):
            print "\n\nThe specified directory: " + filesPath + " does not exist.\n\n"
            sys.exit(1)
        
        # checking if the parameter value exists
        path='/Node:'+nodeName+'/'
        nodeId= AdminConfig.getid(path)
        if (len(nodeId) == 0):
            print "\n\nThe specified node at: " + nodeName + " does not exist.\n\n"
            sys.exit(1)

        # checking if the parameter value exists
        path='/Node:'+nodeName+'/Server:'+serverName+'/'
        serverId= AdminConfig.getid(path)
        if (len(serverId) == 0):
            print "\n\nThe specified server at: " + serverName + " does not exist.\n\n"
            sys.exit(1)

    except:
        print "\n\nException in extractOneServersPropsFiles() when checking parameters\n\n"
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)
    try:
        #environmentNickname = 'happy'
        environmentDatetimeLabel = time.strftime('%Y'+'_'+'%m'+'_'+'%d',time.localtime())
        if environmentNickname != '':
            environmentDatetimeLabel = environmentNickname + '_' + environmentDatetimeLabel

        propertiesFileName = filesPath + 'serverConfigProps_' + serverName + '_' + environmentDatetimeLabel + '.props'
        AdminTask.extractConfigProperties('-configData Server=' + serverName + ' -propertiesFileName ' + propertiesFileName)
        print 'propertiesFileName: ' + propertiesFileName
        print "end of extractOneServersPropsFiles()"
       
    except:
        print "\n\nException in extractOneServersPropsFiles() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        sys.exit(1)        





			
#--------------------------------------------------------------------
# main
#--------------------------------------------------------------------
#when this module is being run as top-level, call the appropriate function
if __name__=="__main__":

    usage = " "
    usage = usage + " "
    usage = usage + "Usage: <wsadmin command> [-p < custom properties file, which tells wsadmin which cell to connect to (optional if called from its own bin)>] -f <this py script> <parent dir of script dir> <cell nickname purely for labelling purposes>"
    usage = usage + " . . . and must have modified soap.client.props of target wsadmin profile if security is enabled\n"
    usage = usage + "Can specify nodename & serverName as optional parameters"
    usage = usage + " "    

    if (len(sys.argv) == 2) or (len(sys.argv) == 4):
        configDir=sys.argv[0]
        #print "configDir " + configDir
        # e.g., C:/qdr/ETP_dev/
        
        archiveDir = configDir + 'server_archives'
        print ""  
        print "archiveDir: " + str(archiveDir)
        
        # environmentNickname is used to construct filenames for the extracted properties files
        environmentNickname = sys.argv[1]
        print "environmentNickname:" + environmentNickname
        #print "environmentNickname " + environmentNickname
    
    if len(sys.argv) == 2:
        extractAllServersPropsFiles(archiveDir, environmentNickname)
        
    if len(sys.argv) == 4:
        
        nodeName = sys.argv[2]
        print "nodeName:" + nodeName

        serverName = sys.argv[3]
        print "serverName:" + serverName

        extractOneServersPropsFile(archiveDir, environmentNickname, nodeName, serverName)
        
    else:
        print ""
        print usage
        print ""
        print "sys.argv: " + str(sys.argv)
        print ""
        sys.exit(1)

  

