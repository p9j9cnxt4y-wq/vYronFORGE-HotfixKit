import unittest
from vyronforge_failure_atlas.contracts import ack_chain
class DesktopLifecycleTests(unittest.TestCase):
    def test_thread_no_turn_blocked(self):self.assertEqual(ack_chain(thread=True,turn=False,first_exec=False,result=False),'BLOCKED_TURN_NOT_STARTED')
    def test_turn_no_execution_blocked(self):self.assertEqual(ack_chain(thread=True,turn=True,first_exec=False,result=False),'BLOCKED_NO_EXECUTION_ACK')
    def test_execution_no_result_blocked(self):self.assertEqual(ack_chain(thread=True,turn=True,first_exec=True,result=False),'BLOCKED_RESULT_NOT_COMMITTED')
    def test_wrong_order_denied(self):self.assertEqual(ack_chain(thread=False,turn=True,first_exec=True,result=True),'INVALID_EVENT_ORDER')
    def test_complete_contract(self):self.assertEqual(ack_chain(thread=True,turn=True,first_exec=True,result=True),'RESULT_COMMITTED_SYNTHETIC_CONTRACT')
