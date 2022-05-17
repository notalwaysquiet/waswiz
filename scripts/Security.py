###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
# Notes

# windows commands - displayHttpQueueTuningParams
# wsadmin.bat -lang jython -f c:\qdr\ETP_dev/config_scripts/WebContainer.py displayHttpQueueTuningParams AUSYDHQ-WS0958Node02 t1_cheetah_server2

# aix commands for Dev1 - displayHttpQueueTuningParams
# ./wsadmin.sh -lang jython -f /etp/wasadmin/was_configurator/ETP_dev/config_scripts/WebContainer.py displayHttpQueueTuningParams servers2HappyNode t1_cheetah_server2
# aix commands for Dev0 - displayHttpQueueTuningParams
# ./wsadmin.sh -lang jython -f /etp/wasadmin/was_configurator/ETP_dev/config_scripts/WebContainer.py displayHttpQueueTuningParams servers2LazNode dev0_t1_cheetah_server2


import sys

# wsadmin objects
import AdminConfig

import Utilities


def modifyLTPASingleSignon(requiresSSL):
    try:
        print "\n\n"
        print "---------------------------------------------------------------"
        print " Modify SSO for LTPA cookies"
        print " requiresSSL:              "+requiresSSL
        msg = " Executing: Security.modifyLTPASingleSignon(\""+requiresSSL+"\")"
        print msg
        print "---------------------------------------------------------------"
        print ""

        securityID = AdminConfig.list('Security')
        authMechanismsList = Utilities.convertToList(AdminConfig.showAttribute(securityID, 'authMechanisms'))


        for authMechID in authMechanismsList:
            if AdminConfig.showAttribute(authMechID, 'authConfig') == 'system.LTPA':
                LTPAAuthMechID = authMechID 
        
        singleSignonID = AdminConfig.showAttribute(LTPAAuthMechID, 'singleSignon')
        
        print AdminConfig.modify(singleSignonID, '[[requiresSSL "' + requiresSSL + '"]]')


    except:
        print "Exception in modifyLTPASingleSignon() "
        sys.excepthook(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
    #endTry
    print "end of modifyLTPASingleSignon()"

    

