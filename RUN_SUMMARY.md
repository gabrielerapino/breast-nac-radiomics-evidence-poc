# Consegna del POC

La pipeline è stata ricostruita nella sola cartella `breast_nac_ultrasound_radiomics_v1`. L’originale è conservato; codice, estrazioni e test ereditati sono recuperabili in `archive/legacy_snapshot.tar.gz`. Sono riutilizzati venv, DOI e percorsi di consegna; i moduli, i dati verificati e le viste sono stati ricostruiti.

**Stato: CHECKS_PASSED_WITH_REVIEW_REQUIRED.** I controlli deterministici passano; le informazioni mancanti e le contraddizioni degli articoli restano aperte. Le stime interessate non sono presentate come adjudicate o definitive.

## Artefatti da aprire

- [Report HTML](outputs/evidence_synthesis_report.html): 15 sezioni e sei figure incorporate.
- [Notebook eseguito](agentic_evidence_synthesis.ipynb): 18 celle di codice eseguite in sequenza nel venv.
- [Prompt unico](RUN_PROMPT.md) e [AGENTS.md](AGENTS.md): mandato e specifica concordati.
- [Verifiche](outputs/verification_summary.json), [rettifiche](outputs/revision_history.csv) e [test corretti](TEST_CHANGES.md).

## Ambiente e accesso alle fonti

Interprete utilizzato: `/home/gabriele/cancer-research/venv/bin/python`; Python 3.12.3. Nessuna dipendenza installata o aggiornata. Versioni in `requirements.txt` e `outputs/verification_summary.json`.

Quattro full text sono archiviati, con verifica dell’identità DOI, presenza del corpo/tabelle e SHA-256. Wang Table 3 e tutti i sei supplementi sono stati consultati; Zhou Figure 5 è stata ispezionata per test e intervalli. Il log dettagliato è `source_access.md`. Il benchmark è disponibile soltanto come abstract/anteprima dell’editore; nessuna lettura del suo full text viene dichiarata.

## Copertura e provenienza

49 righe modello/dataset; 46 AUC esatte trascritte e tre AUC validation Wang mancanti. Le tabelle originali includono tutti i dieci algoritmi radiomici di Zhou. Le figure principali mostrano i modelli selezionati. 515 righe di provenance, con fonti per AUC, metriche, CI e campi narrativi.

| Studio | Campi disponibili / attesi | Campi mancanti | Righe performance | AUC note |
|---|---:|---:|---:|---:|
| YANG_2022 | 44/54 | 10 | 8 | 8 |
| WANG_2025 | 41/54 | 13 | 9 | 6 |
| WU_2025 | 41/54 | 13 | 8 | 8 |
| FRONTIERS_2024 | 49/54 | 5 | 24 | 24 |

La copertura considera NR e “Not reported” mancanti. Gli anchor source-bound possono includere campi aggiuntivi o esplicitamente mancanti: il loro conteggio non è una percentuale di validazione. MATCH conferma numeri con parser/distinta lettura source-based; SOURCE_BOUND identifica una trascrizione o interpretazione curata dall’agente costruttore. Nessuna equivalenza viene attribuita al consenso tra parser.

## Comparabilità delle sei coppie

| Coppia | Score | Criteri valutabili | Rating | Motivo principale |
|---|---:|---:|---|---|
| YANG_2022 / WANG_2025 | 0.611111 | 9/9 | moderate | 5.5/9 evaluable criteria; unavailable excluded. endpoint_definition: Different targets: RECIST versus MHR; binary coding does not make them equivalent. |
| YANG_2022 / WU_2025 | 0.5 | 8/9 | moderate | 4/8 evaluable criteria; unavailable excluded. endpoint_definition: Different targets: RECIST versus pCR; binary coding does not make them equivalent.; regimen: The primary source does not support enough detail for this semantic comparison. |
| YANG_2022 / FRONTIERS_2024 | 0.666667 | 9/9 | moderate | 6/9 evaluable criteria; unavailable excluded. endpoint_definition: Different targets: RECIST versus pCR; binary coding does not make them equivalent. |
| WANG_2025 / WU_2025 | 0.4375 | 8/9 | low | 3.5/8 evaluable criteria; unavailable excluded. endpoint_definition: Different targets: MHR versus pCR; binary coding does not make them equivalent.; regimen: The primary source does not support enough detail for this semantic comparison. |
| WANG_2025 / FRONTIERS_2024 | 0.555556 | 9/9 | moderate | 5/9 evaluable criteria; unavailable excluded. endpoint_definition: Different targets: MHR versus pCR; binary coding does not make them equivalent. |
| WU_2025 / FRONTIERS_2024 | 0.625 | 8/9 | moderate | 5/8 evaluable criteria; unavailable excluded. regimen: The primary source does not support enough detail for this semantic comparison. |

La coppia pCR riconosce la categoria comune; la formulazione operativa di Wu resta da chiarire. La comune acquisizione baseline è parzialmente allineata, mentre le performance radiomiche baseline e longitudinali restano distinte per il pooling. Tutte le 54 motivazioni sono in `outputs/comparability_detailed.csv`.

## Incremental value: confronti primari disponibili

| Studio | Modello A / modello B | Dataset | ΔAUC | Test / p | Classe |
|---|---|---|---:|---|---|
| YANG_2022 | RS2 / RS1 | internal_validation | 0.068 | NR / NR | Suggestive |
| YANG_2022 | Delta RS / RS1 | internal_validation | -0.011 | NR / NR | Not demonstrated |
| YANG_2022 | Nomogram RS1+RS2+Ki-67 / RS1 | internal_validation | 0.141 | NR / NR | Suggestive |
| YANG_2022 | Nomogram RS1+RS2+Ki-67 / RS2 | internal_validation | 0.073 | NR / NR | Suggestive |
| WANG_2025 | Model_Combined / Model_Clinic | internal_validation | NR | NR / NR | Indeterminate |
| WANG_2025 | Model_Combined / Model_RSA | internal_validation | NR | NR / NR | Indeterminate |
| WANG_2025 | RSA early / RSA baseline | training | 0.143 | NR / NR | Indeterminate |
| WANG_2025 | RSA delta / RSA baseline | training | 0.098 | NR / NR | Indeterminate |
| WU_2025 | Radiomics / Clinical | external_validation | 0.156 | DeLong / 0.029 | Demonstrated |
| WU_2025 | Fusion / Clinical | external_validation | 0.211 | DeLong / 0.003 | Demonstrated |
| WU_2025 | Fusion / Radiomics | external_validation | 0.055 | NR / NR | Suggestive |
| WU_2025 | Fusion / Deep learning | external_validation | 0.043 | NR / NR | Suggestive |
| FRONTIERS_2024 | GBM radiomics / GBM clinical | internal_validation | -0.034 | NR / NR | Not demonstrated |
| FRONTIERS_2024 | GBM clinical+radiomics / GBM clinical | internal_validation | 0.131 | DeLong / 0.01 | Demonstrated |
| FRONTIERS_2024 | GBM clinical+radiomics / GBM radiomics | internal_validation | 0.165 | DeLong / 0.005 | Demonstrated |

Fonti e motivi per ciascun contrasto sono in `outputs/incremental_value.csv`. I test Zhou validation sono quelli di Figure 5H, p=.010 e .005. I test Wu in Table 2 hanno Clinic come benchmark; non vengono applicati a fusion versus radiomics/deep learning. Il test Yang p=.086 resta un confronto di training secondario. I p-value Wang .006/.042 non vengono trasferiti alla validation per l’attribuzione ambigua del dataset.

Wu: ΔAUC fusion−deep è .043 con entrambe le AUC di Table 2; .017 con entrambe le AUC del testo; il precedente .003 univa le due versioni. Le alternative sono preservate in `outputs/source_sensitivity.csv`. La significatività dei contrasti multimodali non isola il contributo della sola radiomica.

## Questioni aperte e impatto

18 check REVIEW_REQUIRED, non 18 problemi indipendenti: alcuni si riferiscono allo stesso valore o conflitto. Nessuna discordanza deterministica rimane tra estrazione e parser numerico indipendente. Le discordanti estrazioni prodotte artificialmente nei test bloccano la consegna.

- Yang: periodo di arruolamento, percentuali errate nel testo, specificity del nomogramma e dataset dei suoi test. Conteggi, AUC e confronti validation restano separati dalle discrepanze.
- Wang: AUC validation esatte, attribuzione dataset dei test e conteggi complessivi degli outcome. Nessun valore viene ricavato arrotondando 51.5% o interpretando ~0.90 come esatto.
- Wu: AUC fusion/deep esterne discordanti, feature counts, subtype totals, definizione operativa pCR e split numerici. Le alternative sono visibili e le stime di effetto interessate provvisorie.
- Zhou: CI clinical validation che esclude l’AUC e sensitivity/recall discordanti. Il CI inutilizzabile resta NR; il punto AUC e i p-value diretti sono tracciabili.

## Poolability e sintesi

- Four prespecified studies; 3 endpoint categories (RECIST, Miller–Payne MHR, pCR). This is not an exhaustive systematic review.
- Available primary matched contrasts: 4 Demonstrated, 5 Suggestive, 2 Not demonstrated, 4 Indeterminate. Contrasts within a study are correlated and are not independent study counts.
- Zhou 2024 has a direct clinical+radiomics versus clinical-only baseline validation contrast supported by Figure 5H; it provides evidence within one small internal cohort.
- Wu 2025 validates multimodal models externally, but longitudinal information, clinical and deep features complicate attribution to radiomics alone; table/prose discrepancies leave effect sizes provisional.
- Wang 2025 exact validation AUCs and dataset attribution of tests remain unresolved. Yang distinguishes early and delta from baseline; training tests are not borrowed for validation.
- Poolability: not justified. No joint stratum contains two independent studies with the same endpoint, imaging role, model composition and validation role. The pCR pair uses baseline versus pre+midpoint radiomics; operational pathology and source precision also need review. AUC differences alone cannot supply the within-patient covariance needed to pool incremental effects.
- 18 REVIEW_REQUIRED checks remain visible. Clinical usefulness beyond discrimination is not established by AUC differences alone.

## Benchmark e freeze

Il nuovo confronto avviene dopo il freeze corrente; la precedente esposizione al benchmark è dichiarata. La review copre otto studi e una ricerca fino a gennaio 2023, quindi non include i due studi del 2025. Il suo riassunto di accuratezza non misura gli stessi contrasti incrementali. L’interpretazione prudente è coerente con i limiti descritti nell’abstract, senza trasferirne numeri all’estrazione primaria.

Freeze corrente SHA-256: `34343e5eae96d4678c1340d1b0a720f0474210a345c2b65f08f53c14ea533c01`. Le versioni sono in `outputs/freezes/`; il freeze storico è preservato in `archive/` e verificato contro l’originale. Gli input, AGENTS.md e i moduli sono identificati per hash nel freeze. Il benchmark registra il digest senza alterarlo.

## Verifiche realmente eseguite

- 39 test passati, zero fallimenti. Comprendono numeri alterati, split scambiati, schema, criteri/denominatori, casi mancanti, significatività, dataset priority, freeze, CSV/HTML e una possibilità positiva di pooling su fixture sintetica.
- Rigenerazione ripetuta: 36 artefatti confrontati mediante SHA-256, tutti identici (CSV, JSON, SVG, PNG, HTML e confronto benchmark).
- Un percorso source→estrazione→validation→ΔAUC→test→CSV→HTML verificato: Zhou clinical+radiomics .863 versus clinical .732, Δ=.131, p=.010 sul validation set.
- Notebook: 18 celle eseguite in processo con IPython, output preservati e schema nbformat validato. Non è un test di kernel Jupyter: i socket sono bloccati dal workspace.
- Report: 15 sezioni, sei SVG incorporati, ID univoci, navigazione interna valida e valori incorporati uguali ai CSV/freeze. Tutte le sei figure sono state ispezionate visivamente. La resa completa nel browser non è verificata: Chromium è bloccato dalle restrizioni del workspace.

## Riesecuzione verificata

```bash
cd /home/gabriele/cancer-research/meta-analysis-demo/breast_nac_ultrasound_radiomics_v1
/home/gabriele/cancer-research/venv/bin/python -B run_pipeline.py
/home/gabriele/cancer-research/venv/bin/python -B -m unittest discover -s tests -v
/home/gabriele/cancer-research/venv/bin/python -B scripts/execute_notebook.py
```

Gli output comprendono tutti i CSV/JSON prescritti, il confronto benchmark, report, notebook, sei figure SVG/PNG, sottogruppi candidati, copertura, sensibilità alle fonti e traccia delle rettifiche. Il comando normale non richiede rete.
