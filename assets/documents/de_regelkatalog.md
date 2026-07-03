REGELKATALOG
============

Dokumentstand: Aktiver Proof-of-Concept und Entwicklungsstand.

DevBox besitzt einen funktionsfähigen lokalen Launcher, eine grafische Hauptoberfläche, modulare Strukturansichten, Stammdaten- und Dokumentationspflege, Dokumentations-Snapshots, lokale Werkzeugerkennung, eine Repository-Seite sowie erste Bausteine für den DevBox-spezifischen Veröffentlichungsprozess.

Der deskNode-Bereich ist aktiv in DevBox integriert. Supervisor und Daemon können aus der GUI gestartet und gestoppt werden; deren Konsolenausgabe wird im deskNode-Log angezeigt. Die Produktversion kann aus den Stammdaten bearbeitet werden. UX-Themes können benannt, angelegt, gelöscht, dupliziert, umbenannt und gespeichert werden. Nach dem Speichern werden die deskNode-Produktdaten aktualisiert.

DeskNode verfügt im aktuellen Proof of Concept über eine gekoppelte Worker-Architektur. Tapo, FRITZ!DECT und Shelly werden lokal über eigene venmods entdeckt und überwacht; bei unterstützten Geräten werden Schaltzustände und Leistungswerte verarbeitet. Der Daemon synchronisiert die venmod-Daten in einen globalen Gerätebestand, hält einen initialen Sicherheitslesezyklus ein und startet die Hauptoberfläche erst nach der globalen Erst-Synchronisierung. Die Strukturverwaltung unterstützt mehrere Gebäude-Wurzeln, pro Gebäude einen vollständigen Geräte-Pool und zusätzliche additive Zuordnungen zu Räumen oder anderen Strukturgliedern.

Die Symbolverwaltung ist als funktionsfähige Katalogoberfläche vorhanden. Sie verwaltet deskNode-Gerätekategorien und Verbrauchergeräte über Auswahlmenüs sowie Dialoge zum Anlegen, Bearbeiten und Löschen. Neue Geräte erhalten eine einzelne PNG-Quelle, die unter ihrer record_id als symbol_source_<record_id>.png abgelegt wird. Nach jeder erfolgreichen Katalogänderung wird create_manufacturer_db.py ausgeführt, damit mnfctr_db.r0b die aktuellen Theme-, Kategorien- und Gerätedaten enthält.

Der Graphic-Pack-Build ist als Proof of Concept funktionsfähig. Er erzeugt aus Symbolquellen und UX-Themes vorbereitete Grafikzustände für Verbraucher. Die aktuelle deskNode-Laufzeit nutzt bereits Sprach-, Theme- und Grafikdaten; Asset-Auswahl, weitere Symbolabdeckung und visuelle Zustände werden weiterentwickelt.

DevBox und deskNode sind keine fertigen Endnutzer- oder Release-Versionen. Besonders Credential-Speicherung, Langzeitstabilität größerer Gerätebestände, herstellerspezifische Sonderfälle, Tests, Packaging und Plattformportierung sind noch offene Entwicklungsaufgaben.

Erstveröffentlichung: 
Autor / Herausgeber: Markus Walloner
Land: Germany (DE)

1. Geltungsbereich
------------------

Dieser Regelkatalog bezieht sich auf das in der begleitenden Projektdokumentation beschriebene Projekt.

Kurzbeschreibung:
DevBox ist die lokale Entwicklungszentrale der CYXnTrol Development Platform. Die PySide6-Oberfläche bündelt Projektstruktur, Stammdaten, Dokumentation, lokale Werkzeuge, Produktmodule, Repository-Vorbereitung und wiederkehrende Entwicklungsabläufe.

Mit deskNode ist ein aktives Produktmodul integriert: ein lokaler Geräte- und Strukturhub für Smart-Plugs und angeschlossene Verbraucher. deskNode wird über austauschbare venmods für unterstützte Hersteller und Protokolle erweitert.

DevBox ist kein Endnutzerprodukt. Es ist eine interne Arbeitsumgebung, in der Anforderungen, Datenmodelle, UX-Entscheidungen, Schnittstellen, Builds und Veröffentlichungsstände nachvollziehbar vorbereitet und geprüft werden.


2. Regelkatalog
---------------

DEVBOX-REGELKATALOG

1. Projektroot und Pfade
- Der Projektroot wird über die .root-Datei bestimmt.
- Implementierungen verwenden keine fest codierten Benutzer- oder Laufwerkspfade.
- Relative Projektpfade, Systemvariablen und der über .root bestimmte Root haben Vorrang.

2. Temporäre Arbeitsbereiche
- Exporte, Grafik-Builds, Umstrukturierungen, Repository-Vorbereitung und deskNode-Daemon-Läufe arbeiten in eindeutigen Unterordnern des System-Temp-Verzeichnisses.
- Der echte Projektroot wird nicht als wegwerfbare Arbeitskopie verwendet.
- Erfolg der Hauptoperation und Erfolg eines anschließenden Cleanups werden getrennt bewertet.

3. Python-Start
- Launcher, Builder und produktbezogene Prozesse verwenden ausdrücklich python.exe.
- pythonw.exe wird nicht als Ausführungsbasis verwendet, damit Fehler und Konsolenausgaben nachvollziehbar bleiben.

4. Datenbanken und Migration
- SQLite ist die zentrale Datenquelle für DevBox-Stammdaten und lokale deskNode-Laufzeitdaten.
- Schemaerweiterungen dürfen bestehende Tabellen oder Datensätze nicht löschen, außer eine Funktion erzeugt ausdrücklich eine abgeleitete Produktdatenbank neu.
- UX-Themes liegen zentral in "ux-deskNode" und produktnah in mnfctr_db.r0b als "ux_themes".
- deskNode-Sprachressourcen liegen produktnah in lan.r0b; lokale Nutzereinstellungen liegen getrennt in settings.r0b.
- Der deskNode-Symbolkatalog liegt zentral in desknode_consumer_device_categories und desknode_consumer_devices sowie produktnah in consumer_device_categories und consumer_devices.
- Nach jeder erfolgreichen Änderung an deskNode-Version, Theme, Kategorie oder Verbrauchergerät muss mnfctr_db.r0b aktualisiert werden.

5. deskNode-Laufzeit und venmods
- Jeder venmod besitzt einen klaren Coupler-Vertrag und einen eigenen Worker.
- Ein Worker schreibt nur seine eigene flüchtige venmod-Datenbank. Globale Geräte- und Strukturhaltung werden nicht direkt aus einem venmod geschrieben.
- Der Daemon validiert Coupler-Verträge, spiegelt bestätigte Werte in devices.r0b und sendet Sollzustände nur über die Downstream-Schnittstelle zurück.
- Der Erststart arbeitet zunächst lesend. Erst bestätigte Istwerte und die globale Erst-Synchronisierung geben die Main-GUI frei.
- Extern beobachtete Schaltzustände werden kontrolliert als Ist- und Sollzustand übernommen; ein venmod darf keine unbestätigten Rückschaltungen erzwingen.
- Herstellerlogik bleibt innerhalb des jeweiligen venmods. Funktionierende Tapo-, FRITZ!DECT- und Shelly-Pfade werden nicht ohne konkrete Anforderung umstrukturiert.

6. Credentials und Logs
- Zugangsdaten dürfen nicht in Konsolenausgaben, Worker-Events oder Fehlermeldungen materialisiert werden.
- Der derzeitige lokale Credential-Stand ist keine fertige sichere Vault-Lösung. Ein plattformübergreifender verschlüsselter Vault ist als gemeinsame Plattformkomponente zu entwickeln.
- Logging soll Prozessrolle, Produkt- oder venmod-Kontext und nachvollziehbare Fehlersignale enthalten, aber keine Geheimnisse.

7. Symbolquellen und Grafik-Build
- Ein Verbrauchergerät wird über eine stabile record_id und einen device_key referenziert, nicht über einen gerenderten Dateinamen.
- Neue Verbrauchergeräte benötigen genau eine PNG-Quelle.
- Die Quell-PNG wird als resources/graphics/symbol_source_<record_id>.png abgelegt.
- Kategorien gehören in die Datenbank, nicht in den Quelldateinamen.
- Der Builder erzeugt Skalierung, Masken, Theme-Varianten und finale Assets aus Symbolquellen und UX-Themes.
- Inkscape und GIMP werden nur über ausdrücklich gestartete Build-Schritte verwendet.

8. Modulgrenzen
- Subscripts sollen klar benannt sein und eine definierte Verantwortung besitzen.
- In Bereichen mit 300-Zeilen-Regel werden größere Abläufe in spezialisierte Subscripts aufgeteilt.
- Produktinterne Build-Skripte dürfen länger sein, wenn ihre zusammenhängende Prozesslogik dadurch verständlicher bleibt.

9. Veröffentlichung und Repository
- Der veröffentlichte DevBox-Stand wird aus einem kontrollierten root_dir-Sollzustand erzeugt.
- README, Lizenz, Dokumente und Bilder erhalten definierte Zielorte und Dateinamen.
- Repository-Zugangsdaten werden nicht in DevBox gespeichert.
- Der aktuelle DevBox-Export umfasst bewusst applications/deskNode/resources/scripts, aber keine __pycache__-, .pyc- oder .pyo-Inhalte.
- Vor einem Push wird der lokale Repository-Stand mit root_dir verglichen; obsolete veröffentlichte Dateien dürfen nur unter definierten Schutzregeln entfernt werden.

10. Externe Werkzeuge
- Pfade zu Inkscape und GIMP werden lokal geprüft und gespeichert.
- Fehlende Werkzeuge blockieren nicht die gesamte DevBox, können jedoch einzelne Funktionen einschränken.
- Installer und externe Programme werden nur durch explizite Nutzeraktion gestartet.


3. Ergänzende Hinweise
----------------------

Zweck:
DevBox soll wiederkehrende und fehleranfällige Entwicklungsarbeit in nachvollziehbare lokale Werkzeuge überführen. Dazu gehören insbesondere die Pflege von Produkt- und Herstellerdaten, strukturierte Dokumentation, vorbereitete Veröffentlichungsschritte, die Integration lokaler Kreativprogramme sowie die kontrollierte Ausführung produktbezogener Entwicklungsfunktionen.

Die Anwendung schafft eine gemeinsame Arbeitsgrundlage für Produkte der CYXnTrol Development Platform. Statt Abläufe nur als Erinnerung, Ordnerkonvention oder Sammlung einzelner Konsolenbefehle zu halten, werden sie als Daten, Skripte, GUI-Funktionen und überprüfbare Prozessketten festgehalten.

Für deskNode dient DevBox als Entwicklungs- und Konfigurationsoberfläche für Produktversionen, UX-Themes, Gerätekategorien, Verbrauchersymbole, Sprachressourcen und vorbereitete Grafikpakete. Die deskNode-Laufzeit soll daraus reproduzierbare Daten und vorbereitete Assets erhalten. Die venmod-Architektur soll zudem neue lokale Gerätepfade ergänzen können, ohne den Daemon oder bereits funktionierende Herstellerpfade unnötig umzubauen.


Kontext:
Die CYXnTrol Development Platform entstand aus praktischer Entwicklungsarbeit mit vielen kleinen Werkzeugen, Datenständen, Grafikdateien, Dokumenten und Testabläufen. Mit wachsender Zahl von Produkten und Funktionen reicht es nicht mehr aus, Informationen nur in einzelnen Dateien oder im Gedächtnis zu halten. Benötigt werden eine stabile Projektwurzel, nachvollziehbare Datenquellen, wiederholbare temporäre Arbeitsbereiche und klar abgegrenzte Produktmodule.

DevBox ist die Antwort auf diesen Bedarf. Es bildet eine lokale Entwicklungszentrale, in der Hersteller- und Produktdaten, Dokumentation, globale Strukturregeln, externe Werkzeuge, Repository-Vorbereitung und spezielle Produktfunktionen zusammengeführt werden.

deskNode ist das erste Produkt, das als eigener aktiver Bereich in DevBox integriert wird. Seine Aufgabe ist die lokale Verwaltung, Visualisierung und Schaltung unterstützter Smart-Plugs. Tapo, FRITZ!DECT und Shelly werden nicht als fest in die Oberfläche eingebaute Sonderfälle behandelt, sondern über venmods mit einem gemeinsamen Coupler- und Worker-Vertrag angebunden. Für Verbraucher werden Namen, Kategorien, stabile technische IDs, PNG-Quellen, Theme-Daten und vorberechnete Grafikzustände in einen reproduzierbaren Ablauf gebracht.


Repository-Hinweis:
Das DevBox-Repository repräsentiert die CYXnTrol Development Platform selbst, nicht ein fertiges Endnutzerprodukt. Es dient als Entwicklungsstand, transparente Arbeitsprobe und Grundlage für die Pflege der Plattform.

Der veröffentlichte Stand wird nicht direkt aus dem produktiven Projektroot kopiert. Für DevBox wird ein gesonderter bereinigter root_dir-Stand erzeugt. Er enthält vorgesehenen Quellcode, Dokumente und Assets, während lokale Laufzeitdaten, temporäre Reste, Installer, Datenbank-WAL-Dateien und nicht veröffentlichte Daten außerhalb des Veröffentlichungspakets bleiben.

Der derzeitige DevBox-Push behandelt applications als bewusstes Auslieferungsfenster: Der Bereich wird zunächst bereinigt. Danach wird applications/deskNode/resources/scripts einschließlich enthaltener Dateien in den Veröffentlichungsstand kopiert. __pycache__-Ordner sowie .pyc- und .pyo-Dateien bleiben ausgeschlossen. Dieser aktuelle Umfang ist ein DevBox-spezifischer Veröffentlichungsprozess und noch kein vollständiger deskNode-Produktrelease. Bevor deskNode einschließlich GUI, Logik und venmods als eigenes Repository oder Release veröffentlicht wird, muss dessen Exportumfang ausdrücklich definiert und getestet werden.

DevBox wird in einem KI-gestützten, iterativen Workflow entwickelt. Anforderungen, Architektur, Datenmodelle, UX-Entscheidungen, Testfälle und Abnahmen werden durch den Projektverantwortlichen gesteuert. Die Implementierung entsteht mit KI-gestützten Entwicklungswerkzeugen und wird gegen die definierten Funktionsanforderungen geprüft.


Copyright (c) 2026 Markus Walloner
