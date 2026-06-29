TODO-LISTE
==========

Dokumentstand: Aktiver Proof-of-Concept und Entwicklungsstand.

DevBox besitzt einen funktionsfähigen lokalen Launcher, eine grafische Hauptoberfläche, modulare Strukturansichten, Stammdaten- und Dokumentationspflege, Dokumentations-Snapshots, lokale Werkzeugerkennung, eine Repository-Seite sowie erste Bausteine für den DevBox-spezifischen Veröffentlichungsprozess.

Der deskNode-Bereich ist aktiv in die DevBox integriert. Supervisor und Daemon können aus der GUI gestartet und gestoppt werden; deren Konsolenausgabe wird im deskNode-Log angezeigt. Die Produktversion kann aus den Stammdaten bearbeitet werden. UX-Themes können benannt, angelegt, gelöscht, dupliziert, umbenannt und gespeichert werden. Nach dem Speichern wird die deskNode-Manufakturdatenbank aktualisiert.

Die Symbolverwaltung ist als erste funktionsfähige Katalogoberfläche vorhanden. Sie verwaltet deskNode-Gerätekategorien und Verbrauchergeräte über Auswahlmenüs sowie Dialoge zum Anlegen, Bearbeiten und Löschen. Neue Geräte erhalten eine einzelne PNG-Quelle, die unter ihrer record_id als symbol_source_<record_id>.png abgelegt wird. Nach jeder erfolgreichen Katalogänderung wird create_manufacturer_db.py ausgeführt, damit mnfctr_db.r0b die aktuellen Theme-, Kategorien- und Gerätedaten enthält.

Der Graphic-Pack-Build ist als Proof-of-Concept funktionsfähig. Er erzeugt aus Symbolquellen und UX-Themes mehrere vorbereitete Grafikzustände für Verbraucher. Die eigentliche deskNode-Laufzeitintegration, Asset-Auswahl, Sprachpakete und vollständige Zustandslogik werden noch weiterentwickelt.

DevBox ist keine fertige Endnutzer- oder Release-Version. Oberflächen, Datenbankmigrationen, Produktmodule, Veröffentlichungsabläufe, Dokumentvorlagen und Tests werden fortlaufend überarbeitet. Diese Dokumentation beschreibt den derzeitigen Stand und muss bei funktionalen Änderungen mitgepflegt werden.

Erstveröffentlichung: 
Projektbeginn: 2026
Autor / Herausgeber: Markus Walloner

1. Projektbezug
---------------

Kurzbeschreibung:
DevBox ist die lokale Entwicklungszentrale der CYXnTrol Development Platform. Die PySide6-Anwendung bündelt Projektstruktur, Stammdaten, Dokumentation, lokale Werkzeuge, Produktmodule, Repository-Vorbereitung und wiederkehrende Entwicklungsabläufe.

DevBox ist kein Endnutzerprodukt. Es ist eine interne Arbeitsumgebung, in der technische Anforderungen, Datenmodelle, Oberflächen, Build-Schritte und Veröffentlichungsstände nachvollziehbar vorbereitet, geprüft und weiterentwickelt werden.


Langbeschreibung:
DevBox verbindet Aufgaben, die sonst über Einzelskripte, Ordner, Tabellen, Konsolenfenster und externe Programme verteilt wären. Die Anwendung verwaltet zentrale Projekt- und Produktdaten, stellt Dokumentationsinhalte bereit, organisiert globale Strukturvorlagen, erkennt lokale Werkzeuge und bündelt produktbezogene Entwicklungsfunktionen in einer gemeinsamen Oberfläche.

Ein aktives Produktmodul ist deskNode. Die deskNode-Seite kann den lokalen Supervisor und Daemon starten und stoppen, die Produktversion aus den Stammdaten bearbeiten, UX-Themes pflegen und die Symbolverwaltung öffnen. Themes werden mit benannten Datensätzen, RGBA-Farben, globalen Schriftdateien, Größen, Konturen und Formregeln gepflegt. Nach jeder erfolgreichen Theme-Änderung wird die produktnahe deskNode-Manufakturdatenbank aktualisiert.

Die Symbolverwaltung ist die zentrale Quelle für Gerätekategorien und Verbrauchersymbole. Kategorien und Geräte werden in der DevBox-Datenbank angelegt, bearbeitet oder gelöscht. Beim Anlegen eines neuen Verbrauchergeräts wird genau eine PNG-Quelle angenommen und anhand der stabilen Datensatz-ID als symbol_source_<record_id>.png im globalen Grafikordner abgelegt. Der Graphic-Pack-Build erzeugt daraus vorberechnete Varianten für Themes und Zustände, damit die spätere deskNode-Laufzeit nur passende Assets auswählen muss.

DevBox arbeitet lokal im Projektkontext. Ein Launcher ermittelt den Projektroot über die Datei .root, stellt Laufzeitdaten unter AppData bereit, prüft externe Werkzeuge und startet die GUI aus einer temporären Arbeitskopie. Der echte Projektroot bleibt die maßgebliche Quelle für Ressourcen, Datenbanken und Funktionsskripte. Eine Einzelinstanzlogik verhindert parallele DevBox-Fenster und aktiviert beim erneuten Start die bereits geöffnete Instanz.

Das Projekt entsteht in einem KI-gestützten, iterativen Entwicklungsprozess. Fachliche Anforderungen, Prozesslogik, Datenmodelle, UX-Entscheidungen, Testfälle und Abnahmen werden durch den Projektverantwortlichen gesteuert; Implementierungsschritte werden mit KI-gestützten Werkzeugen erstellt, überprüft und fortlaufend nachgeschärft.


2. Offene Punkte
----------------

AKTUELLE TODO-LISTE

deskNode und UX-Themes
- Speichern, Migration und Aktualisierung mehrerer UX-Themes unter realen GUI-Bedingungen weiter testen.
- Sicherstellen, dass jeder erfolgreiche Theme-Speichervorgang erst nach Aktualisierung von mnfctr_db.r0b als vollständig gilt.
- Theme-Auswahl in der späteren deskNode-Laufzeit über stabile record_id statt über umbenennbare Theme-Namen anbinden.
- Fehlende Schriftdateien, ungültige RGBA-Werte und defekte Theme-Datensätze robust behandeln.
- Zusätzliche visuelle Zustände für Offline, Warnung, Fehler, unbekannte Geräte und Verbrauchsgrenzen definieren.

Symbolkatalog
- Symbolverwaltung mit realen Kategorien und Verbrauchersymbolen weiter füllen.
- Sprachpakete für Kategorien und Geräte anhand der automatisch erzeugten translation_key-Werte anlegen.
- Suche im späteren deskNode-Symbolwähler über lokalisierte Namen und Suchbegriffe definieren.
- Prüfen, wie umbenannte category_key- oder device_key-Werte ohne Bruch bestehender SmartPlug-Zuordnungen behandelt werden.
- PNG-Austausch für bestehende Geräte gezielt als separaten Bearbeitungsablauf ergänzen.
- Festlegen, wie deskNode consumer_device_id und optional consumer_device_key an SmartPlug-Zuordnungen speichert.

Graphic-Pack-Build
- Die erzeugten Grafikpakete mit mehr Symbolen, mehr Themes und längeren Dateinamen testen.
- Den Builder auf die durch record_id benannten symbol_source_<record_id>.png-Quellen vollständig ausrichten.
- Build-Ergebnisse gegen erwartete Anzahl von Themes, Symbolen, Masken und Zustandsdateien validieren.
- Aufräumen, Archivierung und Installation des finalen Grafikpakets weiter absichern.
- Optional inkrementellen Build entwickeln, damit bei einer kleinen Änderung nicht jedes Asset neu erzeugt werden muss.
- Fehlerbehandlung für fehlende Symbolquellen, Inkscape, GIMP und nicht unterstützte SVG-/PNG-Dateien erweitern.

Repository und Veröffentlichung
- DevBox-Push-to-Git-Prozess in der GUI vollständig testen.
- Prüfen, dass applications/deskNode/resources/scripts vollständig ohne __pycache__-Inhalte im Veröffentlichungsroot landet.
- Repository-URL- und Branch-Einrichtung mit realem Remote-Repository prüfen.
- Soll-/Ist-Abgleich, Schutzregeln und Entfernung obsoleter Repository-Dateien weiter absichern.
- Push-Erfolg und Temp-Cleanup weiterhin getrennt bewerten.

Dokumentation und Qualität
- Formulartexte bei Funktionsänderungen aktualisieren.
- Nutzungsbedingungen und Datenschutzhinweise vor öffentlicher Nutzung rechtlich prüfen und an reale Datenflüsse anpassen.
- PDF-Layout mit unterschiedlichen Textlängen, Seitenumbrüchen und Sonderzeichen testen.
- Logging aller DevBox-Komponenten weiter vereinheitlichen.
- Multi-Monitor-Verhalten, Single-Instance-Fokus, Strukturansicht und deskNode-Ansichten in verschiedenen Auflösungen prüfen.
- Automatisierte Tests für Datenbankmigration, Theme-Speicherung, Symbolkatalog, Grafik-Build, Dokumentexport, Snapshot-Struktur und Repository-Synchronisation ergänzen.


3. Zielbild
-----------

Aktueller Funktionsrahmen:
- Start einer einzelnen DevBox-Instanz mit Aktivierung einer bereits laufenden Instanz.
- Plattformseite mit Bereichen für Projektplattform, Anwendungen, Entwicklungssoftware und Produktmodule.
- Lokale Erkennung und Startmöglichkeit für Inkscape und GIMP.
- Start von Installern für unterstützte Drittprogramme, sofern die Installer im Projekt vorhanden sind.
- Zentrale SQLite-Stammdatenbank für Dach-, Hersteller-, Produkt-, Dokumentations-, Struktur-, Repository-, UX-Theme- und deskNode-Symbolkatalogdaten.
- Struktur-Werkstatt mit Navigation für Dach-Daten, Produkt-Daten, Dokumentationen und globale App-Ordnerstruktur.
- Initialisierung ausschließlich vollständig leerer Produktordner anhand der globalen Strukturvorlage.
- Export von Dokumentations-Snapshots und kontrollierter Import vollständig überarbeiteter deutscher und englischer Dokumentation.
- Erzeugung von Markdown-Dokumenten und PDF-Entwürfen für Nutzungsbedingungen und Datenschutz.
- Repository-Seite mit Produktauswahl, optionalem Commit-Text, optionalen Bildern und Logausgabe.
- Vorbereitung eines bereinigten DevBox-Veröffentlichungsstands in einem temporären Arbeitsbereich.
- deskNode-Tab zum Starten und Stoppen von Supervisor und Daemon mit Live-Konsolenausgabe.
- Bearbeitung der deskNode-Version und anschließende Aktualisierung von mnfctr_db.r0b.
- Oberflächengestaltung mit mehreren benannten UX-Themes, RGBA-Farben, globalen Schriftdateien, Schriftformaten, Radien und Konturen.
- Symbolverwaltung für Gerätekategorien und Verbrauchergeräte über Auswahlmenüs sowie Anlegen, Bearbeiten und Löschen per Dialog.
- Automatische Ableitung von Kategorie- und Geräteschlüsseln sowie Übersetzungsschlüsseln aus Eingaben.
- Annahme genau einer PNG-Quelle für neue Verbrauchergeräte und Ablage als symbol_source_<record_id>.png.
- Aktualisierung der deskNode-Manufakturdatenbank nach jeder erfolgreichen Änderung an Theme oder Symbolkatalog.
- Graphic-Pack-Build aus Symbolquellen, UX-Themes, GIMP-Masken, Inkscape-Vektorisierung und vorberechneten Zustandsvarianten.

Ziele:
- wiederholbare Entwicklungsschritte statt manueller Einzellösungen;
- klare Trennung zwischen DevBox-Stammdaten, deskNode-Laufzeitdaten, temporären Builds und Repository-Export;
- stabile technische Referenzen für Themes, Kategorien, Verbrauchergeräte und Assets;
- Erweiterbarkeit für weitere CYXnTrol-Produkte, ohne DevBox als beliebige Skriptsammlung zu behandeln.


4. Technischer Bezug
--------------------

DevBox ist modular aufgebaut.

Die Startkette beginnt mit einem DevBox-Launcher. Dieser ermittelt den Projektroot über die .root-Datei, stellt lokale Laufzeitdaten unter AppData bereit, prüft gespeicherte Werkzeugpfade und startet die grafische Oberfläche aus einer temporären Kopie. Die temporäre Kopie reduziert das Risiko, dass eine laufende GUI Dateien im echten Projektroot sperrt oder verändert.

Die Haupt-GUI liegt im Bereich resources/applications/devbox/functions und nutzt spezialisierte Subscripts für Seiten, Layout, Datenzugriff, Prozessstarts und Produktmodule. Die grafische Oberfläche verwendet PySide6. Sie greift über den echten Projektroot auf Grafiken, Fonts, Datenbanken, Installer und Funktionsskripte zu.

Die zentrale Stammdatenquelle ist resources/organization/devbox_db.r0b. Dort liegen Produktdaten, Repository-Felder, Dokumentationsfelder, Strukturinformationen, benannte deskNode-UX-Themes sowie die Symbolkatalogtabellen desknode_consumer_device_categories und desknode_consumer_devices. Für lokale Laufzeitdaten verwendet DevBox logfile.r0b und locdata.r0b unter AppData.

deskNode besitzt zusätzlich applications/deskNode/data/mnfctr_db.r0b. Sie wird durch create_manufacturer_db.py neu erzeugt und enthält master_data, ux_themes, consumer_device_categories und consumer_devices. Dadurch bleibt die deskNode-Laufzeit von der vollständigen DevBox-Stammdatenbank entkoppelt.

Der Graphic-Pack-Build verarbeitet globale Symbolquellen, Skalierung, Masken, Vektorisierung und Theme-Daten in temporären Arbeitsordnern. Inkscape und GIMP werden als externe lokale Werkzeuge verwendet. Das Ergebnis ist ein komprimiertes Grafikpaket mit vorberechneten Zustandsvarianten, das deskNode später laden kann.


DevBox verwendet derzeit vor allem folgende Technologien:

- Python als Kernsprache für Launcher, Prozesslogik, Datenaufbereitung, Automationen und produktbezogene Werkzeuge.
- PySide6 für die lokale grafische Benutzeroberfläche.
- SQLite für zentrale Projektstammdaten, deskNode-Manufakturdaten sowie lokale Runtime-, Log- und Standortdaten.
- openpyxl als Übergangs- oder Importwerkzeug für Tabellen, nicht als zentrale Stammdatenquelle.
- ReportLab und svglib für die lokale Erzeugung gestalteter PDF-Dokumente.
- Git und Git Credential Manager für Repository-Vorgänge und Authentifizierung.
- Inkscape für Skalierung, SVG-Arbeit und Vektorisierung von Masken.
- GIMP 3 für nichtinteraktive Bildbearbeitung und vorbereitende Maskenschritte.
- XML-/SVG-Verarbeitung mit Python-Standardbibliotheken für die Bereinigung generierter Masken.
- C#-Generierung, .NET SDK, WiX und perspektivisch weitere Packaging-Werkzeuge für Build- und Installer-Prozesse.
- temporäre Arbeitsbereiche unter dem System-Temp-Verzeichnis für kontrollierte Kopien, Grafik-Builds, Exporte und Veröffentlichungsvorbereitung.

Die technische Struktur trennt GUI, Funktionsskripte, Subscripts, Datenquellen, Produktdatenbanken, externe Werkzeuge und temporäre Arbeitsstände möglichst klar. Der deskNode-Symbolkatalog verknüpft SQLite-Datensätze mit PNG-Quellen über stabile record_id-Werte, während der Graphic-Pack-Build die daraus resultierenden visuellen Varianten erzeugt.


Copyright (c) 2026 Markus Walloner
