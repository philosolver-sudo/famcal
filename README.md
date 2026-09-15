# Familienkalender fürs Kindle – Cloud-Setup

https://calendar.google.com/calendar/ical/qlvhficoedrfg9v581enoap8nk%40group.calendar.google.com/private-d10c9fa8081f743af391d9b8bc88c142/basic.ics



Dieses kleine Projekt erzeugt automatisch alle 30 Minuten ein Bild deines
Google-Kalenders (als PNG, passend für den Kindle-Paperwhite-2-Bildschirm)
und stellt es kostenlos über GitHub Pages bereit. Dein Kindle holt sich
dieses Bild dann selbst ab und zeigt es als Startbildschirm/Screensaver an.

Es läuft komplett in der Cloud (GitHub Actions) – du brauchst dafür keinen
eigenen Server oder Raspberry Pi.

## 1. Google-Kalender-Link besorgen

1. Öffne [Google Calendar](https://calendar.google.com) im Browser.
2. Klick bei dem Kalender, den du anzeigen willst (z.B. deinem Hauptkalender
   oder Nicks Schulkalender), auf die drei Punkte → **Einstellungen und
   Freigabe**.
3. Scrolle zu **"Kalender integrieren"** und kopiere die
   **"Geheime Adresse im iCal-Format"** (endet auf `.ics`).

   Wichtig: Das ist ein privater, aber unauffindbarer Link – niemand kann
   ihn erraten, aber jeder, der ihn kennt, kann deinen Kalender lesen.
   Deshalb landet er gleich als **Secret** in GitHub, nicht offen im Code.

4. Falls du mehrere Kalender kombinieren willst (z.B. deinen + Nicks
   Schulkalender), wiederhole das für jeden Kalender.

## 2. GitHub-Repository anlegen

1. Falls noch nicht vorhanden: kostenloser Account auf
   [github.com](https://github.com).
2. Neues Repository anlegen, z.B. `kindle-familienkalender` (kann **privat**
   bleiben – GitHub Pages funktioniert auch bei privaten Repos, sofern dein
   Account das unterstützt; sonst einfach öffentlich lassen, das Bild selbst
   verrät nichts Sensibles außer eurem Terminplan).
3. Die vier Dateien aus diesem Ordner hochladen (per "Add file → Upload
   files" im Browser reicht völlig):
   - `render_calendar.py`
   - `requirements.txt`
   - `.github/workflows/update-calendar.yml`
   - `README.md` (optional)

## 3. Kalender-Link(s) als Secret hinterlegen

1. Im Repository: **Settings → Secrets and variables → Actions**.
2. Unter **"Secrets"** → **New repository secret**:
   - Name: `ICS_URLS`
   - Wert: dein iCal-Link (bei mehreren Kalendern mit Komma trennen, ohne
     Leerzeichen), z.B.:
     `https://calendar.google.com/.../basic.ics,https://calendar.google.com/.../nick.ics`
3. Optional unter **"Variables"** (nicht geheim, daher hier statt als
   Secret):
   - `CALENDAR_NAMES` = `Familie,Nick Schule` (gleiche Reihenfolge wie oben,
     erscheint als kleiner Zusatz hinter jedem Termin)
   - `DAYS_AHEAD` = `6` (wie viele Tage im Voraus angezeigt werden)

## 4. GitHub Pages aktivieren

1. **Settings → Pages**.
2. Bei **"Build and deployment"**: Branch `main`, Ordner `/docs` auswählen,
   speichern.
3. GitHub zeigt dir die Adresse deiner Seite an, z.B.:
   `https://<dein-username>.github.io/kindle-familienkalender/`
4. Dein Kalenderbild liegt dann unter:
   `https://<dein-username>.github.io/kindle-familienkalender/calendar.png`

   **Diese Bild-URL ist es, die du gleich in die Kindle-Screensaver-
   Extension einträgst.**

## 5. Erster Testlauf

1. Im Repository: **Actions** → Workflow "Kalenderbild aktualisieren" →
   **Run workflow** (manuell auslösen, nicht auf die 30 Minuten warten).
2. Nach ca. 1 Minute sollte im `docs`-Ordner eine `calendar.png` auftauchen
   und unter der Pages-URL von Schritt 4 sichtbar sein.
3. Falls der Lauf rot/fehlgeschlagen ist: im Log nachschauen – meist liegt es
   an einem falsch kopierten iCal-Link oder einem fehlenden Secret-Namen.

## 6. Auf dem Kindle einrichten

Sobald die Bild-URL erreichbar ist:

1. Falls noch nicht installiert: **linkss** (NiLuJe's Screensaver Hack,
   Fork von bfabiszewski/kindle-screensavers, PW2-kompatibel) als
   `extensions`-Ordner per USB installieren – genauso wie KOReader.
2. Danach die **Online-Screensaver**-Extension (PW2-Fork, z.B.
   alextrical/KindleOnlineScreensaver) ebenfalls per USB in `extensions`
   installieren.
3. `onlinescreensaver/bin/config.sh` mit einem Unicode-fähigen Editor (z.B.
   Notepad++, wichtig: Unix-Zeilenenden beibehalten) öffnen und dort deine
   Bild-URL aus Schritt 4 sowie das gewünschte Aktualisierungsintervall
   eintragen (in der Datei ist jede Option kommentiert).
4. Über KUAL → "Online-Screensaver" einmal manuell aktualisieren, um es zu
   testen, danach die automatische Aktualisierung aktivieren.

Meld dich, wenn du bei Schritt 1–5 (Cloud-Teil) durch bist oder irgendwo
hängst – dann gehen wir gemeinsam zum Kindle-Teil über.

