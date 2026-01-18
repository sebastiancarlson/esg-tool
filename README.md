# Gemini CLI Tool

Detta projekt implementerar **Gemini CLI** enligt specifikationen i `GEMINI_CLI_MASTER.md`.

## Installation

1.  Se till att du har Python 3.9+ installerat.
2.  Installera beroenden (om du inte redan gjort det):
    ```bash
    pip install .
    ```
    Eller manuellt:
    ```bash
    pip install google-generativeai typer[all] rich python-dotenv pillow
    ```

## Användning

Du kan köra verktyget direkt via Python eller via det installerade kommandot (om du körde `pip install .`).

### Konfigurera API-nyckel
```bash
python -m gemini_cli.main config --key "DIN_API_NYCKEL"
```

### Chatta
```bash
python -m gemini_cli.main chat
```

### Ställ en fråga (One-shot)
```bash
python -m gemini_cli.main ask "Vad är meningen med livet?"
```

### Använd med filer
```bash
python -m gemini_cli.main ask --file README.md "Sammanfatta denna fil"
```

### Lista modeller
```bash
python -m gemini_cli.main models
```

För fullständig dokumentation, se `GEMINI_CLI_MASTER.md`.
