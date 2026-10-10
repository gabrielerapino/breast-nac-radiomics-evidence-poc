# AGENTS.md — Agentic evidence synthesis: ultrasound radiomics in breast cancer/NAC

## Chiarimenti concordati per questa ricostruzione

La consegna è un POC di sintesi della letteratura dai quattro studi prespecificati fino alla decisione sul pooling. Non è una revisione sistematica con ricerca e screening esaustivi. La pipeline eseguita deve essere deterministica, offline e riproducibile: nessun agente LLM o servizio API a runtime. L’agente costruttore legge le fonti, documenta le estrazioni e implementa i controlli.

È autorizzata la ricostruzione dei componenti ereditati non coerenti con questo obiettivo, previa conservazione recuperabile. Le vecchie estrazioni sono candidate da riverificare, non fatti già validati. Riutilizza il venv `/home/gabriele/cancer-research/venv`. Per questa iterazione la cartella di lavoro è `breast_nac_ultrasound_radiomics_v1`; l’originale resta una testimonianza storica.

Il secondo controllo può usare un parser numerico distinto e passaggi source-based riesaminati dall’agente costruttore. Distingui MATCH numerico, SOURCE_BOUND per interpretazioni curate e REVIEW_REQUIRED per dubbi. Non descrivere il controllo deterministico come un revisore clinico indipendente. Conserva le fonti locali con hash e rendi la rigenerazione possibile senza rete. L’estrazione narrativa resta una trascrizione curata e verificabile, non un estrattore universale di nuovi articoli.

I numeri attesi riportati più avanti sono esempi da controllare. In caso di discrepanza primaria conserva entrambe le versioni, segnala gli effetti sui confronti e non forza il valore atteso. Documenta anche l’eventuale disponibilità del solo abstract del benchmark. La precedente esposizione al benchmark va dichiarata.

Se il workspace impedisce browser o kernel Jupyter, esegui i controlli disponibili e le celle in processo nel venv, preservandone gli output. Distingui questa esecuzione da una verifica del kernel e riporta esplicitamente la resa browser non verificata. Non installare dipendenze o modificare autorizzazioni per aggirare vincoli del workspace.

## Mandato e ambiente di lavoro

Completa una pipeline riproducibile e capace di verificare internamente i propri risultati per sintetizzare quattro studi di radiomica ecografica nel breast cancer/NAC. Questa specifica definisce il comportamento ordinario della pipeline, dall'acquisizione alla consegna.

Lavora nella cartella del progetto corrente: sono già presenti artefatti di una precedente esecuzione e un ambiente virtuale Python con dipendenze installate. Non ricreare il progetto, non cancellare gli output e non ricreare il venv. Non reinstallare dipendenze già disponibili e non eseguire aggiornamenti generalizzati.

Prima di scrivere codice:

1. Ispeziona struttura, moduli, entry point, notebook, test, dati, full text locali, estrazioni, output e ambiente virtuale. Non assumere percorsi o comandi inesistenti.
2. Individua l'interprete del venv esistente e usa quello per esecuzioni e test. Controlla le dipendenze mediante import e metadati; installa solo una dipendenza effettivamente mancante e necessaria, nel medesimo venv, documentandola.
3. Registra stato iniziale e hash dei dati sorgente, delle estrazioni validate e di eventuale synthesis freeze. Conserva una versione recuperabile degli artefatti che aggiorni.
4. Classifica i componenti come riutilizzabili, da integrare o da correggere, sulla base delle regole e dei controlli di questa specifica.
5. Riusa full text e dati già acquisiti se identità e integrità sono verificabili. Recupera solo fonti mancanti o passaggi necessari a sciogliere dubbi. Non ripetere tutta l'estrazione senza motivo.

Correggi o integra i moduli e gli artefatti esistenti. Genera soltanto ciò che manca e rigenera gli output che dipendono da una modifica effettiva. Conserva i percorsi esistenti, incluso quello del report HTML; non crearne copie concorrenti. La logica appartiene ai moduli, non a modifiche manuali ai CSV o a celle isolate del notebook.

I quattro studi e le domande di ricerca sono fissi. Non introdurre riferimenti o dipendenze a progetti ovarici, ADNEX o IOTA. Non cambiare endpoint, timepoint, modelli o performance per migliorare comparabilità e conclusioni. Una correzione fattuale è ammessa solo se sostenuta dalla fonte primaria: conserva il valore precedente, la nuova evidenza e la motivazione in una traccia di revisione, senza sovrascrivere silenziosamente l'estrazione. Distingui sempre dati sorgente, fatti estratti e interpretazioni derivate.

Procedi autonomamente entro questo ambito. Evita over-engineering: estendi i componenti funzionanti invece di sostituirli in blocco.

## Controllo interno e condizioni di consegna

La pipeline deve completare una singola esecuzione logica con controlli e riesami interni prima della consegna. Non attendere un revisore esterno per scoprire incongruenze verificabili automaticamente. Non promettere la risoluzione automatica di informazioni assenti o ambigue.

Separa i passaggi: ingestion → factual extraction → validation → methodological interpretation → comparability → synthesis freeze → benchmark → reporting. Ogni risultato mantiene riferimenti alla fonte e dipendenze dai dati utilizzati.

### Controlli obbligatori

- **Integrità:** quattro study_id univoci, fonti corrette, schema valido, metriche associate a modello, endpoint, dataset e timepoint; nessuna conversione automatica di NR in zero.
- **Validazione fattuale:** secondo controllo source-based di N, split, endpoint, principali AUC, comparator e confronti statistici. Il consenso tra agenti non sostituisce la verifica della fonte.
- **Comparability:** sei coppie e nove criteri ciascuna; nessun criterio duplicato; confronto semantico documentato; mancanti esclusi dal denominatore; score, rating e reasons coerenti. Una differenza lessicale non giustifica un not_aligned clinico.
- **Incremental value:** ricerca sistematica dei confronti disponibili per ogni dataset; preferenza per validation equivalente; calcoli riproducibili; classificazioni supportate dal test del contrasto corretto. Non assegnare Demonstrated solo perché il modello combinato ha AUC maggiore.
- **Coerenza degli artefatti:** CSV, report, figure e notebook utilizzano gli stessi risultati derivati. Non lasciare score /9 con criteri unavailable né classificazioni narrative diverse da quelle strutturate.
- **Sintesi:** conclusioni proporzionate a evidenza, comparabilità e copertura; la decisione di poolability è esplicita e indipendente dal solo rating. Nessun benchmark usato come fonte dell'estrazione primaria.

### Riesame interno limitato

Quando un controllo fallisce, registra studio/coppia/campo, regola violata e fonte coinvolta. Distingui errore deterministico, errore di estrazione, ambiguità della fonte e informazione assente.

- Correggi gli errori deterministici nel modulo responsabile e aggiungi un test pertinente.
- Per un errore fattuale torna alla sezione/tabella/figura primaria, verifica il valore e conserva la traccia della rettifica.
- Per un dubbio semantico rivaluta i fatti clinici disponibili e scrivi una motivazione specifica, senza scegliere il rating desiderato.
- Ricalcola e ricontrolla soltanto i risultati dipendenti dal campo modificato.

Usa al massimo tre tentativi di risoluzione per la stessa questione; interrompi prima se non emergono nuove evidenze. Problemi irrisolti producono REVIEW_REQUIRED con motivo, tentativi e impatto. Non selezionare arbitrariamente tra extractor e validator, non inventare valori e non trasformare un dubbio in una falsa certezza.

Errori di schema, associazione dataset/modello, formule o violazioni delle regole impediscono di dichiarare la consegna validata. Lacune della letteratura possono restare in un output valido se esplicitamente rappresentate come unavailable/Indeterminate/REVIEW_REQUIRED e se le conclusioni ne rispettano i limiti. Report e notebook devono rendere visibili i punti aperti.

### Freeze e benchmark

Non alterare un freeze storico. Se esiste una sintesi congelata, verificane integrità e rapporto temporale col benchmark. Se nuovi risultati primari richiedono una sintesi aggiornata, conserva il freeze precedente e crea una nuova versione con provenienza e motivo, prima del nuovo confronto col benchmark.

Se il benchmark è già stato consultato nella precedente esecuzione, dichiaralo: non affermare che la nuova sintesi sia indipendente o cieca. Isola comunque le fonti primarie dal benchmark e non modifica le conclusioni per ottenere concordanza. Una modifica di un risultato derivato richiede di controllare se sintesi e poolability restano sostenute, senza cambiarle automaticamente.

## Obiettivo

Costruire una pipeline agentica riproducibile per analizzare quattro studi full-text open access sul ruolo della radiomica ecografica nella predizione precoce della risposta alla terapia neoadiuvante nel carcinoma mammario.

Research question:

“Does ultrasound-based radiomics provide incremental predictive value for predicting response to neoadjuvant therapy in breast cancer beyond clinical and conventional ultrasound-based models?”

Domanda secondaria:

“How consistent is the reported predictive performance across different imaging timepoints, radiomics strategies, clinical models, deep-learning approaches and validation designs?”

La pipeline deve distinguere chiaramente:

- predictive performance assoluta;
- incremental value;
- baseline radiomics;
- early-treatment radiomics;
- delta radiomics;
- radiomics-only;
- clinical + radiomics;
- radiomics + deep learning;
- internal vs external validation.

NON assumere che un modello con AUC maggiore dimostri automaticamente incremental value.

## Studi Primari

Usa questi quattro studi.

--------------------------------------------------
PAPER 1 — YANG 2022
--------------------------------------------------

Titolo:
“Treatment Response Prediction Using Ultrasound-Based Pre-, Post-Early, and Delta Radiomics in Neoadjuvant Chemotherapy in Breast Cancer”

DOI:
10.3389/fonc.2022.748008

Full text open access Frontiers.

Aspetti chiave:
- breast cancer;
- NAC;
- baseline ultrasound radiomics;
- early-treatment radiomics;
- delta radiomics;
- clinical variables;
- validation cohort;
- direct comparison between radiomics signatures and combined nomogram.

--------------------------------------------------
PAPER 2 — WANG 2025 / BMC CANCER
--------------------------------------------------

Titolo:
“Integrative multimodal ultrasound and radiomics for early prediction of neoadjuvant therapy response in breast cancer: a clinical study”

DOI:
10.1186/s12885-025-14556-4

PMID:
40629283

PMCID:
PMC12239399

Full text open access.

Aspetti chiave:
- multimodal ultrasound;
- B-mode;
- SWE;
- CEUS;
- baseline and after two cycles;
- PyRadiomics;
- clinical-ultrasound model;
- radiomics-only model;
- combined model;
- train/validation cohorts.

--------------------------------------------------
PAPER 3 — TENGHUI/WU 2025
--------------------------------------------------

Titolo:
“Combination of ultrasound-based radiomics and deep learning with clinical data to predict response in breast cancer patients treated with neoadjuvant chemotherapy”

DOI:
10.3389/fonc.2025.1525285

Full text open access Frontiers.

Aspetti chiave:
- 643 patients;
- two institutions;
- radiomics;
- deep-learning features;
- clinical variables;
- combined/fusion model;
- internal validation;
- external cohort;
- direct model comparisons.

--------------------------------------------------
PAPER 4 — FRONTIERS 2024
--------------------------------------------------

Titolo:
“Machine learning for predicting neoadjuvant chemotherapy effectiveness using ultrasound radiomics features and routine clinical data of patients with breast cancer”

DOI:
10.3389/fonc.2024.1485681

Full text open access Frontiers.

Aspetti chiave:
- 231 patients;
- ultrasound radiomics;
- routine clinical variables;
- training and validation cohorts;
- feature selection;
- LASSO;
- machine-learning models;
- prediction of pathological complete response / treatment effectiveness.

## Benchmark Esterno

Usa come benchmark principale SOLO DOPO aver congelato la sintesi primaria:

Titolo:
“Ultrasound-based radiomics for early predicting response to neoadjuvant chemotherapy in patients with breast cancer: a systematic review with meta-analysis”

Anno:
2024

DOI:
10.1007/s11547-024-01783-1

PMID:
38630147

Questa review include 8 studi e deve essere usata come benchmark metodologico esterno.

NON usarla durante l’estrazione primaria.

Prima:
- analizza i 4 studi;
- produci la sintesi;
- salva synthesis_frozen.json.

Solo dopo:
- consulta la review;
- confronta conclusioni e principali limiti.

NON modificare retroattivamente la sintesi per farla coincidere con il benchmark.

## Schema Di Estrazione

Per ogni studio estrai almeno:

STUDY DESIGN
- study_id
- authors
- year
- country
- centers
- retrospective/prospective
- recruitment period
- N total
- train N
- validation N
- external validation N
- inclusion criteria
- exclusion criteria

PATIENT / DISEASE CHARACTERISTICS
- breast cancer subtype if reported
- stage
- age
- NAC/NAT regimen
- pathological endpoint
- pCR definition
- responder definition
- responder N
- non-responder N
- prevalence of target outcome

REFERENCE STANDARD
- surgery performed
- pathology assessment
- pCR/pathologic response definition
- timing of reference standard

ULTRASOUND
- modality
- B-mode
- SWE
- CEUS
- QUS if applicable
- transducer/scanner if reported
- acquisition timing
- pretreatment
- after cycle 1/2/etc.
- longitudinal imaging
- number of images per patient if reported

SEGMENTATION
- manual/automatic
- 2D/3D
- operator count
- operator expertise
- interobserver assessment
- segmentation software

RADIOMICS
- software
- initial feature count
- feature families
- preprocessing
- normalization
- discretization
- feature robustness testing
- feature selection method
- final selected features

MODEL
- radiomics-only
- clinical-only
- ultrasound-only
- combined clinical-radiomics
- deep learning
- radiomics + deep learning
- algorithm
- hyperparameter tuning
- CV strategy
- train/validation strategy
- external validation

TIMEPOINT ROLE
Classifica ogni modello come:
- baseline
- early-treatment
- delta
- longitudinal combined

PERFORMANCE
Per ogni modello e dataset role estrai:
- AUC
- 95% CI
- sensitivity
- specificity
- accuracy
- precision
- recall
- F1
- PPV
- NPV
- calibration
- Brier
- decision curve
- threshold
- p-value / DeLong comparison

Ogni metrica deve avere:
- study_id
- model_id
- dataset_role
- timepoint_role
- metric
- value
- CI_low
- CI_high
- source section
- provenance

## Incremental Value

Questa deve essere una delle parti centrali.

Per ogni studio identifica chiaramente i confronti:

A. radiomics vs clinical-only
B. radiomics vs conventional ultrasound
C. combined clinical+radiomics vs clinical-only
D. early-treatment radiomics vs baseline radiomics
E. delta radiomics vs baseline radiomics
F. radiomics+deep learning vs radiomics-only
G. fusion model vs individual component models

Per ogni confronto calcola, se possibile:

- delta AUC
- delta sensitivity
- delta specificity
- statistical comparison
- DeLong p-value
- calibration difference
- decision-curve/net-benefit difference

NON dichiarare incremental value solo perché:
- AUC è alta;
- combined model è numericamente migliore;
- validation performance è alta.

Classifica:

- Demonstrated
- Suggestive
- Not demonstrated
- Indeterminate

con una breve motivazione source-linked.


## Selezione e interpretazione dei confronti

Seleziona il risultato primario tra confronti equivalenti con questa priorità: external_validation > internal_validation > test > training. Equivalente significa stesso endpoint, contrasto di modelli e timepoint comparabili: non sostituire confronti diversi solo perché esiste una validation. Non usare training come primario quando esiste il relativo confronto validation. Training può comparire come dato secondario esplicitamente etichettato; da solo non soddisfa la definizione validation/test di Demonstrated o Suggestive.

Confronta AUC sullo stesso dataset e outcome; per confronti temporali espliciti conserva entrambi i timepoint. Calcola `delta_AUC = auc_a - auc_b` soltanto con valori verificabili. Non inferire significatività dalla differenza di AUC, dai singoli CI o da un test relativo a un altro dataset/contrasto.

| Classification | Regola |
| --- | --- |
| Demonstrated | Miglioramento sullo stesso validation/test dataset e confronto statistico diretto, appropriato e verificato a supporto. |
| Suggestive | Miglioramento numerico sullo stesso validation/test dataset, significatività non verificata. |
| Not demonstrated | Nessun miglioramento oppure confronto statistico diretto disponibile ma non significativo. |
| Indeterminate | Confronto assente, non isolabile, non compatibile o insufficiente per applicare le altre classi. |

Un risultato non significativo non prova equivalenza. Documenta test, contrasto, dataset, p-value, eventuali CI e criterio di significatività riportato; non applicare automaticamente p-value di training alla validation. Un fusion model vs clinical incorpora radiomics e deep learning: non attribuire il suo intero vantaggio alla sola radiomica.

### Confronti da ricercare e verificare

I numeri sotto sono riferimenti attesi da verificare sul full text e sulla provenance. Non sono dati già validati né risultati da imporre. Se la fonte riporta altro, conserva il valore verificato e documenta la discrepanza.

**FRONTIERS_2024, internal_validation**

- GBM clinical+radiomics vs GBM clinical: 0.863 vs 0.732, delta_AUC 0.131;
- GBM clinical+radiomics vs GBM radiomics-only: 0.863 vs 0.698, delta_AUC 0.165.

Verifica DeLong, p-value, CI o altre comparazioni dirette. Senza comparazione statistica verificata, Suggestive e non Demonstrated. Reason esemplificativa: “Combined clinical+radiomics performance exceeded the clinical-only model on the same internal validation set (ΔAUC=0.131), but a verified statistical comparison for this validation contrast was not identified.”

**WU_2025, external_validation**

AUC di riferimento: Clinical 0.666; Radiomics 0.822; Deep learning 0.874; Fusion 0.877.

- Fusion vs Clinical: delta_AUC 0.211;
- Fusion vs Radiomics: delta_AUC 0.055;
- Fusion vs Deep learning: delta_AUC 0.003.

Cerca comparazioni pairwise/DeLong/significatività nel full text. Senza test verificato, il miglioramento numerico supporta Suggestive; con test non significativo, Not demonstrated; Demonstrated solo con test appropriato favorevole verificato.

**WANG_2025**

Verifica i confronti Combined vs Clinical (p=0.006) e Combined vs Radiomics (p=0.042). Verifica dataset e contrasto prima di usarli come supporto. Cerca AUC esatte del validation set per Model_Combined, Model_Clinic e Model_RSA. Se recuperate, completa delta_AUC e rimuovi soltanto il REVIEW_REQUIRED sul valore approssimato risolto. Altrimenti conserva il flag e non inventare numeri.

**YANG_2022**

Delta RS vs RS1: p=0.086 → Not demonstrated. Per early vs baseline, senza test diretto verificato: Suggestive soltanto se il miglioramento è confrontabile sul medesimo validation set, altrimenti Indeterminate. Preferisci internal validation al training; non forzare confronti assenti.

### Schema obbligatorio

`outputs/incremental_value.csv`:

`study_id, comparison, model_a, model_b, dataset_role, timepoint_role, auc_a, auc_b, delta_AUC, statistical_test, p_value, classification, reason, source`

Per confronti temporali `timepoint_role` deve esplicitare il ruolo di entrambi i modelli. `source` identifica sezione/tabella/figura e studio; valori non verificabili restano mancanti, con reason e REVIEW_REQUIRED quando necessario. Non trasformare NR in zero.


## Endpoint Harmonization

Questa parte è molto importante.

Gli studi potrebbero non usare esattamente lo stesso endpoint.

Distingui chiaramente:

- pathological complete response (pCR)
- Miller–Payne response
- responder/non-responder
- major histological response
- other pathological response definitions

NON trattare endpoint diversi come equivalenti.

Crea:

outputs/endpoint_mapping.csv

con:
- study
- endpoint_name
- endpoint_definition
- binary mapping
- comparable_to_pCR
- notes

## Temporal Comparability

Gli studi possono usare immagini a momenti diversi.

Estrarre esplicitamente:

- baseline only
- after 1 cycle
- after 2 cycles
- mid-treatment
- post-treatment
- delta between timepoints

NON confrontare direttamente:
baseline AUC
vs
early-treatment AUC
vs
delta AUC

senza segnalarne la differenza.

## Methodological Considerations

NON usare una sezione pubblica chiamata:
“bias flags”
o
“risk heatmap”.

Usa terminologia più neutra:

“Methodological considerations”

Estrarre:

- single/multicenter
- internal/external validation
- selected cohort
- class imbalance
- image exclusions
- missing data
- acquisition standardization
- operator dependence
- patient-level splitting
- feature selection inside validation procedure
- external generalization

Non assegnare automaticamente giudizi tipo “high risk”.

Usa:
- observed
- unclear
- not reported
- not applicable

## Comparability

Usa esattamente nove criteri, senza duplicare endpoint/response definition o aggiungere model type allo score:

1. endpoint_definition
2. regimen
3. timepoint
4. imaging_modality
5. radiomics_strategy
6. comparator
7. validation
8. population
9. subtype

Per ogni criterio di ogni coppia assegna `aligned`, `partially_aligned`, `not_aligned` o `unavailable`, con valori originali e motivazione specifica. Valuta equivalenza semantica e clinica, non identità delle stringhe. Conserva le definizioni originali: la normalizzazione per il confronto non deve modificare i dati estratti. Non equiparare endpoint diversi soltanto perché entrambi sono binari. WU_2025 vs FRONTIERS_2024 deve riconoscere l'endpoint pCR/non-pCR come aligned quando le definizioni estratte lo confermano.

Null, NR e informazioni insufficienti sono unavailable, non mismatch. Assegna 1 punto ad aligned, 0.5 a partially_aligned e 0 a not_aligned. `evaluated_criteria` è il numero dei criteri diversi da unavailable. `alignment_score = punti / evaluated_criteria`, su scala 0–1. Non usare sempre il denominatore 9. Se nessun criterio è valutabile, lascia score e rating non assegnati e motiva l'insufficienza; non inventare un rating low.

Rating per gli score valutabili:

- high: score >= 0.75;
- moderate: 0.50 <= score < 0.75;
- low: score < 0.50.

Documenta le soglie nel report. Non modificare rating o soglie per ottenere un risultato desiderato. Esponi il denominatore, perché uno score basato su pochi criteri non equivale a evidenza completa. Non dedurre la poolability dal solo score.

### Population

- aligned: popolazione clinica sostanzialmente equivalente, stesso disease setting e treatment setting, nessuna importante differenza documentata di selezione;
- partially_aligned: stesso disease setting generale e treatment context, ma differenze di stage, metastatic status, eligibility, requisito biopsy/pathology, completamento della terapia, selezione o recruitment setting;
- not_aligned: popolazioni clinicamente sostanzialmente diverse, differenze rilevanti di disease spectrum, treatment setting o unità clinica tali da compromettere seriamente la comparabilità;
- unavailable: informazioni insufficienti per classificare.

“Newly diagnosed invasive breast carcinoma treated with NAC” vs “Pathologically confirmed breast cancer receiving NAC” non è automaticamente not_aligned. Se è verificabile il comune setting breast cancer/NAC, almeno partially_aligned, salvo differenze cliniche maggiori esplicitamente documentate. Non inferire equivalenza completa da informazioni mancanti.

### Subtype

- aligned: sostanzialmente gli stessi molecular subtypes, distribuzioni disponibili e sufficientemente simili;
- partially_aligned: principali subtypes inclusi in entrambi, ma distribuzioni precise assenti o diverse; oppure molecular subtype/receptor status generico vs elenco esplicito luminal/HER2/TNBC, quando è verificabile un case mix mult subtype;
- not_aligned: uno studio limitato a uno specifico subtype e l'altro no, oppure differenze biologiche sostanziali documentate nel case mix;
- unavailable: subtype non riportato in uno o entrambi, o informazioni insufficienti a stabilire il confronto.

La sola presenza del campo “molecular subtype reported” non prova la composizione della coorte. Non usare matching lessicale come proxy clinico; non introdurre soglie arbitrarie di similarità delle distribuzioni.

### Coppie e output

Valuta tutte le sei coppie:

- YANG_2022 vs WANG_2025;
- YANG_2022 vs WU_2025;
- YANG_2022 vs FRONTIERS_2024;
- WANG_2025 vs WU_2025;
- WANG_2025 vs FRONTIERS_2024;
- WU_2025 vs FRONTIERS_2024.

`outputs/comparability_detailed.csv` deve contenere 54 righe (sei coppie per nove criteri), con colonne:

`study_a, study_b, criterion, value_a, value_b, status, reason`

`outputs/comparability_matrix.csv` deve contenere sei righe, con colonne:

`study_a, study_b, alignment_score, evaluated_criteria, rating, reason`

Usa motivazioni clinicamente interpretabili, per esempio: “Both studies include patients with breast cancer receiving neoadjuvant treatment; eligibility and disease-spectrum details differ, so population comparability is partial rather than complete.” Evita “Reported characteristics differ.”

## Poolability

Questa volta NON assumere in anticipo che pooling sia impossibile.

La pipeline deve valutarlo.

Separare eventualmente:

- baseline radiomics studies
- early-treatment radiomics studies
- delta-radiomics studies
- pCR endpoint studies

Output:

poolability:
- justified
- partially justified
- not justified

Se solo un sottogruppo è sufficientemente comparabile:
scrivi “partially justified”.

NON produrre automaticamente una meta-analysis.

Se i dati non sono sufficientemente comparabili:
NON generare forest plot.

## Validation Agent

Implementa un secondo controllo sulle estrazioni critiche.

Verifica almeno:

- N
- endpoint definition
- responder N
- train/validation N
- AUC principali
- validation role
- comparator
- timepoint
- incremental-value comparison

Se extractor e validator non concordano:

REVIEW_REQUIRED

Non scegliere arbitrariamente.

## Provenance

Mantieni provenance per ogni campo importante.

Output:
outputs/evidence_provenance.csv

Campi:

study_id
variable
value
source_section
source_table
source_excerpt
source_identifier

Usa estratti brevi.

## Output Strutturati

Genera almeno:

outputs/
    evidence_matrix.csv
    evidence_provenance.csv
    performance_table.csv
    incremental_value.csv
    endpoint_mapping.csv
    timepoint_mapping.csv
    comparability_matrix.csv
    comparability_detailed.csv
    methodological_considerations.csv
    validation_checks.csv
    synthesis_frozen.json
    benchmark_comparison.md
    evidence_synthesis_report.html

## Visualizzazioni

Genera almeno:

1. Study design overview
2. AUC by model and dataset role
3. Baseline vs early vs delta radiomics comparison
4. Incremental-value comparison
5. Pairwise comparability matrix
6. Study → timepoint → model → validation → outcome workflow

NON produrre un forest plot salvo decisione esplicita:
poolability justified.

## Report Html

Struttura:

1. Research question
2. Selected studies
3. Source access
4. Clinical endpoint definitions
5. Imaging timepoints
6. Evidence extraction
7. Comparative evidence
8. Performance comparison
9. Incremental value
10. Methodological considerations
11. Cross-study comparability
12. Poolability decision
13. Final synthesis
14. Benchmark comparison
15. Limitations of the AI pipeline

KEY MESSAGE:

“High predictive performance does not by itself demonstrate incremental value.”

## Notebook

Aggiorna/genera:

agentic_evidence_synthesis.ipynb

Struttura narrativa:

1. Research question
2. Why this problem matters
3. Selected studies
4. Agentic workflow
5. Structured extraction
6. Endpoint harmonization
7. Timepoint harmonization
8. Evidence matrix
9. Performance comparison
10. Incremental value
11. Comparability
12. Poolability
13. Final synthesis
14. Benchmark check
15. Limitations

Il notebook deve importare le funzioni dai moduli.

NON mettere tutta la logica nel notebook.

## Agentic Workflow

Mantieni chiaramente separati:

1. ingestion
2. factual extraction
3. validation
4. methodological interpretation
5. comparability
6. synthesis
7. benchmark

L’agente NON deve:
- correggere dati sulla base della propria conoscenza;
- inventare valori mancanti;
- armonizzare endpoint senza segnalarlo;
- fondere risultati provenienti da dataset role diversi.

## Tests

Mantieni i test esistenti e aggiungi test mirati. Se un test codifica una regola metodologica incompatibile con questa specifica, documenta il conflitto e aggiorna la sola aspettativa errata; non indebolire i controlli per farli passare.

Aggiungi test per:

1. metriche sempre associate a dataset_role;
2. metriche sempre associate a timepoint_role;
3. endpoint definition presente;
4. provenance presente per AUC principali;
5. no pooling se endpoint/timepoint incompatibili;
6. REVIEW_REQUIRED in caso di discordanza;
7. synthesis freeze effettuato prima del benchmark;
8. nessun valore NR trasformato automaticamente in numero;
9. nessun confronto incremental-value senza comparator.

## Criterio Di Successo

Il successo NON consiste nel trovare il modello con AUC più alta.

Il successo consiste nel dimostrare che la pipeline:

- legge quattro studi completi;
- struttura l’evidenza;
- distingue endpoint diversi;
- distingue timepoint diversi;
- distingue absolute performance da incremental value;
- confronta correttamente radiomics, clinical model e deep learning;
- conserva provenance;
- identifica dove serve human review;
- decide responsabilmente se gli studi possono essere quantitativamente aggregati.

## Test di accettazione della pipeline

Oltre ai test di base, verifica:

1. unavailable non è mismatch e non entra nel denominatore;
2. score usa solo criteri valutabili e gestisce zero criteri valutabili;
3. WU_2025 vs FRONTIERS_2024 riconosce pCR come aligned quando le definizioni primarie lo confermano;
4. validation equivalente prevale sul training come confronto primario;
5. delta_AUC corretto, compresi i cinque delta di riferimento FRONTIERS_2024/WU_2025 se i valori sono confermati;
6. Demonstrated richiede un test diretto, appropriato, favorevole e verificato sul dataset e contrasto corretti;
7. population semanticamente simili ma lessicalmente diverse non sono automaticamente not_aligned;
8. breast cancer receiving NAC vs invasive breast carcinoma treated with NAC è almeno partially_aligned salvo differenza clinica maggiore documentata;
9. molecular subtype/receptor status generico vs luminal/HER2/TNBC non è automaticamente not_aligned;
10. subtype not_aligned richiede una differenza clinicamente significativa dello spectrum;
11. la rivalutazione di un criterio non modifica criteri indipendenti;
12. risultati strutturati e rappresentazioni HTML/notebook concordano;
13. riesami senza nuove evidenze terminano con REVIEW_REQUIRED, senza loop infinito;
14. dati sorgente e freeze storici restano integri; correzioni fattuali conservano provenance e storia;
15. a parità di input, configurazione e decisioni validate, la rigenerazione riproduce score, delta e classificazioni.

Esegui i test esistenti e quelli mirati. Verifica almeno un percorso completo dalle fonti ai risultati presentati. Controlla la resa del report e l'esecuzione del notebook col venv esistente. Non dichiarare verifiche non eseguite.

## Consegna finale

Comunica:

1. componenti, fonti e artefatti riutilizzati, corretti o integrati;
2. interprete/venv utilizzato ed eventuali sole dipendenze mancanti aggiunte;
3. stato di accesso e validazione dei quattro full text;
4. copertura dei campi e provenance;
5. comparability: score, criteri valutabili, rating e motivazioni per le sei coppie;
6. incremental value: dataset primario, modelli, delta_AUC, test, classificazioni e fonti;
7. REVIEW_REQUIRED residui e loro impatto sulle conclusioni;
8. decisione di poolability e sintesi in massimo dieci righe;
9. confronto col benchmark e stato del freeze, inclusa eventuale esposizione precedente al benchmark;
10. file aggiornati/prodotti, test e risultati, verifiche di integrità;
11. comando effettivamente verificato per rieseguire la pipeline nel venv esistente.

Consegna gli output come validati soltanto se i controlli obbligatori sono soddisfatti. In caso contrario indica con precisione ciò che resta bloccato e non presentare gli artefatti provvisori come definitivi.
