# 'Development-Backend' App

### Backend app για business logic, επικοινωνία με ERP και ML λειτουργίες

## Περιγραφή

Η εφαρμογή `development-backend` αποτελεί το **backend** μέρος της Web App πλατφόρμας του έργου Development, προσφέροντας APIs για την επικοινωνία με τις βάσεις δεδομένων και την εκτέλεση των απαραίτητων λειτουργιών για τον χρήστη. Το σύστημα είναι βασισμένο στο **Django (Python)** framework και χρησιμοποιεί **PostgreSQL** για τη διαχείριση της βάσης δεδομένων.

Η εφαρμογή εξυπηρετεί λειτουργίες που σχετίζονται με:

1. Διαχείριση χρηστών και δικαιωμάτων (authentication, authorization)
2. Επικοινωνία με την ERP βάση δεδομένων (Dolibarr - [development-erp](https://bitbucket.org/dotsoft-sa/development-backend-2/src/main/development-erp/))
3. Ανάκτηση και χρήση Machine Learning μοντέλων (προέρχονται από [development-ml](https://bitbucket.org/dotsoft-sa/development-backend-2/src/main/development-ml/))
4. Δημιουργία και διαχείριση SKU προβλέψεων ζήτησης
5. Βελτιστοποίηση αποθεμάτων και διανομής

Για ευκολότερη δοκιμή των APIs, παρέχεται το Postman collection αρχείο `development_backend_web_app.postman_collection.json`.

---

## Πώς να Τρέξετε τo App Τοπικά

**Σημαντικές σημειώσεις**:

* Βεβαιωθείτε ότι η βάση δεδομένων "Development" στο `PostgreSQL` και το πρότζεκτ `development-erp` (δείτε περισσότερα [εδώ](https://bitbucket.org/dotsoft-sa/development-backend-2/src/69a1f5f995fd/development-erp/?at=main)) είναι ενεργά.
* Βεβαιωθείτε ότι οι πίνακες του app υπάρχουν ήδη στη "Development" `PostgreSQL` βάση. Αν δεν υπάρχουν, μπορείτε να χρησιμοποιήσετε αυτό το [repository](https://bitbucket.org/dotsoft-sa/development-backend-2/src/main/development-web-app/development-db/) για τη δημιουργία τους.

1.Δημιουργήστε ένα νέο (κενό) πρότζεκτ με το αγαπημένο σας IDE (π.χ., PyCharm)

2.Από το repository, κλωνοποιήστε/κατεβάστε τον φάκελο `development-backend` και μετακινήστε τα αρχεία του στο νέο πρότζεκτ

* To αρχείο `.env` πρέπει να τοποθετηθεί στον root φάκελο του πρότζεκτ. Αυτό το αρχείο πρέπει να σας πρέπει να **δοθεί από τον υπεύθυνο του έργου** (βασιστείτε στο αρχείο `.env.sample`).

3.Δημιουργήστε έναν `venv` φάκελο για το πρότζεκτ (δείτε πως [εδώ](https://stackoverflow.com/a/59895890))

4.Εκτελέστε την εντολή `pip install -r requirements.txt` για να εγκαταστήσετε τα απαραίτητα πακέτα/βιβλιοθήκες

5.Για την εκκίνηση της εφαρμογής, τρέξτε στο terminal την εντολή: `python backend/manage.py runserver`

6.Για την εκτέλεση των unit tests, βεβαιωθείτε ότι βρίσκεστε στον root φάκελο του έργου. Στη συνέχεια, εκτελέστε στο terminal την εντολή `pytest backend/api/tests.py`
