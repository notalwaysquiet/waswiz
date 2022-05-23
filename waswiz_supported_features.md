# waswiz supported features

## Config Items
* websphereVariables (cell or node level only)
* jaasAuthEntry (cell level only)
* virtualHostWebserverEntry  
* server
* serverConfigurationArchive
* jvmCustomProperty (server level)
* jvmProcessDefinition (server level)
* jvmLogRolling (server level)
* transactionService (server level)
* webContainer (server level) 
* webContainerThreadPool (server level)
* webContainerCustomProps (server level)
* dataSource (cluster level if server is clustered, server level otherwise)
* queue (cluster level if server is clustered, server level otherwise)
* queueConnectionFactory (cluster level if server is clustered, server level otherwise)
* jmsActivationSpec (cluster level if server is clustered, server level otherwise)
* sessionReplicationDomain (cluster level only)
* sharedLibrary (cluster level if server is clustered, server level otherwise)
* asynchBeanWorkManager (cluster level if server is clustered, server level otherwise)
* CyberArk identity management support for datasources (an assortment of separate config items)

## Actions
There is a default action every time waswiz is run, which is to **inspect** the WAS cell it is connected to, and compare it to your config file. You can also re-run this action from a menu item. You might want to do this if someone has made a change using the admin console while your script was running.

The other supported actions are: 
* add config items
* modify config items
* replace config items
* delete config items
* an assortment of actions relating to **CyberArk identity management solution**
* an assortment of actions relating to MQ queue connection factory connection pool settings
* change to a different config file from your config files directory

If you want to remove something, it's often just as easy to use the admin console for that.

Note that in cases where you are **adding** a config item and the parent of the config item is a server, you are in reality **modifying** the server, but the waswiz action is **add** not **modify**.

If you want to modify an existing server by adding thingos (e.g., datasources), the action to choose is either **replace** or **add**, depending on whether you are happy to replace all existing thingos for the server, or just want to add the ones that are missing. 

With the **add**, **replace** and **delete** features, you can choose whether the action will be based on the entire config file, or just one category of item at a time, e.g, datasources. This makes it possible to configure an existing server.

The available **add** options are:
* add all items from config file
* add server (clustered or unclustered)
* add virtual host entry(ies) for a server or cluster
* add datasource(s) for a server or cluster
* add datasource(s) at an arbitrary scope
* add jvm custom prop(s) for a server or cluster
* add web container custom prop(s) for a server or cluster
* add mq queue connection factory(ies) for a server or cluster
* add jms activation spec(s) for a server or cluster
* add one or more shared library (& classloader) for a server or cluster
* add cell-scoped websphere variable(s)
* add node-scoped websphere variable(s)
* add cell-scoped jaas authentication entry(ies)
* add **new** asynch bean work manager(s) for a server or cluster

The available **replace** and **delete** options are the same as for **add**.

There is a waswiz action called **modify** which operates on existing was config items. The available **modify** options are 
 * modify an **existing** asynch bean work manager
 * modify pool settings for an **existing** queue connection factory 
 * modify HTTP queue tuning params for an **existing** server