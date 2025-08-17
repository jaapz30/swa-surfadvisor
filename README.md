# SWA surfadvisor — HYBRID + HANDS‑OFF

Volledig automatisch én robuust:
- **Live modus:** de website probeert eerst direct de modellen via Open‑Meteo (GFS, ICON, ECMWF, Météo‑France, KNMI ±60u).
- **Fallback modus:** lukt live niet (bv. CORS/adblock/offline), dan gebruikt de site **fallback.json**.
- **Hands‑off update:** `fallback.json` wordt elk uur automatisch ververst door de meegeleverde **GitHub Action** (server‑side).

## Snel aanzetten (eenmalig)
1. Maak op GitHub een **public repo** (bv. `swa-surfadvisor`).  
2. Upload **alle** bestanden uit deze map (inclusief `.github/` en `scripts/`).  
3. Ga naar **Settings → Pages**: *Deploy from a branch* → `main` / **root** → Save.  
4. Ga naar **Actions** en sta de workflow toe als GitHub daarom vraagt.

Daarna is je site live op:
```
https://<jouw-gebruikersnaam>.github.io/swa-surfadvisor/
```

De workflow draait elk uur en overschrijft `fallback.json` met de nieuwste modeldata.
De website kiest automatisch: **Live** als het kan, anders **fallback.json**, en als dat ook ontbreekt: **demo‑data**.

### Aanpassen (optioneel)
- Locatie (Schokkerhaven): pas LAT/LON in `scripts/generate.py` en in `index.html` aan.  
- Updatefrequentie: wijzig de `cron` in `.github/workflows/update.yml`.  
