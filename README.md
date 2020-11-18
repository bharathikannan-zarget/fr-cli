# freshrelease cli

## Command line interface for freshrelease 

# Requirements

+ python 3.7 and above


# Installation

To install globally use

```
	sudo python setup.py install
```

# Getting started

To start using Freshrelease cli, get api key from freshrelease (profile settings). Use configure command

+ fr-cli configure

```
	Freshrelease Api Key [******************k1ow]: akaekkekekekekekekee
	Freshrelease Domain [freshworks.freshrelease.com]: freshworks.freshrelease.com
	Freshrelease Project Name [FM]: FM
```

All the profile configuration settings will be stored in `~/.freshrelease`.  Initially, we cache priority, status, issue types and sub projects for better performance. You can reload the config using

```
	fr-cli reload
```

# Basic Commands:

Command structure

```
	fr_cli <command> <subcomamnd> [options and parameters]
```

For example, to list all the issues assigned to you

```
	fr_cli issue filter --user "Bharathi Kannan"
```

For extensive filtering

```
	fr_cli issue filter --user "Bharathi Kannan" --subproject "Nucleus" --status "Open" --priority "High"
```

To search specific issues by keyword

```
	fr_cli issue search --query "Journeys"
```


To view help for any command

```
	fr_cli --help
	fr_cli issue --help
```

To create an issue

```
	fr_cli issue create
```

To update an issue

```
	fr_cli issue update
```

To view a particular issue

```
	fr_cli issue find --issue_id <ISSUE ID>
```


This cli supports two major resource groups

+ project - All project related actions
+ issue - All issue related actions (create, filter, find, update)



	
