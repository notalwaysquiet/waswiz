# waswiz
## Summary
Python v2.7 script framework for configuring WAS (Websphere Application Server) v9 using the builtin Python implementation on Java platform (wsadmin engine). Scripts read plain-text config files in windows ini format. Most common configuration items are supported, including clustered or unclustered server, virtual host, datasources for a variety of JDBC providers, MQ queues and queue connection factory etc. 

## How to use
See [waswiz-instructions](https://github.com/notalwaysquiet/waswiz/blob/main/waswiz-instructions.md)

## Supported features, modes, Websphere editions, Websphere versions, and platforms
For list of supported features, see [waswiz_supported_features](https://github.com/notalwaysquiet/waswiz/blob/main/waswiz_supported_features.md).
The script can be run in either batch mode or via interactive text menus.

Supports traditional Websphere only (not Liberty), in ND edition or standalone base WAS ("server1"). 

The earlier versions of these scripts were thoroughly tested on Windows, Linux and AIX as a result of creating multiple dev, qa and prod environments and migrating them repeatedly, e.g., from wasv5 to wsav6.1, wasv6.1 to 7, and from wasv7 to 8.5.5. Developers ran the scripts on Windows to create their local sandbox environment. I have done a lot of refactoring recently, and the current version has not been thoroughly tested yet. I am only testing on Linux at the moment.

## Brief history
These are a rewrite of scripts that I originally wrote for a client. I and a dozen or so other people used the scripts for a period of 12 or 13 years, on Websphere versions 5 to 8.5.5.x. 

## How does it work?
Script reads the plain-text windows ini-format config file and then compares it to the existing config in the WAS cell it is connected to. It displays summary of both configs (config file and cell), with asterisk to show which items are in both the config file and the WAS cell. Script displays nested menus of common user actions, such as "Add" config item(s) to cell, and "Replace" existing config item(s) in cell with the ones in the config file.


## Why script for WAS?
There are several benefits to scripting for WAS administration. The most obvious is that the scripted actions run much faster than an admin can do them by hand in the admin console. The second most obvious reason is repeatability. One developer chose not to use my script to set up his developement environment, and he told me it took him two days to configure by hand in the admin console and it was at least a week before he got it working right. With my script, it would have taken him less than an hour. My script framework adds an additional benefit, which is that the config is read from a plain-text config file. The config files provide a convenient (though non-authoritative) record of the WAS config, and can be added to version control.

## Python version
Note that Websphere v5-8.5.5 used Python 2.1 for its wsadmin engine. I have recently updated the scripts for the (slightly) newer Python v2.7 used by WAS v9. The Python version supported by current Websphere is now only 10 years old now, instead of 20 years old.

## Design & refactoring notes
When I wrote the scripts initially I didn't know Python very well. For example, I didn't know about multiline comments. I knew about [PEP8](https://pep8.org/) but hadn't read it, and didn't try to follow it since the IBM sample wsadmin scripts don't follow it at all. 

Instead, I tried to keep the scripts as simple as possible, so that a sys admin or a Java developer with no prior Python knowledge would be able to edit them. 

Now that I know more about PEP8, I would like to begin to comply with it, but it is probably beyond me to bring all the scripts up to that level. I decided it is OK with me if they will have a mix of camelCase and snake_case.

I have done some refactoring before uploading the scripts to github to make the scripts easier to understand and modify, and to remove duplication. 

## Warning -- not thoroughly tested
The original version of the scripts was thoroughly tested, but I have done a lot of refactoring recently. In theory, I would like to thorougly test the refactored scripts before making them available to others. But the scripts are probably pretty useful already as they are, so I uploaded them to github. I plan to work on them some more. 

## Future work
Future work I am planning for waswiz:
* more thorough testing using demo app to be installed after config script completes. I have only tested so far to verify that the server will start.
* prepare a "demo kit" with java app and scripts for DB and MQ, and corresponding config files for the websphere side of the config. 
* upgrade the comments. E.g., make sure every method has a (multiline) comment
* refactor to clarify better how data is passed around within the scripts, especially in UserInterface.py

See also [to_do.md](https://github.com/notalwaysquiet/waswiz/blob/main/to_do.md) and the [Issues](https://github.com/notalwaysquiet/waswiz/issues) section of this repo. 


H Malloy
