import unittest
import requests
import json

class TestAPIRestAssuredStyle(unittest.TestCase):#afto to unit periexei python tests, trekse to aftomata
    """
    Αυτό το Test Suite μιμείται τη λογική BDD (Behavior Driven Development)
    του RestAssured, αλλά χρησιμοποιεί Python Requests.
    """

    def setUp(self):#h setup kaleitai panta prin apo test
        self.base_url = "http://127.0.0.1:11434" #Ollama Server, prin apo kathe test dhmiourgietai afth h metavlhth, apothikevoume pragmata pou xreiazetai to test px url

    def test_ollama_status_bdd(self):#ekkinhsh test, self einai to antikeimeno ths klashs
        print("\n[API] Testing Ollama Endpoint (RestAssured Style)...")

        #GIVEN (Preparation / Setup)
        # Στο RestAssured: given().baseUri("...")
        endpoint = "/api/tags"#sto ollama epistrefe th lista twn diathesimwn montelwn
        url = f"{self.base_url}{endpoint}"#apotelesma:http://127.0.0.1:11434/api/tags

        try:
            # --- WHEN (Action / Execution) ---
            # Στο RestAssured: .when().get("/api/tags")
            response = requests.get(url, timeout=2.0)#aithma ston server, epistrefontai status code, headers, body, JSON (αν υπάρχει), χρόνο απόκρισης

            # --- THEN (Assertion / Validation) ---
            # Στο RestAssured: .then().statusCode(200)
            print(f"  -> Status Code Check: {response.status_code}")#ti epestrepse o server, 200 → όλα καλά, 404 → λάθος endpoint, 500 → server error,0 ή exception → ο server δεν απάντησε
            self.assertEqual(response.status_code, 200, "Status Code Verification Failed")#elegxoume an epestrepse 200

            # Στο RestAssured: .body("models", not(empty()))
            data = response.json()#Παίρνει το body της HTTP απάντησης, Το μετατρέπει από JSON string → Python dictionary, Σου επιτρέπει να κάνεις έλεγχο στα πεδία του API
            print(f"  -> Body Check: 'models' key present")
            self.assertIn("models", data, "JSON Schema Verification Failed")#Εξασφαλίζει ότι το API τηρεί το συμβόλαιο (contract testing),Προστατεύει από αλλαγές στο schema, Πιάνει corrupted responses,Πιάνει λάθος endpoints, Πιάνει server errors που επιστρέφουν άκυρο JSON
            
            # Στο RestAssured: .header("Content-Type", "application/json")
            content_type = response.headers.get("Content-Type")#παίρνει από την HTTP απάντηση το header Content-Type, το οποίο δηλώνει τι είδους δεδομένα περιέχει το body, epistrefei application/json
            print(f"  -> Header Check: {content_type}")
            self.assertIn("application/json", content_type, "Header Verification Failed")#Το API πρέπει να επιστρέφει JSON. Αν δεν επιστρέφει JSON, το test αποτυγχάνει.

        except requests.exceptions.ConnectionError:#apotyxia syndeshs me ton server
            print("  [WARNING] Ollama Server is down. Skipping test logic.")#Αυτό το block θα εκτελεστεί μόνο όταν η requests.get() (ή οποιαδήποτε άλλη κλήση) αποτύχει να συνδεθεί στον server.

if __name__ == "__main__":
    unittest.main()#πόσα tests πέρασαν, πόσα απέτυχαν, πόσα έσπασαν, πόσα αγνοήθηκαν