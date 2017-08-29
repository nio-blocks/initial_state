from nio import TerminatorBlock
from nio.properties import Property, StringProperty, IntProperty, \
    VersionProperty

from ISStreamer.Streamer import Streamer


class InitialStateLogObject(TerminatorBlock):

    """ Initial State block for logging objects
    """

    version = VersionProperty('0.0.1')
    access_key = StringProperty(
        title='Access Key', default='[[INITIAL_STATE_ACCESS_KEY]]')
    bucket_name = StringProperty(title='Bucket Name', default='New Bucket')
    bucket_key = StringProperty(title='Bucket Key', default='')
    object = Property(title='Object', default='{{ $.to_dict() }}')
    buffer_size = IntProperty(title='Buffer Size', default=10)

    def __init__(self):
        super().__init__()
        self._streamer = None

    def configure(self, context):
        super().configure(context)
        try:
            kwargs = {'access_key': self.access_key()}
            if self.bucket_name():
                kwargs['bucket_name'] = self.bucket_name()
            if self.bucket_key():
                kwargs['bucket_key'] = self.bucket_key()
            if self.buffer_size():
                kwargs['buffer_size'] = self.buffer_size()
            self._streamer = Streamer(**kwargs)
        except Exception as e:
            self.logger.error("Failed to create streamer: {}".format(e))
            raise e

    def process_signals(self, signals):
        for s in signals:
            try:
                self._streamer.log_object(self.object(s))
            except Exception as e:
                self.logger.warning("Failed to log object: {}".format(e))
        self._streamer.flush()

    def stop(self):
        super().stop()
        self._streamer.close()
