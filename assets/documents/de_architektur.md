ARCHITEKTURDOKUMENTATION
========================

Dokumentstand: Aktiver Proof-of-Concept und Entwicklungsstand.

DevBox besitzt einen funktionsfähigen lokalen Launcher, eine grafische Hauptoberfläche, modulare Strukturansichten, Stammdaten- und Dokumentationspflege, Dokumentations-Snapshots, lokale Werkzeugerkennung, eine Repository-Seite sowie erste Bausteine für den DevBox-spezifischen Veröffentlichungsprozess.

Der deskNode-Bereich ist aktiv in die DevBox integriert. Supervisor und Daemon können aus der GUI gestartet und gestoppt werden; deren Konsolenausgabe wird im deskNode-Log angezeigt. Die Produktversion kann aus den Stammdaten bearbeitet werden. UX-Themes können benannt, angelegt, gelöscht, dupliziert, umbenannt und gespeichert werden. Nach dem Speichern wird die deskNode-Manufakturdatenbank aktualisiert.

Die Symbolverwaltung ist als erste funktionsfähige Katalogoberfläche vorhanden. Sie verwaltet deskNode-Gerätekategorien und Verbrauchergeräte über Auswahlmenüs sowie Dialoge zum Anlegen, Bearbeiten und Löschen. Neue Geräte erhalten eine einzelne PNG-Quelle, die unter ihrer record_id als symbol_source_<record_id>.png abgelegt wird. Nach jeder erfolgreichen Katalogänderung wird create_manufacturer_db.py ausgeführt, damit mnfctr_db.r0b die aktuellen Theme-, Kategorien- und Gerätedaten enthält.

Der Graphic-Pack-Build ist als Proof-of-Concept funktionsfähig. Er erzeugt aus Symbolquellen und UX-Themes mehrere vorbereitete Grafikzustände für Verbraucher. Die eigentliche deskNode-Laufzeitintegration, Asset-Auswahl, Sprachpakete und vollständige Zustandslogik werden noch weiterentwickelt.

DevBox ist keine fertige Endnutzer- oder Release-Version. Oberflächen, Datenbankmigrationen, Produktmodule, Veröffentlichungsabläufe, Dokumentvorlagen und Tests werden fortlaufend überarbeitet. Diese Dokumentation beschreibt den derzeitigen Stand und muss bei funktionalen Änderungen mitgepflegt werden.

Erstveröffentlichung: 
Projektbeginn: 2026
Autor / Herausgeber: Markus Walloner
Land: Germany (DE)

1. Kurzüberblick
----------------

DevBox ist die lokale Entwicklungszentrale der CYXnTrol Development Platform. Die PySide6-Anwendung bündelt Projektstruktur, Stammdaten, Dokumentation, lokale Werkzeuge, Produktmodule, Repository-Vorbereitung und wiederkehrende Entwicklungsabläufe.

DevBox ist kein Endnutzerprodukt. Es ist eine interne Arbeitsumgebung, in der technische Anforderungen, Datenmodelle, Oberflächen, Build-Schritte und Veröffentlichungsstände nachvollziehbar vorbereitet, geprüft und weiterentwickelt werden.


2. Architekturüberblick
-----------------------

DevBox ist modular aufgebaut.

Die Startkette beginnt mit einem DevBox-Launcher. Dieser ermittelt den Projektroot über die .root-Datei, stellt lokale Laufzeitdaten unter AppData bereit, prüft gespeicherte Werkzeugpfade und startet die grafische Oberfläche aus einer temporären Kopie. Die temporäre Kopie reduziert das Risiko, dass eine laufende GUI Dateien im echten Projektroot sperrt oder verändert.

Die Haupt-GUI liegt im Bereich resources/applications/devbox/functions und nutzt spezialisierte Subscripts für Seiten, Layout, Datenzugriff, Prozessstarts und Produktmodule. Die grafische Oberfläche verwendet PySide6. Sie greift über den echten Projektroot auf Grafiken, Fonts, Datenbanken, Installer und Funktionsskripte zu.

Die zentrale Stammdatenquelle ist resources/organization/devbox_db.r0b. Dort liegen Produktdaten, Repository-Felder, Dokumentationsfelder, Strukturinformationen, benannte deskNode-UX-Themes sowie die Symbolkatalogtabellen desknode_consumer_device_categories und desknode_consumer_devices. Für lokale Laufzeitdaten verwendet DevBox logfile.r0b und locdata.r0b unter AppData.

deskNode besitzt zusätzlich applications/deskNode/data/mnfctr_db.r0b. Sie wird durch create_manufacturer_db.py neu erzeugt und enthält master_data, ux_themes, consumer_device_categories und consumer_devices. Dadurch bleibt die deskNode-Laufzeit von der vollständigen DevBox-Stammdatenbank entkoppelt.

Der Graphic-Pack-Build verarbeitet globale Symbolquellen, Skalierung, Masken, Vektorisierung und Theme-Daten in temporären Arbeitsordnern. Inkscape und GIMP werden als externe lokale Werkzeuge verwendet. Das Ergebnis ist ein komprimiertes Grafikpaket mit vorberechneten Zustandsvarianten, das deskNode später laden kann.


3. Detaillierte Architektur
---------------------------

DEVBOX-ARCHITEKTUR

1. Systemgrenze
DevBox ist eine lokale, Windows-orientierte Entwicklungsumgebung innerhalb des CYXnTrol-Projektroots. Sie stellt keine allgemeine Cloud-Plattform und keinen eingebauten Mehrbenutzer-Dienst bereit. Externe Dienste werden nur genutzt, wenn der Nutzer sie ausdrücklich über externe Werkzeuge oder einen Repository-Push einbindet.

2. Start- und Instanzebene
Der DevBox-Launcher ermittelt den Projektroot über .root. Er prüft Laufzeitvoraussetzungen, erstellt lokale AppData-Strukturen, initialisiert beziehungsweise prüft logfile.r0b und locdata.r0b, erkennt externe Werkzeuge und verhindert parallele GUI-Instanzen. Ist eine Instanz bereits geöffnet, wird sie aktiviert. Die GUI wird aus einer temporären Kopie gestartet.

3. GUI- und Modul-Ebene
Die Haupt-GUI basiert auf PySide6. Sie enthält Entwicklungsplattform-, Struktur-, Repository- und produktbezogene Seiten. deskNode ist als eigener Tab eingebunden. Dieser bündelt Produktstarts, Logausgabe, Versionsbearbeitung, Oberflächengestaltung und die Symbolverwaltung. Der Graphic-Pack-Build wird von der Symbolverwaltung aus gestartet, weil dort auch die relevanten Kategorien, Verbrauchergeräte und PNG-Quellen gepflegt werden.

4. Zentrale Datenebene
Devbox_db.r0b ist die zentrale Stammdatenbank im Projekt. Sie enthält Hersteller-, Produkt-, Dokumentations-, Struktur- und Repository-Daten. Die Tabelle "ux-deskNode" verwaltet mehrere benannte UX-Themes mit stabilen record_id-Werten. Die Tabellen desknode_consumer_device_categories und desknode_consumer_devices verwalten den deskNode-Symbolkatalog. logfile.r0b und locdata.r0b liegen getrennt unter AppData und enthalten Runtime-Informationen beziehungsweise lokale Werkzeugpfade.

5. Symbolkatalog-Ebene
Eine Kategorie besitzt record_id, category_key, translation_key und Zeitstempel. Ein Verbrauchergerät besitzt record_id, device_key, category_id, translation_key und Zeitstempel. category_id verweist auf die stabile record_id der Kategorie. Beim Anlegen eines neuen Geräts wird genau eine PNG entgegengenommen und als resources/graphics/symbol_source_<record_id>.png abgelegt. Dateinamen enthalten damit keine Kategoriehierarchie und bleiben über die technische ID stabil.

6. Produktdatenebene deskNode
DeskNode erhält eine abgeleitete Manufakturdatenbank mnfctr_db.r0b. create_manufacturer_db.py erzeugt master_data und kopiert aus devbox_db.r0b die Tabellen ux-deskNode als ux_themes, desknode_consumer_device_categories als consumer_device_categories sowie desknode_consumer_devices als consumer_devices. Jede erfolgreiche Änderung an Version, UX-Theme oder Symbolkatalog muss nach dem Datenbank-Commit diese Aktualisierung anstoßen.

7. Grafik-Build-Ebene
graphic_items_bulder.py verarbeitet Symbolquellen in einem temporären Arbeitsbereich. Es kopiert Quellgrafiken, skaliert und zentriert sie, erstellt in GIMP Kontrastmasken, vektorisiert diese mit Inkscape, bereinigt die resultierenden SVGs und erzeugt für jedes UX-Theme mehrere Glow- und Zustandsvarianten. Die finalen Dateien werden als Grafikpaket für deskNode bereitgestellt.

8. Dokumentations- und Veröffentlichungsebene
doc_forms.r0b enthält Formularvorlagen. Ein Dokumentprozess entpackt sie, befüllt sie aus sprachabhängigen Tabellen, erzeugt Markdown- und PDF-Dateien und überführt diese in eine kontrollierte Exportstruktur. Für DevBox wird ein temporärer root_dir als Sollzustand für die Repository-Synchronisation erzeugt. Der Veröffentlichungsstand enthält gezielt applications/deskNode/resources/scripts einschließlich Unterordnern, jedoch ohne __pycache__-Ordner und Python-Bytecode.

9. Integrationspunkte und Sicherheitsprinzip
Git und Git Credential Manager übernehmen Repository-Authentifizierung. Inkscape und GIMP werden als externe lokale Programme behandelt. ReportLab und svglib unterstützen die PDF-Generierung. DevBox trennt Originalbestand, temporäre Verarbeitung, abgeleitete Produktdatenbanken und Veröffentlichungsstand, damit aufwendige Operationen nicht unkontrolliert auf dem echten Projektroot arbeiten.


4. Funktionen und Ziele
-----------------------

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


5. Konfiguration
----------------

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


6. Technologie
-------------

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


7. Repository-Hinweis
---------------------

Das DevBox-Repository repräsentiert die CYXnTrol Development Platform selbst, nicht ein fertiges Endnutzerprodukt. Es dient als Entwicklungsstand, transparente Arbeitsprobe und Grundlage für die Pflege der Plattform.

Der veröffentlichte Stand wird nicht direkt aus dem produktiven Projektroot kopiert. Für DevBox wird ein gesonderter bereinigter root_dir-Stand erzeugt. Er enthält vorgesehenen Quellcode, Dokumente und Assets, während lokale Laufzeitdaten, temporäre Reste, Installer, unnötige Build-Ausgaben und nicht veröffentlichte Daten außerhalb des Veröffentlichungspakets bleiben.

Der temporäre Veröffentlichungsroot behandelt applications als bewusstes Auslieferungsfenster: Der Bereich wird zunächst bereinigt. Danach wird applications/deskNode/resources/scripts einschließlich enthaltener Dateien in den Veröffentlichungsstand kopiert. __pycache__-Ordner sowie .pyc- und .pyo-Dateien bleiben ausgeschlossen. Der echte lokale Produktordner wird dadurch nicht verändert.

DevBox wird in einem KI-gestützten, iterativen Workflow entwickelt. Anforderungen, Architektur, Datenmodelle, UX-Entscheidungen, Testfälle und Abnahmen werden durch den Projektverantwortlichen gesteuert. Die Implementierung entsteht mit KI-gestützten Entwicklungswerkzeugen und wird gegen die definierten Funktionsanforderungen geprüft.


Copyright (c) 2026 Markus Walloner
