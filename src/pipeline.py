"""Deterministic orchestration. Primary stages cannot read benchmark inputs."""
import csv
from .sources import ROOT, OUT, ingest, digest, canonical, load_json, table
from .extraction import extract, provenance, FIELDS, METRICS
from .validation import validate, contract, independent_tables
from .analysis import CRITERIA,compare,detail_rows,pair_rows,summarize_pair,incremental,poolability,methodology,available

COMPARABILITY_CRITERIA=CRITERIA
MATRIX_FIELDS=['study_id']+FIELDS+['source_access']

def write_csv(name,rows,fields=None):
    OUT.mkdir(exist_ok=True)
    fields=fields or list(dict.fromkeys(k for row in rows for k in row))
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

def write_json(path,obj):
    path.parent.mkdir(exist_ok=True,parents=True)
    payload=canonical(obj)
    if not path.exists() or path.read_text()!=payload:path.write_text(payload,encoding='utf-8')

def tests_from_sources():
    result=[]
    wu=table('WU_2025.html',2)
    second=independent_tables('WU_2025.html')[1]
    for row,mid in [(2,'Fusion'),(3,'Deep learning'),(4,'Radiomics')]:
        for col,role in [(5,'internal_validation'),(6,'external_validation')]:
            pv=float(wu[row][col]);verified=pv==float(second[row][col])
            result.append(dict(study_id='WU_2025',model_a=mid,model_b='Clinical',dataset_role=role,test='DeLong',
                p_value=pv,verified=verified,source='Wu Table 2 (Clinic benchmark footnote); column '+str(col)))
    for item in load_json(ROOT/'inputs'/'reviewed_tests.json'):
        image=ROOT/'sources'/item['file']
        if digest(image.read_bytes())!=item['sha256']:raise ValueError('Reviewed figure changed')
        result.append({**item,'verified':item['reviewed'],'test':'DeLong'})
    from .sources import soup
    text=' '.join(soup('YANG_2022.html').get_text(' ',strip=True).split())
    if '0.086' not in text:raise ValueError('Yang direct test absent')
    result.append(dict(study_id='YANG_2022',model_a='Delta RS',model_b='RS1',dataset_role='training',test='DeLong',
                       p_value=.086,verified=True,source='Yang Results / Performance: training AUCs .743 versus .722, p=.086'))
    return result

def evidence_matrix(papers=None):return [{k:p.get(k,'NR') for k in MATRIX_FIELDS} for p in papers or extract()]
def performance_rows(papers=None):return [m for p in papers or extract() for m in p['performance']]
def metric_rows(papers=None):
    from .sources import source_location
    rows=[]
    for m in performance_rows(papers):
        for metric in METRICS:
            ev=m.get('metric_provenance',{}).get(metric)
            rows.append(dict(study_id=m['study_id'],model_id=m['model_id'],endpoint=m['endpoint'],dataset_role=m['dataset_role'],
              timepoint_role=m['timepoint_role'],metric=metric,value=m[metric],CI_low=m['CI_low'] if metric=='AUC' else 'NR',
              CI_high=m['CI_high'] if metric=='AUC' else 'NR',source_section=ev['section'] if ev else m['source_section'],
              source_table=f"Table {ev['table']}" if ev and 'table' in ev else 'NR' if ev else m['source_table'],source_identifier=source_location({'source_url':m['source_identifier'].split(' | ')[0]},ev) if ev else m['source_identifier'],
              CI_source=m.get('CI_source',m['source_identifier']) if metric=='AUC' else 'NR',extraction_status=m['extraction_status']))
    return rows
def provenance_rows(papers=None):return provenance(papers or extract())
def incremental_rows(papers=None):return incremental(papers or extract(),tests_from_sources())[0]
def validation_rows(papers=None):return validate(papers or extract())
def comparability_detail_rows(papers=None):return detail_rows(papers or extract())
def comparability_rows(papers=None):return pair_rows(comparability_detail_rows(papers))
def _comparison_status(c,a,b):return compare(c,a,b)
def assess_poolability(papers=None):
    result,_=poolability(papers or extract());return result['poolability'],result['reason']

def endpoint_rows(papers):
    return [dict(study=p['study_id'],endpoint_name=p['endpoint'],endpoint_definition=p['endpoint_definition'],
       binary_mapping='Target response=1; absence=0 (analysis normalization; not a claim about original coding)',
       comparable_to_pCR='category yes; operational definition needs review' if p['study_id']=='WU_2025' else 'yes' if p['endpoint_code']=='pCR' else 'no',
       notes='Original endpoint retained; binary mapping does not imply equivalence.') for p in papers]

def freeze_synthesis(papers=None,inc=None,checks=None):
    papers=papers or extract();inc=inc or incremental_rows(papers);checks=checks or validate(papers)
    pooling,candidates=poolability(papers)
    primary=[r for r in inc if r['primary'] and r['model_a']!='NR']
    counts={c:sum(r['classification']==c for r in primary) for c in ['Demonstrated','Suggestive','Not demonstrated','Indeterminate']}
    review=sum(r['status']=='REVIEW_REQUIRED' for r in checks)
    result=dict(research_question='Does ultrasound-based radiomics provide incremental predictive value for predicting response to neoadjuvant therapy in breast cancer beyond clinical and conventional ultrasound-based models?',
      primary_studies=[p['study_id'] for p in papers],primary_synthesis_frozen=True,
      benchmark_consulted_in_this_primary_run=False,previous_benchmark_exposure=True,
      benchmark_exposure_note='The inherited project already consulted the benchmark; this rerun is not blind or independent of prior exposure.',
      poolability=pooling['poolability'],poolability_reason=pooling['reason'],pooling_performed=False,forest_plot_produced=False,
      validation_status='CHECKS_PASSED_WITH_REVIEW_REQUIRED' if review else 'CHECKS_PASSED',
      review_required_count=review,primary_comparison_counts=counts,
      key_message='High predictive performance does not by itself demonstrate incremental value.',
      synthesis=[
        f"Four prespecified studies; {len({p['endpoint_code'] for p in papers})} endpoint categories (RECIST, Miller–Payne MHR, pCR). This is not an exhaustive systematic review.",
        f"Available primary matched contrasts: {counts['Demonstrated']} Demonstrated, {counts['Suggestive']} Suggestive, {counts['Not demonstrated']} Not demonstrated, {counts['Indeterminate']} Indeterminate. Contrasts within a study are correlated and are not independent study counts.",
        'Zhou 2024 has a direct clinical+radiomics versus clinical-only baseline validation contrast supported by Figure 5H; it provides evidence within one small internal cohort.',
        'Wu 2025 validates multimodal models externally, but longitudinal information, clinical and deep features complicate attribution to radiomics alone; table/prose discrepancies leave effect sizes provisional.',
        'Wang 2025 exact validation AUCs and dataset attribution of tests remain unresolved. Yang distinguishes early and delta from baseline; training tests are not borrowed for validation.',
        f"Poolability: {pooling['poolability']}. {pooling['reason']}",
        f"{review} REVIEW_REQUIRED checks remain visible. Clinical usefulness beyond discrimination is not established by AUC differences alone."],
      limitations=['Protocol-selected four studies; no exhaustive search or screening.',
        'Narrative transcription and semantic mappings were curated by the building agent; deterministic source checks do not replace independent clinical appraisal.',
        'Source contradictions, missing exact validation metrics and uncertain feature-selection nesting remain.',
        'No patient data, model fitting, invented confidence intervals or imputed confusion matrices.',
        'Previous benchmark exposure prevents a claim of blind synthesis.'])
    inputs=['inputs/reviewed_studies.json','inputs/reviewed_tests.json','inputs/reviewed_intervals.json','inputs/source_manifest.json','AGENTS.md']
    result['input_sha256']={name:digest((ROOT/name).read_bytes()) for name in inputs}
    result['code_sha256']={str(path.relative_to(ROOT)):digest(path.read_bytes()) for path in sorted((ROOT/'src').glob('*.py'))}
    payload=canonical(result);sha=digest(payload.encode())
    versions=OUT/'freezes';versions.mkdir(parents=True,exist_ok=True)
    version=versions/(sha+'.json')
    if version.exists() and version.read_text()!=payload:raise ValueError('Immutable freeze collision')
    if not version.exists():version.write_text(payload)
    current=OUT/'synthesis_frozen.json'
    if current.exists() and current.read_text()!=payload:
        previous=current.read_bytes();old=versions/(digest(previous)+'.json')
        if not old.exists():old.write_bytes(previous)
    write_json(current,result)
    return result

def generate_primary():
    records=ingest();papers=extract(records);checks=validate(papers)
    inc,coverage=incremental(papers,tests_from_sources());detail=detail_rows(papers);pairs=pair_rows(detail)
    contract(papers,detail,pairs,inc,checks)
    OUT.mkdir(exist_ok=True)
    for name,rows in [
      ('evidence_matrix.csv',evidence_matrix(papers)),('performance_table.csv',metric_rows(papers)),
      ('performance_wide.csv',performance_rows(papers)),('evidence_provenance.csv',provenance(papers)),
      ('incremental_value.csv',inc),('comparison_coverage.csv',coverage),('endpoint_mapping.csv',endpoint_rows(papers)),
      ('timepoint_mapping.csv',[dict(study=p['study_id'],timepoints_reported=p['timepoints'],model_roles='; '.join(p['semantic']['timepoints'])) for p in papers]),
      ('comparability_detailed.csv',detail),('comparability_matrix.csv',pairs),('methodological_considerations.csv',methodology(papers)),
      ('validation_checks.csv',checks),('statistical_tests.csv',tests_from_sources()),
      ('poolability_candidates.csv',poolability(papers)[1])]:write_csv(name,rows)
    write_json(OUT/'structured_studies.json',papers)
    write_json(OUT/'ingestion_records.json',[dict(study_id=p['study_id'],doi=p['doi'],source_url=p['source_url'],file='sources/'+p['study_id']+'.html',
        sha256=digest((ROOT/'sources'/(p['study_id']+'.html')).read_bytes()),status='FULL_TEXT_ARCHIVED') for p in papers])
    write_json(OUT/'pipeline_stages.json',['ingestion','factual extraction','validation','methodological interpretation','comparability','synthesis freeze'])
    freeze=freeze_synthesis(papers,inc,checks)
    sensitivity=[]
    for fusion,deep,label in [(.877,.834,'Both Table 2'),(.891,.874,'Both Results prose'),(.877,.874,'Legacy mixed sources; not a coherent primary pair')]:
        sensitivity.append(dict(study_id='WU_2025',dataset_role='external_validation',scenario=label,
          fusion_auc=fusion,deep_auc=deep,delta_AUC=round(fusion-deep,6),classification='Suggestive',
          note='No direct Fusion vs Deep statistical test verified; alternative values remain unresolved.'))
    write_csv('source_sensitivity.csv',sensitivity)
    coverage_rows=[]
    for p in papers:
        total=len(FIELDS);known=sum(available(p.get(k,'NR')) for k in FIELDS)
        coverage_rows.append(dict(study_id=p['study_id'],fields_expected=total,fields_present=known,fields_missing=total-known,
          source_bound_fields=len(p['provenance']),performance_rows=len(p['performance']),
          known_auc=sum(m['AUC']!='NR' for m in p['performance'])))
    write_csv('coverage_summary.csv',coverage_rows)
    from .audit import revision_history
    write_csv('revision_history.csv',revision_history(papers))
    from .plots import generate_figures
    generate_figures(papers,inc,pairs)
    return dict(studies=len(papers),performance_rows=len(performance_rows(papers)),review_required=freeze['review_required_count'],
      poolability=freeze['poolability'],validation_status=freeze['validation_status'])

def generate_benchmark_report():
    frozen=load_json(OUT/'synthesis_frozen.json');before=digest((OUT/'synthesis_frozen.json').read_bytes())
    if not frozen['primary_synthesis_frozen']:raise RuntimeError('Primary freeze required before benchmark')
    facts=load_json(ROOT/'inputs'/'benchmark_review.json')
    if digest((ROOT/facts['archive_file']).read_bytes())!=facts['source_sha256']:
        raise ValueError('Benchmark source integrity failure')
    body=(f"# External methodological benchmark\n\n{facts['title']} ({facts['year']}), DOI {facts['doi']}.\n\n"
      f"Source: {facts['source_url']}\nAccess: {facts['access']}\n\n{facts['summary']}\n\n"
      'The review predates the two 2025 studies and covers a broader evidence set. Its pooled accuracy is not a pooled incremental contrast against clinical/conventional ultrasound models. '
      'The four-study POC retains distinct outcomes and imaging roles; it supports cautious interpretation of combined-model performance and does not borrow benchmark numbers for extraction.\n\n'
      'This project was exposed to the benchmark previously. The current comparison occurs after the new freeze, but cannot be described as blind or independent. '
      'Benchmark findings do not change the primary synthesis.\n')
    (OUT/'benchmark_comparison.md').write_text(body)
    write_json(OUT/'benchmark_state.json',dict(benchmark_consulted=True,previous_exposure=True,access=facts['access'],primary_freeze_sha256=before,
      synthesis_unchanged=digest((OUT/'synthesis_frozen.json').read_bytes())==before))
    if digest((OUT/'synthesis_frozen.json').read_bytes())!=before:raise ValueError('Benchmark altered primary freeze')
    stages=load_json(OUT/'pipeline_stages.json');stages+=['benchmark','reporting'];write_json(OUT/'pipeline_stages.json',stages)
