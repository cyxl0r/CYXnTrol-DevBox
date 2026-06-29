# README

## Kurzbeschreibung

DevBox ist die lokale Entwicklungszentrale der CYXnTrol Development Platform. Die PySide6-Anwendung bündelt Projektstruktur, Stammdaten, Dokumentation, lokale Werkzeuge, Produktmodule, Repository-Vorbereitung und wiederkehrende Entwicklungsabläufe.

DevBox ist kein Endnutzerprodukt. Es ist eine interne Arbeitsumgebung, in der technische Anforderungen, Datenmodelle, Oberflächen, Build-Schritte und Veröffentlichungsstände nachvollziehbar vorbereitet, geprüft und weiterentwickelt werden.


## Langbeschreibung

DevBox verbindet Aufgaben, die sonst über Einzelskripte, Ordner, Tabellen, Konsolenfenster und externe Programme verteilt wären. Die Anwendung verwaltet zentrale Projekt- und Produktdaten, stellt Dokumentationsinhalte bereit, organisiert globale Strukturvorlagen, erkennt lokale Werkzeuge und bündelt produktbezogene Entwicklungsfunktionen in einer gemeinsamen Oberfläche.

Ein aktives Produktmodul ist deskNode. Die deskNode-Seite kann den lokalen Supervisor und Daemon starten und stoppen, die Produktversion aus den Stammdaten bearbeiten, UX-Themes pflegen und die Symbolverwaltung öffnen. Themes werden mit benannten Datensätzen, RGBA-Farben, globalen Schriftdateien, Größen, Konturen und Formregeln gepflegt. Nach jeder erfolgreichen Theme-Änderung wird die produktnahe deskNode-Manufakturdatenbank aktualisiert.

Die Symbolverwaltung ist die zentrale Quelle für Gerätekategorien und Verbrauchersymbole. Kategorien und Geräte werden in der DevBox-Datenbank angelegt, bearbeitet oder gelöscht. Beim Anlegen eines neuen Verbrauchergeräts wird genau eine PNG-Quelle angenommen und anhand der stabilen Datensatz-ID als symbol_source_<record_id>.png im globalen Grafikordner abgelegt. Der Graphic-Pack-Build erzeugt daraus vorberechnete Varianten für Themes und Zustände, damit die spätere deskNode-Laufzeit nur passende Assets auswählen muss.

DevBox arbeitet lokal im Projektkontext. Ein Launcher ermittelt den Projektroot über die Datei .root, stellt Laufzeitdaten unter AppData bereit, prüft externe Werkzeuge und startet die GUI aus einer temporären Arbeitskopie. Der echte Projektroot bleibt die maßgebliche Quelle für Ressourcen, Datenbanken und Funktionsskripte. Eine Einzelinstanzlogik verhindert parallele DevBox-Fenster und aktiviert beim erneuten Start die bereits geöffnete Instanz.

Das Projekt entsteht in einem KI-gestützten, iterativen Entwicklungsprozess. Fachliche Anforderungen, Prozesslogik, Datenmodelle, UX-Entscheidungen, Testfälle und Abnahmen werden durch den Projektverantwortlichen gesteuert; Implementierungsschritte werden mit KI-gestützten Werkzeugen erstellt, überprüft und fortlaufend nachgeschärft.


## Zweck

DevBox soll wiederkehrende und fehleranfällige Entwicklungsarbeit in nachvollziehbare lokale Werkzeuge überführen. Dazu gehören insbesondere die Pflege von Produkt- und Herstellerdaten, strukturierte Dokumentation, vorbereitete Veröffentlichungsschritte, die Integration lokaler Kreativprogramme sowie die kontrollierte Ausführung produktbezogener Entwicklungsfunktionen.

Die Anwendung schafft eine gemeinsame Arbeitsgrundlage für Produkte der CYXnTrol Development Platform. Statt Abläufe nur als Erinnerung, Ordnerkonvention oder Sammlung einzelner Konsolenbefehle zu halten, werden sie als Daten, Skripte, GUI-Funktionen und überprüfbare Prozessketten festgehalten.

Für deskNode dient DevBox zusätzlich als Entwicklungs- und Konfigurationsoberfläche für Produktversionen, UX-Themes, Gerätekategorien, Verbrauchersymbole und vorbereitete Grafikpakete. Die spätere deskNode-Laufzeit soll daraus reproduzierbare Daten und bereits gerenderte Assets erhalten.


## Einordnung

Die CYXnTrol Development Platform entstand aus praktischer Entwicklungsarbeit mit vielen kleinen Werkzeugen, Datenständen, Grafikdateien, Dokumenten und Testabläufen. Mit wachsender Zahl von Produkten und Funktionen reicht es nicht mehr aus, Informationen nur in einzelnen Dateien oder im Gedächtnis zu halten. Benötigt werden eine stabile Projektwurzel, nachvollziehbare Datenquellen, wiederholbare temporäre Arbeitsbereiche und klar abgegrenzte Produktmodule.

DevBox ist die Antwort auf diesen Bedarf. Es bildet eine lokale Entwicklungszentrale, in der Hersteller- und Produktdaten, Dokumentation, globale Strukturregeln, externe Werkzeuge, Repository-Vorbereitung und spezielle Produktfunktionen zusammengeführt werden.

deskNode ist das erste Produkt, das als eigener aktiver Bereich in DevBox integriert wird. Seine Aufgabe ist die Verwaltung und Visualisierung von Smart-Plugs und angeschlossenen Verbrauchern. Für diese Verbraucher werden nicht nur Namen, sondern auch Kategorien, stabile technische IDs, PNG-Quellen, Theme-Daten und vorberechnete Grafikzustände in einen reproduzierbaren Ablauf gebracht. Damit müssen Symbolvarianten nicht mehr manuell für jede Kombination aus Theme und Zustand erstellt werden.


## Kernidee

Die Kernidee von DevBox lautet: Wiederkehrende Entwicklungsprozesse sollen nicht jedes Mal neu erfunden werden. Sie sollen als verständliche Werkzeuge, Datenstrukturen und Abläufe dauerhaft verfügbar bleiben.

Ein einzelnes Skript kann eine konkrete Aufgabe lösen. Mehrere Skripte und Produkte benötigen jedoch gemeinsame Regeln: einen eindeutig bestimmbaren Projektroot, sichere temporäre Arbeitsbereiche, zentrale Stammdaten, portable Pfade, nachvollziehbare Logs, getrennte Runtime-Daten und eine Oberfläche, in der Funktionen auffindbar bleiben.

Ein zweites zentrales Prinzip ist die Trennung von Entwurf, Quelle und Laufzeit. deskNode-UX-Themes sowie Geräte- und Symbolkataloge werden in DevBox gepflegt, anschließend in die deskNode-Manufakturdatenbank überführt und für Builds verwendet. Der Produktbetrieb soll auf vorbereitete, konsistente Daten und Assets zugreifen können, ohne die Editorlogik der DevBox zu benötigen.


## Funktionen und Ziele

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


## Architekturüberblick

DevBox ist modular aufgebaut.

Die Startkette beginnt mit einem DevBox-Launcher. Dieser ermittelt den Projektroot über die .root-Datei, stellt lokale Laufzeitdaten unter AppData bereit, prüft gespeicherte Werkzeugpfade und startet die grafische Oberfläche aus einer temporären Kopie. Die temporäre Kopie reduziert das Risiko, dass eine laufende GUI Dateien im echten Projektroot sperrt oder verändert.

Die Haupt-GUI liegt im Bereich resources/applications/devbox/functions und nutzt spezialisierte Subscripts für Seiten, Layout, Datenzugriff, Prozessstarts und Produktmodule. Die grafische Oberfläche verwendet PySide6. Sie greift über den echten Projektroot auf Grafiken, Fonts, Datenbanken, Installer und Funktionsskripte zu.

Die zentrale Stammdatenquelle ist resources/organization/devbox_db.r0b. Dort liegen Produktdaten, Repository-Felder, Dokumentationsfelder, Strukturinformationen, benannte deskNode-UX-Themes sowie die Symbolkatalogtabellen desknode_consumer_device_categories und desknode_consumer_devices. Für lokale Laufzeitdaten verwendet DevBox logfile.r0b und locdata.r0b unter AppData.

deskNode besitzt zusätzlich applications/deskNode/data/mnfctr_db.r0b. Sie wird durch create_manufacturer_db.py neu erzeugt und enthält master_data, ux_themes, consumer_device_categories und consumer_devices. Dadurch bleibt die deskNode-Laufzeit von der vollständigen DevBox-Stammdatenbank entkoppelt.

Der Graphic-Pack-Build verarbeitet globale Symbolquellen, Skalierung, Masken, Vektorisierung und Theme-Daten in temporären Arbeitsordnern. Inkscape und GIMP werden als externe lokale Werkzeuge verwendet. Das Ergebnis ist ein komprimiertes Grafikpaket mit vorberechneten Zustandsvarianten, das deskNode später laden kann.


## Projektstatus

Aktiver Proof-of-Concept und Entwicklungsstand.

DevBox besitzt einen funktionsfähigen lokalen Launcher, eine grafische Hauptoberfläche, modulare Strukturansichten, Stammdaten- und Dokumentationspflege, Dokumentations-Snapshots, lokale Werkzeugerkennung, eine Repository-Seite sowie erste Bausteine für den DevBox-spezifischen Veröffentlichungsprozess.

Der deskNode-Bereich ist aktiv in die DevBox integriert. Supervisor und Daemon können aus der GUI gestartet und gestoppt werden; deren Konsolenausgabe wird im deskNode-Log angezeigt. Die Produktversion kann aus den Stammdaten bearbeitet werden. UX-Themes können benannt, angelegt, gelöscht, dupliziert, umbenannt und gespeichert werden. Nach dem Speichern wird die deskNode-Manufakturdatenbank aktualisiert.

Die Symbolverwaltung ist als erste funktionsfähige Katalogoberfläche vorhanden. Sie verwaltet deskNode-Gerätekategorien und Verbrauchergeräte über Auswahlmenüs sowie Dialoge zum Anlegen, Bearbeiten und Löschen. Neue Geräte erhalten eine einzelne PNG-Quelle, die unter ihrer record_id als symbol_source_<record_id>.png abgelegt wird. Nach jeder erfolgreichen Katalogänderung wird create_manufacturer_db.py ausgeführt, damit mnfctr_db.r0b die aktuellen Theme-, Kategorien- und Gerätedaten enthält.

Der Graphic-Pack-Build ist als Proof-of-Concept funktionsfähig. Er erzeugt aus Symbolquellen und UX-Themes mehrere vorbereitete Grafikzustände für Verbraucher. Die eigentliche deskNode-Laufzeitintegration, Asset-Auswahl, Sprachpakete und vollständige Zustandslogik werden noch weiterentwickelt.

DevBox ist keine fertige Endnutzer- oder Release-Version. Oberflächen, Datenbankmigrationen, Produktmodule, Veröffentlichungsabläufe, Dokumentvorlagen und Tests werden fortlaufend überarbeitet. Diese Dokumentation beschreibt den derzeitigen Stand und muss bei funktionalen Änderungen mitgepflegt werden.


## Installation und Start

DevBox ist derzeit als lokale Windows-orientierte Entwicklungsumgebung vorgesehen.

Voraussetzungen für einen Entwicklungsstart:
- ein vollständiger CYXnTrol-Projektroot mit einer .root-Datei, deren Inhalt project-root lautet;
- eine funktionierende Python-Installation für die Entwicklungsumgebung;
- die für die GUI benötigten Python-Pakete, insbesondere PySide6;
- ReportLab und svglib für die PDF-Erzeugung;
- optional Git einschließlich Git Credential Manager für Repository-Vorgänge;
- optional Inkscape und GIMP für Grafik-, Masken- und Asset-Build-Funktionen;
- für deskNode ein vorhandener Produktordner applications/deskNode mit Funktions-, Daten- und Ressourcendateien.

Der Start erfolgt über den DevBox-Launcher oder eine daraus erzeugte DevBox-Executable. Der Launcher sucht den Projektroot, stellt lokale Datenbanken unter AppData bereit, prüft externe Werkzeugpfade und startet danach die GUI. Ist bereits eine DevBox-Instanz geöffnet, wird diese in den Vordergrund geholt statt eine zweite Instanz zu starten.

Die deskNode-Schaltflächen starten produktbezogene Skripte über python.exe. Für den Graphic-Pack-Build müssen gültige symbol_source_<record_id>.png-Dateien im globalen Ordner resources/graphics liegen. Neue Quellen werden über die Symbolverwaltung angelegt. Der Build benötigt zusätzlich nutzbare Inkscape- und GIMP-Pfade. Eine produktive Distribution, portable Edition oder Installer-Paketierung erhält später getrennte Packaging- und Signierungsprozesse.


## Konfiguration

Die Konfiguration ist in mehrere Ebenen getrennt.

Projektroot:
Der Projektroot wird über die .root-Datei gefunden. Er ist die maßgebliche Quelle für Skripte, Ressourcen, Formarchive, Installer, globale Fonts und die zentrale DevBox-Datenbank.

Zentrale Stammdaten:
resources/organization/devbox_db.r0b enthält Hersteller-, Produkt-, Dokumentations-, Struktur-, Repository-, UX-Theme- und Symbolkataloginformationen. Die Tabelle "ux-deskNode" enthält mehrere benannte Theme-Datensätze mit record_id und theme_name. Die Tabellen desknode_consumer_device_categories und desknode_consumer_devices enthalten die dauerhaften technischen Kategorien und Verbrauchergeräte. Schemaerweiterungen sollen vorhandene Datensätze erhalten und fehlende Felder über Migration ergänzen.

Symbolkatalog:
Kategorien werden über category_key und einen automatisch abgeleiteten translation_key geführt. Geräte werden über device_key, category_id und einen automatisch abgeleiteten translation_key geführt. Beim Anlegen eines Geräts wird eine einzelne PNG gewählt oder abgelegt und nach resources/graphics/symbol_source_<record_id>.png kopiert. Die Zuordnung zur Kategorie erfolgt über category_id, nicht über einen Dateinamen.

deskNode-Laufzeitdaten:
applications/deskNode/data/mnfctr_db.r0b wird durch create_manufacturer_db.py neu erzeugt. Sie enthält master_data, ux_themes, consumer_device_categories und consumer_devices. Nach jeder erfolgreichen Änderung an Version, Theme, Kategorie oder Verbrauchergerät wird diese Aktualisierung ausgeführt.

Oberflächengestaltung:
Farben werden als achtstellige RGBA-Hexwerte ohne # gespeichert, zum Beispiel 00e4ffff. Schriftdateien werden rekursiv aus resources/fonts gelesen und als projektroot-relative Pfade gespeichert. Schriftrollen umfassen große Überschriften, Bereichsüberschriften, Standardtext, Schaltflächentext, Eingabefeldtext, Statusmeldungen und Protokolltext. Weitere Theme-Werte betreffen Schriftgrößen, Schriftschnitt, Unterstreichung, Konturen, Radien und Zustandsfarben.

Lokale Runtime-Daten:
%appdata%/CYXLabs/CYXnTrol/DevBox/logfile.r0b enthält Logdaten.
%appdata%/CYXLabs/CYXnTrol/DevBox/locdata.r0b enthält geprüfte Pfade für Inkscape und GIMP.

Werkzeugerkennung:
Gespeicherte Pfade werden beim Start geprüft. Ungültige Pfade werden erneut gesucht, zunächst unter Program Files und anschließend im System-Temp-Bereich. Fehlende Werkzeuge beschränken nur die jeweiligen Funktionen.

Repository-Daten:
Repository-URL und Branch werden pro Produkt in product_credentials gepflegt. Git-Zugangsdaten werden nicht in DevBox gespeichert. Für den DevBox-Push wird ein temporärer Veröffentlichungsroot erzeugt; der Produktordner applications wird darin bereinigt und anschließend gezielt mit applications/deskNode/resources/scripts ohne __pycache__-Inhalte befüllt.


## Technologie

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


## Repository-Hinweis

Das DevBox-Repository repräsentiert die CYXnTrol Development Platform selbst, nicht ein fertiges Endnutzerprodukt. Es dient als Entwicklungsstand, transparente Arbeitsprobe und Grundlage für die Pflege der Plattform.

Der veröffentlichte Stand wird nicht direkt aus dem produktiven Projektroot kopiert. Für DevBox wird ein gesonderter bereinigter root_dir-Stand erzeugt. Er enthält vorgesehenen Quellcode, Dokumente und Assets, während lokale Laufzeitdaten, temporäre Reste, Installer, unnötige Build-Ausgaben und nicht veröffentlichte Daten außerhalb des Veröffentlichungspakets bleiben.

Der temporäre Veröffentlichungsroot behandelt applications als bewusstes Auslieferungsfenster: Der Bereich wird zunächst bereinigt. Danach wird applications/deskNode/resources/scripts einschließlich enthaltener Dateien in den Veröffentlichungsstand kopiert. __pycache__-Ordner sowie .pyc- und .pyo-Dateien bleiben ausgeschlossen. Der echte lokale Produktordner wird dadurch nicht verändert.

DevBox wird in einem KI-gestützten, iterativen Workflow entwickelt. Anforderungen, Architektur, Datenmodelle, UX-Entscheidungen, Testfälle und Abnahmen werden durch den Projektverantwortlichen gesteuert. Die Implementierung entsteht mit KI-gestützten Entwicklungswerkzeugen und wird gegen die definierten Funktionsanforderungen geprüft.


## Lizenz

Dieses Projekt steht unter Zero-Clause BSD License 0BSD.

Die vollständigen Lizenzbedingungen befinden sich in der mitgelieferten Lizenzdatei.

## Autor / Herausgeber

Markus Walloner
Markus Walloner
Germany (DE)

Copyright (c) 2026 Markus Walloner
