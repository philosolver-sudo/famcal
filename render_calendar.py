#!/usr/bin/env python3
"""
Rendert einen oder mehrere Google-Kalender (per öffentlichem iCal-Link) als
graustufiges PNG-Bild, passend für den E-Ink-Bildschirm eines alten Kindle
Paperwhite 2 (758 x 1024 Pixel, Hochformat).

Das erzeugte Bild wird von GitHub Actions periodisch neu gebaut und über
GitHub Pages bereitgestellt. Der Kindle holt es sich per "Online Screensaver"
Extension selbst ab.

Konfiguration ausschließlich über Umgebungsvariablen (siehe README.md):
    ICS_URLS      - einer oder mehrere iCal-Links, mit Komma getrennt
    CALENDAR_NAMES- optionale Namen für die Kalender, mit Komma getrennt
                    (gleiche Reihenfolge wie ICS_URLS), z.B. "Familie,Nick Schule"
    DAYS_AHEAD    - wie viele Tage im Voraus angezeigt werden (Default: 6)
    TIMEZONE      - Zeitzone für die Anzeige (Default: Europe/Berlin)
    OUT_PATH      - Zieldatei für das PNG (Default: docs/calendar.png)
    TITLE         - Überschrift oben im Bild (Default: "Familienkalender")
"""

import os
import sys
from datetime import datetime, timedelta, date

import requests
from icalendar import Calendar
import recurring_ical_events
from PIL import Image, ImageDraw, ImageFont
from zoneinfo import ZoneInfo

# --- Konfiguration aus Umgebungsvariablen -----------------------------------

ICS_URLS = [u.strip() for u in os.environ.get("ICS_URLS", "").split(",") if u.strip()]
CALENDAR_NAMES = [n.strip() for n in os.environ.get("CALENDAR_NAMES", "").split(",") if n.strip()]
DAYS_AHEAD = int(os.environ.get("DAYS_AHEAD") or 6)
TZ_NAME = os.environ.get("TIMEZONE", "Europe/Berlin")
OUT_PATH = os.environ.get("OUT_PATH", "docs/calendar.png")
TITLE = os.environ.get("TITLE", "Familienkalender")

WIDTH, HEIGHT = 758, 1024  # Kindle Paperwhite 2 Auflösung, Hochformat

TZ = ZoneInfo(TZ_NAME)

# Auf GitHub-Actions-Ubuntu-Runnern vorinstallierte Schriften (kein Bundling nötig)
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
FONT_REGULAR = os.path.join(FONT_DIR, "DejaVuSans.ttf")

WEEKDAYS_DE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MONTHS_DE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
             "August", "September", "Oktober", "November", "Dezember"]


def load_events():
    """Holt alle konfigurierten Kalender und liefert eine Liste von
    (datum, uhrzeit_text, titel, kalender_name)-Tupeln für die nächsten
    DAYS_AHEAD Tage, chronologisch sortiert."""
    if not ICS_URLS:
        print("FEHLER: keine ICS_URLS gesetzt.", file=sys.stderr)
        sys.exit(1)

    now = datetime.now(TZ)
    start = datetime(now.year, now.month, now.day, tzinfo=TZ)
    end = start + timedelta(days=DAYS_AHEAD)

    all_events = []
    for i, url in enumerate(ICS_URLS):
        name = CALENDAR_NAMES[i] if i < len(CALENDAR_NAMES) else ""
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        cal = Calendar.from_ical(resp.content)

        # recurring_ical_events kümmert sich um wiederkehrende Termine (RRULE)
        occurrences = recurring_ical_events.of(cal).between(start, end)

        for ev in occurrences:
            summary = str(ev.get("SUMMARY", "(ohne Titel)"))
            dtstart = ev.get("DTSTART").dt

            if isinstance(dtstart, datetime):
                dtstart_local = dtstart.astimezone(TZ)
                ev_date = dtstart_local.date()
                time_text = dtstart_local.strftime("%H:%M")
            else:
                # ganztägiger Termin (date statt datetime)
                ev_date = dtstart
                time_text = "ganztägig"

            all_events.append((ev_date, time_text, summary, name))

    # Ganztägige Termine zuerst, danach nach Uhrzeit sortiert (übliche Konvention)
    all_events.sort(key=lambda t: (t[0], t[1] != "ganztägig", t[1]))
    return all_events, start


def group_by_day(events, start, days_ahead):
    """Gruppiert die Termine nach Kalendertag, inkl. leerer Tage."""
    by_day = {}
    for i in range(days_ahead):
        d = (start + timedelta(days=i)).date()
        by_day[d] = []
    for ev_date, time_text, summary, name in events:
        if ev_date in by_day:
            by_day[ev_date].append((time_text, summary, name))
    return by_day


def format_day_header(d: date, today: date) -> str:
    weekday = WEEKDAYS_DE[d.weekday()]
    label = f"{weekday}, {d.day}. {MONTHS_DE[d.month - 1]}"
    if d == today:
        label += "  –  heute"
    elif d == today + timedelta(days=1):
        label += "  –  morgen"
    return label


def render_image(by_day, today):
    img = Image.new("L", (WIDTH, HEIGHT), color=255)  # weißer Hintergrund, Graustufen
    draw = ImageDraw.Draw(img)

    font_title = ImageFont.truetype(FONT_BOLD, 40)
    font_day = ImageFont.truetype(FONT_BOLD, 28)
    font_event = ImageFont.truetype(FONT_REGULAR, 24)
    font_meta = ImageFont.truetype(FONT_REGULAR, 18)

    x_margin = 24
    y = 20

    # Titelzeile + Datum/Uhrzeit der letzten Aktualisierung
    draw.text((x_margin, y), TITLE, font=font_title, fill=0)
    updated = datetime.now(TZ).strftime("%d.%m. %H:%M")
    meta_text = f"Stand: {updated}"
    meta_w = draw.textlength(meta_text, font=font_meta)
    draw.text((WIDTH - x_margin - meta_w, y + 12), meta_text, font=font_meta, fill=0)
    y += 60
    draw.line((x_margin, y, WIDTH - x_margin, y), fill=0, width=2)
    y += 16

    for d, items in by_day.items():
        if y > HEIGHT - 60:
            break  # kein Platz mehr auf dem Bildschirm

        header = format_day_header(d, today)
        draw.text((x_margin, y), header, font=font_day, fill=0)
        y += 34

        if not items:
            draw.text((x_margin + 20, y), "– keine Termine –", font=font_event, fill=110)
            y += 30
        else:
            for time_text, summary, name in items:
                line = f"{time_text}   {summary}"
                if name:
                    line += f"  ({name})"
                draw.text((x_margin + 20, y), line, font=font_event, fill=0)
                y += 32
                if y > HEIGHT - 40:
                    break

        y += 14  # Abstand zwischen Tagen

    return img


def main():
    events, start = load_events()
    today = datetime.now(TZ).date()
    by_day = group_by_day(events, start, DAYS_AHEAD)
    img = render_image(by_day, today)

    os.makedirs(os.path.dirname(OUT_PATH) or ".", exist_ok=True)
    img.save(OUT_PATH, format="PNG")
    print(f"Kalenderbild gespeichert: {OUT_PATH}")


if __name__ == "__main__":
    main()
