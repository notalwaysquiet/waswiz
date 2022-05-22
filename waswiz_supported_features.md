# waswiz supported features

## Attributes
`websphereVariables (cell or node level only)
  symbolicName  
  value  
  description

jaasAuthEntry (cell level only)
  alias
  userid
  password
 
virtualHostWebserverEntry
  hostname
  port
 
server
  baseServerName
  serverConfigTemplateFilename
  nodeList
  nodeHostList
  isClustered
  clusterName
  portRangeStart
  portOffsetForClusterMembers
  hostsWebApps
  createAsteriskHostAlias

serverConfigurationArchive
  serverConfigArchiveDir
  serverConfigFileNameBase
  environmentNickname  

jvmCustomProperty (server level)
  propertyName
  propertyValue
  propertyDescription

jvmProcessDefinition (server level)
  initialHeapSize
  maximumHeapSize
  verboseModeGarbageCollection
  debugMode
  genericJvmArguments
  verboseModeClass
  should support any other attributes of type 'JavaVirtualMachine' not listed here, just add them on

jvmLogRolling (server level)
  rolloverType
  rolloverSize
  baseHour
  rolloverPeriod
  maxNumberOfBackupFiles
  should support any other attributes of type 'StreamRedirect' not listed here, just add them on
 
transactionService (server level)
  transactionLogDirectory
  totalTranLifetimeTimeout
  asyncResponseTimeout
  clientInactivityTimeout
  maximumTransactionTimeout
  heuristicRetryLimit
  heuristicRetryWait
  should support any other attributes of type 'TransactionService' not listed here, just add them on
 
webContainer (server level)
  enableServletCaching
  disablePooling
  allowAsyncRequestDispatching
  asyncIncludeTimeout
  maximumPercentageExpiredEntries
  maximumResponseStoreSize
  should support any other attributes of type 'WebContainer' not listed here, just add them on
 
webContainerThreadPool (server level)
  minimumSize
  maximumSize
  inactivityTimeout
  isGrowable
  should support any other attributes of type 'ThreadPool' not listed here, just add them on
 
webContainerCustomProps (server level)
  propertyName
  propertyValue
  propertyDescription
 
dataSource (cluster level if server is clustered, server level otherwise)
  dataSourceName
  jndiName
  authDataAlias
  description
  statementCacheSize
  maxConnections
  db2OrOracle
  # -following are oracle-specific attributes-
  url
  # -following are db2-specific attributes-
  databaseServerName
  databaseName
  readOnly
  currentSchema
  retrieveMessagesFromServerOnGetMessage
 
queue (cluster level if server is clustered, server level otherwise)
  name
  description
  jndiName
  baseQueueName
  baseQueueManagerName
  queueManager
  queueManagerHost
  queueManagerPort
  serverConnectionChannelName
  CCSID
  useNativeEncoding
  sendAsync
  readAhead
 
queueConnectionFactory (cluster level if server is clustered, server level otherwise)
  name
  jndiName
  description
  queueManager
  host
  port
  channel
  XAEnabled
  transportType

jmsActivationSpec (cluster level if server is clustered, server level otherwise)
  activationSpecName
  jndiName
  description
  destinationJndiName
  destinationType
  qmgrName
  qmgrHostname
  qmgrPortNumber
  qmgrSvrconnChannel
  wmqTransportType

sessionReplicationDomain (cluster level only)
  name
  numberOfReplicas
  requestTimeout
  encryptionType
  useSSL
  replicationDomainMembers
  replicateStatefulSessionBeans
 
sharedLibrary (cluster level if server is clustered, server level otherwise)
  libraryName
  description
  classPath
  useIsolatedClassLoader
  classLoaderMode

asynchBeanWorkManager (cluster level if server is clustered, server level otherwise)
  allowOverrideToModifyExisting
  name
  jndiName
  category
  description
  workTimeout
  workReqQSize
  workReqQFullAction
  numAlarmThreads
  minThreads
  maxThreads
  threadPriority
  isGrowable
  serviceNames`


## Actions
At the moment you can only add, modify or replace. You can't just remove. If you want to remove something, it's easy to just use the admin console for that.

If you want to modify an existing server by adding thingos (e.g., datasources), the action to choose is **replace** or **add**, depending on whether you are happy to replace all existing thingos for the server, or just want to add the ones that are missing. 

With both the Add and Replace feature, you can choose whether the action will be based on the entire config file or just the attributes you choose. is riskier because it is possible that someone has added things to

There is only one thing that the modify option does, which is to modify an existing asynch bean work manager.