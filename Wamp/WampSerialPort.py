from autobahn.twisted.wamp import ApplicationRunner
from Wamp.SerialPortComponent import SerialPortComponent
from Wamp.SerialDataComponent import SerialDataComponent
from Wamp.BackendComponent import AppSession
from Wamp.TcpToWampTwistedComponent import TcpToWampTwistedAppSession
from twisted.internet import reactor


class WampSerialPort:
    def __init__(self):
        #serial_data = WampSerialDataComponent()
        #serial_data.start()
        serial_port = WampSerialPortComponent()
        serial_port.start()
        backend = WampBackend()
        backend.start()
        twisted = TcpToWampTwistedComponent()
        twisted.start()

        # Start the reactor only once
        # So create a start() for each component that
        # creates the runner but does not call run
        reactor.run()


class WampSerialDataComponent:
    def __init__(self):
        self.runner = ApplicationRunner(url=u"ws://localhost:55058/ws", realm=u"realm1")

    def start(self):
        # Pass start_reactor=False to all runner.run() calls
        self.runner.run(SerialDataComponent, start_reactor=False)


class WampSerialPortComponent:
    def __init__(self):
        self.runner = ApplicationRunner(url=u"ws://localhost:55058/ws", realm=u"realm1")

    def start(self):
        # Same as above
        self.runner.run(SerialPortComponent, start_reactor=False)


class WampBackend:
    def __init__(self):
        self.runner = ApplicationRunner(url=u"ws://localhost:55058/ws", realm=u"realm1")

    def start(self):
        # Same as above
        self.runner.run(AppSession, start_reactor=False)


class TcpToWampTwistedComponent:
    def __init__(self):
        self.runner = ApplicationRunner(url=u"ws://localhost:55058/ws", realm=u"realm1")

    def start(self):
        # Same as above
        self.runner.run(TcpToWampTwistedAppSession, start_reactor=False)




