# waswiz Supported Features

## Features
websphereVariables (cell or node level only)
jaasAuthEntry (cell level only)
virtualHostWebserverEntry  
server
serverConfigurationArchive
jvmCustomProperty (server level)
jvmProcessDefinition (server level)
jvmLogRolling (server level)
transactionService (server level)
webContainer (server level) 
webContainerThreadPool (server level)
webContainerCustomProps (server level)
dataSource (cluster level if server is clustered, server level otherwise)
queue (cluster level if server is clustered, server level otherwise)
queueConnectionFactory (cluster level if server is clustered, server level otherwise)
jmsActivationSpec (cluster level if server is clustered, server level otherwise)
sessionReplicationDomain (cluster level only)
sharedLibrary (cluster level if server is clustered, server level otherwise)
asynchBeanWorkManager (cluster level if server is clustered, server level otherwise)

## Actions
There is a default action every time waswiz is run, which is to inspect the WAS cell it is connected to. You can also run this action from a menu item, e.g., for verification purposes after you have made a change.

At the moment the only other supported actions are **add**, **modify** and **replace**. You can't just remove. If you want to remove something, it's easy to just use the admin console for that.

Note that in cases where you are **adding** a config item and the parent of the config item is a server, you are in reality **modifying** the server, but the waswiz action is **add** not **modify**.

If you want to modify an existing server by adding thingos (e.g., datasources), the action to choose is either **replace** or **add**, depending on whether you are happy to replace all existing thingos for the server, or just want to add the ones that are missing. 

With both the **Add** and **Replace** features, you can choose whether the action will be based on the entire config file, or just one category of item ata time, e.g, datasources. This makes it possible to configure an existing server.

The available **Add** options are:
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

The available **Replace** options are the same as for Add.

There is a waswiz action called **Modify** which operates on existing was config items. The available Modify options are 
 * modify an **existing** asynch bean work manager
 * modify pool settings for an existing queue connection factory 
 * modify HTTP queue tuning params for an existing server