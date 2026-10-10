"""Source-bound narrative transcription and live HTML table extraction."""
import re
from .sources import ROOT, ingest, table, paragraph, source_location, load_json, digest

FIELDS = '''authors year country centers design recruitment_period N_total train_N validation_N external_validation_N inclusion_criteria exclusion_criteria population subtype stage age regimen endpoint endpoint_definition pCR_definition responder_N nonresponder_N prevalence reference_standard reference_timing surgery ultrasound SWE CEUS QUS scanner timepoints image_count segmentation segmentation_dimension operator_count operator_expertise interobserver_assessment segmentation_software radiomics_software initial_features feature_families preprocessing normalization discretization feature_robustness feature_selection final_features model_types comparator algorithm tuning cv_strategy validation_type'''.split()
METRICS = ['AUC','sensitivity','specificity','accuracy','precision','recall','F1','PPV','NPV','calibration','Brier','decision_curve','threshold']

def parse_auc(text):
    nums = re.findall(r'\d+\.\d+', text)
    if not nums:
        return 'NR','NR','NR'
    return float(nums[0]), float(nums[1]) if len(nums)>1 else 'NR', float(nums[2]) if len(nums)>2 else 'NR'

def extract(records=None):
    papers=[]
    for record in records or ingest():
        p = {f: record['fields'].get(f,{}).get('value','NR') for f in FIELDS}
        p.update({f:item['value'] for f,item in record['fields'].items()})
        p.update({k:record[k] for k in ['study_id','doi','year','title','source_url','endpoint_code','semantic','issues']})
        p['source_access']='Archived primary full text; identity and SHA-256 verified'
        p['provenance']={k:v['evidence'] for k,v in record['fields'].items()}
        p['performance']=[]
        for spec in record['model_specs']:
            rows=table(spec['file'],spec['table'])
            r,c=spec['row'],spec['column']
            auc,lo,hi=parse_auc(rows[r][c])
            m={**spec, 'study_id':p['study_id'],'endpoint':p['endpoint_code'], 'AUC':auc,'CI_low':lo,'CI_high':hi,
               'extraction_status':'VERIFIED_TRANSCRIPTION', 'source_section':'Results', 'source_table':f"Table {spec['table']}",
               'source_identifier':source_location(record,spec),'raw_auc':rows[r][c]}
            if spec['layout']=='auc_row':
                m.update(zip(['sensitivity','specificity','accuracy'],map(float,rows[r][c+1:c+4])))
            elif spec['layout']=='wu_row':
                m['accuracy']=parse_auc(rows[r][c-2])[0]
            elif spec['layout']=='metric_columns':
                for index,key in [(3,'accuracy'),(4,'sensitivity'),(5,'specificity'),(6,'precision'),(7,'recall'),(8,'F1')]:
                    m[key]=float(rows[index][c])
            elif spec['layout']=='algorithm_columns':
                for index,key in [(2,'accuracy'),(3,'sensitivity'),(4,'specificity'),(5,'PPV'),(6,'NPV')]:m[key]=float(rows[index][c])
            p['performance'].append(m)
        for item in record.get('narrative_performance',[]):
            m={**item,'study_id':p['study_id'],'endpoint':p['endpoint_code'],'CI_low':'NR','CI_high':'NR',
               'source_section':item['evidence']['section'],'source_table':'Results prose; Table 3 for main model pairs',
               'source_identifier':source_location(record,item['evidence']),'extraction_status':'VERIFIED_TRANSCRIPTION'}
            p['performance'].append(m)
        for item in record.get('missing_models',[]):
            p['performance'].append({**item,'study_id':p['study_id'],'endpoint':p['endpoint_code'],'CI_low':'NR','CI_high':'NR',
                'extraction_status':'REVIEW_REQUIRED','source_section':'Abstract / Results / Table 3',
                'source_table':'Table 3','source_identifier':p['source_url']+' | Validation values not explicitly tabulated'})
        # Exact counts are a transparent derivation, not an inferred patient count.
        if isinstance(p['responder_N'],int):
            p['prevalence']=round(p['responder_N']/p['N_total'],6)
        for m in p['performance']:
            key=f"AUC:{m['model_id']}:{m['dataset_role']}"
            if any(issue['field']==key for issue in p['issues']):m['extraction_status']='REVIEW_REQUIRED'
            for metric in METRICS:m.setdefault(metric,'NR')
            m['metric_provenance']={}
            if p['study_id']=='FRONTIERS_2024' and m['model_id']=='GBM radiomics':
                number=2 if m['dataset_role']=='training' else 3
                rows=table('FRONTIERS_2024.html',number)
                for index,key in [(5,'PPV'),(6,'NPV')]:
                    m[key]=float(rows[index][8])
                    m['metric_provenance'][key]=dict(file='FRONTIERS_2024.html',table=number,row=index,column=8,
                        section='Results / Table '+str(number),excerpt=rows[index][8])
            if p['study_id']=='YANG_2022' and m['model_id'].startswith('Nomogram'):
                m['calibration']='Hosmer–Lemeshow p='+('0.11' if m['dataset_role']=='training' else '0.75')+'; calibration curves'
                m['metric_provenance']['calibration']=p['provenance']['calibration']
            elif p['study_id'] in ('WU_2025','FRONTIERS_2024'):
                for metric in ('calibration','decision_curve'):
                    m[metric]=p.get(metric,'NR')
                    if metric in p['provenance']:m['metric_provenance'][metric]=p['provenance'][metric]
            if m['model_id']=='GBM clinical+radiomics' and m['dataset_role']=='internal_validation':
                m['extraction_status']='REVIEW_REQUIRED' # sensitivity/recall inconsistency; AUC itself agrees.
        papers.append(p)
    for item in load_json(ROOT/'inputs'/'reviewed_intervals.json'):
        if digest((ROOT/'sources'/item['file']).read_bytes())!=item['sha256']:
            raise ValueError('Reviewed interval figure changed')
        m=next(m for p in papers for m in p['performance'] if (m['study_id'],m['model_id'],m['dataset_role'])==
               (item['study_id'],item['model_id'],item['dataset_role']))
        lo,hi=item['CI_low'],item['CI_high']
        m['reported_figure_CI']=f'{lo}–{hi}'
        m['CI_source']=item['source']
        if 0<=lo<=m['AUC']<=hi<=1:m.update(CI_low=lo,CI_high=hi)
        else:m['extraction_status']='REVIEW_REQUIRED'
    return papers

def provenance(papers):
    rows=[]
    for p in papers:
        for field,ev in p['provenance'].items():
            rows.append(dict(study_id=p['study_id'],variable=field,value=p.get(field,'NR'),source_section=ev['section'],
              source_table=f"Table {ev['table']}" if 'table' in ev else 'NR',source_excerpt=ev['excerpt'],source_identifier=source_location(p,ev)))
        for m in p['performance']:
            for metric in METRICS:
                if m[metric]=='NR':continue
                ev=m.get('metric_provenance',{}).get(metric)
                rows.append(dict(study_id=p['study_id'],variable=f"{metric}:{m['model_id']}:{m['dataset_role']}",value=m[metric],
                    source_section=ev['section'] if ev else m['source_section'],source_table=f"Table {ev['table']}" if ev and 'table' in ev else 'NR' if ev else m['source_table'],
                    source_excerpt=ev['excerpt'] if ev else str(m.get('raw_auc',m[metric])),
                    source_identifier=source_location(p,ev) if ev else m['source_identifier']))
            for bound in ['CI_low','CI_high']:
                if m[bound]!='NR':
                    rows.append(dict(study_id=p['study_id'],variable=f"{bound}:{m['model_id']}:{m['dataset_role']}",value=m[bound],
                        source_section='Figure 5A/B' if 'CI_source' in m else m['source_section'],
                        source_table='NR' if 'CI_source' in m else m['source_table'],source_excerpt=str(m.get('reported_figure_CI',m.get('raw_auc',''))),
                        source_identifier=m.get('CI_source',m['source_identifier'])))
        if isinstance(p['prevalence'],float):
            rows.append(dict(study_id=p['study_id'],variable='prevalence_derived',value=p['prevalence'],source_section='Derived from verified counts',
              source_table='NR',source_excerpt=f"{p['responder_N']} / {p['N_total']}",source_identifier=p['source_url']))
    return rows
