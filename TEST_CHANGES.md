# Rettifica dei test ereditati

L'intera versione precedente dei test è recuperabile in `archive/legacy_snapshot.tar.gz`. I tre moduli di test conservano i loro nomi; le aspettative ora seguono le fonti e le regole, anziché un'istantanea dei vecchi output.

| Aspettativa precedente | Correzione e motivazione |
|---|---|
| Wang validation Suggestive e colonna `statistical_comparison` | Indeterminate con AUC esatte mancanti e attribuzione dataset dei test ambigua. Usa lo schema `statistical_test`/`p_value` prescritto. |
| Wu fusion − deep learning = 0.003 | Table 2 dà .877 − .834 = .043; il precedente .003 univa Table 2 fusion con deep .874 del testo. Si conservano anche le alternative e la review. |
| Zhou classificato sulla sola frase di significatività | Figure 5H è archiviata e ispezionata: clinical vs combined p=.010; radiomics vs combined p=.005. Test diretti verificati, non forzati a Suggestive. |
| Popolazione/subtype devono coincidere con vecchi CSV | I test interrogano la logica semantica e includono casi mancanti/disgiunti; le distribuzioni incomplete non diventano equivalenza completa. |
| Hash fisso dei sette criteri non corretti | Si controlla che modificare population non alteri gli altri criteri. Nessun hash blocca legittime nuove evidenze. |
| Freeze `benchmark_consulted=False` inteso come cecità | Il nuovo run primario precede il benchmark, ma `previous_benchmark_exposure=True` dichiara la storia reale. |
| Poolability sempre `not justified` | Il caso reale non è poolabile; un caso sintetico sufficientemente compatibile deve poter risultare `partially justified`. Nessun esito è imposto in anticipo. |
| Presenza di provenance come unica prova di correttezza | Test aggiuntivi alterano AUC e split e verificano il secondo parser; si conserva la distinzione SOURCE_BOUND/MATCH. |

Sono verificati inoltre nove criteri per sei coppie, denominatore corretto e caso zero, associazioni delle metriche, assenza di comparator, riesame limitato, test appropriato per Demonstrated, conservazione dei freeze e concordanza CSV/report/moduli. I test sintetici non entrano negli output della demo.
