"""Recoverable factual revision trace against the archived legacy extraction."""
import ast
import tarfile
from .sources import ROOT
from .extraction import FIELDS

def revision_history(papers):
    with tarfile.open(ROOT/'archive'/'legacy_snapshot.tar.gz') as archive:
        source=archive.extractfile('src/data.py').read().decode()
    tree=ast.parse(source)
    assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAPERS' for t in n.targets))
    old=ast.literal_eval(assignment.value)
    rows=[]
    for p in papers:
        previous=next(o for o in old if o['study_id']==p['study_id'])
        for f in FIELDS:
            if str(previous.get(f,'NR'))!=str(p.get(f,'NR')):
                rows.append(dict(study_id=p['study_id'],field=f,previous_value=previous.get(f,'NR'),new_value=p.get(f,'NR'),
                    reason='Re-extracted or re-described from archived primary evidence; unsupported old values are left NR.',source=p['source_url'],
                    previous_artifact='archive/legacy_snapshot.tar.gz::src/data.py'))
        old_models={(m['model_id'],m['dataset_role']):m for m in previous['performance']}
        for m in p['performance']:
            before=old_models.get((m['model_id'],m['dataset_role']))
            if before and str(before['AUC'])!=str(m['AUC']):
                try:equal=float(str(before['AUC']).replace('~',''))==m['AUC']
                except (ValueError,TypeError):equal=False
                if equal:continue
                rows.append(dict(study_id=p['study_id'],field=f"AUC:{m['model_id']}:{m['dataset_role']}",previous_value=before['AUC'],new_value=m['AUC'],
                    reason='Direct primary transcription; contradictory source versions remain REVIEW_REQUIRED, not adjudicated.',
                    source=m['source_identifier'],previous_artifact='archive/legacy_snapshot.tar.gz::src/data.py'))
    return rows
