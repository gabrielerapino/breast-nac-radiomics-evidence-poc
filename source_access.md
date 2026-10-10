# Accesso alle fonti della ricostruzione

I quattro full text sono stati acquisiti dall'editore e archiviati localmente durante questa ricostruzione. `inputs/source_manifest.json` ne registra SHA-256 e dimensioni. L'identità DOI, la disponibilità del corpo dell'articolo e delle tabelle vengono controllate a ogni esecuzione.

| Studio | Fonte | Archivio e stato |
|---|---|---|
| Yang 2022 | https://www.frontiersin.org/journals/oncology/articles/10.3389/fonc.2022.748008/full | `sources/YANG_2022.html`: full text e quattro tabelle; incongruenze su periodo, percentuali e specificity del nomogramma preservate |
| Wang 2025 | https://link.springer.com/article/10.1186/s12885-025-14556-4 | `sources/WANG_2025.html`, `WANG_2025_table3.html`, sei DOCX supplementari: full text; esatte AUC validation e dataset dei test ancora aperti |
| Wu 2025 | https://www.frontiersin.org/journals/oncology/articles/10.3389/fonc.2025.1525285/full | `sources/WU_2025.html`: full text e due tabelle; AUC esterne fusion/deep, feature counts, subtype totals e split numerici ancora aperti |
| Zhou 2024 | https://www.frontiersin.org/journals/oncology/articles/10.3389/fonc.2024.1485681/full | `sources/FRONTIERS_2024.html` e `FRONTIERS_2024_figure5.webp`: full text, cinque tabelle e figura dei confronti statistici; CI clinical validation e sensitivity/recall incoerenti preservati |

Estratti testuali e copie tabulari JSON sono ausili per l'ispezione; l'estrazione normale legge gli HTML originali. Le narrative sono trascrizioni curate con indice del paragrafo, hash, sezione e un estratto breve. I test e gli intervalli della Figure 5 sono trascrizioni visive curate, legate all'hash della figura. Nessuna maggioranza tra parser risolve una contraddizione presente nell'articolo.

La review DOI 10.1007/s11547-024-01783-1 è stata consultata dopo il primo nuovo freeze. L'accesso dell'editore è limitato all'abstract e all'anteprima in abbonamento: `benchmark/review_abstract.html`. Non viene affermata una lettura del full text della review. La vecchia pipeline aveva già consultato il benchmark: questa ricostruzione non è cieca, pur isolando il benchmark dalla nuova estrazione primaria.

Per i valori mancanti Wang sono stati ispezionati full text, Table 3 e tutti i sei supplementi; non sono emerse esatte AUC del validation set. Il riesame si ferma senza inferire numeri dal valore approssimato o dalle percentuali.
# Sanitizzazione delle copie HTML

Le tre pagine Frontiers archiviate contenevano una chiave Google Maps nella configurazione del sito, estranea ai contenuti scientifici. Il valore è stato sostituito con `REDACTED_GOOGLE_MAPS_API_KEY`; paragrafi, tabelle e dati degli articoli sono invariati. `source_sanitization.json` registra hash originali e nuovi hash. Il manifest corrente verifica le copie sanitizzate; i freeze storici conservano i digest delle precedenti copie.

