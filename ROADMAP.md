# Roadmap

## Use freight forwarder as a SDK and build api.
    * could be useful for all

## Improve search using filters.

## Add docker networking code.

## Add post and pre build hooks.
    * Move the injector into a plug in for both post and pre hook.
    * Move testing into post and pre hook.
    * Add hook for git container using that container and volumes to get access to source code.

## Dry run display to the user exact service and hosts definitions being used for action being used.

## Convert config file to a compose format and return to user or hand off to ecs or compose itself.

## Allow the injection of configs for every service when running quality control.
    * should also build in support for puppet db, chef server, and ansible tower. This will allow for easy integration. 

## Catch term from jenkins when ff run is terminated early.

## Review tagging while exporting. Should be using the previous environment tags when daisy chaining images.
 
## travis integration as well as public docs

## Build bill of lading objects to provide better info about container ships etc
