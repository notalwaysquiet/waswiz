###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################
#   This Jython script is just a read-only bean

###############################################################################
# Notes
#--------------------------------------------------------------------
# Set global constants
#--------------------------------------------------------------------

#--------------------------------------------------------------------
# Global level
#--------------------------------------------------------------------
# LTPACookieRequiresSSL admin console default is false, both in WASv7 & WASv8.5
# http://www.ibm.com/developerworks/websphere/techjournal/1210_lansche/1210_lansche.html#step19
# see http://www.ibm.com/developerworks/websphere/techjournal/1004_botzum/1004_botzum.html#step19
# In admin console at Global security > Web and SIP security > Single sign-on (SSO)
LTPACookieRequiresSSL = "true"

#--------------------------------------------------------------------
# Server level
#--------------------------------------------------------------------

#"Defaults" to be used for particular apps and/or servers, particularly security-related
#I am putting these into a file rather than burying them in a script as I do not like hidden defaults
#All too often, the defaults need to be used in multiple places, and then things get very messy

#Secure Cookie Flag for session cookie: Restrict cookies to HTTPS sessions
# Specifies that the session cookies include the secure field. Enabling this feature restricts the exchange of cookies to HTTPS sessions only
# As for other defaultCookieSettings, can be overridden at app level.  
# Recommended security policy is to use Secure flag for all cookies
#   unless there is a very good reason not to
# Admin console default is false
defaultSessionCookieSettingsSecure = "true"

#HTTPOnly for session cookie: Set session cookies to HTTPOnly to help prevent cross-site scripting attacks 
# Specifies that session cookies include the HTTP only field. When checked, browsers that support the HTTP only attribute do not enable cookies to be accessed by client-side scripts. For security cookies, see the global security settings for web single sign-on (SSO).
# As for other defaultCookieSettings, can be overridden at app level.
# Applies to JSESSIONID and LTPA cookies only; for other cookies use com.ibm.ws.webcontainer.HTTPOnlyCookies Web container custom property
# Admin console default in WASv8.5+ is true (in WASv7 was false)
# some apps require that this be set to false
defaultSessionCookieSettingsHttpOnly = "true"

#Use the context root for cookie path
# Set the cookie path to match the context root for each application. This setting restricts the cookie from being sent to other applications and results in having different cookies created when accessing multiple applications
# Value of true fixes cookie clash issue seen for some apps
#   where "secondary" app is opened in 2nd browser tab and results in user getting 401 error in "primary" app 
#   because they were automatically logged out (resembles session timeout).
# As for other defaultCookieSettings, can be overridden at app level.
# New feature in WASv8+; Admin console default is false  
defaultSessionCookieSettingsUseContextRootAsPath = "true"


def getLTPACookieRequiresSSL():
    return LTPACookieRequiresSSL
    
def getDefaultSessionCookieSettingsSecure():
    return defaultSessionCookieSettingsSecure
 
def getDefaultSessionCookieSettingsHttpOnly():
    return defaultSessionCookieSettingsHttpOnly

def getDefaultSessionCookieSettingsUseContextRootAsPath():
    return defaultSessionCookieSettingsUseContextRootAsPath

