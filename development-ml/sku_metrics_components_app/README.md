# 'SKU Metrics Components' App
### Εισαγωγή δεδομένων στον πίνακα `sku_metrics` της βάσης δεδομένων της DOTSOFT

## Περιγραφή

Όπως αναφέρεται [εδώ](https://bitbucket.org/dotsoft-sa/development-backend-2/src/69a1f5f995fd/development-ml/create-ml-development-db-tables-app/README.md?at=main), για τη λειτουργία πρόβλεψης της ζήτησης (SKU ποσοτήτων), υπάρχει ο πίνακας `sku_metrics` στη βάση `PostgreSQL` της DOTSOFT. Ο πίνακας αυτός περιλαμβάνει κρίσιμα δεδομένα που προέρχονται από τα παρακάτω components. Ο στόχος του app είναι, σε προκαθορισμένα χρονικά διαστήματα (με τη χρήση `scheduler`), να αντλεί τις `SKU ORDER` πληροφορίες από το ERP και να τις τροφοδοτεί στα ακόλουθα components, ώστε να εμπλουτίζουν τον πίνακα `sku_metrics` με τα απαραίτητα δεδομένα.

### Data Processing (SKU Metrics) Components:

- **`add_sku_number_user_id_sku_order_record_id.py`**: Είναι το πρώτο component που πρέπει να τρέχει στον κώδικα. Δημιουργεί νέες εγγραφές στον πίνακα `sku_metrics` με βασικές πληροφορίες των SKU παραγγελιών, συγκεκριμένα `sku_number`, `user_id` και `sku_order_record_id` (τα υπόλοιπα `null`).
  <br>
  <br>
- **`add_holidays_weekends_weather.py`**: Προσθέτει μεταβλητές που επηρεάζουν τη ζήτηση, όπως `is_holiday`, `is_weekend`, `mean_temperature` και `rain`, με βάση ημερολογιακά και μετεωρολογικά δεδομένα.  
  <br>
- **`add_google_trends.py`**: Συλλέγει δεδομένα από το **Google Trends** και υπολογίζει τον δείκτη τάσης (`trend_value`) για κάθε SKU, ενσωματώνοντάς τον στον πίνακα `sku_metrics`. Για περισσότερες πληροφορίες [εδώ](https://bitbucket.org/dotsoft-sa/development-backend/src/master/WebAPI-GoogleTrends/)  
  <br>
- **`add_average_competition_price_external.py`**: Χρησιμοποιεί **Web Scraping** για τη συλλογή τιμών από ανταγωνιστικά προϊόντα. Συγκεκριμένα, υπολογίζει και αποθηκεύει στον πίνακα `sku_metrics` τη μέση ανταγωνιστική τιμή (`average_competition_price_external`). Για περισσότερες πληροφορίες [εδώ](https://bitbucket.org/dotsoft-sa/development-backend/src/master/Web-Scraping/)  
  <br>
- **`products_reviews_scraping.py`** & **`add_review_sentiment_score_and_timestamp.py`**  
  <br>
  **A.** `products_reviews_scraping.py`:  Χρησιμοποιεί **Web Scraping** για τη συλλογή κριτικών προϊόντων που είναι παρόμοια με τα SKUs που υπάρχουν στο ERP του πελάτη. Για περισσότερες πληροφορίες [εδώ](https://bitbucket.org/dotsoft-sa/development-backend/src/master/Web-Scraping/)
  <br>
  <br>
  **B.** `add_review_sentiment_score_and_timestamp.py`: Δέχεται τις κριτικές ως input από το `products_reviews_scraping.py` και πραγματοποιεί **sentiment analysis**. Έπειτα, παράγει και προσθέτει τις μεταβλητές `review_sentiment_score` και `review_sentiment_timestamp` στον πίνακα `sku_metrics`. Για περισσότερες πληροφορίες [εδώ](https://bitbucket.org/dotsoft-sa/development-backend/src/master/Web-Scraping/)

---

## Πώς να Τρέξετε τo App Τοπικά

**Σημαντική σημείωση**: Βεβαιωθείτε ότι η `MySQL` βάση και το `EPR-fastapi` του `Dolibarr` ERP είναι ενεργά (δείτε περισσότερα [εδώ](https://bitbucket.org/dotsoft-sa/development-backend-2/src/69a1f5f995fd/development-erp/?at=main))

1.Δημιουργήστε ένα νέο (κενό) πρότζεκτ με το αγαπημένο σας IDE (π.χ., PyCharm)

2.Από το repository, κλωνοποιήστε/κατεβάστε τον φάκελο `sku_metrics_components_app` και μετακινήστε τα αρχεία του στο νέο πρότζεκτ

Α. To αρχείο `.env` πρέπει να τοποθετηθεί στον root φάκελο του πρότζεκτ (βασιστείτε στο αρχείο `.env.sample`). <br>
Β. Κατέβασε το [chrome-driver](https://googlechromelabs.github.io/chrome-for-testing/#stable) που αντιστοιχεί στην έκδοσή του δικού σου Chrome Browser και πρόσθεσε τον φάκελο `chromedriver-win64` στον φάκελο `sku_metrics_components_app/configs`.<br>

* Tα παραπάνω αρχεία πρέπει να σας **δοθούν από τον υπεύθυνο του έργου**

3.Δημιουργήστε έναν `venv` φάκελο για το πρότζεκτ (δείτε πως [εδώ](https://stackoverflow.com/a/59895890))

4.Εκτελέστε την εντολή `pip install -r requirements.txt` για να εγκαταστήσετε τα απαραίτητα πακέτα/βιβλιοθήκες

5.Τρέξτε το αρχείο `main.py` **ή**, εναλλακτικά, εκτελέστε το αρχείο `scheduler_main.py` ώστε η διαδικασία να εκτελείται αυτόματα, π.χ., σε καθημερινή βάση. Εκτελέστε στον terminal την εντολή: `python main.py` ή `python scheduler_main.py` αντίστοιχα.
