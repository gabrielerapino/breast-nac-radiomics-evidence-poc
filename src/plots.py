"""Descriptive figures; no quantitative pooling or forest plot."""
from pathlib import Path
import os
import textwrap
os.environ.setdefault('MPLCONFIGDIR','/tmp/breast-nac-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .sources import ROOT

COLORS={'training':'#9ba6ae','internal_validation':'#238477','external_validation':'#335bb0'}

def generate_figures(papers,inc,pairs):
    folder=ROOT/'figures';folder.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
       'axes.spines.right':False,'svg.hashsalt':'breast-nac-poc-v1','figure.facecolor':'#fafbf9','axes.facecolor':'#fafbf9'})
    def save(fig,name):
        fig.savefig(folder/(name+'.svg'),bbox_inches='tight',metadata={'Date':None})
        fig.savefig(folder/(name+'.png'),dpi=140,bbox_inches='tight');plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,3.8));y=range(len(papers));left=[0]*len(papers)
    for field,label,color in [('train_N','Training','#9ba6ae'),('validation_N','Internal validation','#238477'),('external_validation_N','External validation','#335bb0')]:
        if field=='external_validation_N':
            left=[p.get('primary_cohort_N',base) if p['train_N']=='NR' else base for p,base in zip(papers,left)]
        values=[p[field] if isinstance(p[field],int) else 0 for p in papers]
        ax.barh(y,values,left=left,label=label,color=color)
        left=[a+b for a,b in zip(left,values)]
    # The primary Wu cohort is known, but its integer split is not: keep it visibly unallocated.
    for i,p in enumerate(papers):
        if p['train_N']=='NR':ax.barh(i,p['primary_cohort_N'],left=0,color='white',edgecolor='#9ba6ae',hatch='///',label='Primary cohort; split NR')
        ax.text(p['N_total']+8,i,str(p['N_total']),va='center')
    ax.set_yticks(list(y),[p['study_id'] for p in papers]);ax.set_xlim(0,720);ax.set_xlabel('Patients (reported cohort sizes)')
    ax.set_title('Study design and cohort sizes');ax.legend(loc='lower right',fontsize=8);save(fig,'study_design_overview')
    fig,axes=plt.subplots(2,2,figsize=(13,10))
    for ax,p in zip(axes.flat,papers):
        models=[m for m in p['performance'] if m['AUC']!='NR' and not m.get('is_candidate')]
        for i,m in enumerate(models):
            ax.scatter(m['AUC'],i,color=COLORS[m['dataset_role']],s=42,marker='D' if m['extraction_status']=='REVIEW_REQUIRED' else 'o')
            if m['CI_low']!='NR':ax.plot([m['CI_low'],m['CI_high']],[i,i],color=COLORS[m['dataset_role']],lw=1)
        ax.set_yticks(range(len(models)),[m['model_id']+' · '+m['dataset_role'].replace('_validation',' val') for m in models],fontsize=8)
        ax.set_xlim(.45,1);ax.set_xlabel('Reported AUC');ax.set_title(p['study_id']+' · '+p['endpoint_code']);ax.grid(axis='x',alpha=.18)
    fig.suptitle('Selected model discrimination by cohort; all candidate results in CSV\nDiamonds: a source field requires review; CIs shown only when usable',fontsize=13)
    fig.tight_layout();save(fig,'auc_by_model')
    fig,ax=plt.subplots(figsize=(10,4.8))
    data=[m for p in papers for m in p['performance'] if m['model_type']=='radiomics-only' and m['timepoint_role'] in ('baseline','early-treatment','delta') and m['AUC']!='NR' and not m.get('is_candidate')]
    for i,m in enumerate(data):ax.scatter(m['AUC'],i,color=COLORS[m['dataset_role']],s=50)
    ax.set_yticks(range(len(data)),[m['study_id']+' · '+m['timepoint_role']+' · '+m['dataset_role'] for m in data],fontsize=9)
    ax.set_xlim(.5,1);ax.set_xlabel('Reported AUC');ax.set_title('Imaging timepoints: descriptive comparisons, not pooled estimates')
    fig.tight_layout();save(fig,'timepoint_performance')
    data=[r for r in inc if r['primary'] and r['delta_AUC']!='NR']
    fig,ax=plt.subplots(figsize=(12,max(4,len(data)*.42)))
    colors={'Demonstrated':'#238477','Suggestive':'#d59a2f','Not demonstrated':'#9ba6ae','Indeterminate':'#b08db8'}
    ax.barh(range(len(data)),[r['delta_AUC'] for r in data],color=[colors[r['classification']] for r in data])
    ax.set_yticks(range(len(data)),[r['study_id']+' · '+r['comparison'][2:]+' · '+r['classification'] for r in data],fontsize=8)
    ax.axvline(0,color='#34434e',lw=.8);ax.set_xlabel('AUC(model A) − AUC(model B); same dataset and outcome')
    ax.set_title('Primary matched incremental contrasts\nWu values provisional; training-only contrasts remain Indeterminate')
    fig.tight_layout();save(fig,'incremental_value')
    fig,ax=plt.subplots(figsize=(7,5));ids=[p['study_id'] for p in papers]
    ax.set_xlim(-.5,3.5);ax.set_ylim(3.5,-.5)
    for r in pairs:
        i,j=ids.index(r['study_a']),ids.index(r['study_b'])
        for y,x in [(i,j),(j,i)]:
            ax.add_patch(plt.Rectangle((x-.48,y-.48),.96,.96,color={'high':'#b6d8c9','moderate':'#efddb0','low':'#dfbcb8','NR':'#eeeeee'}[r['rating']]))
            ax.text(x,y,f"{r['alignment_score']:.3f}\n{r['evaluated_criteria']}/9 · {r['rating']}" if r['alignment_score']!='NR' else 'unavailable',ha='center',va='center',fontsize=9)
    ax.set_xticks(range(4),ids,rotation=25,ha='right');ax.set_yticks(range(4),ids);ax.set_title('Pairwise comparability\nDenominator excludes unavailable criteria; score is not poolability')
    fig.tight_layout();save(fig,'pairwise_comparability')
    fig,ax=plt.subplots(figsize=(14,4));ax.axis('off')
    for i,p in enumerate(papers):
        values=[p['study_id'],' / '.join(p['semantic']['timepoints']),p['model_types'],p['validation_type'],p['endpoint_code']]
        for j,text in enumerate(values):
            ax.text(j*.21,.93-i*.25,textwrap.fill(text,26),transform=ax.transAxes,fontsize=8,va='top',
                bbox=dict(boxstyle='round,pad=.5',fc='#e4eeea',ec='#a3beb5'))
    ax.set_title('Study → imaging roles → model composition → validation → outcome',pad=25)
    save(fig,'workflow')
