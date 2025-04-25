# Development-ERP

Το πρότζεκτ βασίζεται στη χρήση ενός ERP συστήματος που παρέχει τις απαραίτητες πληροφορίες για τις προβλέψεις που παράγει ο ML Αλγόριθμος. Για αυτόν τον σκοπό, δημιουργήθηκαν τα παρακάτω components, τα οποία εξασφαλίζουν ένα ολοκληρωμένο σύστημα ERP σε συνδυασμό με τα Development δεδομένα του πρότζεκτ:

- **DB App - Δημιουργίας Development Πινάκων (`create-db-tables-app`)**: Δημιουργία (συμπληρωματικών) πινάκων στη βάση δεδομένων `MySQL` του ERP, με δεδομένα που σχετίζονται με το Development πρότζεκτ.
- **Backend App - Python-FastAPI (`erp-fastapi`)**: Παροχή APIs για πρόσβαση στους πίνακες Development που υπάρχουν στην ERP βάση.
- **PHP ERP Πλατφόρμα - Dolibarr (`dolibarr`)**: Διαχείριση επιχειρηματικών λειτουργιών (π.χ., προβολή πινάκων Development) μέσω του περιβάλλοντος ERP (για περισσότερα [εδώ](https://github.com/Dolibarr/dolibarr)).

Όλα τα παραπάνω components ενορχηστρώνονται και λειτουργούν συνδυαστικά μέσω του Docker Compose, εξασφαλίζοντας μια ευέλικτη και ολοκληρωμένη υποδομή.

## Εκτέλεση με Docker

**1.**Βεβαιωθείτε ότι βρίσκεστε στον root φάκελο `development-erp`

**2.**Τοποθετήστε το αρχείο `development-erp_mysql-data.tar.gz` στον φάκελο αυτόν <br>

**3.**Τοποθετήστε το αρχείο `.env` στον root φάκελο του project και τα υπόλοιπα αντίστοιχα `.env` στους επιμέρους υποφακέλους (κάθε υποφάκελος αντιστοιχεί σε ξεχωριστό project-app).

**4.**Αντιγράψτε τον κωδικό του πεδίου`MYSQL_ROOT_PASSWORD` από το `.env` και επικολλήστε το στο πεδίο `$dolibarr_main_db_pass=` του αρχείου `/dolibarr/htdocs/conf.php`.

* **Όλα τα παραπάνω αρχεία πρέπει να σας δοθούν από τον υπεύθυνο του έργου.**

**5.**(**Για επανεκκίνηση της DB με τα default δεδομένα**) Στον root φάκελο `development-erp`, ανοίξτε π.χ., το **PowerShell** και εκτελέστε την παρακάτω εντολή: <br>
`docker run --rm -v development-erp_mysql-data:/volume -v ${PWD}:/backup alpine sh -c "cd /volume && tar xvf /backup/development-erp_mysql-data.tar.gz --strip 1"`

**6.**Εκτελέστε το αρχείο Docker Compose με την εντολή `docker-compose up --build`