from PyWinRD.Client import WinRDClient

client = WinRDClient(password='test')

client.connect()

client.deploy('Testing Files')

client.debug('Testing Files/Test1.py')
client.debug('Testing Files/Test2.py')

client.terminal('pip install tqdm')
client.debug('Testing Files/Test3.py')

client.disconnect()
