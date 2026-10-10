import copy
import csv
import hashlib
import json
import unittest
from pathlib import Path
from bs4 import BeautifulSoup
from src import pipeline
from src.extraction import extract
from src.analysis import compare
from src.sources import ROOT,OUT,digest

class SemanticComparabilityAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.papers=extract();cls.detail=pipeline.comparability_detail_rows(cls.papers)
    def pair(self,a,b,c):return next(r for r in self.detail if (r['study_a'],r['study_b'],r['criterion'])==(a,b,c))
    def test_lexical_population_difference_does_not_force_mismatch(self):
        self.assertEqual(self.pair('YANG_2022','WU_2025','population')['status'],'partially_aligned')
    def test_case_mix_overlap_is_partial_not_full_distribution_equivalence(self):
        self.assertEqual(self.pair('WU_2025','FRONTIERS_2024','subtype')['status'],'partially_aligned')
    def test_missing_subtype_is_unavailable(self):
        a,b=copy.deepcopy(self.papers[:2]);a['subtype']='NR';a['semantic']['subtype']=[]
        self.assertEqual(compare('subtype',a,b)[2],'unavailable')
    def test_documented_disjoint_subtype_can_be_not_aligned(self):
        a,b=copy.deepcopy(self.papers[:2]);a['subtype']='TNBC only';a['semantic']['subtype']=['TNBC'];b['subtype']='Luminal only';b['semantic']['subtype']=['luminal']
        self.assertEqual(compare('subtype',a,b)[2],'not_aligned')
    def test_reassessing_population_does_not_change_other_criteria(self):
        before=pipeline.comparability_detail_rows(self.papers);papers=copy.deepcopy(self.papers);papers[0]['population']='NR'
        after=pipeline.comparability_detail_rows(papers)
        self.assertEqual([r for r in before if r['criterion']!='population'],[r for r in after if r['criterion']!='population'])
    def test_shared_baseline_acquisition_is_partial_despite_different_model_timing(self):
        self.assertEqual(self.pair('WU_2025','FRONTIERS_2024','timepoint')['status'],'partially_aligned')
        self.assertEqual(pipeline.assess_poolability(self.papers)[0],'not justified')
    def test_csv_report_and_module_results_agree(self):
        with (OUT/'incremental_value.csv').open() as f:rows=list(csv.DictReader(f))
        source=BeautifulSoup((OUT/'evidence_synthesis_report.html').read_text(),'html.parser')
        embedded=json.loads(source.find(id='reviewed-results').string)
        self.assertEqual(rows,embedded['incremental_value'])
        module=pipeline.incremental_rows(self.papers)
        self.assertEqual([r['classification'] for r in rows],[r['classification'] for r in module])
        self.assertEqual([r['delta_AUC'] for r in rows],[str(r['delta_AUC']) for r in module])
    def test_benchmark_freeze_hash_and_event_order(self):
        state=json.loads((OUT/'benchmark_state.json').read_text())
        self.assertEqual(state['primary_freeze_sha256'],digest((OUT/'synthesis_frozen.json').read_bytes()))
        stages=json.loads((OUT/'pipeline_stages.json').read_text())
        self.assertLess(stages.index('synthesis freeze'),stages.index('benchmark'));self.assertTrue(state['synthesis_unchanged'])
    def test_historical_freeze_intact(self):
        historical=ROOT.parent/'breast_nac_ultrasound_radiomics/outputs/synthesis_frozen.json'
        self.assertEqual(digest(historical.read_bytes()),digest((ROOT/'archive/historical_synthesis_frozen.json').read_bytes()))

if __name__=='__main__':unittest.main()
