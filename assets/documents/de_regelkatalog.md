REGELKATALOG
============

Dokumentstand: Aktiver Proof-of-Concept und Entwicklungsstand.

DevBox besitzt einen funktionsfähigen lokalen Launcher, eine grafische Hauptoberfläche, modulare Strukturansichten, Stammdaten- und Dokumentationspflege, Dokumentations-Snapshots, lokale Werkzeugerkennung, eine Repository-Seite sowie erste Bausteine für den DevBox-spezifischen Veröffentlichungsprozess.

Der deskNode-Bereich ist aktiv in die DevBox integriert. Supervisor und Daemon können aus der GUI gestartet und gestoppt werden; deren Konsolenausgabe wird im deskNode-Log angezeigt. Die Produktversion kann aus den Stammdaten bearbeitet werden. UX-Themes können benannt, angelegt, gelöscht, dupliziert, umbenannt und gespeichert werden. Nach dem Speichern wird die deskNode-Manufakturdatenbank aktualisiert.

Die Symbolverwaltung ist als erste funktionsfähige Katalogoberfläche vorhanden. Sie verwaltet deskNode-Gerätekategorien und Verbrauchergeräte über Auswahlmenüs sowie Dialoge zum Anlegen, Bearbeiten und Löschen. Neue Geräte erhalten eine einzelne PNG-Quelle, die unter ihrer record_id als symbol_source_<record_id>.png abgelegt wird. Nach jeder erfolgreichen Katalogänderung wird create_manufacturer_db.py ausgeführt, damit mnfctr_db.r0b die aktuellen Theme-, Kategorien- und Gerätedaten enthält.

Der Graphic-Pack-Build ist als Proof-of-Concept funktionsfähig. Er erzeugt aus Symbolquellen und UX-Themes mehrere vorbereitete Grafikzustände für Verbraucher. Die eigentliche deskNode-Laufzeitintegration, Asset-Auswahl, Sprachpakete und vollständige Zustandslogik werden noch weiterentwickelt.

DevBox ist keine fertige Endnutzer- oder Release-Version. Oberflächen, Datenbankmigrationen, Produktmodule, Veröffentlichungsabläufe, Dokumentvorlagen und Tests werden fortlaufend überarbeitet. Diese Dokumentation beschreibt den derzeitigen Stand und muss bei funktionalen Änderungen mitgepflegt werden.

Erstveröffentlichung: 
Autor / Herausgeber: Markus Walloner
Land: Germany (DE)

1. Geltungsbereich
------------------

Dieser Regelkatalog bezieht sich auf das in der begleitenden Projektdokumentation beschriebene Projekt.

Kurzbeschreibung:
DevBox ist die lokale Entwicklungszentrale der CYXnTrol Development Platform. Die PySide6-Anwendung bündelt Projektstruktur, Stammdaten, Dokumentation, lokale Werkzeuge, Produktmodule, Repository-Vorbereitung und wiederkehrende Entwicklungsabläufe.

DevBox ist kein Endnutzerprodukt. Es ist eine interne Arbeitsumgebung, in der technische Anforderungen, Datenmodelle, Oberflächen, Build-Schritte und Veröffentlichungsstände nachvollziehbar vorbereitet, geprüft und weiterentwickelt werden.


2. Regelkatalog
---------------

DEVBOX-REGELKATALOG

1. Projektroot und Pfade
- Der Projektroot wird über die .root-Datei bestimmt.
- Implementierungen verwenden keine fest codierten Benutzer- oder Laufwerkspfade.
- Relative Projektpfade, Systemvariablen und der über .root bestimmte Root haben Vorrang.

2. Temporäre Arbeitsbereiche
- Exporte, Grafik-Builds, Umstrukturierungen und Repository-Vorbereitung arbeiten in eindeutigen Unterordnern des System-Temp-Verzeichnisses.
- Der echte Projektroot wird nicht als wegwerfbare Arbeitskopie verwendet.
- Erfolg der Hauptoperation und Erfolg eines anschließenden Cleanups werden getrennt bewertet.

3. Python-Start
- Launcher, Builder und produktbezogene Prozesse verwenden ausdrücklich python.exe.
- pythonw.exe wird nicht als Ausführungsbasis verwendet, damit Fehler und Konsolenausgaben nachvollziehbar bleiben.

4. Datenbanken und Migration
- SQLite ist die zentrale Datenquelle für DevBox-Stammdaten.
- Schemaerweiterungen dürfen bestehende Tabellen oder Datensätze nicht löschen, außer eine Funktion erzeugt ausdrücklich eine abgeleitete Produktdatenbank neu.
- UX-Themes liegen zentral in "ux-deskNode" und produktnah in mnfctr_db.r0b als "ux_themes".
- Der deskNode-Symbolkatalog liegt zentral in desknode_consumer_device_categories und desknode_consumer_devices sowie produktnah in consumer_device_categories und consumer_devices.
- Nach jeder erfolgreichen Änderung an deskNode-Version, Theme, Kategorie oder Verbrauchergerät muss mnfctr_db.r0b aktualisiert werden.

5. Symbolquellen und Grafik-Build
- Ein Verbrauchergerät wird über eine stabile record_id und einen device_key referenziert, nicht über einen gerenderten PNG-Dateinamen.
- Neue Verbrauchergeräte benötigen genau eine PNG-Quelle.
- Die Quell-PNG liegt als resources/graphics/symbol_source_<record_id>.png.
- Kategorien gehören in die Datenbank und nicht in den Quell-Dateinamen.
- Der Builder erzeugt Skalierung, Masken, Theme-Varianten und finale Assets aus den Symbolquellen und UX-Themes.
- Inkscape und GIMP werden nur durch ausdrücklich gestartete Build-Schritte verwendet.

6. Logging und Runtime-Daten
- DevBox verwaltet lokale Runtime-Daten unter AppData.
- Fehler, Startzustände und relevante Prozessschritte sollen nachvollziehbar protokolliert werden.
- Jeder DevBox-Baustein soll langfristig einem klaren Log-Kontext zugeordnet sein.

7. Modulgrenzen
- Subscripts sollen klar benannt sein und eine abgegrenzte Verantwortung besitzen.
- In Bereichen mit der 300-Zeilen-Regel werden größere Abläufe in spezialisierte Subscripts aufgeteilt.
- Produktinterne Build-Skripte dürfen umfangreicher sein, wenn ihre zusammenhängende Prozesslogik dadurch verständlicher bleibt.

8. Veröffentlichung und Repository
- Der veröffentlichte DevBox-Stand wird aus einem kontrollierten root_dir-Sollzustand erzeugt.
- README, Lizenz, Dokumente und Bilder erhalten definierte Zielorte und Dateinamen.
- Repository-Zugangsdaten werden nicht in DevBox gespeichert.
- Der Veröffentlichungsexport enthält gezielt applications/deskNode/resources/scripts, aber keine __pycache__-, .pyc- oder .pyo-Inhalte.
- Vor einem Push wird der lokale Repository-Stand gegen root_dir abgeglichen; obsolete veröffentlichte Dateien dürfen nur nach definierten Schutzregeln entfernt werden.

9. Externe Werkzeuge
- Pfade zu Inkscape und GIMP werden lokal geprüft und gespeichert.
- Fehlende Werkzeuge blockieren nicht die gesamte DevBox, können aber einzelne Funktionen einschränken.
- Installer und externe Programme werden ausschließlich durch explizite Nutzeraktion gestartet.


3. Ergänzende Hinweise
----------------------

Zweck:
DevBox soll wiederkehrende und fehleranfällige Entwicklungsarbeit in nachvollziehbare lokale Werkzeuge überführen. Dazu gehören insbesondere die Pflege von Produkt- und Herstellerdaten, strukturierte Dokumentation, vorbereitete Veröffentlichungsschritte, die Integration lokaler Kreativprogramme sowie die kontrollierte Ausführung produktbezogener Entwicklungsfunktionen.

Die Anwendung schafft eine gemeinsame Arbeitsgrundlage für Produkte der CYXnTrol Development Platform. Statt Abläufe nur als Erinnerung, Ordnerkonvention oder Sammlung einzelner Konsolenbefehle zu halten, werden sie als Daten, Skripte, GUI-Funktionen und überprüfbare Prozessketten festgehalten.

Für deskNode dient DevBox zusätzlich als Entwicklungs- und Konfigurationsoberfläche für Produktversionen, UX-Themes, Gerätekategorien, Verbrauchersymbole und vorbereitete Grafikpakete. Die spätere deskNode-Laufzeit soll daraus reproduzierbare Daten und bereits gerenderte Assets erhalten.


Kontext:
Die CYXnTrol Development Platform entstand aus praktischer Entwicklungsarbeit mit vielen kleinen Werkzeugen, Datenständen, Grafikdateien, Dokumenten und Testabläufen. Mit wachsender Zahl von Produkten und Funktionen reicht es nicht mehr aus, Informationen nur in einzelnen Dateien oder im Gedächtnis zu halten. Benötigt werden eine stabile Projektwurzel, nachvollziehbare Datenquellen, wiederholbare temporäre Arbeitsbereiche und klar abgegrenzte Produktmodule.

DevBox ist die Antwort auf diesen Bedarf. Es bildet eine lokale Entwicklungszentrale, in der Hersteller- und Produktdaten, Dokumentation, globale Strukturregeln, externe Werkzeuge, Repository-Vorbereitung und spezielle Produktfunktionen zusammengeführt werden.

deskNode ist das erste Produkt, das als eigener aktiver Bereich in DevBox integriert wird. Seine Aufgabe ist die Verwaltung und Visualisierung von Smart-Plugs und angeschlossenen Verbrauchern. Für diese Verbraucher werden nicht nur Namen, sondern auch Kategorien, stabile technische IDs, PNG-Quellen, Theme-Daten und vorberechnete Grafikzustände in einen reproduzierbaren Ablauf gebracht. Damit müssen Symbolvarianten nicht mehr manuell für jede Kombination aus Theme und Zustand erstellt werden.


Repository-Hinweis:
Das DevBox-Repository repräsentiert die CYXnTrol Development Platform selbst, nicht ein fertiges Endnutzerprodukt. Es dient als Entwicklungsstand, transparente Arbeitsprobe und Grundlage für die Pflege der Plattform.

Der veröffentlichte Stand wird nicht direkt aus dem produktiven Projektroot kopiert. Für DevBox wird ein gesonderter bereinigter root_dir-Stand erzeugt. Er enthält vorgesehenen Quellcode, Dokumente und Assets, während lokale Laufzeitdaten, temporäre Reste, Installer, unnötige Build-Ausgaben und nicht veröffentlichte Daten außerhalb des Veröffentlichungspakets bleiben.

Der temporäre Veröffentlichungsroot behandelt applications als bewusstes Auslieferungsfenster: Der Bereich wird zunächst bereinigt. Danach wird applications/deskNode/resources/scripts einschließlich enthaltener Dateien in den Veröffentlichungsstand kopiert. __pycache__-Ordner sowie .pyc- und .pyo-Dateien bleiben ausgeschlossen. Der echte lokale Produktordner wird dadurch nicht verändert.

DevBox wird in einem KI-gestützten, iterativen Workflow entwickelt. Anforderungen, Architektur, Datenmodelle, UX-Entscheidungen, Testfälle und Abnahmen werden durch den Projektverantwortlichen gesteuert. Die Implementierung entsteht mit KI-gestützten Entwicklungswerkzeugen und wird gegen die definierten Funktionsanforderungen geprüft.


Copyright (c) 2026 Markus Walloner
