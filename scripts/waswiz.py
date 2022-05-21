'''Python v2.7 script framework for configuring WAS (Websphere Application Server) v9 using the builtin Python implementation on Java platform (wsadmin engine). Script reads plain-text config files in windows ini format, analyzes current WAS cell, and presents menus on the commandline. Most common configuration items are supported, including clustered or unclustered server, virtual host, datasources for a variety of JDBC providers, MQ queues and queue connection factory etc.'''
###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################

import sys
import os

global AdminApp
global AdminConfig
global AdminControl
global AdminTask

#--------------------------------------------------------------------
# "main"
# when this module is being run as top-level, call the appropriate function
#--------------------------------------------------------------------
if __name__=="__main__":

    # global configFile

    usage = "Usage: cd into dir containing the scripts, then execute \n"
    usage += " <wsadmin command> -f <this py script> <config file name> \n"
    usage = usage + " . . . and must have modified soap.client.props of target wsadmin profile if security is enabled\n\n\n"

    print "\n\n"

    if len(sys.argv) == 1:
        #----------------------------------------------------------------------
        # Add references for the WebSphere Admin objects to sys.modules
        # sys.modules - dictionary that maps module names to modules which
        # have already been loaded.
        #----------------------------------------------------------------------
        wsadmin_objects = {
                        'AdminApp'      : AdminApp    ,
                        'AdminConfig'   : AdminConfig ,
                        'AdminControl'  : AdminControl,
                        'AdminTask'     : AdminTask,
                      }
        sys.modules.update(wsadmin_objects)

        #----------------------------------------------------------------------
        # Add the scripts dir to python path
        # I can't find any way to get wsadmin to display name & path
        #   of currently running script
        # and it's way too awkward to make scripts dir be an arg
        # so we require script must be run from scripts dir
        # e.g., home/hazel/was_configurator/scripts
        pwd = os.getcwd()
        scripts_dir = pwd
        sys.path.append(scripts_dir)

        #----------------------------------------------------------------------
        # Find the config file.
        # We expect the config_files dir to be a sister dir of pwd
        parent_dir = os.path.split(scripts_dir)[0]
        config_dir = os.path.join(parent_dir, 'config_files')
        config_filename = sys.argv[0]
        configFile = os.path.join(config_dir, config_filename)
        #configFile = config_dir + '/' + config_filename
        '''
        print "parent_dir: " + parent_dir
        print "config_dir: " + config_dir
        print "config_filename: " + config_filename
        print "configFile: " + configFile
        '''
        #----------------------------------------------------------------------
        # Import all the modules this module uses at runtime.
        # We expect these modules to be in the directory we just appended
        #   to search path
        import ConfigFile
        import UserInterface
        import Utilities
        import wini

        UserInterface.start(configFile)
    else:
        print usage
        sys.exit("wrong number of args")





