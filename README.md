# Initial information and credits
This tool is heavily inspired by ACLHound (http://github.com/job/aclhoud).
While I was initially helping out Job Snijders to improve ACLHound 
I soon came to the conclusion that usage of Grako and all that comes with it was unwarranted for the DSL/CL that rarely changes.
Moreover, Grako's AST makes extending the language or processing it a bit of a PITA.
 
Hence, after a few attempts I came up with a few (2, actually) regexps that are quite readable and do the same job.

AccessNinja aims to be as braindead as the task it does. It parses an ACLCL (ACL Configuration Language) and builds
a series of objects containing all the parts of the ACL.

After that it offer a few (only JunOS, currently, rest is WIP) config renderers and config deployers to be able to
render the configuration in the language of a particular device and push your rendered configuration to a device of your choice.

# Getting started

Create a config file in `~/.accessninja/config` with the following contents:
```
[general]
devices = /Users/vlazarenko/REPOS/ecg-networking/devices
objects = /Users/vlazarenko/REPOS/ecg-networking/objects
policies = /Users/vlazarenko/REPOS/ecg-networking/policy
```
The paths should point to your check-out of ACLHound configuration files.

## Basic syntax

```
$ ./an.py
Usage:
  an.py compile <device>|all
  an.py deploy <device>|all
```

* Compile will just render the config to screen and check for errors
* Deploy will actually get your stuff onto the device

Device needs to be configured in `~/.netrc` file.
