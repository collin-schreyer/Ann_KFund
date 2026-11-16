"""Chat guidance uses synthetic pages; no private source is checked into tests."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi import HTTPException
import server


class PrivateChatGuidanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'guidance.txt'
        self.path_patch = patch.object(server, 'CHAT_GUIDANCE_PATH', self.path)
        self.path_patch.start()

    def tearDown(self):
        self.path_patch.stop()
        self.temp.cleanup()

    def test_missing_fails_closed(self):
        self.assertFalse(server.chat_guidance_status()['available'])
        with patch.object(server, 'ask_model') as model:
            with self.assertRaises(HTTPException) as error:
                server.search(server.SearchRequest(question='What is the tip limit?'))
            self.assertEqual(error.exception.status_code, 503)
            model.assert_not_called()

    def test_physical_pages_and_ocr(self):
        self.path.write_text('Synthetic cover\fSynthetic rule: a tip may be 20 percent.\f[OCR - verify against original]\nSynthetic certificate\f', encoding='utf-8')
        metadata = server.chat_guidance_status()
        self.assertEqual(metadata['page_count'], 3)
        self.assertEqual(metadata['ocr_pages'], [3])
        chunks = server.chat_retrieve('What tip limit applies?')
        self.assertEqual(chunks[0]['page'], 2)
        self.assertNotIn('Synthetic certificate', chunks[0]['excerpt'])
        self.assertEqual(server.chat_evidence(['invented'], chunks), [])
        with patch.object(server, 'ask_model', return_value={'answer': 'Sample answer', 'evidence_refs': ['E1']}) as model:
            result = server.search(server.SearchRequest(question='What tip limit applies?'))
            self.assertEqual(result['citations'][0]['page'], 2)
            self.assertIn('OCR', result['note'])
            self.assertIn('Synthetic rule', model.call_args.args[1])

    def test_visible_delimiters_and_reject_misnumbering(self):
        self.path.write_text('=== KFUND PAGE 001 ===\nSynthetic first page\n=== KFUND PAGE 002 ===\nSynthetic second page\n', encoding='utf-8')
        pages = server.chat_guidance_pages()
        self.assertEqual([p['page'] for p in pages], [1, 2])
        self.assertEqual(pages[1]['excerpt'], 'Synthetic second page')
        self.path.write_text('=== KFUND PAGE 001 ===\nFirst\n=== KFUND PAGE 003 ===\nThird\n', encoding='utf-8')
        self.assertFalse(server.chat_guidance_status()['available'])

    def test_overview_supplies_all_pages(self):
        self.path.write_text('\f'.join(f'Synthetic page {i}' for i in range(1, 10)) + '\f', encoding='utf-8')
        chunks = server.chat_retrieve('Summarize the guidelines')
        self.assertEqual([page['page'] for page in chunks], list(range(1, 10)))


if __name__ == '__main__':
    unittest.main()
