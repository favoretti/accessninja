h1. Getting started

Create a config file in `~/.accessninja/config` with the following contents:
```
[general]
devices = /Users/vlazarenko/REPOS/ecg-networking/devices
objects = /Users/vlazarenko/REPOS/ecg-networking/objects
policies = /Users/vlazarenko/REPOS/ecg-networking/policy
```
The paths should point to your check-out of ACLHound configuration files.

h2. Basic syntax

```
$ ./an.py
Usage:
  an.py compile <device>|all
  an.py deploy <device>|all
```

* Compile will just render the config to screen and check for errors
* Deploy will actually get your stuff onto the device

Device needs to be configured in `~/.netrc` file.
