"""Synthetic policy fixtures only: no private source text is stored in tests."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException
import server


SYNTHETIC_PAGE = (
    'Synthetic outside area: tips 11%.\n\n'
    'Synthetic city: tips 11% or 13%.'
)


class GuidanceReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'policy.txt'
        self.path.write_text('\f'.join(['Synthetic page'] * 15 + [SYNTHETIC_PAGE,'Synthetic page 17']) + '\f')
        self.path_patch = patch.object(server, 'CHAT_GUIDANCE_PATH', self.path)
        self.pin_patch = patch.object(server, 'TIP_GUIDANCE_PAGE_SHA256',
                                      hashlib.sha256(SYNTHETIC_PAGE.encode()).hexdigest())
        core_pages={2,3,4,5,6,7,8,9,10,12,13,16,17}
        pages=['Synthetic page'] * 15 + [SYNTHETIC_PAGE,'Synthetic page 17']
        digest=hashlib.sha256('\f'.join(pages[n-1] for n in sorted(core_pages)).encode()).hexdigest()
        self.review_pin_patch=patch.object(server,'REVIEW_GUIDANCE_PAGES_SHA256',digest)
        self.path_patch.start()
        self.pin_patch.start()
        self.review_pin_patch.start()

    def tearDown(self):
        self.review_pin_patch.stop()
        self.pin_patch.stop()
        self.path_patch.stop()
        self.temp.cleanup()

    def check(self, **changes):
        data = dict(subtotal='100.00', charge_amount='11.00', charge_kind='tip',
                    jurisdiction='us_outside_nyc', event_date='2026-03-01',
                    base_confirmed=True, charge_confirmed=True)
        data.update(changes)
        return server.guidance_tip_check(server.GuidanceTipCheckRequest(**data))

    def test_threshold_comes_from_pinned_source_and_boundary_is_exact(self):
        result = self.check()
        self.assertEqual(result['status'], 'within_limit')
        self.assertEqual(result['threshold_percent'], 11)
        self.assertEqual(result['citations'][0]['page'], 16)
        self.assertEqual(self.check(charge_amount='11.01')['status'], 'over_limit')

    def test_nyc_included_exception_requires_explicit_bill_status(self):
        self.assertEqual(self.check(jurisdiction='nyc', charge_amount='12.00')['status'], 'needs_review')
        self.assertEqual(self.check(jurisdiction='nyc', charge_amount='12.00',
                                    nyc_included_on_bill=False)['status'], 'over_limit')
        result = self.check(jurisdiction='nyc', charge_amount='12.00', nyc_included_on_bill=True)
        self.assertEqual(result['status'], 'within_limit')
        self.assertEqual(result['threshold_percent'], 13)

    def test_dates_context_and_ambiguous_charge_fail_closed(self):
        self.assertEqual(self.check(event_date='2025-10-01')['status'], 'within_limit')
        self.assertEqual(self.check(event_date='2026-09-30')['status'], 'within_limit')
        for kwargs in (dict(event_date='2025-09-30'), dict(event_date='2026-10-01'),
                       dict(event_date='2026-02-30'), dict(event_date=''),
                       dict(jurisdiction='overseas'), dict(jurisdiction='unknown'),
                       dict(base_confirmed=False), dict(charge_confirmed=False),
                       dict(charge_kind='service_charge'), dict(charge_kind='unknown'),
                       dict(subtotal='0'), dict(subtotal=None), dict(charge_amount=None),
                       dict(printed_percent='15')):
            with self.subTest(kwargs=kwargs):
                self.assertEqual(self.check(**kwargs)['status'], 'needs_review')

    def test_missing_or_changed_source_fails_closed(self):
        self.path.write_text('\f'.join(['changed'] * 17) + '\f')
        self.assertEqual(self.check()['status'], 'needs_review')
        self.path.unlink()
        with self.assertRaises(HTTPException) as error:
            self.check()
        self.assertEqual(error.exception.status_code, 503)

    def test_event_review_uses_source_citations_and_never_allocates(self):
        mock_answer = {'items': [
            {'index': 0, 'classification': 'NOT_ALLOWABLE', 'rationale': 'Possible issue',
             'evidence_refs': ['E16'], 'questions': []},
            {'index': 1, 'classification': 'K_FUND_ALLOWABLE', 'rationale': 'Unsupported',
             'evidence_refs': ['E16'], 'questions': []},
            {'index': 2, 'classification': 'NOT_ALLOWABLE', 'rationale': 'Service',
             'evidence_refs': ['E16'], 'questions': []},
            {'index': 3, 'classification': 'NOT_ALLOWABLE', 'rationale': 'No source',
             'evidence_refs': ['E999'], 'questions': []},
        ]}
        body = server.AnalyzeRequest(foreign_guests=1,total_guests=2,
            actual_usg_guests=0,actual_non_usg_guests=2,case_id='synthetic-case',
            function_type='reception',items=[
            server.Item(description='Possible issue',amount='1.00'),
            server.Item(description='Regular item',amount='2.00'),
            server.Item(description='Service charge',amount='3.00'),
            server.Item(description='Unsupported item',amount='4.00')])
        with patch.object(server,'ask_model',return_value=mock_answer) as model:
            response=server.analyze(body)
        self.assertEqual(response['guidance_source'],'fy2026_guidance')
        self.assertEqual([i['classification'] for i in response['items']],
                         ['NOT_ALLOWABLE','LEGAL_REVIEW','LEGAL_REVIEW','LEGAL_REVIEW'])
        self.assertEqual(response['items'][0]['citations'][0]['page'],16)
        self.assertEqual(response['totals']['pending'],10)
        self.assertEqual(response['totals']['k_fund'],0)
        self.assertEqual(response['totals']['other'],0)
        self.assertIn('[E16]',model.call_args.args[1])
        model_input=model.call_args.args[1]
        payload=json.loads(model_input.split('Event and line items:\n',1)[1].split('\n\nGuidance:\n',1)[0])
        self.assertEqual(payload['foreign_guests'],1)
        self.assertEqual(payload['actual_non_usg_guests'],2)
        self.assertEqual(payload['actual_usg_guests'],0)
        self.assertEqual(payload['function_type'],'reception')
        self.assertNotIn('case_id',payload)

    def test_no_guidance_does_not_call_model_or_fallback(self):
        self.path.unlink()
        body=server.AnalyzeRequest(foreign_guests=0,total_guests=1,
                                   items=[server.Item(description='Meal',amount='10')])
        with patch.object(server,'ask_model') as model:
            with self.assertRaises(HTTPException) as error:
                server.analyze(body)
            self.assertEqual(error.exception.status_code,503)
            model.assert_not_called()

    def test_changed_policy_page_blocks_event_analysis(self):
        pages=['Synthetic page'] * 15 + [SYNTHETIC_PAGE,'Synthetic page 17']
        pages[3]='Changed policy page'
        self.path.write_text('\f'.join(pages)+'\f')
        body=server.AnalyzeRequest(foreign_guests=0,total_guests=1,
                                   items=[server.Item(description='Meal',amount='10')])
        with patch.object(server,'ask_model') as model:
            with self.assertRaises(HTTPException) as error:
                server.analyze(body)
            self.assertEqual(error.exception.status_code,503)
            model.assert_not_called()

    def test_unknown_guest_counts_remain_unknown_and_zero_is_preserved(self):
        body=server.AnalyzeRequest(items=[server.Item(description='Meal',amount='10')])
        with patch.object(server,'ask_model',return_value={'items':[
            {'index':0,'classification':'LEGAL_REVIEW','rationale':'Review',
             'questions':[],'evidence_refs':['E2']}]}) as model:
            result=server.analyze(body)
        payload=json.loads(model.call_args.args[1].split('Event and line items:\n',1)[1].split('\n\nGuidance:\n',1)[0])
        self.assertIsNone(payload['foreign_guests'])
        self.assertIsNone(payload['total_guests'])
        self.assertIsNone(result['foreign_guests'])
        self.assertIsNone(result['total_guests'])
        self.assertIsNone(result['per_person']['per_person_cost'])
        self.assertEqual(server.AnalyzeRequest(foreign_guests=0,total_guests=None,
                         items=[server.Item(description='Meal',amount='10')]).foreign_guests,0)
        with self.assertRaises(ValueError):
            server.AnalyzeRequest(foreign_guests=2,total_guests=1,
                                  items=[server.Item(description='Meal',amount='10')])

    @staticmethod
    def model_payload(text):
        return json.loads(text.split('Event and line items:\n',1)[1].split('\n\nGuidance:\n',1)[0])

    @staticmethod
    def valid_rows(items):
        return {'items':[{'index':item['index'],'classification':'LEGAL_REVIEW',
                          'rationale':'Review this item','questions':[],
                          'evidence_refs':['E2']} for item in items]}

    def test_full_receipt_batches_preserve_context_and_original_order(self):
        body=server.AnalyzeRequest(items=[server.Item(description=f'Item {i}',amount='1')
                                          for i in range(18)])
        def fake(_prompt,text,**kwargs):
            payload=self.model_payload(text)
            self.assertEqual(len(payload['receipt_context']),18)
            self.assertLessEqual(len(payload['items']),4)
            self.assertEqual(kwargs['timeout'],45)
            self.assertEqual(kwargs['max_retries'],0)
            return self.valid_rows(list(reversed(payload['items'])))
        with patch.object(server,'ask_model',side_effect=fake) as model:
            response=server.analyze(body)
        self.assertEqual(model.call_count,5)
        self.assertEqual([row['description'] for row in response['items']],
                         [f'Item {i}' for i in range(18)])
        self.assertEqual(response['totals']['pending'],18)
        self.assertFalse(response['analysis_incomplete'])
        self.assertTrue(all(row['citations'][0]['page']==2 for row in response['items']))

    def test_incomplete_batch_is_split_once_and_recovers(self):
        body=server.AnalyzeRequest(items=[server.Item(description=f'Item {i}',amount='1')
                                          for i in range(4)])
        def fake(_prompt,text,**kwargs):
            items=self.model_payload(text)['items']
            if len(items)>2:
                self.assertEqual(kwargs['timeout'],45)
                return {'items':[]}
            self.assertEqual(kwargs['timeout'],20)
            return self.valid_rows(items)
        with patch.object(server,'ask_model',side_effect=fake) as model:
            response=server.analyze(body)
        self.assertEqual(model.call_count,3)
        self.assertFalse(response['analysis_incomplete'])
        self.assertEqual(len(response['items']),4)

    def test_partial_timeout_keeps_successes_and_marks_failed_items(self):
        body=server.AnalyzeRequest(items=[server.Item(description=f'Item {i}',amount='1')
                                          for i in range(8)])
        def fake(_prompt,text,**kwargs):
            items=self.model_payload(text)['items']
            if items[0]['index']>=4:
                raise HTTPException(504,'Synthetic timeout')
            return self.valid_rows(items)
        with patch.object(server,'ask_model',side_effect=fake) as model:
            result=server.analyze(body)
        self.assertEqual(model.call_count,4)
        self.assertTrue(result['analysis_incomplete'])
        self.assertEqual(result['unreviewed_item_count'],4)
        self.assertIn('did not complete',result['note'])
        self.assertTrue(all(row['citations'] for row in result['items'][:4]))
        self.assertTrue(all(not row['citations'] and 'did not complete' in row['rationale']
                            for row in result['items'][4:]))
        self.assertEqual(result['totals']['pending'],8)

    def test_all_failed_batches_surface_error_without_inventing_results(self):
        body=server.AnalyzeRequest(items=[server.Item(description=f'Item {i}',amount='1')
                                          for i in range(8)])
        with patch.object(server,'ask_model',side_effect=HTTPException(503,'Unavailable')) as model:
            with self.assertRaises(HTTPException) as error:
                server.analyze(body)
        self.assertEqual(error.exception.status_code,503)
        self.assertEqual(model.call_count,2)

    def test_invalid_classification_and_citation_fields_are_safe(self):
        body=server.AnalyzeRequest(items=[server.Item(description='Meal',amount='1')])
        with patch.object(server,'ask_model',return_value={'items':[{
            'index':0,'classification':['unexpected'],'evidence_refs':{'bad':'value'}}]}):
            result=server.analyze(body)
        self.assertEqual(result['items'][0]['classification'],'LEGAL_REVIEW')
        self.assertEqual(result['items'][0]['citations'],[])


if __name__ == '__main__':
    unittest.main()
