from ..initial_state_log_object_block import InitialStateLogObject
from nio.testing.block_test_case import NIOBlockTestCase
from nio.signal.base import Signal
from unittest.mock import patch, MagicMock
from threading import Event


class MockStreamer():

    def __init__(self, **kwargs):
        pass

    def log_object(self, object):
        pass

    def flush(self):
        pass

    def close(self):
        pass


class TestInitialStateLogObject(NIOBlockTestCase):

    def test_initial_state_log_object_block(self):
        with patch(InitialStateLogObject.__module__+'.Streamer') as s:
            # mock streamer
            s.return_value = MockStreamer()
            s.return_value.log_object = MagicMock()
            s.return_value.flush = MagicMock()
            s.return_value.close = MagicMock()
            # configure block and process signals
            blk = InitialStateLogObject()
            self.configure_block(blk, {
                'bucket_name': 'my bucket',
                'bucket_key': 'bucket key',
                'access_key': 'key',
                'buffer_size': 10,
                'object': '{{ $.to_dict() }}',
                'signal_prefix': 'sig'
            })
            blk.start()
            signals = [Signal({'sig': 'signal1'}),
                       Signal({'sig': 'signal2'})]
            blk.process_signals(signals)
            blk.stop()
            # assertions
            self.assertEqual(s.return_value.log_object.call_count, 2)
            self.assertEqual(s.return_value.flush.call_count, 1)
            self.assertEqual(s.return_value.close.call_count, 1)
            s.return_value.log_object.assert_called_with({'sig': 'signal2'})
            self.assert_num_signals_notified(0)

    def test_exception_log_object(self):
        with patch(InitialStateLogObject.__module__+'.Streamer') as s:
            # mock streamer
            s.return_value = MockStreamer()
            s.return_value.log_object = MagicMock()
            s.return_value.log_object.side_effect = Exception('boooo')
            # configure block and process signals
            blk = InitialStateLogObject()
            self.configure_block(blk, {
                'bucket_name': 'my bucket',
                'bucket_key': 'bucket key',
                'access_key': 'key',
                'buffer_size': 10,
                'object': '{{ $.to_dict() }}',
                'signal_prefix': 'sig'
            })
            blk.logger.warning = MagicMock()
            blk.start()
            signals = [Signal({'sig': 'signal1'}),
                       Signal({'sig': 'signal2'})]
            blk.process_signals(signals)
            blk.stop()
            # assertions
            blk.logger.warning.assert_called_with(
                'Failed to log object: boooo')
