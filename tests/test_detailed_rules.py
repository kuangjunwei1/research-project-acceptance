"""Regression guards for the explicitly selected detailed policy profile.
These check the documented policy contract, not model or Office behavior.
"""
import re
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class DetailedPolicyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rules=(ROOT/'references/detailed-rules.md').read_text(encoding='utf-8')
  cls.entry=(ROOT/'SKILL.md').read_text(encoding='utf-8')
 def test_linked(self):self.assertIn('references/detailed-rules.md',self.entry)
 def test_explicit_applicability(self):self.assertIn('用户明确选择',self.entry)
 def test_threshold_or(self):self.assertRegex(self.rules,r'500万元及以上，或执行期24个月及以上')
 def test_signature_roles(self):self.assertIn('校对、审核、批准后三类签名需手签',self.rules)
 def test_electronic_alternative(self):self.assertIn('电子版签转流程',self.rules)
 def test_word_submission(self):self.assertIn('验收报告需提供Word',self.rules)
 def test_font(self):self.assertIn('四号或小四',self.rules)
 def test_selfcheck_seal(self):self.assertIn('加盖承担单位公章',self.rules)
 def test_pending_grade(self):self.assertIn('等级待资料审查确认',self.rules)
 def test_timing_guard(self):self.assertIn('不能因当前未组织而直接认定逾期',self.rules)
 def test_no_source_fingerprint(self):self.assertIsNone(re.search(r'\b[a-f0-9]{64}\b',self.rules))
 def test_no_source_page_reference(self):self.assertIsNone(re.search(r'物理\d|印刷\d|附录\d',self.rules))

if __name__=='__main__':unittest.main(verbosity=2)
