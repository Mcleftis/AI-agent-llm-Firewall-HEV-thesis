# Ξεκινάμε από Python
FROM python:3.9-slim

# Ρυθμίσεις περιβάλλοντος
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# --- SENIOR MOVE: ΕΓΚΑΤΑΣΤΑΣΗ CHROME ΓΙΑ SELENIUM ---
# Εγκαθιστούμε dependencies για τον Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Κατεβάζουμε και εγκαθιστούμε τον Google Chrome Stable
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# --- ΤΕΛΟΣ CHROME SETUP ---

# Εγκατάσταση βιβλιοθηκών Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Αντιγραφή κώδικα
COPY . .

# Άνοιγμα πόρτας
EXPOSE 8501

# Εντολή εκκίνησης
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]