from nio.common.block.base import Block
from nio.metadata.properties import ExpressionProperty, StringProperty
from nio.common.discovery import Discoverable, DiscoverableType
from ISStreamer.Streamer import Streamer


@Discoverable(DiscoverableType.block)
class InitialStateLogObject(Block):

    """ Initial State block for logging objects
    """

    access_key = StringProperty(title='Access Key', default='[[INITIAL_STATE_ACCESS_KEY]]')
    bucket_name = StringProperty(title='Bucket Name', default='New Bucket')
    bucket_key = StringProperty(title='Bucket Key', default='')
    object = ExpressionProperty(title='Object', default='{{ $.to_dict() }}')
    buffer_size = StringProperty(title='Buffer Size', default='10')

    def __init__(self):
        super().__init__()
        self._streamer = None

    def configure(self, context):
        super().configure(context)
        try:
            kwargs = {'access_key': access_key, 'object': object}
            if self.bucket_name:
                kwargs['bucket_name'] = bucket_name
            if self.bucket_key:
                kwargs['bucket_key'] = bucket_key
            if buffer_size:
                kwargs['buffer_size'] = int(buffer_size)
            self._streamer = Streamer(**kwargs)
        except Exception as e:
            self._logger.error("Failed to create streamer: {}".format(e))
            raise e

    def process_signals(self, signals):
        for s in signals:
            try:
                self._streamer.log_object(self.object(s))
            except Exception as e:
                self._logger.warning("Failed to log object: {}".format(e))
        self._streamer.flush()

    def stop(self):
        super().stop()
        self._streamer.close()