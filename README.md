# Cherry-pick applier

## Prerequisites

To run this program, make sure to have:

- Python 3.9 or greater.
- Gerrit http password generated (how to generate this down below).
- A valid coreid.

### How to generate a Gerrit http password for your account

Go to gerrit.mot.com, log into your account. Then go into your account Settings (the dropdown menu in the upper right corner). In your account settings, look for the `HTTP Password` option in the left column. Once inside the menu, click the `Generate Password` button. Copy the string password it shows. You're done!

#### BONUS

Now, if you don't want to always pass this password and your coreid as an argument, you can export them as a environment variable.

Open your `.bashrc` file and add the following lines

```shell
export GERRIT_USERNAME=# your coreid
export GERRIT_PASSWORD=# your HTTP password
```

The save and exit. Open a new shell session or run the command below for the changes to take effect.

```shell
source .bashrc
```

## How to use

run the `install.sh` script. This script will create a shortcut for the script in the PATH (you will be able to call it without specifying its path) and will install the program's man page that you can access by calling `man applier`.

**Tip**: You can also run the program with -h to see the help prompt.

**NAME**

​	applier - automatically apply cherry-picks to multiple repositories at the same time.

**SYNOPSIS**

​	applier -f FILEPATH [<u>OPTIONS</u>]

**DESCRIPTION**
	Mandatory arguments to long options are mandatory for short options too.

​	-f, --filepath <u>FILEPATH</u>
​			The absolute path to a file with a list of Gerrit links

​	-u, --username <u>USERNAME</u>
​			Set a Gerrit user to use with this session. Otherwise, export GERRIT_USERNAME environment variable

​	-p, --paswrod <u>PASSWORD</u>
​			set a Gerrit password to use with this session. Otherwise, export a GERRIT_PASSWORD environment vartiable

​	-b, --new-branch <u>BRANCH_NAME</u>
​			Choose a branch name to be create in the repos where the cherry-picks will take place

​	-a, --aosp-path <u>AOSP_PATH</u>
​			The absolute path of the AOSP root. If not set, execute this program from the AOSP root

​	--no-threads
​			If you don't want this program using threads

​	-v, --version
​			show program's version number and exit

​	-h, --help
​			show this program help message and exit