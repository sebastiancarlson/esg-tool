Här är ett förslag på en omfattande "Master"-dokumentation för ett Gemini CLI-verktyg i Markdown-format. Du kan spara detta som `GEMINI_CLI_MASTER.md`.

Detta dokument är strukturerat som en komplett guide, från installation till avancerad användning och konfiguration.

---

# Gemini CLI Master Guide

Välkommen till master-dokumentationen för **Gemini CLI**. Detta verktyg ger dig kraften hos Googles Gemini-modeller direkt i din terminal. Det är designat för utvecklare, systemadministratörer och AI-entusiaster som vill integrera generativ AI i sina arbetsflöden.

## Innehållsförteckning

1. [Kom igång](https://www.google.com/search?q=%231-kom-ig%C3%A5ng)
* [Förutsättningar](https://www.google.com/search?q=%23f%C3%B6ruts%C3%A4ttningar)
* [Installation](https://www.google.com/search?q=%23installation)
* [Autentisering](https://www.google.com/search?q=%23autentisering)


2. [Grundläggande Kommandon](https://www.google.com/search?q=%232-grundl%C3%A4ggande-kommandon)
* [Chatt (Interaktivt läge)](https://www.google.com/search?q=%23chatt-interaktivt-l%C3%A4ge)
* [Generera Text (One-shot)](https://www.google.com/search?q=%23generera-text-one-shot)
* [Lista Modeller](https://www.google.com/search?q=%23lista-modeller)


3. [Arbeta med Filer & Bilder](https://www.google.com/search?q=%233-arbeta-med-filer--bilder)
* [Analysera Textfiler](https://www.google.com/search?q=%23analysera-textfiler)
* [Multimodal (Bildanalys)](https://www.google.com/search?q=%23multimodal-bildanalys)


4. [Avancerad Konfiguration](https://www.google.com/search?q=%234-avancerad-konfiguration)
* [Temperatur och Tokens](https://www.google.com/search?q=%23temperatur-och-tokens)
* [Systeminstruktioner](https://www.google.com/search?q=%23systeminstruktioner)
* [JSON-utdata](https://www.google.com/search?q=%23json-utdata)


5. [Pipes och Scripting](https://www.google.com/search?q=%235-pipes-och-scripting)
6. [Felsökning](https://www.google.com/search?q=%236-fels%C3%B6kning)

---

## 1. Kom igång

### Förutsättningar

* **Python:** Version 3.9 eller senare.
* **API-nyckel:** En aktiv API-nyckel från [Google AI Studio](https://www.google.com/search?q=https://aistudio.google.com/).

### Installation

Installera verktyget via pip (förutsatt att paketet är publicerat eller installerat lokalt):

```bash
# Alternativ A: Installera från PyPI (fiktivt paketnamn)
pip install gemini-cli-tool

# Alternativ B: Installera från källkod
git clone https://github.com/ditt-namn/gemini-cli.git
cd gemini-cli
pip install .

```

### Autentisering

För att inte behöva ange din nyckel varje gång, spara den som en miljövariabel.

**Linux/macOS:**

```bash
export GEMINI_API_KEY="din_api_nyckel_här"
# Lägg till i .bashrc eller .zshrc för permanent lagring

```

**Windows (PowerShell):**

```powershell
$env:GEMINI_API_KEY="din_api_nyckel_här"

```

Du kan också köra `gemini config --key "din_nyckel"` för att spara den i en lokal konfigurationsfil.

---

## 2. Grundläggande Kommandon

### Chatt (Interaktivt läge)

Starta en konversation där modellen kommer ihåg vad som sagts tidigare (context awareness).

```bash
gemini chat

```

* **Kommandon i chatten:**
* `/reset`: Rensa historiken.
* `/save <filnamn>`: Spara konversationen.
* `/exit`: Avsluta.



### Generera Text (One-shot)

Skicka en enskild prompt och få svar direkt till `stdout`. Perfekt för snabba frågor.

```bash
gemini ask "Skriv en haiku om Linux"

```

### Lista Modeller

Se vilka modeller som är tillgängliga för din API-nyckel (t.ex. Gemini Pro, Gemini 1.5 Flash).

```bash
gemini models list

```

---

## 3. Arbeta med Filer & Bilder

### Analysera Textfiler

Läs in kod eller textfiler som kontext för din prompt.

```bash
# Be Gemini förklara koden i en fil
gemini ask --file main.py "Vad gör den här koden och hur kan jag optimera den?"

# Sammanfatta en README
gemini ask --file README.md "Sammanfatta projektet på svenska"

```

### Multimodal (Bildanalys)

Använd Gemini Pro Vision (eller Gemini 1.5) för att analysera bilder.

```bash
# Beskriv vad som händer i en bild
gemini ask --image screenshot.png "Beskriv gränssnittet i den här bilden"

# Jämför två bilder
gemini ask --image bild1.jpg --image bild2.jpg "Vilka är skillnaderna?"

```

---

## 4. Avancerad Konfiguration

Du kan styra modellens kreativitet och svarslängd med flaggor.

### Temperatur och Tokens

* **`--temp` (0.0 - 1.0):** Styr kreativiteten. Lågt värde är mer deterministiskt (fakta), högt är mer kreativt.
* **`--max-tokens`:** Begränsa längden på svaret.

```bash
# Exakt och koncist svar
gemini ask "Vad är huvudstaden i Peru?" --temp 0.0

# Kreativt och långt svar
gemini ask "Skriv en sci-fi novell" --temp 0.9 --max-tokens 2000

```

### Systeminstruktioner

Ge modellen en persona eller strikta regler för hur den ska bete sig.

```bash
gemini chat --system "Du är en senior Python-utvecklare. Svara endast med kodblock, ingen förklarande text."

```

### JSON-utdata

Tvinga modellen att svara i JSON-format, vilket är användbart om du bygger andra verktyg ovanpå CLI:t.

```bash
gemini ask "Lista 3 frukter och deras färg" --format json

```

*Utdata:* `[{"frukt": "Äpple", "färg": "Röd"}, ...]`

---

## 5. Pipes och Scripting

Gemini CLI läser från `stdin`, vilket gör det extremt kraftfullt i Unix-pipes.

**Exempel 1: Förklara ett git-fel**

```bash
git push 2>&1 | gemini ask "Jag fick detta felmeddelande, hur fixar jag det?"

```

**Exempel 2: Automatisera dokumentation**

```bash
cat function.py | gemini ask "Skriv docstrings för denna funktion" > function_docs.py

```

**Exempel 3: Skapa en commit-meddelande**

```bash
git diff | gemini ask "Skriv ett kort commit-meddelande baserat på dessa ändringar"

```

---

## 6. Felsökning

* **Error: API Key not found:** Kontrollera att miljövariabeln `GEMINI_API_KEY` är satt.
* **Error: Model overloaded:** Googles servrar är upptagna. Vänta någon minut och försök igen.
* **400 Bad Request:** Ofta p.g.a. att bilden är för stor eller filformatet inte stöds.
* **Debug-läge:** Kör med `--verbose` för att se exakt vilken payload som skickas till API:et.

```bash
gemini ask "Test" --verbose

```

---

*Dokumentation genererad för Gemini CLI v1.0.0*