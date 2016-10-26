# Initial information and credits
This tool is heavily inspired by ACLHound (http://github.com/job/aclhound).
While I was initially helping out Job Snijders to improve ACLHound 
I soon came to the conclusion that usage of Grako and all that comes with it was unwarranted for the DSL/CL that rarely changes.
Moreover, Grako's AST makes extending the language or processing it a bit of a PITA.
 
Hence, after a few attempts I came up with a few (2, actually) regexps that are quite readable and do the same job.

AccessNinja aims to be as braindead as the task it does. It parses an ACLCL (ACL Configuration Language) and builds
a series of objects containing all the parts of the ACL in a configuration-language-agnostic way.

After that it offer a few (only JunOS currently, rest is WIP) config renderers and config deployers to be able to
render the configuration in the language of a particular device and push your rendered configuration to a device of your choice.

One major advantage of AccessNinja over ACLHound is the support of object-groups and port-groups whereever possible, rather than
expanding all the inclusions in separate rules.

# Getting started

Create a config file in `~/.accessninja/config` with the following contents:
```
[general]
devices = /Users/vlazarenko/REPOS/ecg-networking/devices
objects = /Users/vlazarenko/REPOS/ecg-networking/objects
policies = /Users/vlazarenko/REPOS/ecg-networking/policy
```
The paths should point to your check-out of ACLHound configuration files.

## Basic usage

```
$ ./an.py
Usage:
  an.py compile <device>|all
  an.py deploy <device>|all
```

* Compile will just render the config to screen and check for errors
* Deploy will actually get your stuff onto the device

Device needs to be configured in `~/.netrc` file.

# Language semantics

As I stated above, product is inspired by ACLHound, so I just took the same language, as it seems to be working for most use-cases.
Hence, also this part of the documentation is blatantly stolen from ACLHound ;)

## Directory structure/Syntax

In order to fully understand AccessNinja and its operation, it is of most importance that you understand its directory structure, as this is where you'll be spending most of your time when building ACLs.

The directories containing parts the ACLs are defined in `~/.accessninja/config` (as shown above).  These directories should be checked into version control, and an appropriate workflow defined for reviewing and accepting changes.

Ninja needs 3 directories, containing the following information:

*   devices
*   policy
*   objects

### Directory : devices

In the &quot;devices&quot; directory you'll add the devices which you want under control of Ninja. It's just a text file, and it contains a couple of variables.

*   vendor, this defines what OS the device is running, currently it supports : 
    * junos
    * ios (WIP)
    * asa (WIP)
    * arista (WIP)

*   transport, this defines how Ninja should connect to the device to deploy ACLs. ACLHound used to support telnet, I claim that this is insecure and have dropped it in favor of SSH-only for now.
*   include statements, these mention the policies that you would like to put on the devices. Multiple entries are allowed here.

Example device file:

```
$ cat devices/fw001
vendor junos
transport ssh
include nw-management
include test-policy
```


### Directory : policy

In the 'policy' directory you'll add text files that contain the actual ACL that you are building. The name that you choose here, is also the name of the ACL on the device you deploy the policy to. In this textfile, type the complete ACL as you want it. 

#### Policy language
The syntax for this is a variation of the AFPL2 language and is as following:


	< allow | deny > \
	< tcp | udp | any > \
	src < prefix | $ip | @hostgroup | any > [ port number | range | @portgroup | any ] \
	dst < prefix | $ip | @hostgroup | any > [ port number | range | @portgroup | any ] \
	[ stateful ] \
	[ expire YYYYMMDD ] [ log ] [mirror] \
	[ # comment ]

	< allow | deny > < icmp > < any | type <code|any> > \ 
	src < prefix | $ip | @hostgroup | any > \
	dst < prefix | $ip | @hostgroup | any > \
	[ expire YYYYMMDD ] [ log ] \
	[ # comment ]
	
	@policy_name

##### Range statement

Ranges can be configured in three different ways:

*    Specified as an actual range: 1024-2048 , this specifies port 1024 upto and including 2048
*    Specified as "greater then": 1024- , this specifies port 1024 up to and including 65535 
*    Specified as "less then": -1024 , this specifies port 0 up to and including 1024

##### Expire statement (in progress of being implemented)
Note the expire statement. This is something that does not translate as part of an ACL to the device, but is used during the build & deployment process to check if a certain policy/ACL is still valid. Once past the date mentiond in the expire statement, it will not be pushed towards the device.

#### Policy behaviour
Policies allow for inclusions, there are 3 type of object inclusion possibilities: 

*    hosts 
*    ports
*    policies

You do these inclusions by adding an @ sign in front of it. Now hosts & ports use a suffix with their filenames, which is explained in &quot;Objects&quot;. Policies can simple be included by just including the policy on a single line (@policy_name).

Keep in mind, that Ninja does automatically add a &quot;deny any&quot; statement at the end of each ACL, so you don't have to do that yourself, this also keeps behaviour consistent across devices. 

Tip: If you want to log certain denied traffic, you can always add a &quot;deny any any log&quot; statement as your last line. (same theory goes for allowing traffic). 

One last thing to keep in mind, remarks/comments are not being pushed towards the device, as it won't make sense once the actual ACL is compiled and being pushed, as you might end up with the same or more amount of remarks (because of iteration that could take place) then actual ACL lines.

#### Example:

	allow tcp src 10.0.0.0/8 port any dst 2.2.2.2 port 80 stateful # test
	deny tcp src 2.2.2.2 dst 2.2.2.2
	allow tcp src 2.2.2.2 dst 10.0.0.0/8 port 15-10
	allow tcp src 2.2.2.2 dst 10.0.0.0/8 port 5-10 expire 20140504
	allow tcp src @mp-servers dst 10.0.0.0/8
	deny tcp src @bgp-peers port any dst @mp-servers port @webports # another comment
	allow tcp src 2.2.2.2 port 1 dst 10.0.0.0/8 port 1023-
	allow tcp src 2.2.2.2 port 1 dst 10.0.0.0/8 port -1023
	allow any src any dst any mirror
	allow icmp 128 0 src any dst 192.0.2.0/24 # icmpv6 echo request
	allow icmp 129 0 src 192.0.2.0/24 dst any # icmpv6 echo reply



### Directory : objects

In the 'objects' directory you'll add text files which contain either hosts/subnets or ports

*   hosts: These are files which contain hosts or host ranges. Use single IPs or class notation (ie /24, /25) per line
*   ports: These are files which contain ports. Use single port numbers per line

In order for the proper files to be included in the policy, name them accordingly. So  filename wise use objectname.ports for a ports file, and use objectname.hosts for a file filled with host entries.
Where possible, these groups will be converted into object-groups and used accordingly.

Examples could be:

	$ cat objects/mailcluster.hosts
	10.32.2.0/24
	10.34.2.2
	10.34.2.3
	
	$ cat objects/mailcluster.ports
	25
	110
	143
	993
	465
