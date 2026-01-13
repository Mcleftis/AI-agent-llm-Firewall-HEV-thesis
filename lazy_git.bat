@echo off
echo "------------------------------------------------"
echo "       LAZY GIT SCRIPT (New Repo Edition)       "
echo "------------------------------------------------"

:: 0. ΡΥΘΜΙΣΗ: Συνδέουμε το folder με το ΝΕΟ repo
echo "[0/4] Setting remote URL to NEW Repository..."
:: Προσπαθεί να αλλάξει το URL σε αυτό που θες
git remote set-url origin https://github.com/Mcleftis/AI-agent-llm-Firewall-HEV 2>nul
:: Αν δεν υπάρχει καθόλου "origin" (επειδή είναι φρέσκο), το δημιουργεί
if %errorlevel% neq 0 git remote add origin https://github.com/Mcleftis/AI-agent-llm-Firewall-HEV

:: 1. ΠΡΟΣΟΧΗ: Το Pull το απενεργοποίησα (με REM) για τώρα.
:: Επειδή το νέο repo είναι άδειο, αν κάνεις pull θα σκάσει.
:: Μόλις γεμίσει το repo στο μέλλον, βγάλε το "REM" από τις κάτω γραμμές.
REM echo "[1/4] Pulling latest changes from GitHub..."
REM git pull origin main

:: 2. Προσθέτουμε τα αρχεία μας
echo "[2/4] Adding local changes..."
git add .

:: 3. Κάνουμε commit
echo "[3/4] Committing..."
git commit -m "Fresh Start: Secure & Refactored v1.0"

:: 4. Στέλνουμε τα πάντα στο ΝΕΟ repo
echo "[4/4] Pushing to NEW GitHub..."
:: Βάζουμε -u για να 'κουμπώσει' το local main με το github main
git push -u origin main

echo "------------------------------------------------"
echo "Mission Accomplished."
pause