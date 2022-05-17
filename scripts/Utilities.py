###############################################################################
# WebSphere 9x script
# Copyright (c) Hazel Malloy 2022
###############################################################################

import java

import AdminConfig
import AdminTask


'''Takes a string that has been spat out from wsadmin as output from a command that returns a list. But wsadmin output is always string. When output is supposed to represent a "list" the "[" and "]" will prevent us from using splitlines() or similar on it. To convert the "liststring" to a real list, we need to remove the "[" and "]" and then split the string into list items. Copied from IBM sample script "AdminUtilities.py"'''
def convertToList(inlist):
    outlist = []
    if (len(inlist) > 0):
        if (inlist[0] == '[' and inlist[len(inlist) - 1] == ']'):
            # Special checking when the config name contain space
            if (inlist[1] == "\"" and inlist[len(inlist)-2] == "\""):
                clist = inlist[1:len(inlist) -1].split(")\" ")
            else:
                clist = inlist[1:len(inlist) - 1].split(" ")
        else:
            clist = inlist.split(java.lang.System.getProperty("line.separator"))

        for elem in clist:
            elem = elem.rstrip();
            elem = str(elem)
            if (len(elem) > 0):
                if (elem[0] == "\"" and elem[len(elem) -1] != "\""):
                    elem = elem+")\""
                outlist.append(elem)

    return outlist


'''Return name of the cell'''
def get_cell_name():
    cell_id = AdminConfig.list("Cell")
    cell_name = AdminConfig.showAttribute(cell_id, "name")
    return cell_name


'''Return list of node names in the cell (including dmgr)'''
def get_node_name_list():
    node_name_list = convertToList(AdminTask.listNodes())
    return node_name_list


'''Return list of node ids in the cell (includng dmgr)'''
def get_node_id_list():
    return AdminConfig.list("Node")
