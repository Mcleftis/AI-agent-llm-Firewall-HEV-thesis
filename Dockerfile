# Χρησιμοποιούμε Python
FROM python:3.9-slim

# Φάκελος εργασίας μέσα στο container
WORKDIR /app

# Εγκατάσταση απαραίτητων εργαλείων
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Αντιγραφή και εγκατάσταση requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Αντιγραφή όλου του κώδικα
COPY . .

# Εντολή εκκίνησης (Demo mode)
ENTRYPOINT ["python", "main.py"]
CMD ["--mode", "demo", "--driver_mood", "neutral"]