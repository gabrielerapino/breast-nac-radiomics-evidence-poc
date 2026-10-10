"""Report and notebook are views of the same persisted, checked result tables."""
import csv
import html
import json
import re
from pathlib import Path
from .sources import ROOT,OUT,load_json,digest,canonical

SECTIONS=['Research question','Selected studies','Source access','Clinical endpoint definitions','Imaging timepoints',
'Evidence extraction','Comparative evidence','Performance comparison','Incremental value','Methodological considerations',
'Cross-study comparability','Poolability decision','Final synthesis','Benchmark comparison','Limitations of the AI pipeline']

def read_csv(name):
    with (OUT/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def generate_report():
    frozen=load_json(OUT/'synthesis_frozen.json')
    matrix=read_csv('evidence_matrix.csv');inc=read_csv('incremental_value.csv');checks=read_csv('validation_checks.csv')
    def table(name,cols=None,rows=None):
        rows=read_csv(name) if rows is None else rows
        cols=cols or (list(rows[0]) if rows else [])
        header=''.join('<th>'+html.escape(c.replace('_',' '))+'</th>' for c in cols)
        body=''.join('<tr>'+''.join('<td>'+html.escape(str(r.get(c,'NR')))+'</td>' for c in cols)+'</tr>' for r in rows)
        return '<div class="scroll"><table><thead><tr>'+header+'</tr></thead><tbody>'+body+'</tbody></table></div>'
    def figure(name):
        svg=(ROOT/'figures'/(name+'.svg')).read_text()
        ids=re.findall(r'id="([^"]+)"',svg)
        for old in sorted(set(ids),key=len,reverse=True):
            svg=svg.replace('id="'+old+'"','id="'+name+'-'+old+'"').replace('#'+old+'"','#'+name+'-'+old+'"').replace('url(#'+old+')','url(#'+name+'-'+old+')')
        return '<div class="figure">'+svg[svg.index('<svg'):]+'</div>'
    def section(i,body):return f'<section id="s{i}"><h2><span>{i:02d}</span> {SECTIONS[i-1]}</h2>{body}</section>'
    def details(label,content):return '<details><summary>'+label+'</summary>'+content+'</details>'
    text=[]
    text.append(section(1,'<p class="lead">'+html.escape(frozen['research_question'])+'</p><p>Secondary question: how consistent is performance across imaging timepoints, strategies, model components and validation designs?</p><p class="key">'+frozen['key_message']+'</p><p>This POC demonstrates a deterministic source-to-report workflow built by an agent using AGENTS.md. Four studies were prespecified; no comprehensive search, screening or automatic meta-analysis was performed.</p>'))
    text.append(section(2,figure('study_design_overview')+table('evidence_matrix.csv',['study_id','authors','year','N_total','train_N','validation_N','external_validation_N','design'])))
    ing=load_json(OUT/'ingestion_records.json')
    sources='<ul>'+''.join(f'<li><b>{r["study_id"]}</b> — <a href="{html.escape(r["source_url"])}">primary full text</a> · <a href="../{r["file"]}">archived HTML</a> · SHA-256 <code>{r["sha256"][:16]}…</code></li>' for r in ing)+'</ul>'
    text.append(section(3,sources+'<p>All four primary full texts are archived and checked for DOI identity, document completeness and hashes. Wang Table 3, six supplements and Zhou Figure 5 are also retained. Exact source selectors are exported in the provenance table.</p><p>Numerical table transcriptions are checked by an independent parser. Narrative facts have reviewed source anchors; SOURCE_BOUND does not claim automated clinical verification.</p>'))
    text.append(section(4,table('endpoint_mapping.csv')))
    text.append(section(5,table('timepoint_mapping.csv')+'<p>Early means after two cycles in Yang/Wang; Wu midpoint is not assumed to mean two cycles. Baseline, delta and longitudinal information are retained separately.</p>'))
    text.append(section(6,table('coverage_summary.csv')+details('Study-level extraction and missing fields',table('evidence_matrix.csv'))+details('Field provenance and source witnesses',table('evidence_provenance.csv'))))
    text.append(section(7,figure('workflow')+table('comparison_coverage.csv')+'<p>Unavailable contrasts remain Indeterminate. Clinical+conventional ultrasound is distinguished from clinical-only; a fusion model containing clinical and deep features does not isolate the radiomics contribution.</p>'))
    text.append(section(8,figure('auc_by_model')+figure('timepoint_performance')+details('All reported model and dataset performance',table('performance_wide.csv',['study_id','model_id','model_type','dataset_role','timepoint_role','AUC','CI_low','CI_high','CI_source','sensitivity','specificity','accuracy','precision','recall','F1','PPV','NPV','calibration','Brier','decision_curve','threshold','extraction_status','source_identifier']))))
    cols=['study_id','comparison','dataset_role','timepoint_role','auc_a','auc_b','delta_AUC','statistical_test','p_value','classification','reason']
    text.append(section(9,'<p>Equivalent contrasts prioritize external validation → internal validation → test → training. Demonstrated requires a verified favorable direct test on the same validation/test cohort. A non-significant test does not establish equivalence; training alone is insufficient.</p>'+figure('incremental_value')+table('incremental_value.csv',cols,[r for r in inc if r['primary']=='True'])+details('All datasets, secondary contrasts and provenance',table('incremental_value.csv'))+'<h3>Source discrepancy sensitivity</h3>'+table('source_sensitivity.csv')+'<p>The coherent Wu table pair gives ΔAUC=0.043 for fusion versus deep learning. The coherent prose pair gives 0.017. The old 0.003 combined values from different source versions. None has a verified direct fusion-versus-deep test.</p><p>Calibration and DCA are described where reported; numerical differences and within-patient covariance remain unavailable. Missing values are NR, never zero.</p>'))
    text.append(section(10,table('methodological_considerations.csv')))
    text.append(section(11,'<p>Nine criteria: aligned=1, partially aligned=0.5, not aligned=0; unavailable excluded. High ≥0.75; moderate ≥0.50; low &lt;0.50. With zero evaluable criteria, score and rating are unassigned. Scores describe alignment and do not establish poolability.</p>'+figure('pairwise_comparability')+table('comparability_matrix.csv')+details('All 54 source-supported criterion decisions',table('comparability_detailed.csv'))))
    text.append(section(12,'<p class="decision">'+html.escape(frozen['poolability'])+'</p><p>'+html.escape(frozen['poolability_reason'])+'</p>'+table('poolability_candidates.csv')+'<p>No forest plot or quantitative meta-analysis was generated. Independent studies, compatible definitions, model composition, imaging timing, validation and usable precision must be considered jointly.</p>'))
    review=[r for r in checks if r['status']=='REVIEW_REQUIRED']
    text.append(section(13,'<ul>'+''.join('<li>'+html.escape(s)+'</li>' for s in frozen['synthesis'])+'</ul><h3>Open source questions and impact</h3>'+table('validation_checks.csv',rows=review)+details('All second-pass checks',table('validation_checks.csv'))))
    benchmark='Primary synthesis is frozen; benchmark not yet accessed in this run.'
    if (OUT/'benchmark_state.json').exists() and (OUT/'benchmark_comparison.md').exists():
        state=load_json(OUT/'benchmark_state.json')
        if state['primary_freeze_sha256']==digest((OUT/'synthesis_frozen.json').read_bytes()):benchmark=(OUT/'benchmark_comparison.md').read_text()
    text.append(section(14,'<pre>'+html.escape(benchmark)+'</pre><p>The inherited project had already consulted the benchmark. The new freeze precedes this run’s benchmark step, but the work is not blind.</p>'))
    text.append(section(15,'<ul>'+''.join('<li>'+html.escape(s)+'</li>' for s in frozen['limitations'])+'</ul><p>The workflow demonstrates reproducibility of reviewed transcriptions, interpretations and calculations. It is not a general autonomous extractor for arbitrary new articles, and source contradictions cannot be repaired by repeated execution.</p>'))
    nav=''.join(f'<a href="#s{i}">{i}. {h}</a>' for i,h in enumerate(SECTIONS,1))
    payload=json.dumps({'incremental_value':inc,'comparability':read_csv('comparability_matrix.csv'),'freeze':frozen},ensure_ascii=False).replace('</','<\\/')
    doc='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Breast NAC · Evidence synthesis POC</title><style>
:root{--ink:#1d3436;--green:#176a61;--muted:#53676a}*{box-sizing:border-box}body{margin:0;background:#f6f8f5;color:var(--ink);font:15px/1.6 system-ui,sans-serif}header{background:#183e3a;color:white;padding:50px max(5%,calc((100vw - 1200px)/2));}header p{color:#d2e4de;max-width:900px}h1{font-size:clamp(28px,4vw,46px);line-height:1.12;max-width:950px;margin:12px 0}.eyebrow{letter-spacing:.17em;text-transform:uppercase;font-size:12px}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:28px}.card{background:#ffffff15;padding:14px;border:1px solid #ffffff25;border-radius:8px}.card b{display:block;font-size:23px}.card small{color:#d2e4de}main{max-width:1240px;margin:auto;padding:30px 24px}nav{display:flex;gap:7px;flex-wrap:wrap;margin:12px 0 30px}nav a{font-size:12px;text-decoration:none;background:#e2ebe6;padding:6px 10px;border-radius:5px;color:var(--ink)}section{background:white;border:1px solid #dce5df;border-radius:10px;padding:25px;margin-bottom:22px;scroll-margin:20px}h2{font-size:23px;line-height:1.3;margin:0 0 20px}h2 span{color:#77938c;margin-right:10px;font-size:17px}h3{font-size:17px}.lead{font-size:22px;line-height:1.45}.key{border-left:4px solid var(--green);background:#edf5f0;padding:15px;font-weight:650}.decision{text-transform:uppercase;color:var(--green);font-size:24px;font-weight:700}.scroll{overflow:auto;max-height:550px;margin:15px 0;border:1px solid #e0e6e1;border-radius:6px}table{border-collapse:collapse;width:100%;font-size:12px}th,td{padding:10px 12px;border-bottom:1px solid #e3e9e4;text-align:left;vertical-align:top;min-width:100px;max-width:550px;overflow-wrap:anywhere}th{background:#edf3ef;position:sticky;top:0;white-space:nowrap}tr:nth-child(even){background:#fafcf9}details{margin:15px 0}summary{cursor:pointer;color:var(--green);font-weight:600}a{color:#1e7167}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.65 system-ui;background:#f1f5f1;padding:20px}.figure{overflow:auto;text-align:center;margin:22px 0}.figure svg{max-width:100%;height:auto}code{font-size:12px}footer{text-align:center;padding:20px;color:var(--muted)}@media(max-width:700px){.cards{grid-template-columns:repeat(2,1fr)}section{padding:17px}main{padding:16px}.figure svg{min-width:600px}}@media print{nav{display:none}.scroll{max-height:none;overflow:visible}details{display:block}section{break-inside:avoid}}</style></head><body>'''
    doc+='<header><div class="eyebrow">Source-backed evidence synthesis · POC</div><h1>Ultrasound radiomics in breast neoadjuvant therapy</h1><p>A deterministic pipeline built from AGENTS.md, with archived full texts, matched comparisons and visible source uncertainties.</p><div class="cards">'
    for number,label in [('4','Prespecified full texts'),('3','Distinct endpoint categories'),(str(len(review)),'Review checks open'),('No pooling','Current evidence decision')]:doc+=f'<div class="card"><b>{number}</b><small>{label}</small></div>'
    doc+='</div></header><main><nav>'+nav+'</nav>'+''.join(text)+'</main><footer>Primary freeze SHA-256: '+digest((OUT/'synthesis_frozen.json').read_bytes())+'</footer><script type="application/json" id="reviewed-results">'+payload+'</script></body></html>'
    (OUT/'evidence_synthesis_report.html').write_text(doc,encoding='utf-8')

def generate_notebook():
    cells=[]
    def md(text):cells.append(dict(cell_type='markdown',id=f'cell-{len(cells):02d}',metadata={},source=text.splitlines(True)))
    def code(text):cells.append(dict(cell_type='code',id=f'cell-{len(cells):02d}',metadata={},execution_count=None,outputs=[],source=text.splitlines(True)))
    md('# Ultrasound radiomics in breast NAC\n\nA reproducible POC built by an agent from AGENTS.md. Deterministic execution uses archived sources and reviewed mappings; it does not call language models. Source uncertainties remain visible.')
    code("from pathlib import Path\nimport sys, json\nROOT = Path.cwd().resolve()\nwhile not (ROOT / 'src' / 'extraction.py').exists():\n    if ROOT == ROOT.parent: raise RuntimeError('Run this notebook from the project folder')\n    ROOT = ROOT.parent\nsys.path.insert(0, str(ROOT))\nfrom src.sources import ingest, OUT\nfrom src.report import read_csv\nfrom src.pipeline import performance_rows, incremental_rows, comparability_rows\nfrom IPython.display import display, SVG\nimport pandas as pd\ndef show(name): display(pd.DataFrame(read_csv(name)))\nprint('Project:', ROOT)\nprint('Source identity and hashes:', len(ingest()), 'verified full texts')")
    narrative=[
       ('Research question','Does ultrasound-based radiomics provide incremental value beyond clinical and conventional ultrasound models?',None),
       ('Why this problem matters','Absolute discrimination and added predictive information answer different questions. High AUC alone does not prove incremental value.',None),
       ('Selected studies','Four studies were prespecified; this is not an exhaustive search or screening review.','evidence_matrix.csv'),
       ('Agent-built workflow','Ingestion → source-bound extraction → independent numerical checks → methodology → comparability → synthesis freeze → benchmark → reporting. No hosted agents run at execution.','pipeline_stages.json'),
       ('Structured extraction','Narrative facts have source anchors; performance tables are parsed from archived HTML. SOURCE_BOUND marks a reviewed mapping, not automated clinical adjudication.','coverage_summary.csv'),
       ('Endpoint harmonization','RECIST, Miller–Payne MHR and pCR stay distinct. Binary normalization does not imply clinical equivalence.','endpoint_mapping.csv'),
       ('Timepoint harmonization','Baseline, after two cycles, midpoint, delta and longitudinal models retain their own roles.','timepoint_mapping.csv'),
       ('Evidence matrix','Missing values remain NR. Review the original source evidence for consequential fields.','evidence_provenance.csv'),
       ('Performance comparison','Each estimate has study, model, outcome, dataset and imaging role.','performance_wide.csv'),
       ('Incremental value','Equivalent validation contrasts precede training. Statistical tests belong to a specific contrast and dataset. Fusion gains do not isolate radiomics.','incremental_value.csv'),
       ('Comparability','Nine criteria; unavailable excluded; high ≥.75, moderate ≥.50, low <.50. A score does not establish poolability.','comparability_matrix.csv'),
       ('Poolability','Joint endpoint/timepoint/model/validation strata must contain independent studies with usable precision. No automatic meta-analysis.','poolability_candidates.csv'),
       ('Final synthesis','Content-addressed freezes are retained. The current synthesis is read from the same artifact as the report.','synthesis_frozen.json'),
       ('Benchmark check','This step follows the current primary freeze. Prior benchmark exposure is declared; this is not a blind replication.','benchmark_comparison.md'),
       ('Limitations','Curated semantic interpretations, missing validation metrics and source contradictions limit conclusions. See the open checks and their impact.','validation_checks.csv')]
    for i,(heading,body,file) in enumerate(narrative,1):
        md(f'## {i}. {heading}\n\n{body}')
        if file:
            if file.endswith('.csv'):code(f"show('{file}')")
            elif file.endswith('.json'):code(f"display(json.loads((OUT / '{file}').read_text()))")
            else:code(f"print((OUT / '{file}').read_text() if (OUT / '{file}').exists() else 'Benchmark not yet accessed in this run')")
        fig={9:'auc_by_model',10:'incremental_value',11:'pairwise_comparability'}.get(i)
        if fig:code(f"display(SVG(filename=str(ROOT / 'figures' / '{fig}.svg')))")
    code("# Recompute derived results without changing the frozen artifacts.\nassert len(comparability_rows()) == 6\nexported = read_csv('incremental_value.csv')\nassert len(incremental_rows()) == len(exported)\nprint('Module results and persisted view have matching row counts.')")
    doc=dict(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},nbformat=4,nbformat_minor=5)
    (ROOT/'agentic_evidence_synthesis.ipynb').write_text(canonical(doc),encoding='utf-8')
