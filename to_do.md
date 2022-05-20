# to_do.txt

## Bugs to fix
method missing in Destroyer to blow away node-scoped websphere vars 

## Bugs & fixed
19/05/22 get_node_list() includes dmgr in results

## Doco
* create example config files for all supported features
* post the list of supported features
  
## Testing
test & debug Destroyer as standalone (batch mode)
test & debug Configurator (aka Creator) as standalone (batch mode)
test every feature for unclustered server
test every feature for clustered server on 2 nodes
  
## Enhancements
* add "blow away" feature to user interface
* rename Configurator to Creator. I just like that name better, to contrast better with Destroyer, and make it clear they are "opposites" in some way
* refactor to clarify better how data is passed around within the scripts, especially in UserInterface.py -- probably make it a class
* upgrade the comments. E.g., make sure every method has a (multiline) comment
* prepare a "demo kit" with java app and scripts for DB and MQ, and corresponding config files for the websphere side of the config.
* more thorough testing using demo app (to be installed after config script completes). I have only tested so far to verify that the server will start.
* per Troy Rose's suggestion 20/5/22, look into TOML as an upgrade from ini format for the config files

## Tasks done
20/05/22 write simple instructions
