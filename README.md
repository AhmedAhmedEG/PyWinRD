# Description
Python library that provides remote debugging capabilities for python files between two windows machines, the library supports logging of clients activities and redirecting all the print and input operations to the client and shadowing them in the server.

# How to install
```pip install pywinrd```

# Classes
The library provides only two classes, ```WinRDServer``` and ```WinRDClient```, they both have the optional defualt arguments ```host``` and ```port```.

1- For the ```WinRDServer``` class, the default host and port are set to ```''``` and ```2345``` by default.
> **_NOTE:_** The host ```''``` is special host value for the socket library that makes the server accessible from all the network interfaces.

2- For the ```WinRDClient``` class, the default host and port are set to ```'localhost'``` and ```2345``` by default.

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
client.debug('path/to/your/file')
```
