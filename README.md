# animeAPP
To use this application, you should use linux environment or WSL in windows.
Instruction:
1. in the root directory of this app, run "./bin/installEnv" command, if it says something like "Permission denied", you should run
   "chmod +x bin/installEnv" first. This command will install a virtual environment on your machine and install anime app package to
   this environment.
2. in the root directory of this app, run "./bin/animeAPPrun" command, if it says something like "Permission denied", you should run
   "chmod +x bin/animeAPPrun" first. This command will activate the virtual environment and run the app.
3. copy the IP address from the terminal and paste it in your chrome search bar

File organization:
1. anime: app package.
2. bin: directory of some shell scripts (don't run animeDB).
3. sql: db schema file and python crawler file.
4. var: sqlite db file.
