# Moduline WebUI

A web based UI for GOcontroll Moduline controllers.  
Configure interfaces and services, check errorcodes or see general system information.

## Development

-- App will require access to create and write log to file "/var/log/go_webui.log", 
so you could run app as root !! 
... also app want to create and write to file "/etc/go_webui.conf" may root will be with you.

for development set up a venv in the project, enter it and install the necessary packages:  
`python3 -m venv .venv` #Create the venv  
`source .venv/bin/activate` #Enter the venv  

then run  
`pip install --editable .`  
to install the module in your venv while using the regular project files as the source

then run  
`go-webui -passkey test`  
to launch the webserver with the passkey 'test'

`python3 setup.py sdist`  
to build the package for distribution