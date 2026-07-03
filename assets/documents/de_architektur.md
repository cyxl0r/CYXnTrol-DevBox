ARCHITEKTURDOKUMENTATION
========================

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
Land: Germany (DE)

1. Kurzüberblick
----------------

DevBox ist die lokale Entwicklungszentrale der CYXnTrol Development Platform. Die PySide6-Oberfläche bündelt Projektstruktur, Stammdaten, Dokumentation, lokale Werkzeuge, Produktmodule, Repository-Vorbereitung und wiederkehrende Entwicklungsabläufe.

Mit deskNode ist ein aktives Produktmodul integriert: ein lokaler Geräte- und Strukturhub für Smart-Plugs und angeschlossene Verbraucher. deskNode wird über austauschbare venmods für unterstützte Hersteller und Protokolle erweitert.

DevBox ist kein Endnutzerprodukt. Es ist eine interne Arbeitsumgebung, in der Anforderungen, Datenmodelle, UX-Entscheidungen, Schnittstellen, Builds und Veröffentlichungsstände nachvollziehbar vorbereitet und geprüft werden.


2. Architekturüberblick
-----------------------

DevBox ist modular aufgebaut.

Die Startkette beginnt mit einem DevBox-Launcher. Dieser ermittelt den Projektroot über die .root-Datei, stellt lokale Laufzeitdaten unter AppData bereit, prüft gespeicherte Werkzeugpfade und startet die grafische Oberfläche aus einer temporären Kopie. Die temporäre Kopie reduziert das Risiko, dass eine laufende GUI Dateien im echten Projektroot sperrt oder verändert.

Die Haupt-GUI liegt im Bereich resources/applications/devbox/functions und nutzt spezialisierte Subscripts für Seiten, Layout, Datenzugriff, Prozessstarts und Produktmodule. Die grafische Oberfläche verwendet PySide6. Sie greift über den echten Projektroot auf Grafiken, Fonts, Datenbanken, Installer und Funktionsskripte zu.

Die zentrale Stammdatenquelle ist resources/organization/devbox_db.r0b. Dort liegen Produktdaten, Repository-Felder, Dokumentationsfelder, Strukturinformationen, benannte deskNode-UX-Themes sowie die Symbolkatalogtabellen desknode_consumer_device_categories und desknode_consumer_devices. Für lokale DevBox-Runtime-Daten verwendet die Anwendung logfile.r0b und locdata.r0b unter AppData.

deskNode besitzt eigene abgeleitete Produktdaten unter applications/deskNode/data, insbesondere mnfctr_db.r0b für Manufaktur- und Theme-Daten sowie lan.r0b für Sprachressourcen. Bei einem Lauf erstellt der Supervisor einen eindeutigen Temp-Kontext. Der Daemon koppelt verfügbare venmods über coupler.py ein, validiert deren Verträge, richtet einen lokalen Worker-Control-Hub ein und startet für jeden akzeptierten venmod einen Worker. Die Worker schreiben nur ihre jeweilige flüchtige venmod-Datenbank. Der Daemon führt bestätigte Daten in der globalen AppData-Datenbank devices.r0b zusammen und protokolliert aufgelöste Leistungswerte separat.

Die aktuelle deskNode-Integration enthält venmods für Tapo, FRITZ!DECT und Shelly. Die Produkt-GUI wartet beim Start auf den bestätigten Erstzyklus aller gekoppelten venmods und zeigt danach den synchronisierten Gerätebestand. Strukturzuordnungen, UX-Einstellungen und die Darstellung liegen getrennt von den herstellerspezifischen Worker-Daten.

Der Graphic-Pack-Build verarbeitet globale Symbolquellen, Skalierung, Masken, Vektorisierung und Theme-Daten in temporären Arbeitsordnern. Inkscape und GIMP werden als externe lokale Werkzeuge verwendet. Das Ergebnis ist ein komprimiertes Grafikpaket mit vorberechneten Zustandsvarianten, das deskNode zur Laufzeit laden kann.


3. Detaillierte Architektur
---------------------------

DEVBOX-ARCHITEKTUR

1. Systemgrenze
DevBox ist eine lokale, Windows-orientierte Entwicklungsumgebung innerhalb des CYXnTrol-Projektroots. Sie stellt keine allgemeine Cloud-Plattform und keinen eingebauten Mehrbenutzer-Dienst bereit. Externe Dienste werden nur genutzt, wenn der Nutzer sie ausdrücklich über externe Werkzeuge oder einen Repository-Push einbindet. deskNode kommuniziert im aktuellen Proof of Concept mit unterstützten Geräten über das lokale Netzwerk und betreibt keinen deskNode-eigenen Cloud-Dienst.

2. Start- und Instanzebene
Der DevBox-Launcher ermittelt den Projektroot über .root. Er prüft Laufzeitvoraussetzungen, erstellt lokale AppData-Strukturen, initialisiert beziehungsweise prüft logfile.r0b und locdata.r0b, erkennt externe Werkzeuge und verhindert parallele GUI-Instanzen. Ist eine Instanz bereits geöffnet, wird sie aktiviert. Die GUI wird aus einer temporären Kopie gestartet.

3. GUI- und Modul-Ebene
Die Haupt-GUI basiert auf PySide6. Sie enthält Entwicklungsplattform-, Struktur-, Repository- und produktbezogene Seiten. deskNode ist als eigener Tab eingebunden. Dieser bündelt Produktstarts, Logausgabe, Versionsbearbeitung, Oberflächengestaltung und die Symbolverwaltung. Der Graphic-Pack-Build wird von der Symbolverwaltung aus gestartet, weil dort auch die relevanten Kategorien, Verbrauchergeräte und PNG-Quellen gepflegt werden.

4. Zentrale Datenebene
Devbox_db.r0b ist die zentrale Stammdatenbank im Projekt. Sie enthält Hersteller-, Produkt-, Dokumentations-, Struktur- und Repository-Daten. Die Tabelle "ux-deskNode" verwaltet mehrere benannte UX-Themes mit stabilen record_id-Werten. Die Tabellen desknode_consumer_device_categories und desknode_consumer_devices verwalten den deskNode-Symbolkatalog. logfile.r0b und locdata.r0b liegen getrennt unter AppData und enthalten Runtime-Informationen beziehungsweise lokale Werkzeugpfade.

5. Produktdatenebene deskNode
DeskNode erhält abgeleitete Produktdaten: mnfctr_db.r0b enthält master_data, UX-Themes sowie Kategorie- und Gerätedaten; lan.r0b enthält das Sprachpaket. fonts.r0b und graphic_items.r0b werden als Laufzeitarchive verwendet. settings.r0b, devices.r0b und log_device_power.r0b liegen im deskNode-AppData-Bereich. Die GUI hält Sprache und Theme getrennt von den Manufakturdaten, während devices.r0b globales Inventar, Soll-/Istwerte, Darstellung und additive Strukturzuordnungen verwaltet.

6. deskNode-Runtime-Ebene
Der deskNode-Supervisor erzeugt pro Lauf einen eindeutigen Temp-Kontext und startet den Daemon. Der Daemon findet coupler.py-Dateien unter venmod, validiert die jeweiligen Kopplungsverträge, fasst die globale Gerätestruktur zusammen und startet pro akzeptiertem venmod einen Worker. Ein lokaler Worker-Control-Hub übernimmt Befehle und Ereignisse. Jeder Worker schreibt ausschließlich seine eigene flüchtige SQLite-Datenbank. Der Daemon spiegelt bestätigte Daten in devices.r0b und zeichnet aufgelöste Leistungswerte in log_device_power.r0b auf.

7. Venmod-Ebene
Tapo, FRITZ!DECT und Shelly sind als getrennte venmods angebunden. Tapo nutzt den lokalen python-kasa-Pfad. FRITZ!DECT arbeitet über eine FRITZ!Box und deren lokale AHA-Schnittstelle. Shelly verwendet den lokalen RPC-Pfad für unterstützte Switch-Kanäle. Die Herstellerpfade folgen demselben äußeren Coupler-, Worker- und Synchronisationsvertrag, behalten ihre konkrete Discovery-, Authentifizierungs- und Monitorlogik jedoch getrennt. Ein venmod darf den globalen Gerätebestand nicht direkt schreiben.

8. Sicherheits- und Synchronisationsprinzip
Bei einem neuen Daemon-Lauf werden alte globale Soll-/Istwerte sicher zurückgesetzt. Venmods lesen den realen Zustand zunächst ein und melden ihren Erstzyklus. Erst wenn alle gekoppelten venmods abgeschlossen und ihre Daten global gespiegelt sind, verlässt die Haupt-GUI den Ladebildschirm. Ausdrückliche Schaltaufträge laufen über Sollzustände, venmod-spezifische Ausführung und bestätigtes Rücklesen. Kurzzeitige Monitorfehler werden von der zentralen Livewertlogik abgefedert, damit einzelne fehlerhafte Samples nicht sofort Offline-Darstellungen erzeugen.

9. Geräte- und Struktur-Ebene
Eine Installation enthält mindestens ein Gebäude. Mehrere unabhängige Gebäude-Wurzeln sind möglich. Jedes Gebäude besitzt einen festen Geräte-Pool als vollständige Übersicht; ein Gerät kann dort und zusätzlich in einem Raum, Bereich, Desk, Rack oder anderen Strukturglied liegen. Die Baumdarstellung zeigt räumliche beziehungsweise funktionale Strukturglieder; der Geräte-Pool dient als gesonderter Gesamtzugriff für das jeweilige Gebäude.

10. Symbolkatalog- und Grafik-Build-Ebene
Eine Kategorie besitzt record_id, category_key, translation_key und Zeitstempel. Ein Verbrauchergerät besitzt record_id, device_key, category_id, translation_key und Zeitstempel. category_id verweist auf die stabile record_id der Kategorie. Beim Anlegen eines neuen Geräts wird genau eine PNG entgegengenommen und als resources/graphics/symbol_source_<record_id>.png abgelegt. graphic_items_bulder.py verarbeitet diese Quellen in einem temporären Arbeitsbereich, erzeugt Masken, Theme- und Zustandsvarianten und stellt das Grafikpaket für deskNode bereit.

11. Dokumentations- und Veröffentlichungsebene
Doc_forms.r0b enthält Formularvorlagen. Ein Dokumentprozess entpackt sie, befüllt sie aus sprachabhängigen Tabellen, erzeugt Markdown- und PDF-Dateien und überführt diese in eine kontrollierte Exportstruktur. Für DevBox wird ein temporärer root_dir als Sollzustand für die Repository-Synchronisation erzeugt. Der aktuelle DevBox-Veröffentlichungsstand enthält gezielt applications/deskNode/resources/scripts einschließlich Unterordnern, jedoch ohne __pycache__-Ordner und Python-Bytecode.

12. Bekannte Sicherheitsgrenze
Die derzeitige Credential-Verarbeitung ist ein Entwicklungsstand und noch kein plattformübergreifend verschlüsselter Vault. Zugangsdaten dürfen nicht geloggt werden; für einen produktiven oder öffentlichen Einsatz muss die geplante gemeinsame Vault-Komponente vorliegen. DevBox trennt Originalbestand, temporäre Verarbeitung, abgeleitete Produktdatenbanken und Veröffentlichungsstand, damit aufwendige Operationen nicht unkontrolliert auf dem echten Projektroot arbeiten.


4. Funktionen und Ziele
-----------------------

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


5. Konfiguration
----------------

Die Konfiguration ist in mehrere Ebenen getrennt.

Projektroot:
Der Projektroot wird über die .root-Datei gefunden. Er ist die maßgebliche Quelle für Skripte, Ressourcen, Formarchive, Installer, globale Fonts und die zentrale DevBox-Datenbank.

Zentrale DevBox-Stammdaten:
resources/organization/devbox_db.r0b enthält Hersteller-, Produkt-, Dokumentations-, Struktur-, Repository-, UX-Theme- und Symbolkataloginformationen. Die Tabelle "ux-deskNode" enthält benannte Theme-Datensätze mit record_id und theme_name. Die Tabellen desknode_consumer_device_categories und desknode_consumer_devices enthalten die dauerhaften technischen Kategorien und Verbrauchergeräte. Schemaerweiterungen sollen vorhandene Datensätze erhalten und fehlende Felder über Migration ergänzen.

DeskNode-Produktdaten:
applications/deskNode/data/mnfctr_db.r0b enthält master_data, ux_themes, consumer_device_categories und consumer_devices. applications/deskNode/data/lan.r0b enthält das Sprachpaket language_package. fonts.r0b und graphic_items.r0b dienen als Produktarchive für die Laufzeit. create_manufacturer_db.py aktualisiert die abgeleitete Manufakturdatenbank nach erfolgreichen Änderungen an Version, Theme, Kategorie oder Verbrauchergerät.

DeskNode-AppData und Laufzeit:
Aus master_data wird der lokale AppData-Pfad gebildet, aktuell typischerweise %APPDATA%/CYXLabs/CYXnTrol/deskNode. settings.r0b speichert die gewählte UI-Sprache und das aktive UX-Theme sowie vom Supervisor benötigte Laufzeitinformationen. devices.r0b enthält den globalen Gerätebestand und additive Strukturzuordnungen. log_device_power.r0b protokolliert aufgelöste Leistungswerte. Jeder aktive Daemon-Lauf besitzt zusätzlich einen eindeutigen Temp-Ordner mit runtime_state.r0b und getrennten flüchtigen venmod-Datenbanken.

Gerätestruktur:
Eine frische Installation erhält mindestens eine Gebäude-Wurzel. Jedes Gebäude besitzt intern einen festen Geräte-Pool als vollständige Gebäudeübersicht. Geräte können im Pool verbleiben und zusätzlich räumlichen oder funktionalen Gliedern zugeordnet werden. Die Strukturverwaltung unterstützt mehrere unabhängige Gebäude-Wurzeln.

Venmods:
Ein venmod wird über eine coupler.py gefunden und muss einen gültigen Kopplungsvertrag melden. Dieser beschreibt Name, Workerstart, flüchtige Datenbank, Gerätetabelle sowie Upstream- und Downstream-Spaltenzuordnungen. Der Daemon validiert diese Angaben vor dem Workerstart. Tapo, FRITZ!DECT und Shelly sind die derzeit eingebundenen lokalen Pfade.

Credentials und Sicherheitsstand:
Zugangsdaten werden nur für Herstellerpfade benötigt, die eine Anmeldung verlangen. Sie werden nicht in Logs ausgegeben. Der aktuelle Proof of Concept besitzt jedoch noch keinen plattformübergreifenden verschlüsselten Credential-Vault; lokal persistierte Entwicklungsdaten dürfen daher nicht als gehärteter Secret Store behandelt werden. Die geplante Vault-Lösung soll als gemeinsame Plattformkomponente entstehen, nicht als venmod-spezifische Sonderlösung.

Oberflächengestaltung:
Farben werden als achtstellige RGBA-Hexwerte ohne # gespeichert, zum Beispiel 00e4ffff. Schriftdateien werden rekursiv aus resources/fonts gelesen und als projektroot-relative Pfade gespeichert. Schriftrollen umfassen große Überschriften, Bereichsüberschriften, Standardtext, Schaltflächentext, Eingabefeldtext, Statusmeldungen und Protokolltext. Weitere Theme-Werte betreffen Schriftgrößen, Schriftschnitt, Unterstreichung, Konturen, Radien und Zustandsfarben.

Werkzeugerkennung und Repository-Daten:
Gespeicherte Pfade werden beim Start geprüft. Ungültige Inkscape- oder GIMP-Pfade werden erneut gesucht. Repository-URL und Branch werden pro Produkt in product_credentials gepflegt. Git-Zugangsdaten werden nicht in DevBox gespeichert. Für den DevBox-Push wird ein temporärer Veröffentlichungsroot erzeugt; der aktuelle Exportumfang wird durch den kontrollierten Push-Prozess festgelegt.


6. Technologie
-------------

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


7. Repository-Hinweis
---------------------

Das DevBox-Repository repräsentiert die CYXnTrol Development Platform selbst, nicht ein fertiges Endnutzerprodukt. Es dient als Entwicklungsstand, transparente Arbeitsprobe und Grundlage für die Pflege der Plattform.

Der veröffentlichte Stand wird nicht direkt aus dem produktiven Projektroot kopiert. Für DevBox wird ein gesonderter bereinigter root_dir-Stand erzeugt. Er enthält vorgesehenen Quellcode, Dokumente und Assets, während lokale Laufzeitdaten, temporäre Reste, Installer, Datenbank-WAL-Dateien und nicht veröffentlichte Daten außerhalb des Veröffentlichungspakets bleiben.

Der derzeitige DevBox-Push behandelt applications als bewusstes Auslieferungsfenster: Der Bereich wird zunächst bereinigt. Danach wird applications/deskNode/resources/scripts einschließlich enthaltener Dateien in den Veröffentlichungsstand kopiert. __pycache__-Ordner sowie .pyc- und .pyo-Dateien bleiben ausgeschlossen. Dieser aktuelle Umfang ist ein DevBox-spezifischer Veröffentlichungsprozess und noch kein vollständiger deskNode-Produktrelease. Bevor deskNode einschließlich GUI, Logik und venmods als eigenes Repository oder Release veröffentlicht wird, muss dessen Exportumfang ausdrücklich definiert und getestet werden.

DevBox wird in einem KI-gestützten, iterativen Workflow entwickelt. Anforderungen, Architektur, Datenmodelle, UX-Entscheidungen, Testfälle und Abnahmen werden durch den Projektverantwortlichen gesteuert. Die Implementierung entsteht mit KI-gestützten Entwicklungswerkzeugen und wird gegen die definierten Funktionsanforderungen geprüft.


Copyright (c) 2026 Markus Walloner
