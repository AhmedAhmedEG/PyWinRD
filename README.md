# Description
Python library that provides remote debugging capabilities for python files between two Windows machines, independent of the IDE you are using.

# How to install
```pip install pywinrd```


# Features
- Redirects all stdout, stderr and stin operations (print, raise and input statements) to the client.
- Debugs the scripts in a subprocess, isolated from the main server.
- Supports password authentication between server/client.
- Supports executing terminal commands on the server.
- Supports deploying files or folders to the server.
- Auto cleanup for deployed/debugged files when client disconnects.

# Classes
The library provides only two classes, ```WinRDServer``` and ```WinRDClient```, they both have the optional default arguments ```host```, ```port``` and ```password```.

1- For the ```WinRDServer``` class, the host/port defaults are set to ```host=''``` and ```port='2345'```.
> **_NOTE:_** The host ```''``` is special host value for the socket library that makes the server accessible from all the network interfaces.

2- For the ```WinRDClient``` class, the host/port defaults are set to ```host='localhost'``` and ```port='2345'```.

3- For both classes, the default password is an empty string, the passwords on server/client should match for the connection to start.

# Example

ServerTest.py
```
from PyWinRD.Server import WinRDServer

server = WinRDServer()
server.start()
```

ClientTest.py
```
from PyWinRD.Client import WinRDClient

client = WinRDClient()
client.connect()

client.deploy('path/to/file/or/folder')
client.debug('path/to/python/script')
client.terminal('termninal command')

client.disconnect()
```
