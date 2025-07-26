# Stocks Analysis Project

Projekat za analizu akcija i finansijskih podataka.

## Podešavanje

### 1. Kreiranje virtual environment-a
```bash
python3 -m venv venv
source venv/bin/activate  # Na macOS/Linux
# ili
venv\Scripts\activate     # Na Windows
```

### 2. Instaliranje dependencies
```bash
pip install -r requirements.txt
```

### 3. Konfiguracija
```bash
cp .env.example .env
# Editujte .env fajl sa vašim podešavanjima
```

### 4. Pokretanje
```bash
python main.py
```

## Struktura projekta

- `main.py` - Glavna skripta
- `requirements.txt` - Python dependencies  
- `.env` - Environment varijable (ne commituje se)
- `.env.example` - Primer environment varijabli 