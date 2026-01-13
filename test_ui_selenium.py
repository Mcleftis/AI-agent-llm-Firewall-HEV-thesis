import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


#fixture gia na anoigei kai na kleinei o browser aftomata
@pytest.fixture(scope="module")#scope module, o driver dhmiourgeitai mia fora ana arxeio test, ola ta test ston chrome tha xrhsimopoioun ton idio driver
def driver():
    print("\n[SETUP] Initializing Headless Chrome Driver...")
    
    chrome_options = Options()#arxikopoish rythmisewn prwtou anoikseis ton driver
    chrome_options.add_argument("--headless")  #xwris gui,idaniko gia docker
    chrome_options.add_argument("--no-sandbox")#aparaithto gia docker gia na mhn krasarei to docker
    chrome_options.add_argument("--disable-dev-shm-usage")#apovefgei provlhmata shared-memory gia docker
    chrome_options.add_argument("--window-size=1920,1080")

    #egkatastash tou swstou driver
    service = Service(ChromeDriverManager().install())#katevazei aftomata ton chrome driver pou exoume sto pc mas
    driver = webdriver.Chrome(service=service, options=chrome_options)#fortwneis to chrome se headless kai pleon o driver einai ok
    
    yield driver  #to yield dinei ton driver se ola ta test pou ton xreiazontai
    
    print("\n[TEARDOWN] Closing Driver...")
    driver.quit()#meta to peras twn test kleinei o chrome, den afhnei skoupidia

#testing

def test_app_title_load(driver):
    """
    Test 1: Smoke Test - Ελέγχουμε αν η εφαρμογή ανοίγει και έχει τον σωστό τίτλο.
    """
    #ypothetoume oti to test trexei topika
    driver.get("http://localhost:8501")#trexei sto default port
    
    #na fortwsei h javascript ths streamlit
    time.sleep(3)
    
    # Ελέγχουμε τον τίτλο της σελίδας
    page_title = driver.title
    print(f"Detected Page Title: {page_title}")
    
  
    assert "Neuro-Symbolic" in driver.page_source or "Hybrid" in driver.page_source, "UI CRITICAL FAILURE: Title not found!"#ui health check tsekarei an yparxei mia apo tis 2 lekseis, einai testing gia na tsekaroume an tha kolhssei h selida h tha pesei

def test_sidebar_presence(driver):#exoume to fixture driver, opote anoigei headless chrome, fortwnei thn efarmogh, kai ektelei test panw sto dom
    """
    Test 2: Structure Test - Ελέγχουμε αν υπάρχει η Sidebar.
    """
    try:
        sidebar = driver.find_element(By.CSS_SELECTOR, "[data-testid='stSidebar']")#swstos tropos na vreis th sidebar, an den to brei to selenium tha shkwsei exception
        assert sidebar.is_displayed(), "Sidebar is hidden!"#elegxos an einia orath
        print("Sidebar detected successfully.")
    except Exception as e:
        pytest.fail(f"UI FAILURE: Sidebar not found. Error: {e}")

def test_main_content_loaded(driver):#fixture anoigei prin to test kai dinei etoima stoixeia, driver erxetai apo to fixture opote einai hdh etoimh h selida
    """
    Test 3: Smoke Test - Ελέγχουμε αν φορτώθηκε το κυρίως σώμα της εφαρμογής.
    Αντί να ψάχνουμε για textarea (που μπορεί να λείπει), ψάχνουμε το 'stApp' container.
    """
    try:
        main_app = driver.find_element(By.CLASS_NAME, "stApp")#ekei vazei synhthws olo to UI to streamlit
        
        assert main_app.is_displayed(), "Main Application container is invisible!"#elegxei an yparxei kai oti einai orato, an den exei ginei render failure, an exei fortwsei to frontend
        print("✅ Main Streamlit App Container detected successfully.")
        
    except Exception as e:
        pytest.fail(f"UI CRITICAL FAILURE: Main app container not found. Error: {e}")