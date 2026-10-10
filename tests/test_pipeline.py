import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src import pipeline
from src.extraction import extract
from src.validation import validate,contract,bounded_review
from src.analysis import classify,poolability

class PipelineContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.papers=extract()
    def test_each_performance_has_dataset_timepoint_endpoint_and_source(self):
        for m in pipeline.performance_rows(self.papers):
            self.assertTrue(all(m.get(k) for k in ['study_id','model_id','endpoint','dataset_role','timepoint_role','source_identifier']))
    def test_metric_rows_keep_dataset_and_timepoint(self):
        self.assertTrue(all(r['dataset_role'] and r['timepoint_role'] and r['source_identifier'] for r in pipeline.metric_rows(self.papers)))
    def test_all_ten_zhou_radiomics_algorithms_have_both_reported_roles(self):
        paper=next(p for p in self.papers if p['study_id']=='FRONTIERS_2024')
        for role in ['training','internal_validation']:
            models=[m for m in paper['performance'] if m['model_type']=='radiomics-only' and m['dataset_role']==role]
            self.assertEqual(len(models),10)
            self.assertTrue(all(m['AUC']!='NR' and m['PPV']!='NR' and m['NPV']!='NR' for m in models))
    def test_endpoint_definitions_present(self):
        self.assertTrue(all(p['endpoint_definition']!='NR' for p in self.papers))
    def test_known_auc_provenance_has_one_row_per_model_and_role(self):
        known=[m for m in pipeline.performance_rows(self.papers) if m['AUC']!='NR']
        prov=[r for r in pipeline.provenance_rows(self.papers) if r['variable'].startswith('AUC:')]
        self.assertEqual(len(known),len(prov))
    def test_independent_source_parser_detects_changed_auc(self):
        papers=copy.deepcopy(self.papers);papers[0]['performance'][0]['AUC']=.700
        check=next(r for r in validate(papers) if r['field']=='AUC:RS1:training')
        self.assertEqual(check['status'],'REVIEW_REQUIRED');self.assertEqual(check['validator_value'],.722)
    def test_independent_labelled_source_parser_detects_swapped_split(self):
        papers=copy.deepcopy(self.papers);papers[0]['train_N'],papers[0]['validation_N']=65,152
        checks=validate(papers)
        self.assertTrue(any(r['field']=='train_N' and r['status']=='REVIEW_REQUIRED' for r in checks))
    def test_nr_stays_nr(self):
        wang=next(p for p in self.papers if p['study_id']=='WANG_2025')
        self.assertTrue(all(m['AUC']=='NR' for m in wang['performance'] if m['dataset_role']=='internal_validation'))
    def test_missing_comparators_remain_indeterminate(self):
        for r in pipeline.incremental_rows(self.papers):
            if r['model_a']=='NR':self.assertEqual((r['classification'],r['delta_AUC']),('Indeterminate','NR'))
    def test_training_is_not_demonstrated_or_suggestive(self):
        self.assertEqual(classify(.9,.7,'training',dict(verified=True,p_value=.01)),'Indeterminate')
    def test_non_significant_direct_test_is_not_demonstrated(self):
        self.assertEqual(classify(.9,.7,'internal_validation',dict(verified=True,p_value=.08)),'Not demonstrated')
    def test_no_pooling_for_incompatible_joint_strata(self):
        decision,rows=poolability(self.papers)
        self.assertEqual(decision['poolability'],'not justified');self.assertFalse(decision['forest_plot_produced'])
        self.assertTrue(all(r['study_count']==1 for r in rows))
    def test_partial_poolability_can_be_reached_by_compatible_inputs(self):
        papers=copy.deepcopy(self.papers[:1]);other=copy.deepcopy(papers[0]);other['study_id']='TEST_INDEPENDENT_STUDY';papers.append(other)
        extra=copy.deepcopy(self.papers[3]);papers.append(extra)
        result,_=poolability(papers)
        self.assertEqual(result['poolability'],'partially justified')
    def test_review_terminates_without_new_evidence(self):
        result=bounded_review(['A','A','B','C'])
        self.assertEqual(result['attempts'],1);self.assertEqual(result['status'],'REVIEW_REQUIRED')
        self.assertEqual(bounded_review(['A','B','C','D'])['attempts'],3)
    def test_freeze_is_immutable_and_benchmark_exposure_honest(self):
        with tempfile.TemporaryDirectory() as d,patch.object(pipeline,'OUT',Path(d)):
            first=pipeline.freeze_synthesis(self.papers)
            original=(Path(d)/'synthesis_frozen.json').read_bytes()
            pipeline.freeze_synthesis(self.papers)
            self.assertEqual(len(list((Path(d)/'freezes').glob('*.json'))),1)
            altered=copy.deepcopy(self.papers);altered[0]['issues'].append(dict(field='test',reason='synthetic',impact='test'))
            pipeline.freeze_synthesis(altered)
            self.assertEqual(len(list((Path(d)/'freezes').glob('*.json'))),2)
            self.assertIn(original,[f.read_bytes() for f in (Path(d)/'freezes').glob('*.json')])
            self.assertTrue(first['previous_benchmark_exposure']);self.assertFalse(first['benchmark_consulted_in_this_primary_run'])
    def test_contract_rejects_invalid_metric_association(self):
        papers=copy.deepcopy(self.papers);papers[0]['performance'][0]['dataset_role']=''
        with self.assertRaises(ValueError):contract(papers,pipeline.comparability_detail_rows(self.papers),pipeline.comparability_rows(self.papers),pipeline.incremental_rows(self.papers))
    def test_contract_rejects_false_demonstrated_claim(self):
        rows=pipeline.incremental_rows(self.papers);rows[0]['classification']='Demonstrated'
        with self.assertRaises(ValueError):contract(self.papers,pipeline.comparability_detail_rows(self.papers),pipeline.comparability_rows(self.papers),rows)
    def test_source_disagreement_blocks_delivery(self):
        papers=copy.deepcopy(self.papers);papers[0]['performance'][0]['AUC']=.700
        with self.assertRaises(ValueError):
            contract(papers,pipeline.comparability_detail_rows(papers),pipeline.comparability_rows(papers),pipeline.incremental_rows(papers),validate(papers))

if __name__=='__main__':unittest.main()
