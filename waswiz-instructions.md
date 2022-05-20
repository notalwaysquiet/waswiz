# waswiz Instructions
## How to install waswiz
### 1. Download
To download the code as a zip, go to the main page for the code repository https://github.com/notalwaysquiet/waswiz. Click on the big green button that says "Code" with a little downwards-pointing triangle on it. Choose "Download ZIP" on the dropdown menu that appears. The file will be called "waswiz-main".
### 2. Unzip
Unzip the code wherever is convenient on your system. It will unzip as a folder with the name "waswiz-main" (even if you rename the zip file). The folder structure from the repository will be inside that, in particular the scripts directory. Don't rename any of the subfolders or files, but you can rename the top-level folder. It can be named anything -- for example, "was-configurator" is a good choice.
## How to run waswiz 
### 1. Start your WAS if nec
For WAS ND, the dmgr must be started. For base WAS, your "server1" must be started.
### 2. Start a terminal (or DOS, or whatever) and change to the scripts directory
For example, I cd to /home/hazel/repos/waswiz/scripts.
### 3. Run waswiz script
Syntax for WAS ND, on Linux/UNIX: '<path to your dmgr profile>/bin/wsadmin.sh -f waswiz.py <filename of your config file>'

Example:
'sudo /opt/IBM/wasv9/profiles/dmgrPlum/bin/wsadmin.sh -f waswiz.py cheetah_v1_0.ini'

The script will print an error message and exit if your config file does not match the WAS cell you have connected to.
### 4. Write (or edit) your config file
Use an existing config file as an example. The example config files are heavily commented to help you out. Substitute the name of your cell, and other information as instructed in the comments. 

More example config files should be coming soon.
