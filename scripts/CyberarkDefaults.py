###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script includes the following procedures:
#getConnectionTimeout

###############################################################################
# Notes
#--------------------------------------------------------------------
# Set global constants
#--------------------------------------------------------------------

# constant name of config entry for Cyberark login module
# must be manually created in admin console prior to running script
loginModuleAliasName  = "CyberArkLogin"

# https://docs.cyberark.com/Product-Doc/OnlineHelp/AAM-CP/Latest/en/Content/CP%20and%20ASCP/Configuring-App-Server-WebSphere-AppServerClassic.htm?tocpath=Administration%7CApplication%20Server%20Credential%20Provider%7CWebSphere%20Configuration%7C_____1

# create jvm custom prop with this value if none is spec. in config file
# From Cyberark Guide: If the CPM is configured to change passwords automatically, 
# disable the CM Subject Cache (set to false) to configure the ASCP for use on WebSphere v8+
# cyberark default is true if we do not specify anything, but better to specify for clarity
# the "recipe" from the consultants said to set to false, so initially they all had it fase
# but that leads to frequent lookups which caused perf issues for PE, IQC and UserAdmin
# so we set those ones to true
# Jan 2020 cyberark logs are growing too fast so we are setting all existing (and future) ones to true
usingCMSubjectCache = "true"
#usingCMSubjectCache = "false"

usingCMSubjectCachePropDescription = "for Cyberark: 'true' enables the jvm CM Subject Cache to reduce agent lookups"

# create namespace binding string with this value if none is spec. in config file
# TTL for cred in cache on the jvm instead of requesting from agent every time
# time in seconds
localCacheLifeSpanStringToBind = "1800"
#localCacheLifeSpanStringToBind = ""

def getLoginModuleAliasName():
    return loginModuleAliasName

def getUsingCMSubjectCache():
    return usingCMSubjectCache
    
def getUsingCMSubjectCachePropDescription():
    return usingCMSubjectCachePropDescription
    
    
    
    
def getLocalCacheLifeSpanStringToBind():
    return localCacheLifeSpanStringToBind
    
def getReasonStringToBind(WAScellName, appNickname):
    reasonStringToBind = 'from ' + WAScellName + ': from ' + appNickname
    return reasonStringToBind
