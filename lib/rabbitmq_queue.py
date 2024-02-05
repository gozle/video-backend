class Queue:
    def __init__(self, name, routing_key,
                 get_publish_items=None,
                 consume_callback=None,
                 durable=False):

        self.name = name
        self.routing_key = routing_key
        self.durable = durable
        self.get_publish_items = get_publish_items
        self.consume_callback = consume_callback

    @property
    def publish_items(self):
        return self.get_publish_items()
