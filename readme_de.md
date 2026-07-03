# README

## Kurzbeschreibung

DevBox ist die lokale Entwicklungszentrale der CYXnTrol Development Platform. Die PySide6-Oberfläche bündelt Projektstruktur, Stammdaten, Dokumentation, lokale Werkzeuge, Produktmodule, Repository-Vorbereitung und wiederkehrende Entwicklungsabläufe.

Mit deskNode ist ein aktives Produktmodul integriert: ein lokaler Geräte- und Strukturhub für Smart-Plugs und angeschlossene Verbraucher. deskNode wird über austauschbare venmods für unterstützte Hersteller und Protokolle erweitert.

DevBox ist kein Endnutzerprodukt. Es ist eine interne Arbeitsumgebung, in der Anforderungen, Datenmodelle, UX-Entscheidungen, Schnittstellen, Builds und Veröffentlichungsstände nachvollziehbar vorbereitet und geprüft werden.


## Langbeschreibung

DevBox verbindet Aufgaben, die sonst über Einzelskripte, Ordner, Tabellen, Konsolenfenster und externe Programme verteilt wären. Die Anwendung verwaltet zentrale Projekt- und Produktdaten, stellt Dokumentationsinhalte bereit, organisiert globale Strukturvorlagen, erkennt lokale Werkzeuge und bündelt produktbezogene Entwicklungsfunktionen in einer gemeinsamen Oberfläche.

Das erste aktive Produktmodul ist deskNode. deskNode ist eine lokale Steuer- und Strukturumgebung für Smart-Plugs und angeschlossene Verbraucher. Ein Supervisor startet einen Daemon; dieser koppelt gefundene venmods über einen gemeinsamen Vertrag ein und startet pro venmod einen eigenen Worker. Der aktuelle Proof of Concept enthält lokale Pfade für Tapo, FRITZ!DECT und Shelly. Geräte werden in einer globalen Inventardatenbank geführt, während jeder Worker nur seine eigene flüchtige Laufzeitdatenbank schreibt. Der Daemon synchronisiert die bestätigten Livewerte, Sollzustände und Geräteidentitäten zwischen den Ebenen.

deskNode organisiert Geräte zusätzlich in unabhängigen Gebäudebäumen. Jedes Gebäude besitzt einen Geräte-Pool als vollständige Gebäudeübersicht sowie optionale räumliche oder funktionale Strukturglieder. Ein Gerät kann im Pool eines Gebäudes bleiben und zusätzlich einem Raum, Bereich, Desk oder anderen Strukturglied zugeordnet sein. Die grafische Oberfläche visualisiert diese Struktur, Geräte- und Leistungswerte sowie lokale Schaltzustände.

Die DevBox-Seite für deskNode startet und stoppt Supervisor und Daemon, zeigt deren Konsolenausgabe, pflegt Produktversionen, UX-Themes und den Symbolkatalog. Themes werden mit benannten Datensätzen, RGBA-Farben, globalen Schriftdateien, Größen, Konturen und Formregeln gepflegt. Kategorien und Verbrauchersymbole werden über stabile technische IDs und PNG-Quellen verwaltet. Der Graphic-Pack-Build erzeugt daraus vorbereitete Varianten für Themes und Zustände.

DevBox arbeitet lokal im Projektkontext. Ein Launcher ermittelt den Projektroot über die Datei .root, stellt Laufzeitdaten unter AppData bereit, prüft externe Werkzeuge und startet die GUI aus einer temporären Arbeitskopie. Der echte Projektroot bleibt die maßgebliche Quelle für Ressourcen, Datenbanken und Funktionsskripte. Eine Einzelinstanzlogik verhindert parallele DevBox-Fenster und aktiviert beim erneuten Start die bereits geöffnete Instanz.

Das Projekt entsteht in einem KI-gestützten, iterativen Entwicklungsprozess. Fachliche Anforderungen, Prozesslogik, Datenmodelle, UX-Entscheidungen, Testfälle und Abnahmen werden durch den Projektverantwortlichen gesteuert; Implementierungsschritte werden mit KI-gestützten Werkzeugen erstellt, überprüft und fortlaufend nachgeschärft.


## Zweck

DevBox soll wiederkehrende und fehleranfällige Entwicklungsarbeit in nachvollziehbare lokale Werkzeuge überführen. Dazu gehören insbesondere die Pflege von Produkt- und Herstellerdaten, strukturierte Dokumentation, vorbereitete Veröffentlichungsschritte, die Integration lokaler Kreativprogramme sowie die kontrollierte Ausführung produktbezogener Entwicklungsfunktionen.

Die Anwendung schafft eine gemeinsame Arbeitsgrundlage für Produkte der CYXnTrol Development Platform. Statt Abläufe nur als Erinnerung, Ordnerkonvention oder Sammlung einzelner Konsolenbefehle zu halten, werden sie als Daten, Skripte, GUI-Funktionen und überprüfbare Prozessketten festgehalten.

Für deskNode dient DevBox als Entwicklungs- und Konfigurationsoberfläche für Produktversionen, UX-Themes, Gerätekategorien, Verbrauchersymbole, Sprachressourcen und vorbereitete Grafikpakete. Die deskNode-Laufzeit soll daraus reproduzierbare Daten und vorbereitete Assets erhalten. Die venmod-Architektur soll zudem neue lokale Gerätepfade ergänzen können, ohne den Daemon oder bereits funktionierende Herstellerpfade unnötig umzubauen.


## Einordnung

Die CYXnTrol Development Platform entstand aus praktischer Entwicklungsarbeit mit vielen kleinen Werkzeugen, Datenständen, Grafikdateien, Dokumenten und Testabläufen. Mit wachsender Zahl von Produkten und Funktionen reicht es nicht mehr aus, Informationen nur in einzelnen Dateien oder im Gedächtnis zu halten. Benötigt werden eine stabile Projektwurzel, nachvollziehbare Datenquellen, wiederholbare temporäre Arbeitsbereiche und klar abgegrenzte Produktmodule.

DevBox ist die Antwort auf diesen Bedarf. Es bildet eine lokale Entwicklungszentrale, in der Hersteller- und Produktdaten, Dokumentation, globale Strukturregeln, externe Werkzeuge, Repository-Vorbereitung und spezielle Produktfunktionen zusammengeführt werden.

deskNode ist das erste Produkt, das als eigener aktiver Bereich in DevBox integriert wird. Seine Aufgabe ist die lokale Verwaltung, Visualisierung und Schaltung unterstützter Smart-Plugs. Tapo, FRITZ!DECT und Shelly werden nicht als fest in die Oberfläche eingebaute Sonderfälle behandelt, sondern über venmods mit einem gemeinsamen Coupler- und Worker-Vertrag angebunden. Für Verbraucher werden Namen, Kategorien, stabile technische IDs, PNG-Quellen, Theme-Daten und vorberechnete Grafikzustände in einen reproduzierbaren Ablauf gebracht.


## Kernidee

Die Kernidee von DevBox lautet: Wiederkehrende Entwicklungsprozesse sollen nicht jedes Mal neu erfunden werden. Sie sollen als verständliche Werkzeuge, Datenstrukturen und Abläufe dauerhaft verfügbar bleiben.

Ein einzelnes Skript kann eine konkrete Aufgabe lösen. Mehrere Skripte und Produkte benötigen jedoch gemeinsame Regeln: einen eindeutig bestimmbaren Projektroot, sichere temporäre Arbeitsbereiche, zentrale Stammdaten, portable Pfade, nachvollziehbare Logs, getrennte Runtime-Daten und eine Oberfläche, in der Funktionen auffindbar bleiben.

Ein zweites zentrales Prinzip ist die Trennung von Entwurf, Quelle und Laufzeit. deskNode-UX-Themes, Sprachressourcen sowie Geräte- und Symbolkataloge werden in DevBox gepflegt und anschließend in produktnahe Datenbestände überführt. Im Betrieb trennt deskNode globales Inventar, flüchtige venmod-Datenbanken und kontrollierte Worker-Kommunikation. Dadurch sollen neue Gerätepfade ergänzt werden können, ohne bestehende Herstellerintegrationen oder Nutzerdaten unkontrolliert zu vermischen.


## Funktionen und Ziele

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


## Architekturüberblick

DevBox ist modular aufgebaut.

Die Startkette beginnt mit einem DevBox-Launcher. Dieser ermittelt den Projektroot über die .root-Datei, stellt lokale Laufzeitdaten unter AppData bereit, prüft gespeicherte Werkzeugpfade und startet die grafische Oberfläche aus einer temporären Kopie. Die temporäre Kopie reduziert das Risiko, dass eine laufende GUI Dateien im echten Projektroot sperrt oder verändert.

Die Haupt-GUI liegt im Bereich resources/applications/devbox/functions und nutzt spezialisierte Subscripts für Seiten, Layout, Datenzugriff, Prozessstarts und Produktmodule. Die grafische Oberfläche verwendet PySide6. Sie greift über den echten Projektroot auf Grafiken, Fonts, Datenbanken, Installer und Funktionsskripte zu.

Die zentrale Stammdatenquelle ist resources/organization/devbox_db.r0b. Dort liegen Produktdaten, Repository-Felder, Dokumentationsfelder, Strukturinformationen, benannte deskNode-UX-Themes sowie die Symbolkatalogtabellen desknode_consumer_device_categories und desknode_consumer_devices. Für lokale DevBox-Runtime-Daten verwendet die Anwendung logfile.r0b und locdata.r0b unter AppData.

deskNode besitzt eigene abgeleitete Produktdaten unter applications/deskNode/data, insbesondere mnfctr_db.r0b für Manufaktur- und Theme-Daten sowie lan.r0b für Sprachressourcen. Bei einem Lauf erstellt der Supervisor einen eindeutigen Temp-Kontext. Der Daemon koppelt verfügbare venmods über coupler.py ein, validiert deren Verträge, richtet einen lokalen Worker-Control-Hub ein und startet für jeden akzeptierten venmod einen Worker. Die Worker schreiben nur ihre jeweilige flüchtige venmod-Datenbank. Der Daemon führt bestätigte Daten in der globalen AppData-Datenbank devices.r0b zusammen und protokolliert aufgelöste Leistungswerte separat.

Die aktuelle deskNode-Integration enthält venmods für Tapo, FRITZ!DECT und Shelly. Die Produkt-GUI wartet beim Start auf den bestätigten Erstzyklus aller gekoppelten venmods und zeigt danach den synchronisierten Gerätebestand. Strukturzuordnungen, UX-Einstellungen und die Darstellung liegen getrennt von den herstellerspezifischen Worker-Daten.

Der Graphic-Pack-Build verarbeitet globale Symbolquellen, Skalierung, Masken, Vektorisierung und Theme-Daten in temporären Arbeitsordnern. Inkscape und GIMP werden als externe lokale Werkzeuge verwendet. Das Ergebnis ist ein komprimiertes Grafikpaket mit vorberechneten Zustandsvarianten, das deskNode zur Laufzeit laden kann.


## Projektstatus

Aktiver Proof-of-Concept und Entwicklungsstand.

DevBox besitzt einen funktionsfähigen lokalen Launcher, eine grafische Hauptoberfläche, modulare Strukturansichten, Stammdaten- und Dokumentationspflege, Dokumentations-Snapshots, lokale Werkzeugerkennung, eine Repository-Seite sowie erste Bausteine für den DevBox-spezifischen Veröffentlichungsprozess.

Der deskNode-Bereich ist aktiv in DevBox integriert. Supervisor und Daemon können aus der GUI gestartet und gestoppt werden; deren Konsolenausgabe wird im deskNode-Log angezeigt. Die Produktversion kann aus den Stammdaten bearbeitet werden. UX-Themes können benannt, angelegt, gelöscht, dupliziert, umbenannt und gespeichert werden. Nach dem Speichern werden die deskNode-Produktdaten aktualisiert.

DeskNode verfügt im aktuellen Proof of Concept über eine gekoppelte Worker-Architektur. Tapo, FRITZ!DECT und Shelly werden lokal über eigene venmods entdeckt und überwacht; bei unterstützten Geräten werden Schaltzustände und Leistungswerte verarbeitet. Der Daemon synchronisiert die venmod-Daten in einen globalen Gerätebestand, hält einen initialen Sicherheitslesezyklus ein und startet die Hauptoberfläche erst nach der globalen Erst-Synchronisierung. Die Strukturverwaltung unterstützt mehrere Gebäude-Wurzeln, pro Gebäude einen vollständigen Geräte-Pool und zusätzliche additive Zuordnungen zu Räumen oder anderen Strukturgliedern.

Die Symbolverwaltung ist als funktionsfähige Katalogoberfläche vorhanden. Sie verwaltet deskNode-Gerätekategorien und Verbrauchergeräte über Auswahlmenüs sowie Dialoge zum Anlegen, Bearbeiten und Löschen. Neue Geräte erhalten eine einzelne PNG-Quelle, die unter ihrer record_id als symbol_source_<record_id>.png abgelegt wird. Nach jeder erfolgreichen Katalogänderung wird create_manufacturer_db.py ausgeführt, damit mnfctr_db.r0b die aktuellen Theme-, Kategorien- und Gerätedaten enthält.

Der Graphic-Pack-Build ist als Proof of Concept funktionsfähig. Er erzeugt aus Symbolquellen und UX-Themes vorbereitete Grafikzustände für Verbraucher. Die aktuelle deskNode-Laufzeit nutzt bereits Sprach-, Theme- und Grafikdaten; Asset-Auswahl, weitere Symbolabdeckung und visuelle Zustände werden weiterentwickelt.

DevBox und deskNode sind keine fertigen Endnutzer- oder Release-Versionen. Besonders Credential-Speicherung, Langzeitstabilität größerer Gerätebestände, herstellerspezifische Sonderfälle, Tests, Packaging und Plattformportierung sind noch offene Entwicklungsaufgaben.


## Installation und Start

DevBox ist derzeit als lokale, Windows-orientierte Entwicklungsumgebung vorgesehen.

Voraussetzungen für einen Entwicklungsstart:
- ein vollständiger CYXnTrol-Projektroot mit einer .root-Datei, deren Inhalt project-root lautet;
- eine funktionierende Python-Installation für die Entwicklungsumgebung;
- die für die GUI benötigten Python-Pakete, insbesondere PySide6;
- ReportLab und svglib für die PDF-Erzeugung;
- optional Git einschließlich Git Credential Manager für Repository-Vorgänge;
- optional Inkscape und GIMP für Grafik-, Masken- und Asset-Build-Funktionen;
- für deskNode ein vorhandener Produktordner applications/deskNode mit Funktions-, Daten-, venmod- und Ressourcendateien;
- für den Tapo-venmod ein Python-Environment mit python-kasa; für FRITZ!DECT und Shelly erreichbare lokale Geräte beziehungsweise Gateways im selben Netzwerk.

Der Start erfolgt über den DevBox-Launcher oder eine daraus erzeugte DevBox-Executable. Der Launcher sucht den Projektroot, stellt lokale Datenbanken unter AppData bereit, prüft externe Werkzeugpfade und startet danach die GUI. Ist bereits eine DevBox-Instanz geöffnet, wird diese in den Vordergrund geholt statt eine zweite Instanz zu starten.

Die deskNode-Schaltflächen starten produktbezogene Skripte über python.exe. Der deskNode-Supervisor erstellt pro Lauf einen temporären Runtime-Kontext und startet den Daemon. Dieser koppelt verfügbare venmods ein. Bei Geräten, die eine Anmeldung benötigen, fordert die deskNode-GUI lokale Zugangsdaten an und wartet auf die herstellerspezifische Prüfung. Nach dem bestätigten Erstzyklus und der globalen Synchronisierung erscheint die Hauptoberfläche.

Für den Graphic-Pack-Build müssen gültige symbol_source_<record_id>.png-Dateien im globalen Ordner resources/graphics liegen. Neue Quellen werden über die Symbolverwaltung angelegt. Der Build benötigt zusätzlich nutzbare Inkscape- und GIMP-Pfade. Eine produktive Distribution, portable Edition oder Installer-Paketierung erhält später getrennte Packaging- und Signierungsprozesse.


## Konfiguration

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


## Technologie

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


## Repository-Hinweis

Das DevBox-Repository repräsentiert die CYXnTrol Development Platform selbst, nicht ein fertiges Endnutzerprodukt. Es dient als Entwicklungsstand, transparente Arbeitsprobe und Grundlage für die Pflege der Plattform.

Der veröffentlichte Stand wird nicht direkt aus dem produktiven Projektroot kopiert. Für DevBox wird ein gesonderter bereinigter root_dir-Stand erzeugt. Er enthält vorgesehenen Quellcode, Dokumente und Assets, während lokale Laufzeitdaten, temporäre Reste, Installer, Datenbank-WAL-Dateien und nicht veröffentlichte Daten außerhalb des Veröffentlichungspakets bleiben.

Der derzeitige DevBox-Push behandelt applications als bewusstes Auslieferungsfenster: Der Bereich wird zunächst bereinigt. Danach wird applications/deskNode/resources/scripts einschließlich enthaltener Dateien in den Veröffentlichungsstand kopiert. __pycache__-Ordner sowie .pyc- und .pyo-Dateien bleiben ausgeschlossen. Dieser aktuelle Umfang ist ein DevBox-spezifischer Veröffentlichungsprozess und noch kein vollständiger deskNode-Produktrelease. Bevor deskNode einschließlich GUI, Logik und venmods als eigenes Repository oder Release veröffentlicht wird, muss dessen Exportumfang ausdrücklich definiert und getestet werden.

DevBox wird in einem KI-gestützten, iterativen Workflow entwickelt. Anforderungen, Architektur, Datenmodelle, UX-Entscheidungen, Testfälle und Abnahmen werden durch den Projektverantwortlichen gesteuert. Die Implementierung entsteht mit KI-gestützten Entwicklungswerkzeugen und wird gegen die definierten Funktionsanforderungen geprüft.


## Lizenz

Dieses Projekt steht unter Zero-Clause BSD License 0BSD.

Die vollständigen Lizenzbedingungen befinden sich in der mitgelieferten Lizenzdatei.

## Autor / Herausgeber

Markus Walloner
Markus Walloner
Germany (DE)

Copyright (c) 2026 Markus Walloner
