@echo off
echo "------------------------------------------------"
echo "       LAZY GIT SCRIPT (Senior Edition)         "
echo "------------------------------------------------"

:: 1. Πρώτα τραβάμε τυχόν αλλαγές από το GitHub για να μην έχουμε conflict
echo "[1/4] Pulling latest changes from GitHub..."
git pull origin main

:: 2. Προσθέτουμε τα αρχεία μας
echo "[2/4] Adding local changes..."
git add .

:: 3. Κάνουμε commit (με ώρα και ημερομηνία για να είμαστε ωραίοι)
echo "[3/4] Committing..."
git commit -m "Auto-update: %date% %time%"

:: 4. Στέλνουμε τα πάντα πάνω
echo "[4/4] Pushing to GitHub..."
git push origin main

echo "------------------------------------------------"
echo "Telos. Pame gia kafe."
pause