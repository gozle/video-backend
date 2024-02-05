import json
import threading

import pika
import logging
import functools


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class Publisher:
    def __init__(self, amqp_url, app_id,
                 queues, exchange, exchange_type):
        self._connection = None
        self._channel = None

        self._url = amqp_url
        self.app_id = app_id

        self.queues = queues
        self.exchange = exchange
        self.exchange_type = exchange_type

        self._deliveries = None
        self._acked = None
        self._nacked = None
        self._message_number = None

        self._stopping = False

    def connect(self):
        LOGGER.info('Connecting to %s', self._url)
        return pika.SelectConnection(
            pika.URLParameters(self._url),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)

    def on_connection_open(self, connection):
        LOGGER.info('Connection opened')
        self.open_channel()

    def on_connection_open_error(self, connection, err):
        LOGGER.error('Connection open failed, reopening in 5 seconds: %s', err)
        self._connection.ioloop.call_later(5, self._connection.ioloop.stop)

    def on_connection_closed(self, connection, reason):
        self._channel = None
        if self._stopping:
            self._connection.ioloop.stop()
        else:
            LOGGER.warning('Connection closed, reopening in 5 seconds: %s',
                           reason)
            self._connection.ioloop.call_later(5, self._connection.ioloop.stop)

    def open_channel(self):
        LOGGER.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        LOGGER.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange()

    def add_on_channel_close_callback(self):
        LOGGER.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        LOGGER.warning('Channel %i was closed: %s', channel, reason)
        self._channel = None
        if not self._stopping:
            self._connection.close()

    def setup_exchange(self):
        LOGGER.info('Declaring exchange %s', self.exchange)

        cb = functools.partial(self.on_exchange_declareok, exchange_name=self.exchange)
        self._channel.exchange_declare(exchange=self.exchange,
                                       exchange_type=self.exchange_type,
                                       callback=cb)

    def on_exchange_declareok(self, frame, exchange_name):
        LOGGER.info('Issuing consumer related RPC commands')
        self.enable_delivery_confirmations()

        LOGGER.info('Exchange declared: %s', exchange_name)
        self.setup_queues()

    def setup_queues(self):
        for queue in self.queues:
            LOGGER.info('Declaring queue %s', queue.name)

            cb = functools.partial(self.on_queue_declareok, queue=queue)
            self._channel.queue_declare(queue=queue.name,
                                        durable=queue.durable,
                                        callback=cb)

    def on_queue_declareok(self, frame, queue):
        LOGGER.info(f'Binding {self.exchange} to {queue.name} with {queue.routing_key}',)
        cb = functools.partial(self.on_bindok, queue=queue)

        self._channel.queue_bind(queue.name,
                                 self.exchange,
                                 routing_key=queue.routing_key,
                                 callback=cb)

    def on_bindok(self, frame, queue):
        LOGGER.info(f'Queue {queue.name} bound to {self.exchange}.{queue.routing_key}')

        a = threading.Thread(target=self.start_publishing, args=(queue, ))
        a.start()

    def start_publishing(self, queue):
        for item in queue.items_to_publish:
            if self._stopping:
                return
            self.publish_message(item, queue)

    def enable_delivery_confirmations(self):
        LOGGER.info('Issuing Confirm.Select RPC command')
        self._channel.confirm_delivery(self.on_delivery_confirmation)

    def on_delivery_confirmation(self, method_frame):
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        ack_multiple = method_frame.method.multiple
        delivery_tag = method_frame.method.delivery_tag

        LOGGER.info('Received %s for delivery tag: %i (multiple: %s)',
                    confirmation_type, delivery_tag, ack_multiple)

        if confirmation_type == 'ack':
            self._acked += 1
        elif confirmation_type == 'nack':
            self._nacked += 1

        del self._deliveries[delivery_tag]

        if ack_multiple:
            for tmp_tag in list(self._deliveries.keys()):
                if tmp_tag <= delivery_tag:
                    self._acked += 1
                    del self._deliveries[tmp_tag]

        LOGGER.info(
            'Published %i messages, %i have yet to be confirmed, '
            '%i were acked and %i were nacked', self._message_number,
            len(self._deliveries), self._acked, self._nacked)

    def publish_message(self, message, queue, headers=None):
        if self._channel is None or not self._channel.is_open:
            return

        properties = pika.BasicProperties(app_id=self.app_id,
                                          content_type='application/json',
                                          headers=headers)

        self._channel.basic_publish(self.exchange, queue.routing_key,
                                    json.dumps(message),
                                    properties)
        self._message_number += 1
        self._deliveries[self._message_number] = True
        LOGGER.info('Published message # %i', self._message_number)

    def run(self):
        while not self._stopping:
            self._connection = None
            self._deliveries = {}
            self._acked = 0
            self._nacked = 0
            self._message_number = 0

            try:
                self._connection = self.connect()
                self._connection.ioloop.start()
            except KeyboardInterrupt:
                self.stop()
                if (self._connection is not None and
                        not self._connection.is_closed):
                    self._connection.ioloop.stop()

        LOGGER.info('Stopped')

    def stop(self):
        LOGGER.info('Stopping')
        self._stopping = True
        self.close_channel()
        self.close_connection()

    def close_channel(self):
        if self._channel is not None:
            LOGGER.info('Closing the channel')
            self._channel.close()

    def close_connection(self):
        if self._connection is not None:
            LOGGER.info('Closing connection')
            self._connection.close()