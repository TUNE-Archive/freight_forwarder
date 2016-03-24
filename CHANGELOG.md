# Change Log
#### All notable changes to this project will be documented in this file. This project adheres to Semantic Versioning.

## [1.0.2] - 2016-03-24
* Resolved a bug where an export operation was using an image declaration from the same `deploy` environment 
  instead of export definition
* Resolved a bug where an environment's host service definition was being ignored and using the defined default
* Updated `FreightForwarder` to allow for the passing of a config path override and a verbosity level for logs.

## [1.0.1] - 2016-03-18

### Changes:
* Removing attach from export.
* Updated config validation to support beta environment.
* Added ContainerShip unit tests.
* When attached we now catch KeyboardInterrupt to allow the run to finish.

### New Features:
* Travis CI integration.
* Codecov integration.

### Bugs Resolved:
* Commercial invoice will now correctly set default to docker hub if the config doesn't contain a default registry.
* No longer attach to services that weren't passed during quality control.
* Fixing issue with python 3.4 arg parse. will now display usage if no arguments are passed.

## [1.0.0] - 2016-02-02

### Breaking Changes:
* Due to configuration validation additions users will more than likely will have
to make updates their freight-forwarder.yml. There isn't a way around this sorry for
any inconveniences.
* Injector environment variable name changes.  The names have change to be prefixed with INJECTOR inplace of CIA.  These
 changes were made to make open sourcing the projects easier.

### Changes:
* Updated configuration file format to use yaml.
* Added logger to remove print statements and provide nice formatting.
* Updated a number of expection messages to be more clear.
* Updated injector to with better exceptions and messages to provide the user
better insight.
* Updated injector to use oauth tokens for CIA.
* When running containers that have dependencies and dependents will now intelligently
create and restart only the containers that are required to.
* timestamp label will now be populated.
* Updated code base to support python3
* Export will no longer attempt to build and start dependents only dependencies.
* added unit tests, improved test coverage

### New Features:
* Simplified configuration file to make it easier to understand and integrate with.
* Added in-depth configuration file validation and a friendly easy to read output.
* Configuration file errors will provide hinting to assist user when fixing issues.
* Configuration file errors will provide line number when possible.
* Use child processes to store logs in queue to display to users if required. This
is required when log driver is set to something other than json-file.
* Added state file for actions and queue to stop users from running multiple commands
when containers are dependent on each other.  This is to prevent unexpected outcomes
when building and deploying.
* Added the ability to use the freight forwarder tagging scheme or not.
* Added the ability to use image cache or not.
* Search for images and list tags added to marshalling yard
* V2 registry support.

### Removed:
* Old configuration file design.

### Bugs Resolved:
* Fixed issue with deploying.  Containers with similar names were being delete
when they shouldn't be.
* Ports were backwards in the configuration file definition.
* Fixed logic issue with ulimits.
* Fixed issue when detach was false container would continually be restarted.
* No longer require .dockercfg unless trying to auth with registry.
* Fixed issue when finishing dispatch.  Will no longer attempt to delete state file
and dangling images a second time if host is defined twice.
