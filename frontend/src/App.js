// src/App.js

import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  // State varijable za pohranu podataka
  const [city, setCity] = useState('');
  const [date, setDate] = useState('');
  const [data, setData] = useState(null); // Za spremanje odgovora od backenda
  const [loading, setLoading] = useState(false); // Za prikaz poruke o učitavanju
  const [error, setError] = useState(''); // Za prikaz grešaka

  // Funkcija koja se poziva na klik gumba
  const handleSubmit = async (e) => {
    e.preventDefault(); // Sprječava osvježavanje stranice
    if (!city) {
      setError('Molimo unesite ime grada.');
      return;
    }

    setLoading(true);
    setError('');
    setData(null);

    try {
      // Slanje POST zahtjeva na naš Python backend
      const response = await axios.post('http://127.0.0.1:5000/api/weather-recommendation', {
        city: city,
        date: date,
      });
      setData(response.data); // Spremanje uspješnog odgovora
    } catch (err) {
      // Rukovanje greškama
      if (err.response) {
        setError(err.response.data.error || 'Došlo je do greške na serveru.');
      } else {
        setError('Nije moguće povezati se sa serverom. Provjerite da li je backend pokrenut.');
      }
    } finally {
      setLoading(false); // Prestanak učitavanja u svakom slučaju
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Personalizirani Vremenski Asistent</h1>
        <form onSubmit={handleSubmit} className="weather-form">
          <input
            type="text"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            placeholder="Unesite grad"
            className="input-field"
          />
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="input-field"
          />
          <button type="submit" disabled={loading} className="submit-button">
            {loading ? 'Pretražujem...' : 'Dohvati preporuke'}
          </button>
        </form>

        {error && <p className="error-message">{error}</p>}

        {data && (
          <div className="results">
            <div className="weather-info">
              <h2>Vrijeme za {data.weather.city}</h2>
              <img
                src={`http://openweathermap.org/img/wn/${data.weather.icon}@2x.png`}
                alt={data.weather.description}
              />
              <p className="temperature">{data.weather.temperature.toFixed(1)}°C</p>
              <p className="description">{data.weather.description}</p>
            </div>
            <div className="recommendations-info">
              <h2>AI Preporuke</h2>
              {/* Prikaz preporuka s prijelomima redaka */}
              {data.recommendations.split('\n').map((line, index) => (
                <p key={index}>{line}</p>
              ))}
            </div>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;