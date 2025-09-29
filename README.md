# Personal Weather Assistant

Ova aplikacija služi kao osobni vremenski asistent koji kombinira stvarne vremenske podatke s AI analizom kako bi pružio personalizirane preporuke. Korisnik može unijeti grad i datum, a aplikacija će vratiti korisne savjete o odjeći, aktivnostima i drugim relevantnim informacijama temeljenim na prognozi.

##  Ključne Funkcionalnosti

-   **Unos Podataka:** Jednostavno sučelje za unos grada i datuma.
-   **Dohvaćanje Podataka:** Integracija s OpenWeatherMap API-jem za dobivanje točnih vremenskih podataka (trenutno vrijeme ili prognoza za 5 dana).
-   **AI Analiza:** Korištenje Groq API-ja za slanje vremenskih podataka jezičnom modelu (LLM) na analizu.
-   **Personalizirane Preporuke:** AI generira sažete i korisne preporuke za odjeću, aktivnosti na otvorenom/zatvorenom i općenite savjete.
-   **Korisničko Sučelje:** Čist i responzivan frontend izrađen u Reactu.

## Korištene Tehnologije

| Kategorija | Tehnologija                                       |
| :--------- | :------------------------------------------------ |
| **Backend**  | Python, Flask                                   |
| **Frontend** | React.js, CSS                                   |
| **API-ji**   | OpenWeatherMap API, Groq API                    |
| **Alati**    | Git, npm, pip (venv)                            |

---

## Instalacija i Pokretanje Projekta

Za uspješno pokretanje aplikacije, potrebno je slijediti korake za postavljanje i pokretanje backenda i frontenda odvojeno.

### 1. Preduvjeti
Provjerite imate li instalirano sljedeće:
-   Python 3.8+
-   Node.js v16+ (sa npm-om)
-   Git

### 2. Postavljanje Projekta
Prvo, klonirajte repozitorij na svoje računalo.

```bash
git clone https://github.com/tinpa-ctrl/personal-weather-assistant.git
cd personal-weather-assistant
```

### 3. Backend Setup
Backend server je odgovoran za komunikaciju s vanjskim API-jima.

```bash
# 1. Navigirajte u backend direktorij
cd backend

# 2. Kreirajte i aktivirajte virtualno okruženje
# Na Windowsu:
python -m venv venv
venv\Scripts\activate

# 3. Instalirajte sve potrebne Python pakete
pip install -r requirements.txt
```
#### 4. Kreirajte .env datoteku za API ključeve
U 'backend' folderu napravite novu datoteku pod nazivom '.env'
i u nju dodajte svoje API ključeve u sljedećem formatu:
OPENWEATHERMAP_API_KEY=vas_openweathermap_kljuc
GROQ_API_KEY=vas_groq_kljuc

### 4. Frontend Setup
Frontend aplikacija pruža korisničko sučelje.

```bash
# 1. Iz glavnog direktorija, navigirajte u frontend
cd ../frontend

# 2. Instalirajte sve potrebne Node.js pakete
npm install
```

### 5.Pokretanje Aplikacije
Za rad aplikacije, oba servera (backend i frontend) moraju biti pokrenuta istovremeno. To zahtijeva korištenje dva odvojena terminala/CMD prozora.

Terminal 1: Pokretanje Backenda

```bash
# Provjerite jeste li u /backend direktoriju
# Provjerite je li virtualno okruženje (venv) aktivirano
flask run
```
Backend server će se pokrenuti na http://127.0.0.1:5000

Terminal 2: Pokretanje Frontenda

```bash
# Provjerite jeste li u /frontend direktoriju
npm start
```
Frontend aplikacija će se automatski otvoriti u pregledniku na http://localhost:3000


### 6.Testiranje Funkcionalnosti
Nakon što su oba servera pokrenuta:
Otvorite web preglednik i posjetite http://localhost:3000.
U polje za grad unesite Zagreb.
Odaberite željeni datum pomoću alata za odabir datuma.
Kliknite na gumb "Dohvati preporuke".
Očekivani rezultat: Nakon kratkog čekanja, na stranici će se pojaviti tekstualna preporuka generirana od strane AI-ja, prilagođena vremenskim uvjetima za odabrani grad i datum.


### Primjer Korištenja

![Primjer rada aplikacije](primjer.gif)



Razvio: Tin Paviša