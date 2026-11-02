import unittest
from vyronforge_failure_atlas.contracts import skill_oracle,classify_skill_trace
class SkillRoutingTests(unittest.TestCase):
    def test_positive_selects(self):self.assertEqual(skill_oracle('Please perform ROUTE_ALPHA_POSITIVE.'),'ALPHA_EXPECTED')
    def test_exclusion_vetoes(self):self.assertEqual(skill_oracle('ROUTE_ALPHA_POSITIVE ROUTE_ALPHA_EXCLUDE'),'ALPHA_FORBIDDEN')
    def test_not_a_substring_trigger(self):self.assertEqual(skill_oracle('ROUTE_ALPHA_POSITIVE_SUFFIX'),'ALPHA_FORBIDDEN')
    def test_beta_not_alpha(self):self.assertEqual(skill_oracle('ROUTE_BETA_POSITIVE'),'ALPHA_FORBIDDEN')
    def test_attempt_not_selection(self):self.assertEqual(classify_skill_trace(attempted_read=True,body_loaded=False,internal_selection_event=False),'TOOL_ATTEMPT_OBSERVED_NO_BODY_LOAD')
    def test_body_load_not_host_selection(self):self.assertEqual(classify_skill_trace(attempted_read=True,body_loaded=True,internal_selection_event=False),'BODY_LOADED_NO_INTERNAL_SELECTION_PROOF')
    def test_real_host_selection_separate(self):self.assertEqual(classify_skill_trace(attempted_read=True,body_loaded=True,internal_selection_event=True),'HOST_SELECTION_OBSERVED')
