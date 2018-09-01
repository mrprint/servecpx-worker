# -*- coding: utf8


class MessageBus(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MessageBus, cls).__new__(cls)
            cls.subscribers = {}
        return cls.instance


    def broadcast(self, event, *args, **kwargs):
        if "route" not in kwargs.keys():
            for evt in self.subscribers:
                for listener in self.subscribers[evt]:
                    listener(event, *args, **kwargs)
        else:
            if kwargs["route"] in self.subscribers.keys():
                for listener in self.subscribers[kwargs["route"]]:
                    listener(event, *args, **kwargs)

    #
    def publish(self, event, *args, **kwargs):
        self.broadcast("bus_on_publish", event)
        self.broadcast(event, *args, **kwargs)

    def subscribe(self, event, handler):
        try:
            self.subscribers[event].append(handler)
        except KeyError:
            self.subscribers[event] = [handler]

