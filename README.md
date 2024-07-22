# Moduline WebUI

for development set up a venv, enter it and install the necessary packages:  
`python -m venv .venv` #Create the venv  
`source .venv/bin/activate` #Enter the venv  
`pip install setuptools`  
`pip install build`  
`pip install microdot`  
`pip install PyJWT`  
`pip install netifaces`  

then run  
`pip install --editable .`  
to install the module in your venv while using the regular project files as the source

then run  
`go-webui`  
to launch the webserver