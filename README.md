# Development Project

## Περιγραφή

Το έργο **Development** αποσκοπεί στη δημιουργία προβλέψεων ζήτησης (ενσωματώνοντας εκτιμήσεις ποσοτήτων ανά SKU) καθώς και στη βελτιστοποίηση της διαχείρισης αποθεμάτων και της δρομολόγησης οχημάτων. Όλες οι διαδικασίες βασίζονται σε δεδομένα από το ERP σύστημα του χρήστη.

### Χαρακτηριστικά

* <u>Διαχείριση Μετρήσεων SKU</u>:
    - Καταγράφει δεδομένα που σχετίζονται με περιβαλλοντικούς και εξωτερικούς παράγοντες (π.χ., web scraping, google trends, δεδομένα καιρού, sentiment analysis κλπα).
    - Υποστηρίζει ανάλυση και μοντελοποίηση ζήτησης.

* <u>Προβλέψεις Ποσοτήτων SKU</u>:
    - Αποθηκεύει τις εβδομαδιαίες προβλέψεις ζήτησης για κάθε SKU.
    - Παρακολουθεί σφάλματα πρόβλεψης για αξιολόγηση απόδοσης μοντέλων Μηχανικής Μάθησης.

* <u>Βελτιστοποίηση Αποθέματος</u>:
    - Αποθηκεύει δεδομένα για βέλτιστες παραγγελίες και σημεία αναπαραγγελίας.
    - Μειώνει το κόστος διατήρησης, εξάντλησης και μεταφοράς αποθέματος.

* <u>Βελτιστοποίηση Δρομολόγησης Οχημάτων</u>:
    - Καταγράφει δεδομένα δρομολογίων και συνολικό κόστος διανομής.
    - Βελτιστοποιεί τα δρομολόγια των οχημάτων λαμβάνοντας υπόψη κυκλοφοριακές συνθήκες.

### **Figma Link [here](https://www.figma.com/board/SYBXYTliEC9o7ELte12N9v/DEVELOPMENT-DIAGRAMS?node-id=0-1&t=og2jENgD23ouIRLo-1)**
![Component Diagram final (V3 project).png](https://bitbucket.org/repo/kxxq4RR/images/3805833640-Component%20Diagram%20final%20%28V3%20project%29.png)

---

## Εκτέλεση με Docker

**1.**Τοποθετήστε τα αντίστοιχα `.env` και `config` αρχεία στους ανάλογους φακέλους (κάθε φάκελος είναι και ένα διαφορετικό πρότζεκτ-app). **Τα παρακάτω αρχεία πρέπει να σας δοθούν από τον υπεύθυνο του έργου**:

* **`development-erp`**
    - `development-erp_mysql-data.tar.gz`
    - `create-erp-development-db-tables-app/data/order_item.csv`
    - `create-erp-development-db-tables-app/data/product_sku.csv`
    - `create-erp-development-db-tables-app/data/competition.csv`
    - `create-erp-development-db-tables-app/.env`
    - `dolibarr/htdocs/conf.php` (_με τον root κωδικό της βάσης_)
    - `erp-fastapi/.env`
    - `.env`

* **`development-ml`**
    - `development-ml_mldata.tar.gz`
    - `create-ml-development-db-tables-app/.env`
    - `ml-app/.env`
    - `sku_metrics_components_app/.env`
    - `sku_metrics_components_app/configs/chromedriver-win64/` (_automatically downloaded by Docker_)

* **`development-web-app`**
    - `development-web-app_pgdata.tar.gz`
    - `development-db/.env`
    - `development-db/app/configs/users.json`
    - `development-db/app/configs/users_erp_api.json`
    - `development-backend/.env`
    - `development-frontend/.env`

**2.**(**Για επανεκκίνηση των DB με τα default δεδομένα**) Για κάθε πρότζεκτ φάκελο, ανοίξτε π.χ., το **PowerShell** και εκτελέστε τις αντίστοιχες παρακάτω εντολές: <br>
📌 **Βεβαιωθείτε ότι βρίσκεστε στον <u>root</u> φάκελο** `development-backend2` πριν εκτελέσετε την εντολή.

* **`development-erp`**
    1. `cd development-erp`
    2. `docker run --rm -v development-erp_mysql-data:/volume -v ${PWD}:/backup alpine sh -c "cd /volume && tar xvf /backup/development-erp_mysql-data.tar.gz --strip 1"`

* **`development-ml`**
    1. `cd development-ml`
    2. `docker run --rm -v development-ml_pgdata:/volume -v ${PWD}:/backup alpine sh -c "cd /volume && tar xvf /backup/development-ml_pgdata.tar.gz --strip 1"`

* **`development-web-app`**
    1. `cd development-web-app`
    2. `docker run --rm -v development-web-app_pgdata:/volume -v ${PWD}:/backup alpine sh -c "cd /volume && tar xvf /backup/development-web-app_pgdata.tar.gz --strip 1"`

**<u>ΣΗΜΕΙΩΣΗ:</u>** Για το production περιβάλλον, συνιστάται να γίνει απόκρυψη (de-expose) των ports των Docker containers `development-erp/dolibarr-mysql` και `development-web-app/db` (επεξεργαστείτε τα ανάλογα `docker-compose.yml` αρχεία).

**3.** Εκκίνηση όλων των εφαρμογών του πρότζεκτ εκτελώντας στο terminal το **shell script** `./start_all.sh`.  
📌 **Βεβαιωθείτε ότι βρίσκεστε στον <u>root</u> φάκελο** `development-backend2` πριν εκτελέσετε την εντολή.
