[README.md](https://github.com/user-attachments/files/28926105/README.md)
# ⚡ AutoClicker

Un autoclicker leggero con interfaccia grafica per Windows, scritto in Python con tkinter.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-informational?style=flat-square&logo=windows)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## Funzionalità

- **Start / Stop** tramite hotkey globale configurabile (default: `F6`) — funziona anche con la finestra in background
- **Intervallo** click configurabile in millisecondi, con preset rapidi (50 / 100 / 250 / 500 / 1000 ms)
- **Tasto mouse** — sinistro, destro, centrale
- **Doppio click** opzionale
- **Modificatori** — preset (Shift, Ctrl, Alt, Ctrl+Shift, ecc.) o combinazione manuale personalizzata
- **Limite click** — si ferma automaticamente dopo N click
- **Contatore** click in tempo reale con reset
- GUI dark theme

---

## Download

Puoi scaricare direttamente l'eseguibile precompilato dalla cartella [`dist/`](./dist):

> **[⬇ autoclicker.exe](./dist/autoclicker.exe)**

Non richiede Python installato. Al primo avvio Windows potrebbe mostrare un avviso SmartScreen — clicca su *Ulteriori informazioni* → *Esegui comunque*.

> ⚠️ L'app richiede i **privilegi di amministratore** per gestire gli hotkey globali. Verrà chiesta conferma UAC all'avvio.

---

## Eseguire da sorgente

### Requisiti

- Python 3.10+
- pip

### Installazione dipendenze

```bash
pip install pynput keyboard
```

### Avvio

```bash
python autoclicker.py
```

---

## Build del .exe

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --uac-admin autoclicker.py
```

L'eseguibile verrà generato in `dist\autoclicker.exe`.

---

## Note

- Il flag `--uac-admin` fa sì che Windows mostri il prompt UAC all'avvio, necessario per i hotkey globali con la libreria `keyboard`.
- L'app non effettua connessioni di rete di alcun tipo.
- Testato su Windows 10 / 11.
