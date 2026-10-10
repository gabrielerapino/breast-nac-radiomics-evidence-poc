"""Execute this notebook in process using the existing venv, without sockets.

This supports the restricted workspace; it is not a Jupyter kernel test.
All cells run in order and their stdout and rich display outputs are preserved.
"""
import os
from pathlib import Path
import sys
import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
os.environ.setdefault('MPLCONFIGDIR','/tmp/breast-nac-matplotlib')
os.environ.setdefault('IPYTHONDIR','/tmp/breast-nac-ipython')
shell=InteractiveShell.instance()
nb=nbformat.read(ROOT/'agentic_evidence_synthesis.ipynb',as_version=4)
count=0
for cell in nb.cells:
    if cell.cell_type!='code':continue
    count+=1
    with capture_output(stdout=True,stderr=True,display=True) as captured:
        result=shell.run_cell(cell.source,store_history=False)
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError(f'Notebook cell {count} failed') from result.error_before_exec or result.error_in_exec
    outputs=[]
    if captured.stdout:outputs.append(nbformat.v4.new_output('stream',name='stdout',text=captured.stdout))
    if captured.stderr:outputs.append(nbformat.v4.new_output('stream',name='stderr',text=captured.stderr))
    for display in captured.outputs:
        outputs.append(nbformat.v4.new_output('display_data',data=display.data,metadata=display.metadata))
    cell.outputs=outputs;cell.execution_count=count
nb.metadata['execution_method']='In-process IPython; no Jupyter sockets. Kernel execution blocked by workspace policy.'
nb.metadata['verified_interpreter']=sys.executable
nbformat.validate(nb)
nbformat.write(nb,ROOT/'agentic_evidence_synthesis.ipynb')
print(f'Notebook: {count} cells executed in order; {sys.executable}; schema valid')
