import os
import json
import datetime

from collections import Counter

from tornado import web, ioloop
from tornadio2 import SocketConnection, TornadioRouter, SocketServer, event

import brukva

ROOT = os.path.normpath(os.path.dirname(__file__))

SUBSCRIBERS = []
# Will be instantiated as a ServerStats instance below.
STATS = None

class ServerStats(object):
    items = Counter()
    total = 0
    start = datetime.datetime.now()

    def __init__(self, stats_frequency_ms=10000):
        # Setup a periodic CB to output the stats.
        self.ioloop = ioloop.IOLoop.instance()
        self.pc = ioloop.PeriodicCallback(self.show_stats,
                stats_frequency_ms, io_loop=self.ioloop)
        self.pc.start()


    def log(self, message, level="info"):
        now = datetime.datetime.now()
        if level:
            print "[%s] %s - %s" % (level.upper(),
                    now.strftime("%Y-%m-%d %H:%M:%S"), message,)
        else:
            print "%s - %s" % (now.strftime("%Y-%m-%d %H:%M:%S"), message,)



    def incr(self, item, amount):
        self.items[item] += amount
        self.total += amount

    
    def show_stats(self):
        self.log("-" * 79, level=None)
        now = datetime.datetime.now()
        total = self.total
        seconds = (now - self.start).seconds

        # Calculate events per second.
        if seconds > 0 and total > 0:
            eps = float(total) / float(seconds) 
            self.log("Processing ~%.2f events per second." % eps)

        for key, val in self.items.items():
            if key == "sent_messages":
                self.log("Sent %d total messages so far." % val)
            else:
                self.log("Processed %d total %s events thus far." % (val, key,),
                        level="info")

        self.log("-" * 79, level=None)

def broadcast_events(event):
    """
    Generic event broadcaster. We subscribe to the 'events' redis queue, and
    anytime we get anything new from there, we emit that event to all of our
    http clients. This method is a brukva callback.
    """
    # Get the message body from the redis message.
    raw_event = event.body
    if not raw_event:
        # If there was no body to be had, let's just return.
        STATS.log("Recieved empty event body.", level="warn")
        return

    try:
        # Let's try to parse the JSON obj.
        event = json.loads(raw_event)
    except ValueError, e:
        # Ruh roh raggy... Wouldn't parse. Let's log it.
        STATS.log("Couldn't parse JSON object: %s" % str(raw_event), level="warn")
        return

    # Let's ensure this is a properly formed event (eg. kind, and json body.)
    kind = event.get('kind')
    body = event.get('body')
    if not kind or not body:
        STATS.log("Not a proper event: %s" % event, level="warn")
        return

    for subscriber in SUBSCRIBERS:
        STATS.incr('sent_messages', 1)
        subscriber.emit(kind, body)

    STATS.incr(kind, 1)


class StepPageHandler(web.RequestHandler):
    """
    Renders each step page for the talk.
    """
    def get(self, step):
        self.render('step-%s.html' % step)


class WebSocketHandler(SocketConnection):
    """
    Manages the global list of subscribers.
    """
    def on_open(self, *args, **kwargs):
        SUBSCRIBERS.append(self)

    def on_close(self):
        if self in SUBSCRIBERS:
            SUBSCRIBERS.remove(self)

# Create tornadio router
WSRouter = TornadioRouter(WebSocketHandler,
                            dict(enabled_protocols=['websocket', 'xhr-polling',
                                                    'jsonp-polling', 'htmlfile']))

# Create socket application
application = web.Application(
    WSRouter.apply_routes([(r"/step-(\d)+[/]?", StepPageHandler)]),
    flash_policy_port = 843,
    flash_policy_file = os.path.join(ROOT, 'flashpolicy.xml'),
    template_path = os.path.join(ROOT, 'templates'),
    static_path = os.path.join(ROOT, 'static'),
    socket_io_port = 8001,
    enable_pretty_logging = True
)

if __name__ == '__main__':
    socketio_server = SocketServer(application, auto_start=False)

    STATS = ServerStats()

    redis = brukva.Client(host='localhost', port=6379, selected_db=0)
    redis.connect()
    redis.subscribe('events')
    redis.listen(broadcast_events)

    ioloop.IOLoop.instance().start()


