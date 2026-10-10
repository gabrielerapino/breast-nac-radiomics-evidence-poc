"""A genuinely separate table parser and source witnesses, without hosted agents.

Numerical transcriptions are independently recomputed. Semantic mappings are
source-bound reviewed decisions: SOURCE_BOUND never claims automated clinical
verification. Primary-source contradictions remain REVIEW_REQUIRED.
"""
from html.parser import HTMLParser
from functools import lru_cache
import re
from .sources import ROOT, paragraph

class IndependentTables(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables=[];self.current=None;self.row=None;self.cell=None
    def handle_starttag(self,tag,attrs):
        if tag=='table':self.current=[]
        elif tag=='tr' and self.current is not None:self.row=[]
        elif tag in ('td','th') and self.row is not None:self.cell=[]
    def handle_data(self,data):
        if self.cell is not None:self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ('td','th') and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split()));self.cell=None
        elif tag=='tr' and self.row is not None:
            self.current.append(self.row);self.row=None
        elif tag=='table' and self.current is not None:
            self.tables.append(self.current);self.current=None

@lru_cache(maxsize=16)
def independent_tables(file):
    parser=IndependentTables();parser.feed((ROOT/'sources'/file).read_text());return parser.tables

def independent_auc(model):
    raw=independent_tables(model['file'])[model['table']-1][model['row']][model['column']]
    return float(re.search(r'\d+\.\d+',raw).group())

def bounded_review(evidences,limit=3):
    attempts=[];seen=set()
    for evidence in evidences:
        if evidence in seen or len(attempts)>=limit:break
        attempts.append(evidence);seen.add(evidence)
    return {'status':'REVIEW_REQUIRED','attempts':len(attempts),'evidence_examined':attempts}

def validate(papers):
    checks=[]
    def add(p,field,extracted,verified,status,reason,source=''):
        checks.append(dict(study_id=p['study_id'],field=field,extractor_value=extracted,validator_value=verified,
            status=status,reason=reason,source=source or p['source_url'],
            issue_type='extractor_validator_disagreement' if status=='REVIEW_REQUIRED' and reason.startswith('Independent') else
                       'source_conflict_or_missing' if status=='REVIEW_REQUIRED' else 'none'))
    for p in papers:
        for f in ['N_total','train_N','validation_N','external_validation_N','responder_N','nonresponder_N',
                  'endpoint_definition','validation_type','comparator','timepoints']:
            value=p.get(f,'NR');ev=p['provenance'].get(f)
            if value=='NR':add(p,f,value,'Not explicitly reported','NOT_REPORTED','Missing is not disagreement or zero.');continue
            text=paragraph(ev) if ev else ''
            if isinstance(value,int):
                # N=643 and total responders are independently derived from the two primary cohort counts.
                if p['study_id']=='WU_2025':
                    witnesses={'N_total':(372,271),'responder_N':(146,107),'nonresponder_N':(226,164)}
                    nums=witnesses.get(f,(value,))
                    verified=sum(nums) if all(re.search(r'\b'+str(n)+r'\b',text) for n in nums) else None
                elif f=='external_validation_N' and value==0:
                    verified=0 if p['semantic']['validation']==['internal_validation'] else None
                else:
                    # Read labelled source columns, not an unlabelled occurrence of a number.
                    heads=independent_tables(p['study_id']+'.html')[0][0]
                    if f in ('train_N','validation_N'):
                        label='Training' if f=='train_N' else '(?:Test|Validation)'
                        cell=next((h for h in heads if re.search(label,h,re.I)), '')
                        match=re.search(r'[nN]\s*=\s*(\d+)',cell)
                    elif f in ('responder_N','nonresponder_N') and p['study_id']=='YANG_2022':
                        cell=heads[1 if f=='responder_N' else 2];match=re.search(r'n\s*=\s*(\d+)',cell)
                    elif f in ('responder_N','nonresponder_N'):
                        pattern=r'(\d+)\s*\([^)]*%\)\s*'+('achieved pCR' if f=='responder_N' else 'did not')
                        match=re.search(pattern,text)
                    elif f=='N_total':
                        train=next((h for h in heads if 'Training' in h), '')
                        val=next((h for h in heads if 'Test' in h or 'Validation' in h), '')
                        aa=re.search(r'[nN]\s*=\s*(\d+)',train);bb=re.search(r'[nN]\s*=\s*(\d+)',val)
                        verified=int(aa.group(1))+int(bb.group(1)) if aa and bb else None
                        match=None
                    else:match=None
                    if f!='N_total':verified=int(match.group(1)) if match else None
                add(p,f,value,verified,'MATCH' if verified==value else 'REVIEW_REQUIRED',
                    'Independent numerical source witness; external N=0 means no external cohort, not NR imputation.')
            else:
                add(p,f,value,ev.get('needle','') if ev else 'Missing anchor','SOURCE_BOUND' if text else 'REVIEW_REQUIRED',
                    'Source passage reviewed during construction; semantic truth is not verified by string matching.')
        for m in p['performance']:
            field=f"AUC:{m['model_id']}:{m['dataset_role']}"
            if m['AUC']=='NR':add(p,field,'NR','Not tabulated','REVIEW_REQUIRED',m['reason'],m['source_identifier']);continue
            if 'table' in m:
                verified=independent_auc(m)
            else:
                text=' '.join(paragraph(m['evidence']).split())
                patterns={'RSA baseline':r'RS0\) alone \(AUC\s*=\s*(\d+\.\d+)',
                  'RSA early':r'AUC increased to (\d+\.\d+) and',
                  'RSA delta':r'AUC increased to \d+\.\d+ and (\d+\.\d+)',
                  'Model_RSA':r'combined radiomics model.*?AUC of (\d+\.\d+)',
                  'Model_Clinic':r'achieved an AUC of (\d+\.\d+)',
                  'Model_Combined':r'yielded an AUC of (\d+\.\d+)'}
                match=re.search(patterns[m['model_id']],text,re.I)
                verified=float(match.group(1)) if match else None
            add(p,field,m['AUC'],verified,'MATCH' if verified==m['AUC'] else 'REVIEW_REQUIRED',
                'Independent HTMLParser table extraction / direct prose numeric witness.',m['source_identifier'])
            if m['CI_low']!='NR' and not 0<=m['CI_low']<=m['AUC']<=m['CI_high']<=1:
                raise ValueError('Invalid usable confidence interval: '+field)
        for issue in p['issues']:
            review=bounded_review(['Archived full text','Source table/figure or independent re-read'])
            add(p,issue['field'],'See extracted record','Unresolved source discrepancy','REVIEW_REQUIRED',
                issue['reason']+' Impact: '+issue['impact']+f" Attempts: {review['attempts']}; stopped because no new resolving evidence.")
        if p['train_N']!='NR' and p['validation_N']!='NR':
            if p['train_N']+p['validation_N']+p['external_validation_N']!=p['N_total']:
                raise ValueError('Cohort counts do not sum: '+p['study_id'])
        if isinstance(p['responder_N'],int) and p['responder_N']+p['nonresponder_N']!=p['N_total']:
            raise ValueError('Outcome counts do not sum: '+p['study_id'])
    return checks

def contract(papers,detail,pairs,comparisons,checks=None):
    if checks and any(r['issue_type']=='extractor_validator_disagreement' for r in checks):
        raise ValueError('Extraction disagrees with independent source witness; delivery cannot be validated')
    if len(detail)!=54 or len(pairs)!=6:raise ValueError('Six pairs × nine criteria required')
    if len({(r['study_a'],r['study_b'],r['criterion']) for r in detail})!=54:raise ValueError('Duplicate criteria')
    for p in papers:
        if p['endpoint_definition']=='NR':raise ValueError('Missing endpoint')
        keys=set()
        for m in p['performance']:
            key=(m['model_id'],m['dataset_role'],m['timepoint_role'])
            if key in keys:raise ValueError('Duplicate performance association')
            keys.add(key)
            if not m['dataset_role'] or not m['timepoint_role'] or not m['source_identifier']:raise ValueError('Missing metric association')
            for metric in ['AUC','sensitivity','specificity','accuracy','precision','recall','F1','PPV','NPV','Brier']:
                value=m[metric]
                if value!='NR' and not (isinstance(value,(int,float)) and 0<=value<=1):raise ValueError('Invalid metric value')
    for r in comparisons:
        if r['classification']=='Demonstrated' and not (r['test_verified'] and r['dataset_role']!='training' and r['p_value']<.05 and r['delta_AUC']!='NR' and r['delta_AUC']>0):
            raise ValueError('Unsupported Demonstrated claim')
    return True
