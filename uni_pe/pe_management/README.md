# Applicazione per il monitoraggio iniziative di Public Engagement

Questo strumento consente l'inserimento e il monitoraggio dei dati relativi alle iniziative di Public Engagement.

Elementi di base:

- gestione iniziative ex-ante ed ex-post;
- multi-tenant;
- gestione di diversi livelli di accesso;
- notifiche e-mail;
- log;
- statistiche e reportistica *(work in progress)*.

### Ex-ante ed ex-post

Sono gestite tutte le iniziative nelle due varianti possibili:

- **ex-ante**: iniziative caricate in anticipo rispetto alla data di inizio. Per questa tipologia è previsto l'inserimento dei dati informativi, non di quelli di monitoraggio, e possono essere richiesti patrocinio e promozione sui canali istituzionali;
- **ex-post**: iniziative caricate dopo essere terminate. Per queste i dati da inserire includono anche quelli di monitoraggio. Nonostante sia comunque previsto un workflow di approvazione, non è possibile richiede il patrocinio e la promozione.

### Multi-tenant

L'applicazione consente la definizione di diverse strutture, ognuna delle quali può gestire in autonomia il flusso di lavorazione delle singole iniziative ad essa afferenti. Ad ogni struttura vengono associati gli operatori delegati all'espletamento delle attività di validazione e concessione patrocinio.

### Utenti e livelli di accesso

Sono previste 3 tipologie di utenti:

- referenti (o delegati) dell'iniziativa;
- operatori di struttura:
	- *validazione*;
	- *concessione del patrocinio*.
- operatori di Ateneo.

**Referenti (o delegati)**

I referenti inseriscono le iniziative, avendo cura di compilare tutte le sezioni, e ne richiedono la validazione. Inseriscono i dati di monitoraggio se l'iniziativa è terminata.

Possono modificare i dati e annullare la richiesta di validazione fino alla presa in carico di un operatore di struttura.

E', inoltre, sempre consentita la cancellazione dell'iniziativa in quanto l'utente è reputato "proprietario" dell'inserimento.

**Operatori di struttura (validazione)**

Una volta prese in carico le iniziative di competenza della struttura, gli operatori procedono alla validazione dei dati. Questa operazione può concludersi positivamente o negativamente (in questo caso è necessario che l'operatore specifichi una motivazione). 

E' consentita la modifica dei dati inseriti dal referente o dal suo delegato.

**Operatori di struttura (patrocinio)**

Se per l'iniziativa è stato richiesto il patrocinio, le iniziative valutate positivamente dagli operatori di struttura validatori vengono prese in carico dagli operatori addetti al patrocinio che, in base a un processo interno alla struttura, caricano l'esito della procedura di assegnazione del patrocinio. 

Come per la validazione, questa operazione può concludersi con esito positivo o negativo e, nel secondo caso, è richiesto l'inserimento di una motivazione.

**Operatori di Ateneo**

Gli operatori di Ateneo rappresentano la figura con privilegi più elevati e accedono a tutte le iniziative inserite. 

Hanno la facoltà di:

- modificare i dati delle iniziative valutate positivamente dalle strutture, tranne quelle per cui è stato concesso il patrocinio (cosi da non alterare i dati su cui si è basata questa scelta);
- disabilitare (e riabilitare) le iniziative non pertinenti;
- procedere al caricamento di iniziative ex-post bypassando il flusso di gestione che coinvolge le singole strutture.

### Notifiche e-mail

Ogni step di avanzamento del flusso di lavorazione di ogni istanza scatena l'invio di e-mail di notifica agli attori coinvolti nella gestione. 

E' previsto, contestualmente all'approvazione dell'iniziativa da parte degli operatori di struttura, l'invio di messaggi agli uffici responsabili della promozione sui canali istituzionali qualora questa opzione sia stata scelta in fase di inserimento.

Naturalmente il referente (che è il "proprietario" dell'iniziativa) è sempre aggiornato ad ogni cambiamento di stato della sua richiesta.

### Log

La scheda di dettaglio di ogni iniziativa è corredata da una sezione che comprende l'elenco di tutti gli aggiornamenti effettuati, per garantire un livello di trasparenza elevato nei confronti degli utenti coinvolti nel workflow.