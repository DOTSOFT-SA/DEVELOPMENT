README.md

# ERP FastAPI
### Πρόσβαση στους 'Development' πίνακες της βάσης δεδομένων του συστήματος ERP

## Περιγραφή

Η παρούσα αποτελεί μία (backend) `FastAPI-Python` εφαρμογή, η οποία παρέχει πρόσβαση στους <u>πέντε</u> (5) Development πίνακες που βρίσκονται στη `MySQL` βάση του Dolibarr ERP. Συγκεκριμένα, για κάθε πίνακα, η εφαρμογή προσφέρει GET και POST API URLs για την ανάκτησης δεδομένων σε μορφή JSON. Υπενθύμιση, οι πίνακες αυτοί περιλαμβάνουν δεδομένα που χρησιμοποιούνται στο Web App και στον ML αλγόριθμο του πρότζεκτ (για προβλέψεις ζήτησης, αποθεμάτων και routing).

A. `sku_order_development` <br>
B. `inventory_params_development` <br>
C. `vehicle_development`, `location_development`, `route_development` <br>

Για ευκολότερη δοκιμή των APIs, παρέχεται το Postman collection αρχείο `erp_fastapi_development.postman_collection.json` .

---

## Πώς να Τρέξετε τo App Τοπικά

1.Δημιουργήστε ένα νέο (κενό) πρότζεκτ με το αγαπημένο σας IDE (π.χ., PyCharm)

2.Από το repository, κλωνοποιήστε/κατεβάστε τον φάκελο `erp-fastapi` και μετακινήστε τα αρχεία του στο νέο πρότζεκτ

* To αρχείο `.env` πρέπει να τοποθετηθεί στον root φάκελο του πρότζεκτ. Αυτό το αρχείο πρέπει να σας **δοθεί από τον υπεύθυνο του έργου** (βασιστείτε στο αρχείο `.env.sample`)

3.Δημιουργήστε έναν `venv` φάκελο για το πρότζεκτ (δείτε πως [εδώ](https://stackoverflow.com/a/59895890))

4.Εκτελέστε την εντολή `pip install -r requirements.txt` για να εγκαταστήσετε τα απαραίτητα πακέτα/βιβλιοθήκες

5.Για να ξεκινήσει η εφαρμογή, εκτελέστε το αρχείο/script `main.py` χρησιμοποιώντας το IDE σας ή εκτελέστε στο terminal την εντολή `uvicorn main:app --reload --port 7000`

6.Για την εκτέλεση των unit tests, βεβαιωθείτε ότι βρίσκεστε στον root φάκελο του έργου. Στη συνέχεια, εκτελέστε το αρχείο `/tests/tests.py` είτε μέσω του IDE σας είτε χρησιμοποιώντας την εντολή `pytest tests/tests.py` στο terminal

---

## Περιγραφή Λειτουργιών

Πριν ανατρέξετε τις παρακάτω λειτουργίες, βεβαιωθείτε ότι τα tables που αναφέρονται παραπάνω υπάρχουν στη `MySQL` βάση δεδομένων του Dolibarr ERP. **Αν δεν υπάρχουν**, μπορείτε να χρησιμοποιήσετε αυτό το [repository](https://bitbucket.org/dotsoft-sa/development-backend-2/src/main/development-erp/create-erp-development-db-tables-app/) για τη δημιουργία τους.

### **0. Δημιουργία `Login Bearer Token` ** - POST `/auth/login-token`
- Για την κλήση των παρακάτω APIs, απαιτείται η δημιουργία ενός `Bearer Token` για authorization. Για τη δημιουργία του `token`, το όνομα χρήστη (`API_USERNAME`) και ο κωδικός πρόσβασης (`API_PASSWORD`) μπορούν να βρεθούν στο αρχείο `.env`.

### **1. Πρόσβαση SKU** - GET `/api/sku_order_development`
- Παροχή API για ανάκτηση και αναζήτηση ERP δεδομένων SKU με φίλτρα όπως αριθμός SKU, όνομα SKU, κ.λπ.

### **2. Παράμετροι Αποθέματος (Inventory Parameters)** - GET `/api/inventory_params_development`
- Παροχή πληροφοριών όπως κόστος παραγγελίας, κόστος αποθέματος, και άλλες κρίσιμες μεταβλητές για τον υπολογισμό αποθεμάτων.
- Δυνατότητα φιλτραρίσματος βάσει αριθμού SKU (`sku_number`).

### **3. Οχήματα (Vehicles)** - GET `/api/vehicle_development`
- Διαχείριση δεδομένων σχετικά με οχήματα, όπως χωρητικότητα, κόστος ανά δρομολόγιο κ.λπ.
- Φιλτράρισμα βάσει `vehicle_id`.

### **4. Τοποθεσίες (Locations)** - GET `/api/location_development`
- Παροχή δεδομένων τοποθεσιών, όπως ζήτηση, χαρακτηρισμός ως αποθήκη (depot), κ.λπ.
- Φιλτράρισμα βάσει `location_id` ή/και `location_name`.

### **5. Διαδρομές (Routes)** - GET `/api/route_development`
- Δυνατότητα ανάκτησης δεδομένων διαδρομών, όπως απόσταση, συντελεστές κυκλοφορίας κ.λπ.
- Φιλτράρισμα βάσει `route_id`.

### **6. Ομαδοποίηση Δεδομένων για Δρομολόγηση (Distribution Routing)** - GET `/api/distribution_routing_data`
- Συγκέντρωση δεδομένων από οχήματα, τοποθεσίες και διαδρομές (3, 4, 5) για τη δημιουργία JSON μοντέλου που χρησιμοποιείται στον 'ML Αλγόριθμο – Βελτιστοποίησης Διανομής' (`DistributionOptimizationwithtraffic.py` [εδώ](https://bitbucket.org/dotsoft-sa/development-backend-2/src/main/development-web-app/development-backend/backend/api/services/facades/distribution_optimization_routing_facade.py)).

### **7. Ανάκτηση SKU με το πιο πρόσφατο `order_date`** - POST `/api/sku_order_latest/`
- Δυνατότητα αναζήτησης SKU παραγγελιών με βάση μία λίστα από `ids`, επιστρέφοντας μόνο το SKU με το πιο πρόσφατο `order_date`.
- Ο χρήστης αποστέλλει μία λίστα με `sku_order_ids` σε μορφή JSON, και το API επιστρέφει το πιο πρόσφατο καταχωρημένο SKU από αυτά.
- Χρησιμοποιείται στον 'ML Αλγόριθμο – Πρόβλεψη Ζήτησης' (`Prediction.py` [εδώ](https://bitbucket.org/dotsoft-sa/development-backend-2/src/main/development-web-app/development-backend/backend/api/services/facades/model_inference_service_facade.py))

### **8. Ανάκτηση Inventory παραμέτρων με το πιο πρόσφατο `created_at`** - POST `/api/get_inventory_params_development_latest/`
- Δυνατότητα αναζήτησης εγγραφών `inventory_params_development` με βάση το `sku_number`, επιστρέφοντας την πιο πρόσφατη εγγραφή με βάση το πεδίο `created_at`.
- Ο χρήστης αποστέλλει ένα `sku_number` σε μορφή JSON, και το API επιστρέφει την πιο πρόσφατη καταχωρημένη εγγραφή που σχετίζεται με αυτό.
- Χρησιμοποιείται στον 'ML Αλγόριθμο – Βελτιστοποίησης αποθεμάτων' (`InventoryService.py` [εδώ](https://bitbucket.org/dotsoft-sa/development-backend-2/src/main/development-web-app/development-backend/backend/api/services/facades/inventory_service_facade.py))