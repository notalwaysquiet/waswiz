# waswiz
Python v2.7 script framework for configuring WAS (Websphere Application Server) v9 using the builtin Python implementation on Java platform (wsadmin engine). Scripts read plain-text config files in windows ini format. Most common configuration items are supported, including clustered or unclustered server, virtual host, datasources for a variety of JDBC providers, MQ queues and queue connection factory etc.

These are a rewrite of scripts that I originally wrote for a client. I and many other people used the scripts for the past 12 or 13 years, on Websphere versions 5.1 to 8.5.5.x. Supports traditional Websphere only (not Liberty), in ND edition or standalone base WAS ("server1"). The earlier version of the scripts were thoroughly tested on Windows, Linux and AIX as a result of creating multiple dev, qa and prod environments and migrating them repeatedly, e.g., from wasv5 to wsav6.1, wasv6.1 to 7, and from wasv7 to 8.5.5. Developers ran the scripts on Windows to create their local sandbox environment.

Note that Websphere v5-8.5.5 used Python 2.1 for its wsadmin engine. I have recently updated the scripts for the (slightly) newer Python v2.7 used by WAS v9. The Python version supported by current Websphere is now only 10 years old now, instead of 20 years old.

When I wrote the scripts initially I didn't know Python very well. For example, I didn't know about multiline comments. I knew about PEP 8 but didn't try to follow it since the IBM sample wsadmin scripts don't follow it at all. Instead, I tried to keep the scripts as simple as possible, so that a sys admin or a Java developer with no prior Python knowledge would be able to edit them. 

I have done some refactoring to make the scripts easier to understand and modify. In theory, I would like to thorougly test the refactored scripts before making them available to others. But the scripts are probably pretty useful already as they are, so I am uploading them. I plan to work on them some more. 

Future work I am planning for them (currently under way):
* more thorough testing using demo app to be installed after config script completes. I have only tested so far to verify that the server will start.
* prepare a "demo kit" with java app and scripts for DB and MQ, and corresponding config files for the websphere side of the config. 
* upgrade the comments. E.g., make sure every method has a (multiline) comment
* refactor to clarify better how data is passed around within the scripts.
* write new instructions to reflect the refactored version

Script reads the plain-text windows ini-format config file and then compares it to the existing config in the WAS cell it is connected to. It displays summary of both configs (config file and cell), with asterisk to show which items are in both the config file and the WAS cell. Script displays nested menus of common user actions, such as "Add" config item(s) to cell, and "Replace" existing config item(s) in cell with the ones in the config file.

H Malloy
