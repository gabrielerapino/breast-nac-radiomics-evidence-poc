# Breast NAC ultrasound radiomics — POC riproducibile

Questo progetto dimostra come un agente, guidato da `AGENTS.md`, possa costruire una pipeline verificabile per una sintesi della letteratura. La pipeline eseguita è deterministica e offline: legge le fonti archiviate, applica le trascrizioni narrative curate, estrae le tabelle, verifica i dati e rigenera analisi, report e notebook. Non richiede servizi LLM, API, token o download durante la normale esecuzione.

I quattro studi sono prespecificati. Questa demo non comprende una ricerca bibliografica esaustiva e uno screening PRISMA. Non è un estrattore universale per nuovi articoli. La decisione sul pooling viene calcolata; una meta-analisi quantitativa non viene avviata automaticamente.

## Aprire la demo

- Report autonomo con figure incorporate: [evidence_synthesis_report.html](outputs/evidence_synthesis_report.html).
- Notebook con celle e output: [agentic_evidence_synthesis.ipynb](agentic_evidence_synthesis.ipynb).
- Consegna e risultati completi: [RUN_SUMMARY.md](RUN_SUMMARY.md).
- Unico mandato riutilizzabile: [RUN_PROMPT.md](RUN_PROMPT.md), insieme a [AGENTS.md](AGENTS.md).

Il report si può aprire direttamente nel browser. I collegamenti alle copie locali delle fonti richiedono di conservare la struttura della cartella. Il contenuto del report e le figure sono incorporati nell'HTML, che si può condividere singolarmente.

## Rigenerare

### Dopo il clone

Gli output sono già inclusi. Per rigenerarli in un nuovo ambiente, usa Python 3.12 e le dipendenze fissate in `requirements.txt`:

```bash
git clone https://github.com/gabrielerapino/breast-nac-radiomics-evidence-poc.git
cd breast-nac-radiomics-evidence-poc
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -B run_pipeline.py
python -B scripts/execute_notebook.py
```

Per eseguire i controlli: `python -B -m unittest discover -s tests -v`.
Le istruzioni di ambiente in `AGENTS.md` documentano la ricostruzione originale; dopo il clone usa il tuo interprete locale. Le fonti archiviate e i relativi hash fanno parte del repository. I materiali degli editori mantengono le rispettive licenze e attribuzioni indicate nelle fonti.

### Ambiente originale della demo

Dalla cartella `breast_nac_ultrasound_radiomics_v1`:

```bash
/home/gabriele/cancer-research/venv/bin/python -B run_pipeline.py
/home/gabriele/cancer-research/venv/bin/python -B -m unittest discover -s tests -v
/home/gabriele/cancer-research/venv/bin/python -B scripts/execute_notebook.py
```

Il primo comando rigenera gli output e un notebook senza output eseguiti. Il terzo esegue tutte le celle in ordine, nel venv esistente, e salva stdout e display. Usa IPython nello stesso processo e non richiede socket Jupyter. In un ambiente normale il notebook resta eseguibile con Jupyter usando il medesimo interprete. Qui l'avvio del kernel Jupyter e di Chromium è impedito dalle restrizioni del workspace: non viene dichiarata una verifica del kernel o della resa completa nel browser.

`run_pipeline.py --primary-only` produce la sintesi primaria prima di leggere il record del benchmark. La normale esecuzione rigenera prima la parte primaria, crea il freeze, poi legge il benchmark archiviato e produce le viste. La precedente esposizione al benchmark è esplicitamente dichiarata. L'accesso nuovo al benchmark è limitato all'abstract/anteprima dell'editore.

## Organizzazione

| Percorso | Ruolo |
|---|---|
| `sources/` | Quattro full text HTML, Wang Table 3 e sei supplementi, Zhou Figure 5; copie testuali e tabelle per ispezione |
| `inputs/source_manifest.json` | SHA-256 delle fonti primarie archiviate |
| `inputs/reviewed_studies.json` | Trascrizioni narrative, passaggi con indice/hash, associazioni modello/dataset/timepoint e questioni aperte |
| `inputs/reviewed_tests.json` | Trascrizioni visive dei test in Zhou Figure 5, con hash della figura |
| `inputs/reviewed_intervals.json` | CI letti nella figura; quelli incoerenti col punto AUC restano inutilizzabili |
| `src/sources.py`, `src/extraction.py` | Ingestion verificata e lettura delle tabelle originali |
| `src/validation.py` | Secondo parser HTML indipendente, controlli di associazione, numeri, schema e riesame limitato |
| `src/analysis.py` | Confronti equivalenti, classificazioni, comparabilità e sottogruppi per pooling |
| `src/pipeline.py` | Orchestrazione, freeze versionati e benchmark separato |
| `src/report.py`, `src/plots.py` | Viste costruite dagli stessi risultati; sei figure descrittive |
| `benchmark/` | Anteprima della review, isolata dall'estrazione primaria |
| `archive/` | Snapshot recuperabile del progetto copiato e freeze storico |
| `outputs/revision_history.csv` | Valori precedenti, nuovi valori e fonti per le rettifiche |
| `outputs/freezes/` | Versioni della sintesi identificate dal contenuto; nessuna modifica retroattiva |

## Cosa significano i controlli

- `MATCH`: il numero è confermato da una lettura indipendente di colonne etichettate o da un calcolo su conteggi espliciti.
- `SOURCE_BOUND`: il passaggio sorgente è preservato e la mappatura narrativa è stata curata durante la costruzione. Non significa che un algoritmo abbia verificato la correttezza clinica dell'interpretazione.
- `NOT_REPORTED`: informazione non esplicitamente riportata; non diventa zero.
- `REVIEW_REQUIRED`: conflitto, associazione ambigua o valore critico mancante, con motivo e impatto.

Un `MATCH` di trascrizione può coesistere con un `REVIEW_REQUIRED` sulla stessa AUC: due parser confermano ciò che dice la tabella, mentre il testo dell'articolo riporta un numero diverso. La tabella viene mantenuta come trascrizione primaria provvisoria; le alternative sono mostrate separatamente. Il controllo deterministico non risolve il conflitto editoriale.

`Demonstrated` riguarda il contrasto preciso verificato, non la validità clinica generale del modello. Un fusion model comprende anche deep learning, covariate cliniche e/o informazione temporale aggiuntiva: il suo vantaggio non è interamente attribuibile alla sola radiomica.

## Riproducibilità e limiti

I CSV, il report e le figure usano gli stessi risultati. Le fonti vengono controllate mediante hash a ogni esecuzione. Il freeze registra hash degli input, di AGENTS.md e dei moduli. Le versioni precedenti vengono conservate, e il benchmark registra il digest del freeze senza modificarlo.

`scripts/prepare_records.py` documenta le trascrizioni curate dall'agente e può ricostruire gli input dalle stesse fonti archiviate. Non è necessario per la normale rigenerazione. Modificare una trascrizione richiede tornare alla fonte, registrare la rettifica e rigenerare i risultati; cambiare un valore per ottenere un risultato desiderato non costituisce validazione.

I vecchi test sono conservati nello snapshot. Le loro aspettative incompatibili con fonti e specifica sono documentate in `TEST_CHANGES.md`; i test attuali controllano anche dati alterati, denominatore zero, priorità dei dataset, immutabilità dei freeze e accordo CSV/HTML.
