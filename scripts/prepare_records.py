"""Build reviewed, source-bound extraction inputs. Not used by the normal runner.

Narrative values below are explicit transcriptions/interpretations made while
reading the archived primary articles. A selector and paragraph hash bind them
to their evidence. Performance numbers are parsed from original HTML tables.
"""
import hashlib
import json
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'sources'

def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')

def anchor(study, needle, section):
    soup = BeautifulSoup((SOURCE / f'{study}.html').read_text(), 'html.parser')
    for i, tag in enumerate(soup.find_all('p')):
        text = tag.get_text(' ', strip=True)
        if ' '.join(needle.lower().split()) in ' '.join(text.lower().split()):
            return {'file': f'{study}.html', 'paragraph': i, 'section': section,
                    'sha256': hashlib.sha256(text.encode()).hexdigest(),
                    'excerpt': text[:160], 'needle': needle}
    raise ValueError((study, needle))

studies = []
def study(sid, doi, year, title, endpoint):
    obj = {'study_id': sid, 'doi': doi, 'year': year, 'title': title,
           'endpoint_code': endpoint, 'fields': {}, 'model_specs': [],
           'semantic': {}, 'issues': []}
    studies.append(obj)
    return obj

def fields(s, needle, section, **values):
    evidence = anchor(s['study_id'], needle, section)
    for key, value in values.items():
        s['fields'][key] = {'value': value, 'evidence': evidence,
                            'review': 'Source passage inspected; narrative mapping curated by the building agent.'}

def spec(s, model, kind, role, timepoint, table, row, col, layout='auc_row', file=None):
    s['model_specs'].append({'model_id': model, 'model_type': kind,
        'dataset_role': role, 'timepoint_role': timepoint,
        'file': file or s['study_id'] + '.html', 'table': table,
        'row': row, 'column': col, 'layout': layout})

y = study('YANG_2022', '10.3389/fonc.2022.748008', 2022,
 'Treatment Response Prediction Using Ultrasound-Based Pre-, Post-Early, and Delta Radiomics in Neoadjuvant Chemotherapy in Breast Cancer', 'RECIST')
fields(y, 'Ethical approval for this retrospective', 'Methods / Patients',
 authors='Yang et al.', country='China', centers='Single center; Guizhou Medical University', design='Retrospective',
 recruitment_period='December 2018–December 2020 (Methods; abstract says January 2018)',
 N_total=217, train_N=152, validation_N=65, external_validation_N=0,
 train_responder_N=89, train_nonresponder_N=63, validation_responder_N=38, validation_nonresponder_N=27,
 population='Newly diagnosed invasive breast carcinoma treated with NAC',
 inclusion_criteria='Previously untreated biopsy-confirmed invasive carcinoma; 4–8 NAC cycles; baseline and after-two-cycle US',
 exclusion_criteria='Bilateral/multiple lesions; large or poor-quality images; incomplete clinical/US data',
 subtype='Molecular typing recorded; Table 1 includes luminal A/B, HER2, triple-negative',
 regimen='Paclitaxel and anthracycline-based; 4–8 cycles', validation_type='Random stratified internal 7:3 holdout')
fields(y, 'Participants were then classified', 'Methods / Patients',
 endpoint='RECIST responder / non-responder', endpoint_definition='At least 30% reduction in longest dimension on both US and MRI versus baseline',
 pCR_definition='Not the target endpoint', reference_standard='Radiological size response assessed by two radiologists using US and MRI',
 reference_timing='Pre- versus post-treatment; exact response assessment cycle not explicit', responder_N=127, nonresponder_N=90)
fields(y, 'All patients were examined using a Logiq', 'Methods / US examination',
 ultrasound='B-mode grayscale and conventional Doppler descriptors', SWE='Not reported', CEUS='Not reported', QUS='Not reported',
 scanner='GE Logiq E9; linear probe, central frequency 7 MHz', timepoints='Pretreatment and after 2 NAC cycles',
 image_count='Largest long-axis image per timepoint', acquisition_standardization='One scanner; settings adjusted per lesion')
fields(y, 'A region of interest (ROI) was manually', 'Methods / Segmentation',
 segmentation='Manual 2D ITK-SNAP ROI; reader >5 years; repeat segmentation in 50 patients after one week',
 segmentation_dimension='2D', operator_count=1, operator_expertise='>5 years', segmentation_software='ITK-SNAP',
 radiomics_software='USKit 1.3.0', feature_families='First-order, shape, texture, transform/wavelet')
fields(y, 'A total of 788 candidate', 'Results / Feature selection', initial_features=788,
 final_features='RS1:9; RS2:11; delta:8', feature_selection='ICC >0.7, mRMR, LASSO', feature_robustness='Repeat segmentation ICC >0.7')
fields(y, 'The prediction model for predicting tumor', 'Methods / Model construction',
 algorithm='Logistic regression', cv_strategy='10-fold CV in training', comparator='Clinical-only; baseline/early/delta signatures; longitudinal nomogram',
 model_types='Radiomics-only; clinical-only; clinical+radiomics', tuning='Not reported')
fields(y, 'Table 4 displays the results', 'Results / Nomogram', calibration='Hosmer–Lemeshow p=0.11 training; p=0.75 validation; curves', decision_curve='Not reported')
fields(y,'Of the 217 breast masses','Abstract / Results',responder_N=127,nonresponder_N=90)
y['semantic'] = dict(timepoints=['baseline','early-treatment','delta','longitudinal combined'], modalities=['B-mode'],
 strategy=['radiomics','clinical+radiomics'], comparators=['clinical','radiomics'],
 validation=['internal_validation'], population='breast/NAC', subtype=['luminal','HER2','TNBC'], regimen=['anthracycline','taxane'])
for r, mid, tp, kind in [(2,'RS1','baseline','radiomics-only'),(3,'RS2','early-treatment','radiomics-only'),
 (4,'Delta RS','delta','radiomics-only'),(5,'Nomogram RS1+RS2+Ki-67','longitudinal combined','clinical+radiomics')]:
    for role,col in [('training',1),('internal_validation',5)]: spec(y,mid,kind,role,tp,3,r,col)
y['issues'] = [
 {'field':'recruitment_period','reason':'Abstract starts January 2018; Methods starts December 2018.', 'impact':'Recruitment provenance; not AUC calculations.'},
 {'field':'prevalence','reason':'Results says 127 (62.5%) and 90 (37.5%); counts and abstract support 58.5% and 41.5%.', 'impact':'Prevalence calculated explicitly from counts; prose discrepancy retained.'},
 {'field':'specificity:Nomogram RS1+RS2+Ki-67:internal_validation','reason':'Table 3 says 0.789; Results prose says 0.798.', 'impact':'Table transcription provisional; specificity delta flagged.'},
 {'field':'nomogram_tests','reason':'Nomogram vs RS1 p<0.001 and vs RS2 p=0.376 reported without unambiguous dataset allocation.', 'impact':'Do not transfer these tests to validation contrasts.'}]

w = study('WANG_2025','10.1186/s12885-025-14556-4',2025,
 'Integrative multimodal ultrasound and radiomics for early prediction of neoadjuvant therapy response in breast cancer: a clinical study','MHR')
fields(w,'This retrospective study included female', 'Methods / Patients',
 authors='Wang et al.', country='China', centers='Single center; West China Hospital', design='Retrospective',
 recruitment_period='April 2020–December 2022', population='Female non-metastatic breast cancer patients completing NAT and surgery',
 inclusion_criteria='Pathological diagnosis; 6–8 anthracycline/taxane cycles; baseline and after-two-cycle US; surgery/pathology',
 exclusion_criteria='Prior breast cancer/treatment; pregnancy/lactation; timing violations; poor images/large lesions; incomplete data',
 regimen='Anthracycline and taxane-based, 6–8 cycles', surgery='Yes; definitive surgery after NAT')
fields(w,'This retrospective study included 239', 'Abstract / Methods',N_total=239,train_N=167,validation_N=72,external_validation_N=0)
fields(w,'Patients were randomly stratified', 'Methods / Model construction',
 validation_type='Random stratified internal 7:3 holdout', algorithm='Multivariate logistic regression',
 cv_strategy='LASSO 10-fold CV', feature_selection='Univariate screening; VIF; LASSO; stepwise regression',
 comparator='Clinical+conventional multimodal ultrasound; radiomics-only; combined',
 model_types='Clinical+ultrasound; radiomics-only; combined clinical+ultrasound+radiomics')
fields(w,'The primary tumor response was assessed', 'Methods / Final efficacy evaluation',
 endpoint='Miller–Payne MHR / non-MHR', endpoint_definition='Miller–Payne G4–G5 = major histological response; G1–G3 = non-major response',
 pCR_definition='MHR includes grades 4 and 5; not equivalent to pCR', reference_standard='Core biopsy versus post-treatment surgical pathology',
 reference_timing='After completion of NAT and surgery')
fields(w,'Baseline examinations were uniformly', 'Methods / Ultrasound',
 ultrasound='B-mode, Doppler, SWE, CEUS; radiomics on grayscale images', SWE='Yes',CEUS='Yes',QUS='Not reported',
 scanner='Siemens OXANA2 ABVS; follow-up same system or Philips Affiniti',
 acquisition_standardization='Standardized protocol; follow-up scanner may change', operator_expertise='At least 5 years')
fields(w,'This retrospective study included female', 'Methods / Patients',timepoints='Baseline and after 2 NAT cycles')
fields(w,'Using PyRadiomics, a total', 'Results / Radiomics',radiomics_software='PyRadiomics',initial_features=1395,
 final_features='Baseline:7; after two cycles:13; delta:10', feature_families='Wavelet and texture',
 preprocessing='Not reported', normalization='Not reported', discretization='Not reported')
fields(w,'Of 239 patients included', 'Results / General information',prevalence='51.5% MHR (reported; overall counts not explicit)',responder_N='NR',nonresponder_N='NR')
fields(w,'cases were classified into four IHC subtypes','Methods / Pathological information',subtype='Luminal A, Luminal B, HER2-positive, triple-negative')
fields(w,'PyRadiomics v3.1.0','Methods / Radiomics',radiomics_software='PyRadiomics 3.1.0',feature_families='First-order, morphology, texture, wavelet')
# These passages are located independently of the old records.
for needle in ['U-Net','U-net']:
    try:
        fields(w,needle,'Methods / Radiomics',segmentation='U-Net segmentation with radiologist manual correction',segmentation_software='U-Net')
        break
    except ValueError: pass
w['semantic'] = dict(timepoints=['baseline','early-treatment','delta','longitudinal combined'],modalities=['B-mode','Doppler','SWE','CEUS'],
 strategy=['radiomics','clinical+radiomics'],comparators=['clinical+ultrasound','radiomics'],validation=['internal_validation'],
 population='breast/NAC',subtype=['luminal','HER2','TNBC'],regimen=['anthracycline','taxane'])
w['narrative_models'] = [
 ('RSA baseline','radiomics-only','training','baseline',0.690,'when using baseline radiomics'),
 ('RSA early','radiomics-only','training','early-treatment',0.833,'when using baseline radiomics'),
 ('RSA delta','radiomics-only','training','delta',0.788,'when using baseline radiomics'),
 ('Model_RSA','radiomics-only','training','longitudinal combined',0.863,'when using baseline radiomics'),
 ('Model_Clinic','clinical+ultrasound','training','baseline',0.854,'achieved an AUC of 0.854'),
 ('Model_Combined','clinical+ultrasound+radiomics','training','longitudinal combined',0.914,'yielded an AUC of 0.914')]
for mid,kind in [('Model_RSA','radiomics-only'),('Model_Clinic','clinical+ultrasound'),('Model_Combined','clinical+ultrasound+radiomics')]:
    w.setdefault('missing_models',[]).append(dict(model_id=mid,model_type=kind,dataset_role='internal_validation',
        timepoint_role='longitudinal combined' if mid!='Model_Clinic' else 'baseline',AUC='NR',
        reason='Exact validation AUC is not in the inspected full text or Table 3; combined is only approximately 0.90.'))
w['issues'] = [
 {'field':'validation_AUC','reason':'Exact validation AUCs unavailable; do not convert approximately 0.90 to an exact estimate.', 'impact':'Validation incremental value is Indeterminate.'},
 {'field':'comparison_tests','reason':'Abstract assigns p=.006/.042 to validation, but Table 3 pairs them with the training AUCs .854/.863/.914.', 'impact':'Dataset allocation remains ambiguous; no Demonstrated validation claim.'},
 {'field':'responder_N','reason':'51.5% is reported overall, but Table S1 header has MHR=90 and NMHR=77 in training only.', 'impact':'Do not infer overall counts by rounding a percentage.'}]

u = study('WU_2025','10.3389/fonc.2025.1525285',2025,
 'Combination of ultrasound-based radiomics and deep learning with clinical data to predict response in breast cancer patients treated with neoadjuvant chemotherapy','pCR')
fields(u,'Data collection at Xiangyang', 'Methods / Patients',authors='Wu et al.',country='China',centers='Two institutions: Xiangyang First People’s Hospital and Zou Ping Hospital',
 design='Retrospective', recruitment_period='Jan 2022–Feb 2024; Mar 2022–Feb 2024',N_total=643,train_N='NR',validation_N='NR',
 primary_cohort_N=372,external_validation_N=271,responder_N=253,nonresponder_N=390,
 validation_type='Internal 7:3 stratified split; independent external center',regimen='NAC; specific regimens not reported')
fields(u,'Inclusion criteria were as follows', 'Methods / Patients',population='Confirmed invasive breast cancer, completed NAC and surgery',
 inclusion_criteria='Invasive breast cancer; complete NAC/surgery; pre- and midpoint US; complete clinical/pathological data',
 surgery='Yes; surgery after completed NAC',timepoints='Pretreatment and midpoint of NAC')
fields(u,'Exclusion criteria included', 'Methods / Patients',exclusion_criteria='Bilateral cancer; incomplete/non-standard treatment/surgery; poor/missing US; metastatic disease/secondary malignancy')
fields(u,'ypT0/is ypN0', 'Introduction / Endpoint definition',endpoint='pCR / non-pCR',
 endpoint_definition='Postoperative pCR; ypT0/is ypN0 stated in Introduction; operational adjudication not explicit in Methods',
 pCR_definition='ypT0/is ypN0 (Introduction)',reference_standard='Postoperative surgical pathology',reference_timing='After NAC and surgery')
fields(u,'Regarding molecular subtypes', 'Results / Patient characteristics',subtype='HR+/HER2−, HER2+, TNBC; distributions in Table 1 have inconsistent totals')
fields(u,'Breast ultrasound examinations were conducted', 'Methods / Data processing',
 ultrasound='B-mode US before and at midpoint of NAC',scanner='Resona 7; Philips; GE LOGIQ E20; Samsung',operator_expertise='Five radiologists with >10 years',
 image_count='Largest cross-sectional tumor image at each of two timepoints')
fields(u,'all images were rescaled', 'Methods / Data processing',
 segmentation='Manual 2D largest cross-sectional ROIs; two readers, senior supervision; blinded consensus',segmentation_software='3D Slicer',
 segmentation_dimension='2D images (software name is not a 3D acquisition)',operator_count=2,preprocessing='512×512 linear interpolation; 3-sigma pixel outliers; deep input 128×128')
fields(u,'1,216 features per ROI', 'Methods / Model construction',radiomics_software='PyRadiomics',
 initial_features='1216/ROI; 2438/patient in Methods; 2920 in Abstract (conflicting)',feature_families='Shape, first-order, GLCM, GLRLM, GLSZM, GLDM, NGTDM; ResNet50 deep features',
 feature_selection='Clinical univariate p<0.05; best internal-validation model; early feature fusion',final_features='NR')
fields(u,'The composite (Combine) model', 'Methods / Model construction',algorithm='Eight ML algorithms; ResNet50; early feature fusion',
 model_types='Clinical; radiomics; deep learning; clinical+radiomics+deep learning fusion',comparator='Clinical, radiomics and standalone deep learning',
 calibration='Calibration curves and Brier scores',decision_curve='DCA reported',cv_strategy='Not reported')
u['semantic']=dict(timepoints=['longitudinal combined'],modalities=['B-mode'],strategy=['radiomics','fusion','deep learning'],
 comparators=['clinical','radiomics','deep learning'],validation=['internal_validation','external_validation'],population='breast/NAC',
 subtype=['luminal','HER2','TNBC'],regimen=[])
for r,mid,kind in [(2,'Fusion','clinical+radiomics+deep learning'),(3,'Deep learning','deep learning'),(4,'Radiomics','radiomics-only'),(5,'Clinical','clinical-only')]:
    for role,col in [('internal_validation',3),('external_validation',4)]:
        spec(u,mid,kind,role,'baseline' if mid=='Clinical' else 'longitudinal combined',2,r,col,'wu_row')
u['issues']=[
 {'field':'AUC:Fusion:external_validation','reason':'Table 2 AUC .877 (.834–.919); abstract/results .891 (.848–.934). Table value retained as provisional transcription.', 'impact':'Fusion effect sizes uncertain; both versions are shown in sensitivity output.'},
 {'field':'AUC:Deep learning:external_validation','reason':'Table 2 AUC .834 (.808–.889); abstract/results .874 (.838–.909).', 'impact':'Fusion minus deep learning is .043 in Table 2, versus .003 using the legacy mixed sources; do not impose the expected delta.'},
 {'field':'endpoint_definition','reason':'ypT0/is ypN0 is in Introduction; detailed operational pathology criterion absent in Methods.', 'impact':'Shared pCR category; operational harmonization still needs review before pooling.'},
 {'field':'initial_features','reason':'Abstract 2920; Methods 1216 per ROI and 2438 per patient; 2×1216=2432, not 2438.', 'impact':'Feature counts not resolved.'},
 {'field':'subtype','reason':'Primary Table 1 subtype counts sum to 352, not 372; receptor category totals also inconsistent.', 'impact':'Category overlap can be compared; exact distributions cannot be trusted.'},
 {'field':'train_N','reason':'372 patients split 7:3; exact integer training and internal-validation sizes not explicit.', 'impact':'No invented integer split.'}]

f=study('FRONTIERS_2024','10.3389/fonc.2024.1485681',2024,
 'Machine learning for predicting neoadjuvant chemotherapy effectiveness using ultrasound radiomics features and routine clinical data of patients with breast cancer','pCR')
fields(f,'The study included patients diagnosed', 'Methods / Patients',authors='Zhou et al.',country='China',centers='Single center; Affiliated Tumor Hospital of Nantong University',design='Retrospective',
 recruitment_period='December 2014–September 2023',N_total=231,train_N=185,validation_N=46,external_validation_N=0,
 population='Pathologically confirmed breast cancer completing NAC and surgery',
 inclusion_criteria='pCR/non-pCR pathology after NAC/surgery; full NAC; preoperative US and biopsy',
 exclusion_criteria='Missing pathology; incomplete NAC; inadequate images; bilateral/multifocal tumors',validation_type='Random internal holdout',surgery='Yes; NAC followed by surgery')
fields(f,'The 231 participants were subjected', 'Methods / Effectiveness assessment',endpoint='pCR / non-pCR',
 endpoint_definition='No residual invasive carcinoma, DCIS may remain; no ipsilateral sentinel/axillary node involvement',
 pCR_definition='ypT0/is ypN0 equivalent operational definition',reference_standard='Postoperative histopathology',reference_timing='After NAC and surgery')
fields(f,'Out of 231 participants', 'Abstract / Results',responder_N=98,nonresponder_N=133,prevalence='42.42% (98/231)')
fields(f,'Clinical parameter comprised', 'Methods / Clinical parameters',subtype='Luminal A/B-like, HER2-enriched, triple-negative',stage='T1–4 and N0–3 recorded')
fields(f,'Ultrasonography was conducted', 'Methods / Ultrasonography',ultrasound='Pretreatment B-mode ultrasound',scanner='GE Logic E9 and Philips EPIQ7',
 image_count='Maximum diameter image per participant',segmentation='Two manual readers; third reader repeated 55 images after one month; ITK-SNAP 3.8.0',
 segmentation_dimension='2D',operator_count=2,operator_expertise='>10 years; repeat reader 9 years',segmentation_software='ITK-SNAP 3.8.0',feature_robustness='ICC >0.75')
fields(f,'These RFs were obtained from the pre-treatment', 'Methods / Radiomics',timepoints='Pretreatment before NAC',radiomics_software='PyRadiomics',
 feature_families='First-order, GLCM, GLDM, GLRLM, GLSZM, NGTDM, shape')
fields(f,'a total of 1,562 RFs', 'Results / Radiomics',initial_features=1562,final_features=12)
fields(f,'Before feature selection, the threshold', 'Methods / Screening',feature_selection='ICC >0.75; Z-score; Pearson correlation; LASSO',
 normalization='Z-score',algorithm='Ten ML algorithms; GBM selected',tuning='Mesh search',preprocessing='Z-score; Pearson correlation',
 model_types='Radiomics-only; clinical-only; clinical+radiomics',comparator='Clinical-only and radiomics-only GBM; combined GBM',cv_strategy='10-fold CV reported in table captions')
fields(f,'We use calibration curves', 'Methods / Model evaluation',calibration='Calibration curves',decision_curve='DCA training and validation')
f['fields']['regimen']={'value':'AC-T, TCbHP, AT, TP, AC, TC (Table 1)', 'evidence':anchor('FRONTIERS_2024','AC-T, adriamycin','Table 1 footnote'),'review':'Table footnote inspected.'}
f['semantic']=dict(timepoints=['baseline'],modalities=['B-mode'],strategy=['radiomics','clinical+radiomics'],comparators=['clinical','radiomics'],
 validation=['internal_validation'],population='breast/NAC',subtype=['luminal','HER2','TNBC'],regimen=['anthracycline','taxane','HER2-targeted'])
for col,mid,kind in [(1,'GBM clinical','clinical-only'),(2,'GBM radiomics','radiomics-only'),(3,'GBM clinical+radiomics','clinical+radiomics')]:
 for role,offset in [('training',0),('internal_validation',3)]:spec(f,mid,kind,role,'baseline',5,2,col+offset,'metric_columns')
for col,algorithm in enumerate(['LR','NB','SVM','KNN','RF','ET','LGBM','GBM','AB','MLP'],1):
 if algorithm=='GBM':continue # The selected GBM model is already represented by Table 5.
 for role,number in [('training',2),('internal_validation',3)]:
  spec(f,algorithm+' radiomics','radiomics-only',role,'baseline',number,1,col,'algorithm_columns')
  f['model_specs'][-1]['is_candidate']=True
f['issues']=[
 {'field':'CI:GBM clinical:internal_validation','reason':'Figure 5B prints AUC .732 and 95% CI .758–.968, which excludes the point estimate.', 'impact':'Invalid reported CI retained in discrepancy log; usable CI left NR, no CI-based pooling.'},
 {'field':'recall:GBM clinical+radiomics:internal_validation','reason':'Table 5 sensitivity .750 and recall .850 differ for the same model/dataset.', 'impact':'Both transcribed, flagged; no confusion matrix inferred from rounded metrics.'}]

for s in studies:
 s['semantic']['acquisition_roles']=(['baseline','after 2 cycles'] if s['study_id'] in ('YANG_2022','WANG_2025') else
                                     ['baseline','midpoint'] if s['study_id']=='WU_2025' else ['baseline'])
 soup=BeautifulSoup((SOURCE/(s['study_id']+'.html')).read_text(),'html.parser')
 tab=soup.find_all('table')[0]
 rows=[[c.get_text(' ',strip=True) for c in r.find_all(['td','th'],recursive=False)] for r in tab.find_all('tr')]
 r=next(i for i,row in enumerate(rows) if row and row[0].lower().startswith('age'))
 text=' | '.join(rows[r])
 s['fields']['age']={'value':'Table 1 original columns: '+json.dumps(rows[0],ensure_ascii=False)+'; original age row: '+text,
  'evidence':{'file':s['study_id']+'.html','table':1,'row':r,'column':None,'section':'Results / Table 1',
     'sha256':hashlib.sha256(text.encode()).hexdigest(),'excerpt':text[:160],'needle':'Age row, with original cohort columns'},
  'review':'Original cohort/response columns preserved; no pooled or invented overall mean.'}
 s['source_url']=('https://link.springer.com/article/'+s['doi'] if s['study_id']=='WANG_2025' else
                  'https://www.frontiersin.org/journals/oncology/articles/'+s['doi']+'/full')
 for mid,kind,role,tp,value,needle in s.pop('narrative_models',[]):
  s.setdefault('narrative_performance',[]).append(dict(model_id=mid,model_type=kind,dataset_role=role,timepoint_role=tp,
    AUC=value,evidence=anchor(s['study_id'],needle,'Results / Model construction'),
    dataset_note='Training allocation supported by abstract and matching Table 3 AUCs; early/delta Results allocation less explicit.'))
dump(ROOT/'inputs'/'reviewed_studies.json',studies)
manifest=[]
for path in sorted(SOURCE.iterdir()):
 if path.is_file():manifest.append(dict(file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size))
dump(ROOT/'inputs'/'source_manifest.json',manifest)
print('Source-bound records prepared:',len(studies))
