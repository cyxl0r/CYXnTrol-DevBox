TODO-LISTE
==========

Dokumentstand: Aktiver Proof-of-Concept und Entwicklungsstand.

DevBox besitzt einen funktionsfähigen lokalen Launcher, eine grafische Hauptoberfläche, modulare Strukturansichten, Stammdaten- und Dokumentationspflege, Dokumentations-Snapshots, lokale Werkzeugerkennung, eine Repository-Seite sowie erste Bausteine für den DevBox-spezifischen Veröffentlichungsprozess.

Der deskNode-Bereich ist aktiv in DevBox integriert. Supervisor und Daemon können aus der GUI gestartet und gestoppt werden; deren Konsolenausgabe wird im deskNode-Log angezeigt. Die Produktversion kann aus den Stammdaten bearbeitet werden. UX-Themes können benannt, angelegt, gelöscht, dupliziert, umbenannt und gespeichert werden. Nach dem Speichern werden die deskNode-Produktdaten aktualisiert.

DeskNode verfügt im aktuellen Proof of Concept über eine gekoppelte Worker-Architektur. Tapo, FRITZ!DECT und Shelly werden lokal über eigene venmods entdeckt und überwacht; bei unterstützten Geräten werden Schaltzustände und Leistungswerte verarbeitet. Der Daemon synchronisiert die venmod-Daten in einen globalen Gerätebestand, hält einen initialen Sicherheitslesezyklus ein und startet die Hauptoberfläche erst nach der globalen Erst-Synchronisierung. Die Strukturverwaltung unterstützt mehrere Gebäude-Wurzeln, pro Gebäude einen vollständigen Geräte-Pool und zusätzliche additive Zuordnungen zu Räumen oder anderen Strukturgliedern.

Die Symbolverwaltung ist als funktionsfähige Katalogoberfläche vorhanden. Sie verwaltet deskNode-Gerätekategorien und Verbrauchergeräte über Auswahlmenüs sowie Dialoge zum Anlegen, Bearbeiten und Löschen. Neue Geräte erhalten eine einzelne PNG-Quelle, die unter ihrer record_id als symbol_source_<record_id>.png abgelegt wird. Nach jeder erfolgreichen Katalogänderung wird create_manufacturer_db.py ausgeführt, damit mnfctr_db.r0b die aktuellen Theme-, Kategorien- und Gerätedaten enthält.

Der Graphic-Pack-Build ist als Proof of Concept funktionsfähig. Er erzeugt aus Symbolquellen und UX-Themes vorbereitete Grafikzustände für Verbraucher. Die aktuelle deskNode-Laufzeit nutzt bereits Sprach-, Theme- und Grafikdaten; Asset-Auswahl, weitere Symbolabdeckung und visuelle Zustände werden weiterentwickelt.

DevBox und deskNode sind keine fertigen Endnutzer- oder Release-Versionen. Besonders Credential-Speicherung, Langzeitstabilität größerer Gerätebestände, herstellerspezifische Sonderfälle, Tests, Packaging und Plattformportierung sind noch offene Entwicklungsaufgaben.

Erstveröffentlichung: 
Projektbeginn: 2026
Autor / Herausgeber: Markus Walloner

1. Projektbezug
---------------

Kurzbeschreibung:
DevBox ist die lokale Entwicklungszentrale der CYXnTrol Development Platform. Die PySide6-Oberfläche bündelt Projektstruktur, Stammdaten, Dokumentation, lokale Werkzeuge, Produktmodule, Repository-Vorbereitung und wiederkehrende Entwicklungsabläufe.

Mit deskNode ist ein aktives Produktmodul integriert: ein lokaler Geräte- und Strukturhub für Smart-Plugs und angeschlossene Verbraucher. deskNode wird über austauschbare venmods für unterstützte Hersteller und Protokolle erweitert.

DevBox ist kein Endnutzerprodukt. Es ist eine interne Arbeitsumgebung, in der Anforderungen, Datenmodelle, UX-Entscheidungen, Schnittstellen, Builds und Veröffentlichungsstände nachvollziehbar vorbereitet und geprüft werden.


Langbeschreibung:
DevBox verbindet Aufgaben, die sonst über Einzelskripte, Ordner, Tabellen, Konsolenfenster und externe Programme verteilt wären. Die Anwendung verwaltet zentrale Projekt- und Produktdaten, stellt Dokumentationsinhalte bereit, organisiert globale Strukturvorlagen, erkennt lokale Werkzeuge und bündelt produktbezogene Entwicklungsfunktionen in einer gemeinsamen Oberfläche.

Das erste aktive Produktmodul ist deskNode. deskNode ist eine lokale Steuer- und Strukturumgebung für Smart-Plugs und angeschlossene Verbraucher. Ein Supervisor startet einen Daemon; dieser koppelt gefundene venmods über einen gemeinsamen Vertrag ein und startet pro venmod einen eigenen Worker. Der aktuelle Proof of Concept enthält lokale Pfade für Tapo, FRITZ!DECT und Shelly. Geräte werden in einer globalen Inventardatenbank geführt, während jeder Worker nur seine eigene flüchtige Laufzeitdatenbank schreibt. Der Daemon synchronisiert die bestätigten Livewerte, Sollzustände und Geräteidentitäten zwischen den Ebenen.

deskNode organisiert Geräte zusätzlich in unabhängigen Gebäudebäumen. Jedes Gebäude besitzt einen Geräte-Pool als vollständige Gebäudeübersicht sowie optionale räumliche oder funktionale Strukturglieder. Ein Gerät kann im Pool eines Gebäudes bleiben und zusätzlich einem Raum, Bereich, Desk oder anderen Strukturglied zugeordnet sein. Die grafische Oberfläche visualisiert diese Struktur, Geräte- und Leistungswerte sowie lokale Schaltzustände.

Die DevBox-Seite für deskNode startet und stoppt Supervisor und Daemon, zeigt deren Konsolenausgabe, pflegt Produktversionen, UX-Themes und den Symbolkatalog. Themes werden mit benannten Datensätzen, RGBA-Farben, globalen Schriftdateien, Größen, Konturen und Formregeln gepflegt. Kategorien und Verbrauchersymbole werden über stabile technische IDs und PNG-Quellen verwaltet. Der Graphic-Pack-Build erzeugt daraus vorbereitete Varianten für Themes und Zustände.

DevBox arbeitet lokal im Projektkontext. Ein Launcher ermittelt den Projektroot über die Datei .root, stellt Laufzeitdaten unter AppData bereit, prüft externe Werkzeuge und startet die GUI aus einer temporären Arbeitskopie. Der echte Projektroot bleibt die maßgebliche Quelle für Ressourcen, Datenbanken und Funktionsskripte. Eine Einzelinstanzlogik verhindert parallele DevBox-Fenster und aktiviert beim erneuten Start die bereits geöffnete Instanz.

Das Projekt entsteht in einem KI-gestützten, iterativen Entwicklungsprozess. Fachliche Anforderungen, Prozesslogik, Datenmodelle, UX-Entscheidungen, Testfälle und Abnahmen werden durch den Projektverantwortlichen gesteuert; Implementierungsschritte werden mit KI-gestützten Werkzeugen erstellt, überprüft und fortlaufend nachgeschärft.


2. Offene Punkte
----------------

AKTUELLE TODO-LISTE

deskNode-Runtime und venmods
- Den gemeinsamen venmod-Vertrag mit weiteren Herstellerpfaden und mehreren gleichzeitigen Geräten testen.
- Tapo-Operationen unter größeren Gerätebeständen, längeren Laufzeiten, 403-Fehlern, Reauthentifizierung und schnellen Schaltfolgen weiter messen und stabilisieren.
- Tapo-Monitoring auf den tatsächlich erforderlichen lokalen Minimalumfang begrenzen und herstellerspezifische Detailabfragen nur gezielt verwenden.
- FRITZ!DECT mit mehreren FRITZ!Boxen, wechselnden Gateways, Offline-Geräten und AHA-Sonderfällen testen.
- Shelly um dokumentierte Authentifizierung, HTTPS, gegebenenfalls Gen1-Kompatibilität und zusätzliche Gerätekategorien erweitern, ohne den bestehenden RPC-Pfad zu destabilisieren.
- Polling-Kapazitäten, Backoff, Discovery-Frequenzen und Priorität von Schaltbefehlen durch belastbare Messwerte konfigurierbar machen.
- End-to-End-Logging für Sollwert, Downstream-Befehl, Worker-Ausführung, Rücklesen, Bestätigung und Timeout ergänzen.

Credentials und Sicherheit
- Eine gemeinsame DevBox-/deskNode-Credential-Vault-Komponente konzipieren und implementieren.
- Für den portablen Vault geprüfte Kryptobausteine, ein Master-Passwort- beziehungsweise Schlüsselmodell, Migration, Passwortwechsel und sichere Runtime-Übergabe festlegen.
- Keine eigene Kryptografie entwickeln und keine Klartext-Credentials in globalen Geräte-, venmod- oder Runtime-Tabellen belassen.
- Optionalen Auto-Unlock über native Schlüsselablagen erst nach einem plattformneutralen Vault-Format ergänzen.

DeskNode-Struktur und GUI
- Gebäude-Pools, direkte Zuordnungszahlen, Drag-and-drop und Mehrgebäude-Ansichten unter realen Datenbeständen testen.
- Visuelle Zustände für Offline, Warnung, Fehler, unbekannte Geräte, Pending Commands und Verbrauchsgrenzen definieren.
- Filter, Suche, dichte Operator-Ansicht und skalierbares Verhalten bei vielen Geräten konzipieren.
- Struktur- und Geräteansichten bei unterschiedlichen Bildschirmgrößen, Zoomstufen und langen Bezeichnungen prüfen.
- Sprachauswahl und Theme-Auswahl später über stabile record_id-Bezüge statt umbenennbarer Namen weiterentwickeln.

UX-Themes und Symbolkatalog
- Speichern, Migration und Aktualisierung mehrerer UX-Themes unter realen GUI-Bedingungen weiter testen.
- Fehlende Schriftdateien, ungültige RGBA-Werte und defekte Theme-Datensätze robust behandeln.
- Symbolverwaltung mit realen Kategorien und Verbrauchersymbolen weiter füllen.
- Sprachpakete für Kategorien und Geräte anhand der automatisch erzeugten translation_key-Werte anlegen.
- Suche im deskNode-Symbolwähler über lokalisierte Namen und Suchbegriffe definieren.
- PNG-Austausch für bestehende Geräte gezielt als separaten Bearbeitungsablauf ergänzen.
- Festlegen, wie consumer_device_id und optional consumer_device_key an Gerätezuordnungen gespeichert werden.

Graphic-Pack-Build
- Die erzeugten Grafikpakete mit mehr Symbolen, mehr Themes und längeren Dateinamen testen.
- Den Builder auf die durch record_id benannten symbol_source_<record_id>.png-Quellen vollständig ausrichten.
- Build-Ergebnisse gegen erwartete Anzahl von Themes, Symbolen, Masken und Zustandsdateien validieren.
- Aufräumen, Archivierung und Installation des finalen Grafikpakets weiter absichern.
- Optional inkrementellen Build entwickeln, damit bei einer kleinen Änderung nicht jedes Asset neu erzeugt werden muss.
- Fehlerbehandlung für fehlende Symbolquellen, Inkscape, GIMP und nicht unterstützte SVG-/PNG-Dateien erweitern.

Repository, Dokumentation und Qualität
- DevBox-Push-to-Git-Prozess in der GUI vollständig testen.
- Den vollständigen Exportumfang für ein eigenständiges deskNode-Repository definieren; der aktuelle DevBox-Export umfasst nur resources/scripts und ist kein Produktrelease.
- Repository-URL- und Branch-Einrichtung mit realem Remote-Repository prüfen.
- Soll-/Ist-Abgleich, Schutzregeln und Entfernung obsoleter Repository-Dateien weiter absichern.
- Formulartexte bei Funktionsänderungen aktualisieren.
- Nutzungsbedingungen und Datenschutzhinweise vor öffentlicher Nutzung rechtlich prüfen und an reale Datenflüsse anpassen.
- Automatisierte Tests für Datenbankmigration, Theme-Speicherung, Symbolkatalog, Grafik-Build, Dokumentexport, Snapshot-Struktur, Repository-Synchronisation, venmod-Coupling und Geräte-Workflows ergänzen.
- Packaging, Signierung sowie spätere macOS- und Linux-Portierung getrennt planen und validieren.


3. Zielbild
-----------

Aktueller Funktionsrahmen:
- Start einer einzelnen DevBox-Instanz mit Aktivierung einer bereits laufenden Instanz.
- Plattformseite mit Bereichen für Projektplattform, Anwendungen, Entwicklungssoftware und Produktmodule.
- Lokale Erkennung und Startmöglichkeit für Inkscape und GIMP sowie expliziter Start vorhandener Drittanbieter-Installer.
- Zentrale SQLite-Stammdatenbank für Dach-, Hersteller-, Produkt-, Dokumentations-, Struktur-, Repository-, UX-Theme- und deskNode-Symbolkatalogdaten.
- Struktur-Werkstatt mit Navigation für Dach-Daten, Produkt-Daten, Dokumentationen und globale App-Ordnerstruktur.
- Initialisierung ausschließlich vollständig leerer Produktordner anhand der globalen Strukturvorlage.
- Export von Dokumentations-Snapshots und kontrollierter Import vollständig überarbeiteter deutscher und englischer Dokumentation.
- Erzeugung von Markdown-Dokumenten und PDF-Entwürfen für Nutzungsbedingungen und Datenschutz.
- Repository-Seite mit Produktauswahl, optionalem Commit-Text, optionalen Bildern und Logausgabe.
- Vorbereitung eines bereinigten DevBox-Veröffentlichungsstands in einem temporären Arbeitsbereich.
- deskNode-Tab zum Starten und Stoppen von Supervisor und Daemon mit Live-Konsolenausgabe.
- Bearbeitung der deskNode-Version sowie Aktualisierung der abgeleiteten Produktdatenbanken.
- Oberflächengestaltung mit mehreren benannten UX-Themes, RGBA-Farben, globalen Schriftdateien, Schriftformaten, Radien und Konturen.
- Symbolverwaltung für Gerätekategorien und Verbrauchergeräte mit stabilen record_id-, category_key- und device_key-Bezügen.
- Annahme einer PNG-Quelle für neue Verbrauchergeräte und Ablage als symbol_source_<record_id>.png.
- Graphic-Pack-Build aus Symbolquellen, UX-Themes, GIMP-Masken, Inkscape-Vektorisierung und vorberechneten Zustandsvarianten.
- deskNode-POC mit Supervisor, Daemon, separaten venmod-Workern, globalem Gerätebestand, Stromwertprotokoll und lokalen Gerätepfaden für Tapo, FRITZ!DECT und Shelly.
- deskNode-Struktur mit mehreren unabhängigen Gebäudebäumen, Gebäudepools und additiven Gerätezuordnungen.

Ziele:
- wiederholbare Entwicklungsschritte statt manueller Einzellösungen;
- klare Trennung zwischen DevBox-Stammdaten, deskNode-Laufzeitdaten, venmod-Daten, temporären Builds und Repository-Export;
- stabile technische Referenzen für Themes, Sprachen, Kategorien, Verbrauchergeräte und Assets;
- lokale Geräteintegration ohne deskNode-eigenen Cloud-Dienst;
- Erweiterbarkeit für weitere CYXnTrol-Produkte und venmods, ohne DevBox als beliebige Skriptsammlung zu behandeln.


4. Technischer Bezug
--------------------

DevBox ist modular aufgebaut.

Die Startkette beginnt mit einem DevBox-Launcher. Dieser ermittelt den Projektroot über die .root-Datei, stellt lokale Laufzeitdaten unter AppData bereit, prüft gespeicherte Werkzeugpfade und startet die grafische Oberfläche aus einer temporären Kopie. Die temporäre Kopie reduziert das Risiko, dass eine laufende GUI Dateien im echten Projektroot sperrt oder verändert.

Die Haupt-GUI liegt im Bereich resources/applications/devbox/functions und nutzt spezialisierte Subscripts für Seiten, Layout, Datenzugriff, Prozessstarts und Produktmodule. Die grafische Oberfläche verwendet PySide6. Sie greift über den echten Projektroot auf Grafiken, Fonts, Datenbanken, Installer und Funktionsskripte zu.

Die zentrale Stammdatenquelle ist resources/organization/devbox_db.r0b. Dort liegen Produktdaten, Repository-Felder, Dokumentationsfelder, Strukturinformationen, benannte deskNode-UX-Themes sowie die Symbolkatalogtabellen desknode_consumer_device_categories und desknode_consumer_devices. Für lokale DevBox-Runtime-Daten verwendet die Anwendung logfile.r0b und locdata.r0b unter AppData.

deskNode besitzt eigene abgeleitete Produktdaten unter applications/deskNode/data, insbesondere mnfctr_db.r0b für Manufaktur- und Theme-Daten sowie lan.r0b für Sprachressourcen. Bei einem Lauf erstellt der Supervisor einen eindeutigen Temp-Kontext. Der Daemon koppelt verfügbare venmods über coupler.py ein, validiert deren Verträge, richtet einen lokalen Worker-Control-Hub ein und startet für jeden akzeptierten venmod einen Worker. Die Worker schreiben nur ihre jeweilige flüchtige venmod-Datenbank. Der Daemon führt bestätigte Daten in der globalen AppData-Datenbank devices.r0b zusammen und protokolliert aufgelöste Leistungswerte separat.

Die aktuelle deskNode-Integration enthält venmods für Tapo, FRITZ!DECT und Shelly. Die Produkt-GUI wartet beim Start auf den bestätigten Erstzyklus aller gekoppelten venmods und zeigt danach den synchronisierten Gerätebestand. Strukturzuordnungen, UX-Einstellungen und die Darstellung liegen getrennt von den herstellerspezifischen Worker-Daten.

Der Graphic-Pack-Build verarbeitet globale Symbolquellen, Skalierung, Masken, Vektorisierung und Theme-Daten in temporären Arbeitsordnern. Inkscape und GIMP werden als externe lokale Werkzeuge verwendet. Das Ergebnis ist ein komprimiertes Grafikpaket mit vorberechneten Zustandsvarianten, das deskNode zur Laufzeit laden kann.


DevBox verwendet derzeit vor allem folgende Technologien:

- Python als Kernsprache für Launcher, Prozesslogik, Datenaufbereitung, Automationen und produktbezogene Werkzeuge.
- PySide6 für die lokalen grafischen Benutzeroberflächen von DevBox und deskNode.
- SQLite für zentrale Projektstammdaten, deskNode-Produktdaten sowie lokale Runtime-, Geräte-, Einstellungs-, Sprach- und Protokolldaten.
- python-kasa für die lokale Tapo-Erkennung und Gerätekommunikation im Tapo-venmod.
- Lokale HTTP-, XML- und RPC-Kommunikation für FRITZ!DECT/AHA- und Shelly-Pfade, soweit der jeweilige venmod sie implementiert.
- Einen lokalen Worker-Control-Hub und getrennte Workerprozesse für die venmod-Anbindung.
- openpyxl als Übergangs- oder Importwerkzeug für Tabellen, nicht als zentrale Stammdatenquelle.
- ReportLab und svglib für die lokale Erzeugung gestalteter PDF-Dokumente.
- Git und Git Credential Manager für Repository-Vorgänge und Authentifizierung.
- Inkscape für Skalierung, SVG-Arbeit und Vektorisierung von Masken.
- GIMP 3 für nichtinteraktive Bildbearbeitung und vorbereitende Maskenschritte.
- XML-/SVG-Verarbeitung mit Python-Standardbibliotheken für die Bereinigung generierter Masken.
- C#-Generierung, .NET SDK, WiX und perspektivisch weitere Packaging-Werkzeuge für Build- und Installer-Prozesse.
- temporäre Arbeitsbereiche unter dem System-Temp-Verzeichnis für kontrollierte Kopien, Grafik-Builds, Exporte, Daemon-Laufzeiten und Veröffentlichungsvorbereitung.

Die technische Struktur trennt GUI, Funktionsskripte, Subscripts, Datenquellen, Produktdatenbanken, externe Werkzeuge, globale Gerätehaltung und venmod-spezifische Runtime möglichst klar. Der deskNode-Symbolkatalog verknüpft SQLite-Datensätze mit PNG-Quellen über stabile record_id-Werte, während der Graphic-Pack-Build die daraus resultierenden visuellen Varianten erzeugt.


Copyright (c) 2026 Markus Walloner
