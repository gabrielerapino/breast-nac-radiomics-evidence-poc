"""Transparent comparison rules, matched contrasts and joint pooling strata."""
from itertools import combinations

CRITERIA=('endpoint_definition','regimen','timepoint','imaging_modality','radiomics_strategy','comparator','validation','population','subtype')
WEIGHTS={'aligned':1,'partially_aligned':.5,'not_aligned':0}
ROLES={'external_validation':0,'internal_validation':1,'test':2,'training':3}

def available(value):
    return value is not None and str(value).strip().lower() not in {'','nr','not reported','unclear','unknown','none'}

def compare(criterion,a,b):
    fields={'endpoint_definition':'endpoint_definition','regimen':'regimen','timepoint':'timepoints','imaging_modality':'ultrasound',
      'radiomics_strategy':'model_types','comparator':'comparator','validation':'validation_type','population':'population','subtype':'subtype'}
    va,vb=a.get(fields[criterion],'NR'),b.get(fields[criterion],'NR')
    if not available(va) or not available(vb):return va,vb,'unavailable','Source descriptions are missing or insufficient; criterion excluded from denominator.'
    if criterion=='endpoint_definition':
        if a['endpoint_code']!=b['endpoint_code']:
            return va,vb,'not_aligned',f"Different targets: {a['endpoint_code']} versus {b['endpoint_code']}; binary coding does not make them equivalent."
        return va,vb,'aligned','Both target pCR/non-pCR and describe no invasive breast/nodal disease; Wu operational Methods wording remains REVIEW_REQUIRED.'
    key={'timepoint':'acquisition_roles','imaging_modality':'modalities','radiomics_strategy':'strategy','comparator':'comparators','validation':'validation'}.get(criterion,criterion)
    aa,bb=a['semantic'].get(key),b['semantic'].get(key)
    if not aa or not bb:return va,vb,'unavailable','The primary source does not support enough detail for this semantic comparison.'
    if criterion=='population':
        if aa!=bb:return va,vb,'not_aligned','Different disease or treatment settings are documented.'
        return va,vb,'partially_aligned','Both include breast cancer patients receiving NAC; requirements for completed therapy, surgery, image availability and disease spectrum differ or are incompletely reported.'
    aa,bb=set(aa),set(bb)
    if criterion=='subtype':
        if aa&bb:
            return va,vb,'partially_aligned','Both include hormone-receptor, HER2 and triple-negative categories; exact distributions differ or are incompletely reliable. No subtype restriction is established.'
        return va,vb,'not_aligned','Documented molecular subtype categories do not overlap.'
    reasons={
       'regimen':'Anthracycline/taxane classes overlap; cycle counts and targeted therapies differ.',
       'timepoint':'Some imaging roles overlap, but available baseline, early, delta or midpoint information differs.',
       'imaging_modality':'B-mode overlaps; additional Doppler/SWE/CEUS acquisitions differ.',
       'radiomics_strategy':'Radiomics overlaps; fusion and deep learning components differ.',
       'comparator':'Comparator sets overlap in part; a clinical+ultrasound model is distinct from clinical-only.',
       'validation':'Internal holdout overlaps; external-center validation is available in only one study.'}
    if aa==bb:
        if criterion=='regimen':return va,vb,'partially_aligned',reasons[criterion]
        return va,vb,'aligned','The source-supported '+criterion.replace('_',' ')+' categories match; original descriptions are retained.'
    if aa&bb:return va,vb,'partially_aligned',reasons[criterion]
    return va,vb,'not_aligned','No shared source-supported '+criterion.replace('_',' ')+' role. Original definitions document different categories.'

def detail_rows(papers):
    rows=[]
    for a,b in combinations(papers,2):
        for c in CRITERIA:
            va,vb,status,reason=compare(c,a,b)
            rows.append(dict(study_a=a['study_id'],study_b=b['study_id'],criterion=c,value_a=va,value_b=vb,status=status,reason=reason))
    return rows

def summarize_pair(rows):
    evaluated=[r for r in rows if r['status']!='unavailable']
    points=sum(WEIGHTS[r['status']] for r in evaluated)
    score=points/len(evaluated) if evaluated else None
    rating=None if score is None else 'high' if score>=.75 else 'moderate' if score>=.5 else 'low'
    reason=f"{points:g}/{len(evaluated)} evaluable criteria; unavailable excluded. "
    reason+='; '.join(r['criterion']+': '+r['reason'] for r in rows if r['status'] in ('not_aligned','unavailable'))
    if score is None:reason+='No evaluable criterion; no rating assigned.'
    return dict(alignment_score=round(score,6) if score is not None else 'NR',evaluated_criteria=len(evaluated),rating=rating or 'NR',reason=reason)

def pair_rows(detail):
    keys=list(dict.fromkeys((r['study_a'],r['study_b']) for r in detail))
    return [dict(study_a=a,study_b=b,**summarize_pair([r for r in detail if (r['study_a'],r['study_b'])==(a,b)])) for a,b in keys]

def classify(auc_a,auc_b,role,test=None):
    if not isinstance(auc_a,(int,float)) or not isinstance(auc_b,(int,float)):return 'Indeterminate'
    if auc_a<=auc_b:return 'Not demonstrated'
    if test and test.get('verified') and test.get('p_value')>=.05:return 'Not demonstrated'
    if role=='training':return 'Indeterminate'
    if test and test.get('verified') and test.get('p_value')<.05:return 'Demonstrated'
    return 'Suggestive'

def incremental(papers,tests):
    rows=[];coverage=[]
    contrasts={
      'YANG_2022':[('D early vs baseline radiomics','RS2','RS1'),('E delta vs baseline radiomics','Delta RS','RS1'),
        ('G nomogram vs baseline radiomics','Nomogram RS1+RS2+Ki-67','RS1'),('G nomogram vs early radiomics','Nomogram RS1+RS2+Ki-67','RS2')],
      'WANG_2025':[('C combined vs clinical+ultrasound','Model_Combined','Model_Clinic'),('G combined vs radiomics','Model_Combined','Model_RSA'),
        ('D early vs baseline radiomics','RSA early','RSA baseline'),('E delta vs baseline radiomics','RSA delta','RSA baseline')],
      'WU_2025':[('A radiomics vs clinical-only','Radiomics','Clinical'),('G fusion vs clinical','Fusion','Clinical'),
        ('G fusion vs radiomics','Fusion','Radiomics'),('G fusion vs deep learning','Fusion','Deep learning')],
      'FRONTIERS_2024':[('A radiomics vs clinical-only','GBM radiomics','GBM clinical'),
        ('C clinical+radiomics vs clinical','GBM clinical+radiomics','GBM clinical'),('G clinical+radiomics vs radiomics','GBM clinical+radiomics','GBM radiomics')]}
    for p in papers:
        for comparison,aid,bid in contrasts[p['study_id']]:
            models={(m['model_id'],m['dataset_role']):m for m in p['performance']}
            roles=sorted({role for mid,role in models if mid==aid and (bid,role) in models},key=ROLES.get)
            for i,role in enumerate(roles):
                a,b=models[aid,role],models[bid,role]
                test=next((t for t in tests if t['study_id']==p['study_id'] and t['model_a']==aid and t['model_b']==bid and t['dataset_role']==role),None)
                classification=classify(a['AUC'],b['AUC'],role,test)
                delta=round(a['AUC']-b['AUC'],6) if isinstance(a['AUC'],(float,int)) and isinstance(b['AUC'],(float,int)) else 'NR'
                reason=f"Same {role} cohort and {p['endpoint_code']} outcome. "
                if i>0:reason+='Secondary result; equivalent validation contrast has priority. '
                if delta=='NR':reason+='Exact matched AUCs absent; effect size and validation improvement cannot be verified. '
                elif classification=='Demonstrated':reason+='Direct verified test supports an improvement for this model contrast. '
                elif classification=='Suggestive':reason+='Numerical improvement; no verified test for this exact contrast/dataset. '
                elif classification=='Not demonstrated':reason+='No numerical improvement or the direct test is not significant; this does not establish equivalence. '
                else:reason+='Training alone does not establish validation incremental value. '
                if p['study_id']=='WU_2025':reason+='Table 2 values are provisional where prose disagrees; fusion adds clinical and deep features, so its full gain is not attributable to radiomics alone. '
                if p['study_id']=='WANG_2025':reason+='p=.006/.042 has ambiguous dataset attribution and is not transferred to validation. '
                if a['timepoint_role']!=b['timepoint_role']:reason+='Different information timepoints are explicitly retained; the contrast also changes available timing information. '
                row=dict(study_id=p['study_id'],comparison=comparison,model_a=aid,model_b=bid,dataset_role=role,
                  timepoint_role=a['timepoint_role']+' vs '+b['timepoint_role'],auc_a=a['AUC'],auc_b=b['AUC'],delta_AUC=delta,
                  statistical_test=test['test'] if test else 'NR',p_value=test['p_value'] if test else 'NR',classification=classification,
                  reason=reason.strip(),source=a['source_identifier']+'; '+b['source_identifier']+('; '+test['source'] if test else ''),
                  primary=i==0,test_verified=bool(test and test['verified']))
                for metric in ['sensitivity','specificity']:
                    av,bv=a[metric],b[metric]
                    row['delta_'+metric]=round(av-bv,6) if isinstance(av,(int,float)) and isinstance(bv,(int,float)) else 'NR'
                row.update(calibration_difference='NR',net_benefit_difference='NR')
                rows.append(row)
        for category,label in [('A','radiomics vs clinical-only'),('B','radiomics vs conventional ultrasound-only'),('C','combined vs clinical comparator'),
                               ('D','early vs baseline'),('E','delta vs baseline'),('F','radiomics+DL vs radiomics-only'),('G','fusion/combined vs components')]:
            found=[r for r in rows if r['study_id']==p['study_id'] and r['comparison'].startswith(category+' ')]
            coverage.append(dict(study_id=p['study_id'],category=category,comparison=label,
                status='available' if found else 'unavailable',reason='All matched datasets exported; primary is the highest equivalent validation role.' if found else
                'No isolated, source-supported comparator contrast available. Fusion with clinical+DL does not isolate a radiomics+DL-only contrast.'))
            if not found:
                rows.append(dict(study_id=p['study_id'],comparison=category+' '+label,model_a='NR',model_b='NR',dataset_role='unavailable',
                    timepoint_role='NR',auc_a='NR',auc_b='NR',delta_AUC='NR',statistical_test='NR',p_value='NR',classification='Indeterminate',
                    reason=coverage[-1]['reason'],source=p['source_url'],primary=True,test_verified=False,
                    delta_sensitivity='NR',delta_specificity='NR',calibration_difference='NR',net_benefit_difference='NR'))
    return rows,coverage

def poolability(papers):
    strata={}
    for p in papers:
        for m in p['performance']:
            if m['dataset_role']=='training' or 'radiomics' not in m['model_type'] or m['AUC']=='NR':continue
            key=(p['endpoint_code'],m['timepoint_role'],m['model_type'],m['dataset_role'])
            strata.setdefault(key,[]).append((p,m))
    candidates=[];eligible=[]
    for key,items in sorted(strata.items()):
        ids=sorted({p['study_id'] for p,m in items})
        precision=all(m['CI_low']!='NR' and m['extraction_status']!='REVIEW_REQUIRED' for p,m in items)
        harmonized=all(not any(i['field']=='endpoint_definition' for i in p['issues']) for p,m in items)
        suitable=len(ids)>=2 and precision and harmonized
        reason='Fewer than two independent studies in this joint endpoint/timepoint/model/validation stratum.' if len(ids)<2 else 'Endpoint operational definition or usable precision needs review.'
        candidates.append(dict(endpoint=key[0],timepoint=key[1],model_type=key[2],dataset_role=key[3],studies='; '.join(ids),
            study_count=len(ids),precision_available=precision,eligible=suitable,reason=reason))
        if suitable:eligible.append(ids)
    covered=set(s for ids in eligible for s in ids)
    decision='justified' if len(covered)==len(papers) else 'partially justified' if eligible else 'not justified'
    reason=('A subgroup satisfies the prespecified joint criteria; no automatic meta-analysis is run.' if eligible else
      'No joint stratum contains two independent studies with the same endpoint, imaging role, model composition and validation role. The pCR pair uses baseline versus pre+midpoint radiomics; operational pathology and source precision also need review. AUC differences alone cannot supply the within-patient covariance needed to pool incremental effects.')
    return dict(poolability=decision,reason=reason,pooling_performed=False,forest_plot_produced=False),candidates

def methodology(papers):
    rows=[]
    for p in papers:
        considerations={
          'single_multicenter':('observed',p['centers']), 'internal_external':('observed',p['validation_type']),
          'selected_cohort':('observed',p['inclusion_criteria']), 'class_imbalance':('observed' if isinstance(p['prevalence'],float) else 'unclear',str(p['prevalence'])),
          'image_exclusions':('observed',p['exclusion_criteria']), 'missing_data':('unclear','Incomplete cases excluded; complete imputation/nesting details not verified.'),
          'acquisition_standardization':('observed',p.get('scanner','NR')), 'operator_dependence':('observed',p['segmentation']),
          'patient_level_splitting':('observed',p['validation_type']), 'feature_selection_inside_validation':('unclear','Feature selection and CV are described; full nesting is not established.'),
          'external_generalization':('observed' if 'external_validation' in p['semantic']['validation'] else 'not applicable',
              'Independent external center' if 'external_validation' in p['semantic']['validation'] else 'No external validation cohort')}
        for k,(status,evidence) in considerations.items():rows.append(dict(study_id=p['study_id'],consideration=k,status=status,evidence=evidence,source=p['source_url']))
    return rows
