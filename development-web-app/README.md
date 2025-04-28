# Development-Web-App

Το πρότζεκτ **Development-Web-App** είναι ένα ολοκληρωμένο σύστημα που ενσωματώνει Backend, Frontend και Database για την ανάπτυξη μίας web-based πλατφόρμας που αξιοποιεί μοντέλα ML και ERP δεδομένα. Αποτελεί το προϊόν που, μέσω της **background συνεργασίας** με τις εφαρμογές [development-erp](https://bitbucket.org/dotsoft-sa/development-backend-2/src/main/development-erp/) και [development-ml](https://bitbucket.org/dotsoft-sa/development-backend-2/src/main/development-ml/), επιτρέπει στον χρήστη να αξιοποιήσει λειτουργίες όπως **η πρόβλεψη ζήτησης SKU, η διαχείριση αποθεμάτων και η βελτιστοποίηση δρομολόγησης οχημάτων**, σε ένα ενιαίο ψηφιακό περιβάλλον.


Για αυτόν τον σκοπό, δημιουργήθηκαν τα παρακάτω components:

- **Development-DB**: Δημιουργεί και διαχειρίζεται τους απαραίτητους πίνακες στη βάση δεδομένων `PostgreSQL` του Web App.
- **Development-Backend**: Επικοινωνεί με την `PostgreSQL Web App` και `MySQL-ERP Dolibarr` βάση & Υλοποιεί APIs μέσω Django (Python) framework.
- **Development-Frontend**: Περιλαμβάνει τη React-Vite εφαρμογή, η οποία επικοινωνεί με το `development-backend` για να προσφέρει στους τελικούς χρήστες ένα διαδραστικό περιβάλλον για την παρακολούθηση προβλέψεων ζήτησης SKU, τη διαχείριση αποθεμάτων και τη βελτιστοποίηση δρομολόγησης οχημάτων.

Όλα τα παραπάνω components ενορχηστρώνονται και λειτουργούν συνδυαστικά μέσω του Docker Compose, εξασφαλίζοντας μία ευέλικτη και ολοκληρωμένη υποδομή.

## Εκτέλεση με Docker

**Σημαντική σημείωση**: Βεβαιωθείτε ότι η `MySQL` βάση και το `EPR-fastapi` του `Dolibarr` ERP είναι ενεργά (`development-erp` - δείτε περισσότερα [εδώ](https://bitbucket.org/dotsoft-sa/development-backend-2/src/69a1f5f995fd/development-erp/?at=main))

**1.**Βεβαιωθείτε ότι βρίσκεστε στον root φάκελο `development-web-app`

**2.**Τοποθετήστε το αρχείο `development-web-app_pgdata.tar.gz` στον φάκελο αυτόν <br>

**3.**Τοποθετήστε τα αντίστοιχα `.env` και `config` αρχεία στο root και στους υπό-φακέλους (κάθε υποφάκελος είναι και ένα διαφορετικό πρότζεκτ-app). Τα αρχεία αυτά πρέπει να σας **δοθούν από τον υπεύθυνο του έργου**.

**4.**(**Για επανεκκίνηση της DB με τα default δεδομένα**) Στον root φάκελο `development-backend`, ανοίξτε π.χ., το **PowerShell** και εκτελέστε την παρακάτω εντολή: <br>
`docker run --rm -v development-web-app_pgdata:/volume -v ${PWD}:/backup alpine sh -c "cd /volume && tar xvf /backup/development-web-app_pgdata.tar.gz --strip 1"`

**5.**Εκτελέστε το αρχείο Docker Compose με την εντολή `docker-compose up --build`
