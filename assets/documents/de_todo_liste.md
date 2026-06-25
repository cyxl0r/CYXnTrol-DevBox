TODO-LISTE
==========

Dokumentstand: Aktiver Proof-of-Concept und Entwicklungsstand.

DevBox besitzt bereits einen funktionsfähigen lokalen Launcher, eine grafische Hauptoberfläche, modulare Strukturansichten, Stammdaten- und Dokumentationspflege, Dokumentations-Snapshots, Formularimporte, lokale Werkzeugerkennung, eine Repository-Seite sowie erste Bausteine für den DevBox-spezifischen Repository-Prozess.

Die Anwendung ist noch keine fertige Endnutzer- oder Release-Version. Oberflächen, Veröffentlichungsabläufe, Dokumentvorlagen, Repository-Synchronisation und einzelne Entwicklungsmodule werden fortlaufend überarbeitet. Die aktuelle Dokumentation beschreibt den derzeitigen Entwicklungsstand und muss bei funktionalen Änderungen mitgepflegt werden.

Erstveröffentlichung: 
Projektbeginn: 2026
Autor / Herausgeber: Markus Walloner

1. Projektbezug
---------------

Kurzbeschreibung:
DevBox ist die lokale Entwicklungszentrale der CYXnTrol Development Platform. Sie bündelt wiederkehrende Arbeiten rund um Projektstruktur, Stammdaten, Dokumentation, Build-Werkzeuge, externe Kreativprogramme und Repository-Pflege in einer PySide6-Oberfläche.

DevBox ist kein Endnutzerprodukt. Die Anwendung dient als interne Arbeitsumgebung, mit der Entwicklungsabläufe nachvollziehbar vorbereitet, gepflegt und für spätere Veröffentlichungen strukturiert werden.


Langbeschreibung:
DevBox verbindet mehrere Entwicklungsaufgaben, die sonst über einzelne Skripte, Ordner, Tabellen, Konsolenfenster und externe Programme verteilt wären. Die Oberfläche stellt die Plattformdaten bereit, verwaltet Produktdaten und Dokumentationsinhalte, bereitet strukturierte Dokumente vor und bietet Werkzeuge für die Pflege eines kontrollierten Entwicklungsbestands.

Die Anwendung arbeitet lokal im Projektkontext. Ein Launcher ermittelt den Projektroot über die Datei .root, erstellt für die GUI eine temporäre Arbeitskopie und startet die grafische Oberfläche kontrolliert. Der echte Projektroot bleibt dabei die maßgebliche Quelle für Ressourcen, Datenbanken und Werkzeuge. Die DevBox verhindert parallele GUI-Instanzen und holt eine vorhandene Instanz beim erneuten Start in den Vordergrund.

Neben der Struktur-Werkstatt enthält DevBox eine Repository-Seite. Dort kann ein vorbereiteter Veröffentlichungsstand für die DevBox selbst erzeugt werden. Dieser Stand entsteht in einem temporären Arbeitsbereich, wird von nicht vorgesehenen Runtime-, Installer- und lokalen Daten bereinigt, erhält die gepflegten Dokumente und kann anschließend mit dem hinterlegten Repository verbunden werden. Dieser Sonderprozess gilt zunächst nur für DevBox; spätere Produkte erhalten eigene, passende Veröffentlichungsschemata.

DevBox erkennt außerdem lokale Installationsorte von Inkscape und GIMP, verwaltet diese Fundorte in einer lokalen SQLite-Datei und stellt für verfügbare Anwendungen Startbuttons bereit. Fehlende Fundorte werden beim Start erneut geprüft. Damit verbindet die Plattform ihre eigenen Daten, Skripte und Werkzeuge zu einer zentralen, lokal nachvollziehbaren Entwicklungsumgebung.


2. Offene Punkte
----------------

AKTUELLE TODO-LISTE

Repository und Veröffentlichung
- DevBox-Push-to-Git-Prozess in der GUI vollständig testen.
- Repository-URL- und Branch-Einrichtung mit realem Remote-Repository prüfen.
- Soll-/Ist-Abgleich, Schutzregeln und Entfernung obsoleter Repository-Dateien weiter absichern.
- Push-Erfolg und Temp-Cleanup weiterhin getrennt bewerten.
- Repository-Logausgabe und Fehlerdarstellung weiter verfeinern.
- Veröffentlichungsschemata für spätere Produkte getrennt von DevBox planen.

Dokumentation
- Formulartexte bei Funktionsänderungen aktualisieren.
- Nutzungsbedingungen und Datenschutzhinweise vor öffentlicher Nutzung rechtlich prüfen und an reale Datenflüsse anpassen.
- PDF-Layout mit unterschiedlichen Textlängen, Seitenumbrüchen und Sonderzeichen testen.
- Lizenzformulare vor Veröffentlichung mit dem vollständigen unveränderten Lizenztext ergänzen.

DevBox-Architektur
- Logging aller DevBox-Komponenten weiter vereinheitlichen.
- locdata- und logfile-Struktur langfristig dokumentieren.
- weitere Struktur-Werkstatt-Bereiche als konfigurierbare Module ergänzen.
- Altlasten und nicht mehr genutzte Skripte kontrolliert prüfen und bereinigen.
- die Compiler-/Packaging-Kette wieder als klaren DevBox-Bereich einbinden.

Werkzeuge und Qualität
- Start, Installation und Fehlerbehandlung externer Werkzeuge weiter testen.
- Multi-Monitor-Verhalten, Single-Instance-Fokus und Strukturansicht in verschiedenen Auflösungen prüfen.
- automatisierte Tests für Datenbankmigration, Dokumentexport, Snapshot-Struktur und Repository-Synchronisation ergänzen.


3. Zielbild
-----------

Aktueller Funktionsrahmen:
- Start einer einzelnen DevBox-Instanz mit Aktivierung einer bereits laufenden Instanz.
- Plattformseite mit Bereichen für Projektplattform, Anwendungen und Entwicklungssoftware.
- Lokale Erkennung und Startmöglichkeit für Inkscape und GIMP.
- Start von Installern für unterstützte Drittprogramme, sofern die Installer im Projekt vorhanden sind.
- zentrale SQLite-Stammdatenbank für Dach-, Produkt-, Dokumentations- und Strukturinformationen.
- Struktur-Werkstatt mit Navigation für Dach-Daten, Produkt-Daten, Dokumentationen und globale App-Ordnerstruktur.
- Dokumentations-Snapshot und kontrollierter Import vollständig überarbeiteter deutscher und englischer Dokumentinhalte.
- Erzeugung von Markdown-Dokumenten sowie PDF-Entwürfen für Nutzungsbedingungen und Datenschutzbestimmungen.
- Repository-Seite mit Produktauswahl, optionalem Commit-Text, optionalen Bildern und Logausgabe.
- Vorbereitung eines bereinigten, dokumentierten DevBox-Repository-Stands in einem temporären Arbeitsbereich.
- lokale Log- und Standortdatenbank unter AppData.

Ziele der nächsten Ausbaustufen:
- den DevBox-spezifischen Push-to-Git-Prozess weiter absichern und komfortabel machen;
- Repository-Daten pro Produkt pflegen;
- weitere strukturierte Entwicklungswerkzeuge als eigenständige Module hinzufügen;
- spätere Veröffentlichungsschemata für andere Produkte von der DevBox-Sonderlogik trennen;
- Fehlerzustände, Logs und Statusanzeigen weiter vereinheitlichen.


4. Technischer Bezug
--------------------

DevBox ist modular aufgebaut.

Die Startkette beginnt mit einem DevBox-Launcher. Dieser ermittelt den Projektroot über die .root-Datei, stellt lokale Laufzeitdaten unter AppData bereit, prüft gespeicherte Werkzeugpfade und startet die grafische Oberfläche aus einer temporären Kopie. Die temporäre Kopie reduziert das Risiko, dass eine laufende GUI Dateien im echten Projektroot sperrt oder verändert.

Die Haupt-GUI liegt im Bereich functions und nutzt mehrere Subscripts für Seiten, Layout, Datenzugriff und Spezialfunktionen. Die grafische Oberfläche verwendet PySide6. Sie greift über den echten Projektroot auf Ressourcen wie Grafiken, Fonts, Datenbankdateien, Installer und Funktionsskripte zu.

Die zentrale Stammdatenquelle ist die SQLite-Datei devbox_db.r0b unter resources/organization. Dort liegen unter anderem Produktdaten, Repository-Felder, Dokumentationsfelder und Strukturinformationen. Für lokale Laufzeitdaten verwendet DevBox separate SQLite-Dateien unter AppData: logfile.r0b für Protokolle und locdata.r0b für geprüfte Pfade zu externen Werkzeugen.

Dokumentationsformulare liegen komprimiert in doc_forms.r0b. Für einen Export werden sie in einen temporären docs-Ordner entpackt, mit Daten aus der SQLite-Datenbank befüllt und anschließend als Markdown-Dateien, PDF-Dokumente und Repository-taugliche Assets in einen vorbereiteten root_dir-Stand überführt. Dieser root_dir dient als kontrollierter Soll-Zustand für die DevBox-Repository-Pflege.


DevBox verwendet derzeit vor allem folgende Technologien:

- Python als Kernsprache für Launcher, Geschäftslogik, Datenaufbereitung und Automationen.
- PySide6 für die lokale grafische Benutzeroberfläche.
- SQLite für zentrale Projektstammdaten sowie lokale Laufzeit-, Log- und Standortdaten.
- openpyxl als Übergangs- oder Importwerkzeug für Tabellen, nicht als zentrale Stammdatenquelle.
- ReportLab und svglib für die lokale Erzeugung gestalteter PDF-Dokumente.
- Git und Git Credential Manager für Repository-Vorgänge und Authentifizierung.
- Inkscape und GIMP als externe, lokal gestartete Kreativwerkzeuge.
- C#-Generierung, .NET SDK, WiX und perspektivisch weitere Packaging-Werkzeuge für Build- und Installer-Prozesse.
- temporäre Arbeitsbereiche unter dem System-Temp-Verzeichnis für kontrollierte Kopien, Exporte und Veröffentlichungsvorbereitung.

Die technische Struktur trennt möglichst klar zwischen GUI, Funktionsskripten, Subscripts, Datenquellen und temporären Arbeitsständen.


Copyright (c) 2026 Markus Walloner
