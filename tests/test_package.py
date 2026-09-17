import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlsplit
import yaml

ROOT=Path(__file__).resolve().parents[1]
class PackageTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.text=(ROOT/'SKILL.md').read_text(encoding='utf-8')
  cls.meta=yaml.safe_load(cls.text.split('---',2)[1])
  cls.ui=yaml.safe_load((ROOT/'agents/openai.yaml').read_text(encoding='utf-8'))
 def test_name(self):self.assertEqual(self.meta['name'],ROOT.name)
 def test_name_syntax(self):self.assertRegex(self.meta['name'],r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
 def test_description(self):self.assertTrue(self.meta['description'].strip())
 def test_author(self):self.assertEqual(self.meta['metadata']['author'],'kuangjunwei1')
 def test_ui_prompt(self):self.assertIn('$'+self.meta['name'],self.ui['interface']['default_prompt'])
 def test_ui_description(self):self.assertTrue(25<=len(self.ui['interface']['short_description'])<=64)
 def test_links(self):
  for p in [ROOT/'SKILL.md',*(ROOT/'references').glob('*.md')]:
   for link in re.findall(r'\[[^\]]+\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
    parsed=urlsplit(link)
    if parsed.scheme:continue
    target=(p.parent/parsed.path).resolve();self.assertTrue(target.is_relative_to(ROOT));self.assertTrue(target.is_file())
 def test_utf8(self):
  for p in ROOT.rglob('*'):
   if p.is_file() and p.suffix in {'.md','.yaml','.json','.py'}:self.assertNotIn('\ufffd',p.read_text(encoding='utf-8'))
 def test_no_business_binaries(self):self.assertFalse([p for p in ROOT.rglob('*') if p.suffix.lower() in {'.pdf','.docx','.xlsx','.xls','.png','.jpg','.pem','.pfx','.key'}])
 def test_no_absolute_business_path(self):
  for p in [ROOT/'SKILL.md',*(ROOT/'references').glob('*.md')]:self.assertIsNone(re.search(r'[A-Z]:[/\\]',p.read_text(encoding='utf-8')))
 def test_eval_ids(self):
  cases=json.loads((ROOT/'tests/evals.json').read_text(encoding='utf-8'))['cases'];self.assertEqual(len(cases),len({c['id']for c in cases}))
 def test_eval_inputs(self):
  for c in json.loads((ROOT/'tests/evals.json').read_text(encoding='utf-8'))['cases']:self.assertTrue(c['request']);self.assertTrue(c['evidence'])
 def test_readme(self):self.assertTrue((ROOT/'README.md').is_file())
 def test_tool(self):self.assertTrue((ROOT/'scripts/inspect_materials.py').is_file())
 def test_no_template_placeholders(self):self.assertIsNone(re.search(r'\b(?:TODO|TBD|FIXME)\b',self.text))
if __name__=='__main__':unittest.main(verbosity=2)
