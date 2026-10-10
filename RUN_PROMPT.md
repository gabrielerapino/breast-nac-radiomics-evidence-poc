# Mandato unico per costruire o ricostruire il POC

Lavora in questa cartella e segui `AGENTS.md`. Costruisci una pipeline deterministica, riproducibile e offline per la sintesi dei quattro studi prespecificati, dall'acquisizione delle fonti alla decisione sul pooling, al confronto con il benchmark e alla consegna di report HTML e notebook.

Riusa il venv esistente. Conserva uno snapshot recuperabile e l'integrità dei freeze storici. Puoi ricostruire i componenti precedenti non coerenti con la specifica. Non considerare le vecchie estrazioni come validate: verifica i fatti critici sui full text, archivia le fonti con hash, registra provenance e rettifiche e distingui estrazioni da interpretazioni.

Non usare agenti LLM o servizi API a runtime. Implementa un secondo controllo source-based, con un parser numerico separato, e documenta quali mappature semantiche sono curate dall'agente costruttore. Non dichiarare verifiche indipendenti che non siano state realmente eseguite.

Completa i riesami e i test internamente senza richiedere prompt correttivi. Le discrepanze degli articoli e le informazioni assenti devono restare visibili come REVIEW_REQUIRED o NR; non imporre i numeri attesi. Non inventare significatività, precisione, split o matrici di confusione. Valuta i sottogruppi sulla base dei dati e non avviare automaticamente una meta-analisi.

Congela la sintesi primaria prima del nuovo confronto col benchmark e dichiara l'esposizione precedente. Crea tutte le viste dagli stessi risultati verificati. Consegna il POC con comandi effettivamente eseguiti, risultati dei controlli, decisione sul pooling e limiti. Per restrizioni del workspace, descrivi separatamente le verifiche disponibili e quelle non eseguibili.
