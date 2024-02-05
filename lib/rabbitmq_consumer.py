import json
import time
import pika
import logging
import functools


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class Consumer:
    def __init__(self, amqp_url, app_id,
                 queue, exchange, exchange_type,
                 prefetch_count=1):
        self.app_id = app_id
        self.queue = queue
        self.exchange = exchange
        self.exchange_type = exchange_type

        self.should_reconnect = False
        self.was_consuming = False

        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._url = amqp_url
        self._consuming = False
        self._prefetch_count = prefetch_count

    def connect(self):
        LOGGER.info('Connecting to %s', self._url)
        return pika.SelectConnection(
            parameters=pika.URLParameters(self._url),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)

    def close_connection(self):
        self._consuming = False
        if self._connection.is_closing or self._connection.is_closed:
            LOGGER.info('Connection is closing or already closed')
        else:
            LOGGER.info('Closing connection')
            self._connection.close()

    def on_connection_open(self, connection):
        LOGGER.info('Connection opened')
        self.open_channel()

    def on_connection_open_error(self, connection, err):
        LOGGER.error('Connection open failed: %s', err)
        self.reconnect()

    def on_connection_closed(self, connection, reason):
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            LOGGER.warning('Connection closed, reconnect necessary: %s', reason)
            self.reconnect()

    def reconnect(self):

        self.should_reconnect = True
        self.stop()

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
        self.close_connection()

    def setup_exchange(self):
        LOGGER.info('Declaring exchange: %s', self.exchange)

        cb = functools.partial(
            self.on_exchange_declareok, exchange=self.exchange)

        self._channel.exchange_declare(exchange=self.exchange,
                                       exchange_type=self.exchange_type,
                                       callback=cb)

    def on_exchange_declareok(self, frame, exchange):
        LOGGER.info('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()

        LOGGER.info('Exchange declared: %s', exchange)
        self.setup_queues()

    def setup_queues(self):
        LOGGER.info('Declaring queue %s', self.queue.name)

        cb = functools.partial(self.on_queue_declareok)
        self._channel.queue_declare(queue=self.queue.name,
                                    durable=self.queue.durable,
                                    callback=cb)

    def on_queue_declareok(self, frame):
        LOGGER.info(f'Binding {self.exchange} to {self.queue.name} with {self.queue.routing_key}', )

        cb = functools.partial(self.on_bindok)
        self._channel.queue_bind(self.queue.name,
                                 self.exchange,
                                 routing_key=self.queue.routing_key,
                                 callback=cb)

    def on_bindok(self, frame):
        LOGGER.info(f'Queue {self.queue.name} bound to {self.exchange}.{self.queue.routing_key}')
        self.set_qos(self.queue)

    def set_qos(self, queue):
        cb = functools.partial(self.on_basic_qos_ok)
        self._channel.basic_qos(
            prefetch_count=self._prefetch_count, callback=cb)

    def on_basic_qos_ok(self, frame):
        LOGGER.info('QOS set to: %d', self._prefetch_count)
        self.start_consuming()

    def start_consuming(self):
        self.was_consuming = True
        self._consuming = True

        cb = functools.partial(self.on_message)
        self._consumer_tag = self._channel.basic_consume(
            self.queue.name, cb)

    def add_on_cancel_callback(self):
        LOGGER.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        LOGGER.info('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def on_message(self, _unused_channel, basic_deliver, properties, body):
        LOGGER.info('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, body)
        if self.queue.consume_callback:
            self.queue.consume_callback(json.loads(body), self.queue)
        self.acknowledge_message(basic_deliver.delivery_tag)

    def acknowledge_message(self, delivery_tag):
        LOGGER.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def stop_consuming(self):
        if self._channel:
            LOGGER.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            cb = functools.partial(
                self.on_cancelok, userdata=self._consumer_tag)
            self._channel.basic_cancel(self._consumer_tag, cb)

    def on_cancelok(self, _unused_frame, userdata):
        self._consuming = False
        LOGGER.info(
            'RabbitMQ acknowledged the cancellation of the consumer: %s',
            userdata)
        self.close_channel()

    def close_channel(self):
        LOGGER.info('Closing the channel')
        self._channel.close()

    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        if not self._closing:
            self._closing = True
            LOGGER.info('Stopping')
            if self._consuming:
                self.stop_consuming()
                self._connection.ioloop.start()
            else:
                self._connection.ioloop.stop()
            LOGGER.info('Stopped')


class ReconnectingConsumer:
    def __init__(self, amqp_url, app_id,
                 queue, exchange, exchange_type,
                 prefetch_count=1):
        self.app_id = app_id
        self.queue = queue
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.prefetch_count = prefetch_count

        self._reconnect_delay = 0
        self._amqp_url = amqp_url
        self._consumer = Consumer(
            self._amqp_url,
            self.app_id,
            self.queue,
            self.exchange,
            self.exchange_type
        )

    def run(self):
        while True:
            try:
                self._consumer.run()
            except KeyboardInterrupt:
                self._consumer.stop()
                break
            self._maybe_reconnect()

    def _maybe_reconnect(self):
        if self._consumer.should_reconnect:
            self._consumer.stop()
            reconnect_delay = self._get_reconnect_delay()
            LOGGER.info('Reconnecting after %d seconds', reconnect_delay)
            time.sleep(reconnect_delay)
            self._consumer = Consumer(
                self._amqp_url,
                self.app_id,
                self.queue,
                self.exchange,
                self.exchange_type
            )

    def _get_reconnect_delay(self):
        if self._consumer.was_consuming:
            self._reconnect_delay = 0
        else:
            self._reconnect_delay += 1
        if self._reconnect_delay > 30:
            self._reconnect_delay = 30
        return self._reconnect_delay
