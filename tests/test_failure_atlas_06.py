import unittest
from vyronforge_failure_atlas.contracts import classify_computer_use
class ComputerUseTests(unittest.TestCase):
    def test_discovery_only_not_pass(self):self.assertEqual(classify_computer_use(discovered=True,approved=False,captured=False,input_confirmed=False,closed=False),'BLOCKED_APPROVAL')
    def test_capture_failure(self):self.assertEqual(classify_computer_use(discovered=True,approved=True,captured=False,input_confirmed=False,closed=False),'BLOCKED_CAPTURE')
    def test_input_denied(self):self.assertEqual(classify_computer_use(discovered=True,approved=True,captured=True,input_confirmed=False,closed=False),'BLOCKED_INPUT')
    def test_not_closed_not_pass(self):self.assertEqual(classify_computer_use(discovered=True,approved=True,captured=True,input_confirmed=True,closed=False),'INCOMPLETE_NOT_PASS')
    def test_all_states_needed(self):self.assertEqual(classify_computer_use(discovered=True,approved=True,captured=True,input_confirmed=True,closed=True),'PASS_SYNTHETIC_STATE_CONTRACT')
