import copy
import unittest
from src import pipeline
from src.extraction import extract
from src.analysis import summarize_pair,classify

class ComparabilityCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.papers=extract()
    def test_unavailable_is_not_mismatch(self):
        a,b=copy.deepcopy(self.papers[:2]);a['regimen']='NR'
        self.assertEqual(pipeline._comparison_status('regimen',a,b)[2],'unavailable')
    def test_denominator_excludes_unavailable(self):
        detail=pipeline.comparability_detail_rows(self.papers)
        for pair in pipeline.comparability_rows(self.papers):
            rows=[r for r in detail if r['study_a']==pair['study_a'] and r['study_b']==pair['study_b']]
            self.assertEqual(pair['evaluated_criteria'],sum(r['status']!='unavailable' for r in rows))
    def test_zero_denominator_has_no_low_rating(self):
        result=summarize_pair([dict(status='unavailable',criterion='regimen',reason='NR')])
        self.assertEqual((result['alignment_score'],result['rating'],result['evaluated_criteria']),('NR','NR',0))
    def test_nine_unique_criteria_for_six_pairs(self):
        detail=pipeline.comparability_detail_rows(self.papers)
        self.assertEqual(len(detail),54);self.assertEqual(len({(r['study_a'],r['study_b'],r['criterion']) for r in detail}),54)
    def test_wu_and_frontiers_share_pcr_category_with_caveat(self):
        r=next(r for r in pipeline.comparability_detail_rows(self.papers) if r['study_a']=='WU_2025' and r['criterion']=='endpoint_definition')
        self.assertEqual(r['status'],'aligned');self.assertIn('REVIEW_REQUIRED',r['reason'])

class IncrementalCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.rows=pipeline.incremental_rows()
    def row(self,study,start):return next(r for r in self.rows if r['study_id']==study and r['comparison'].startswith(start) and r['primary'])
    def test_yang_validation_priority(self):
        r=self.row('YANG_2022','D ');self.assertEqual((r['dataset_role'],r['delta_AUC'],r['classification']),('internal_validation',.068,'Suggestive'))
        self.assertIn('early-treatment vs baseline',r['timepoint_role'])
    def test_verified_reference_deltas(self):
        for study,start,expected in [('WU_2025','G fusion vs clinical',.211),('WU_2025','G fusion vs radiomics',.055),
           ('FRONTIERS_2024','C ',.131),('FRONTIERS_2024','G ',.165)]:self.assertAlmostEqual(self.row(study,start)['delta_AUC'],expected)
    def test_wu_table_delta_is_not_legacy_mixed_source_delta(self):
        self.assertEqual(self.row('WU_2025','G fusion vs deep learning')['delta_AUC'],.043)
    def test_frontiers_direct_validation_figure_tests(self):
        for prefix,pv in [('C ',.010),('G ',.005)]:
            r=self.row('FRONTIERS_2024',prefix);self.assertEqual(r['p_value'],pv);self.assertEqual(r['classification'],'Demonstrated');self.assertIn('5H',r['source'])
    def test_wang_no_borrowed_training_test_for_validation(self):
        r=self.row('WANG_2025','C ');self.assertEqual((r['delta_AUC'],r['p_value'],r['classification']),('NR','NR','Indeterminate'))
    def test_yang_delta_training_test_is_secondary(self):
        r=next(r for r in self.rows if r['study_id']=='YANG_2022' and r['comparison'].startswith('E ') and r['dataset_role']=='training')
        self.assertEqual(r['classification'],'Not demonstrated');self.assertFalse(r['primary']);self.assertEqual(r['p_value'],.086)
    def test_demonstrated_needs_exact_verified_favorable_contrast(self):
        for r in self.rows:
            if r['classification']=='Demonstrated':
                self.assertTrue(r['test_verified']);self.assertLess(r['p_value'],.05);self.assertGreater(r['delta_AUC'],0);self.assertNotEqual(r['dataset_role'],'training')

if __name__=='__main__':unittest.main()
