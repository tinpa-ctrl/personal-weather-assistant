# ==============================================================================
# === 1. UVOZ POTREBNIH BIBLIOTEKA (ALATA) ===
# ==============================================================================
# Uvozimo sve "alate" koji će nam trebati za rad. Svaki ima svoju specifičnu namjenu.

import os  # Omogućuje nam čitanje varijabli iz operativnog sustava (npr. API ključeva).
from dotenv import load_dotenv  # Specifično za učitavanje naših tajnih ključeva iz .env datoteke.
from flask import Flask, request, jsonify  # Osnovni alati iz Flask biblioteke za izradu web servera.
                                           # Flask - glavni objekt aplikacije.
                                           # request - za čitanje podataka koje nam šalje frontend.
                                           # jsonify - za pretvaranje Python rječnika u ispravan JSON format.
from flask_cors import CORS  # Omogućuje da naš frontend (koji radi na portu 3000) može slati zahtjeve našem backendu (koji radi na portu 5000).
import requests  # Biblioteka za slanje HTTP zahtjeva drugim API-jima (u našem slučaju OpenWeatherMap).
from groq import Groq  # Službena Groq biblioteka za komunikaciju s njihovim AI modelima.
from datetime import datetime, date, timedelta  # Jako važno! Alati za rad s datumima i vremenom.
                                                # Omogućuju nam pretvaranje teksta u datume, uspoređivanje datuma itd.

# ==============================================================================
# === 2. INICIJALIZACIJA I KONFIGURACIJA ===
# ==============================================================================
# Ovdje postavljamo temelje naše aplikacije.

# Učitaj varijable iz .env datoteke (OPENWEATHERMAP_API_KEY i GROQ_API_KEY)
load_dotenv()

# Kreiraj instancu naše Flask web aplikacije.
app = Flask(__name__)

# Omogući CORS za cijelu aplikaciju. Ovo je kao da kažemo: "Vrata su otvorena za zahtjeve s drugih domena."
CORS(app)

# Učitaj API ključeve iz .env datoteke u Python varijable za lakše korištenje.
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Kreiraj "klijenta" za komunikaciju s Groq-om. Ovaj objekt će imati metode za slanje zahtjeva AI modelu.
groq_client = Groq(api_key=GROQ_API_KEY)


# ==============================================================================
# === 3. GLAVNA LOGIKA: DOHVAĆANJE VREMENSKIH PODATAKA ===
# ==============================================================================
# Ova funkcija je "mozak" za dohvaćanje vremena. Postala je pametnija jer sada zna
# rukovati s današnjim danom i budućim danima na različite načine.

def get_weather_data(city, target_date_str):
    """Dohvaća vremenske podatke ovisno o tome je li traženi datum danas ili u budućnosti."""

    # Prvo, pretvaramo tekstualni datum koji smo dobili od frontenda (npr. "2025-09-28")
    # u pravi "date" objekt s kojim Python može raditi (uspoređivati ga, itd.).
    target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
    today = date.today()

    # --- GRANA 1: Ako je korisnik odabrao DANAŠNJI DAN ---
    # Koristimo jednostavniji i precizniji '/weather' endpoint koji daje TRENUTNO stanje.
    if target_date == today:
        print("Dohvaćam trenutno vrijeme za danas...")
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {'q': city, 'appid': OPENWEATHERMAP_API_KEY, 'units': 'metric', 'lang': 'hr'}
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Ako API vrati grešku (npr. 404), ovo će izazvati iznimku.
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Greška prilikom dohvaćanja trenutnih vremenskih podataka: {e}")
            return None

    # --- GRANA 2: Ako je korisnik odabrao DATUM U BUDUĆNOSTI ---
    # Moramo koristiti kompliciraniji '/forecast' endpoint.
    else:
        print(f"Dohvaćam prognozu za budući datum: {target_date_str}...")
        base_url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {'q': city, 'appid': OPENWEATHERMAP_API_KEY, 'units': 'metric', 'lang': 'hr'}
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            forecast_data = response.json()

            # SADRŽAJ ODGOVORA: Ovaj API vraća dugačku listu prognoza, svaka za interval od 3 sata.
            # NAŠ ZADATAK: Moramo proći kroz tu listu i pronaći najbolji unos za traženi dan.
            # "Najbolji" unos definiramo kao onaj koji je najbliži podnevu (12:00 sati).

            best_entry = None
            # Prolazimo kroz svaki trosatni unos u listi...
            for entry in forecast_data.get('list', []):
                # Pretvaramo UNIX timestamp (sekunde od 1970.) u Python datumski objekt.
                entry_date = datetime.fromtimestamp(entry['dt']).date()
                # Ako se datum unosa poklapa s datumom koji korisnik traži...
                if entry_date == target_date:
                    # ... i ako je to unos za podne (12:00)...
                    if '12:00:00' in entry['dt_txt']:
                        best_entry = entry  # ... to je naš idealan kandidat!
                        break  # Pronašli smo ga, nema potrebe dalje tražiti.

            # REZERVNI PLAN: Što ako nema unosa točno za podne? (npr. za peti dan u budućnosti)
            # Ako nismo našli unos za podne, jednostavno ćemo uzeti PRVI dostupni unos za taj dan.
            if not best_entry:
                 for entry in forecast_data.get('list', []):
                    if datetime.fromtimestamp(entry['dt']).date() == target_date:
                        best_entry = entry
                        break
            
            # FORMATIRANJE ODGOVORA: Odgovor od '/forecast' API-ja je malo drugačiji od '/weather'.
            # Nedostaje mu ime grada ('name'). Zato ga ručno dodajemo kako bi naš frontend
            # uvijek dobivao podatke u istom formatu, bez obzira koji smo API pozvali.
            if best_entry:
                best_entry['name'] = forecast_data.get('city', {}).get('name', city)
                return best_entry
            
            return None  # Ako nismo pronašli nijedan unos za traženi dan.

        except requests.exceptions.RequestException as e:
            print(f"Greška prilikom dohvaćanja prognoze: {e}")
            return None


# ==============================================================================
# === 4. LOGIKA ZA AI PREPORUKE ===
# ==============================================================================
# Ova funkcija uzima obrađene vremenske podatke i šalje ih AI modelu za generiranje preporuka.

def get_ai_recommendations(weather_data, target_date_str):
    """Sastavlja prompt i šalje ga Groq API-ju."""

    if not weather_data:
        return "Nije moguće generirati preporuke jer podaci o vremenu nisu dostupni."

    # Pripremamo sve podatke koje želimo poslati AI modelu.
    description = weather_data['weather'][0]['description']
    temp = weather_data['main']['temp']
    feels_like = weather_data['main']['feels_like']
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']
    
    # KLJUČNA PROMJENA: U našem "promptu" (uputi za AI) sada uključujemo i datum.
    # To daje AI modelu bolji kontekst da ne generira preporuke za "danas",
    # nego baš za dan koji je korisnik tražio.
    prompt = f"""
    Na temelju sljedećih vremenskih podataka za datum {target_date_str}, generiraj personalizirane preporuke.
    Budi prijateljski nastrojen i daj savjete u tri kategorije: Odjeća, Aktivnosti i Dodatni savjeti.
    Koristi hrvatski jezik.

    Vremenski podaci:
    - Opis: {description}
    - Temperatura: {temp}°C
    - Osjećaj kao: {feels_like}°C
    - Vlažnost: {humidity}%
    - Brzina vjetra: {wind_speed} m/s

    Formatiraj odgovor kao čist tekst, bez Markdowna, koristeći naslove 'Odjeća:', 'Aktivnosti:' i 'Dodatni savjeti:'.
    """

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-20b",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Greška prilikom komunikacije s Groq API: {e}")
        return "Došlo je do greške prilikom generiranja AI preporuka."


# ==============================================================================
# === 5. API ENDPOINT - "VRATA" NAŠE APLIKACIJE ===
# ==============================================================================
# Ovo je jedina točka kroz koju naš frontend komunicira s backendom.
# Ona se ponaša kao "kontrolor prometa": prima zahtjev, poziva druge funkcije da obave posao
# i na kraju šalje formatirani odgovor natrag.

@app.route('/api/weather-recommendation', methods=['POST'])
def weather_recommendation():
    """Prima zahtjev od frontenda, orkestrira dohvaćanje podataka i vraća odgovor."""
    
    # 1. Čitanje podataka koje je poslao React.
    data = request.json
    city = data.get('city')
    date_str = data.get('date')

    # 2. Validacija unosa - provjera jesu li svi potrebni podaci tu.
    if city: city = city.strip() # Uklanjamo slučajne praznine
    if not city or not date_str:
        return jsonify({"error": "Grad i datum su obavezni"}), 400

    # 3. Dodatna validacija - provjera da korisnik nije odabrao datum predaleko u budućnosti.
    selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    max_date = date.today() + timedelta(days=5) # Današnji datum + 5 dana
    if selected_date > max_date:
        return jsonify({"error": "Moguće je dohvatiti prognozu samo do 5 dana unaprijed."}), 400

    # 4. Orkestracija - pozivanje naših pomoćnih funkcija.
    # Prvo dohvati vremenske podatke...
    weather_data = get_weather_data(city, date_str)
    # Ako podaci nisu pronađeni, vrati grešku.
    if not weather_data or str(weather_data.get("cod")) == "404":
         return jsonify({"error": f"Nije moguće pronaći grad '{city}' ili dohvatiti podatke za taj datum."}), 404

    # ...zatim, ako je sve u redu, generiraj AI preporuke.
    recommendations = get_ai_recommendations(weather_data, date_str)

    # 5. Sastavljanje uspješnog odgovora.
    # Pakiramo sve podatke u lijepo formatiran rječnik.
    response_data = {
        "weather": {
            "city": weather_data['name'],
            "temperature": weather_data['main']['temp'],
            "description": weather_data['weather'][0]['description'],
            "icon": weather_data['weather'][0]['icon'],
            "feels_like": weather_data['main']['feels_like'],
            "humidity": weather_data['main']['humidity'],
            "wind_speed": weather_data['wind']['speed']
        },
        "recommendations": recommendations
    }
    
    # 6. Slanje odgovora. jsonify će ovo pretvoriti u JSON i poslati ga natrag Reactu.
    return jsonify(response_data)


# ==============================================================================
# === 6. POKRETANJE SERVERA ===
# ==============================================================================
# Ova linija osigurava da će se naš Flask server pokrenuti samo ako ovu datoteku
# pokrenemo direktno (npr. s `flask run`), a ne ako je uvezemo u neku drugu datoteku.
if __name__ == '__main__':
    # Pokreni aplikaciju u "debug" modu (prikazuje detaljne greške) na portu 5000.
    app.run(debug=True, port=5000)