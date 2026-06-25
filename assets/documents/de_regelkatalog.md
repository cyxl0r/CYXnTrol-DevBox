REGELKATALOG
============

Dokumentstand: Aktiver Proof-of-Concept und Entwicklungsstand.

DevBox besitzt bereits einen funktionsfähigen lokalen Launcher, eine grafische Hauptoberfläche, modulare Strukturansichten, Stammdaten- und Dokumentationspflege, Dokumentations-Snapshots, Formularimporte, lokale Werkzeugerkennung, eine Repository-Seite sowie erste Bausteine für den DevBox-spezifischen Repository-Prozess.

Die Anwendung ist noch keine fertige Endnutzer- oder Release-Version. Oberflächen, Veröffentlichungsabläufe, Dokumentvorlagen, Repository-Synchronisation und einzelne Entwicklungsmodule werden fortlaufend überarbeitet. Die aktuelle Dokumentation beschreibt den derzeitigen Entwicklungsstand und muss bei funktionalen Änderungen mitgepflegt werden.

Erstveröffentlichung: 
Autor / Herausgeber: Markus Walloner
Land: Germany (DE)

1. Geltungsbereich
------------------

Dieser Regelkatalog bezieht sich auf das in der begleitenden Projektdokumentation beschriebene Projekt.

Kurzbeschreibung:
DevBox ist die lokale Entwicklungszentrale der CYXnTrol Development Platform. Sie bündelt wiederkehrende Arbeiten rund um Projektstruktur, Stammdaten, Dokumentation, Build-Werkzeuge, externe Kreativprogramme und Repository-Pflege in einer PySide6-Oberfläche.

DevBox ist kein Endnutzerprodukt. Die Anwendung dient als interne Arbeitsumgebung, mit der Entwicklungsabläufe nachvollziehbar vorbereitet, gepflegt und für spätere Veröffentlichungen strukturiert werden.


2. Regelkatalog
---------------

DEVBOX-REGELKATALOG

1. Projektroot und Pfade
- Der Projektroot wird über die Datei .root ermittelt.
- Implementierungen verwenden keine fest verdrahteten Benutzer- oder Laufwerkspfade.
- Relative Projektpfade, Systemvariablen und der über .root ermittelte Root haben Vorrang.

2. Temporäre Arbeitsbereiche
- Umbauten, Exporte, Build-Schritte und Repository-Vorbereitungen arbeiten in eindeutigen Unterordnern des System-Temp-Verzeichnisses.
- Der echte Projektroot bleibt während solcher Vorgänge unverändert.
- Erfolg eines Hauptvorgangs und Erfolg des anschließenden Cleanups werden getrennt bewertet.

3. Python-Start
- Launcher und Builder verwenden ausdrücklich python.exe.
- pythonw.exe wird nicht als Ausführungsbasis verwendet, damit Fehler und Konsolenausgaben nachvollziehbar bleiben.

4. Datenbanken und Migration
- SQLite ist die zentrale Datenbasis für DevBox-Stammdaten.
- Schema-Erweiterungen dürfen bestehende Tabellen und Datensätze nicht löschen.
- Fehlende Spalten werden per Migration ergänzt.

5. Logging und Laufzeitdaten
- DevBox führt lokale Laufzeitdaten unter AppData.
- Fehler, Startzustände und relevante Prozessschritte sollen nachvollziehbar protokolliert werden.
- Jeder DevBox-Baustein soll langfristig einem klaren Logkontext zuordenbar sein.

6. Modulgrenzen
- Funktionsskripte und Subscripts sollen klein, klar benannt und auf eine konkrete Aufgabe begrenzt bleiben.
- Neue Push-to-Git-Skripte dürfen jeweils nicht mehr als 300 Zeilen umfassen.
- Große Abläufe werden in spezialisierte Unterskripte zerlegt.

7. Veröffentlichung und Repository
- Der veröffentlichte DevBox-Stand entsteht aus einem kontrollierten root_dir-Sollzustand.
- README, Lizenz, Dokumente und Bilder erhalten definierte Zielorte und Dateinamen.
- Repository-Zugangsdaten werden nicht in DevBox gespeichert.
- Vor einem Push wird der lokale Repository-Stand mit root_dir abgeglichen; obsolete veröffentlichte Dateien dürfen nur nach den definierten Schutzregeln entfernt werden.

8. Externe Werkzeuge
- Pfade zu Inkscape und GIMP werden lokal geprüft und gespeichert.
- Nicht gefundene Werkzeuge blockieren nicht die gesamte DevBox, können aber zu eingeschränkten Funktionen führen.
- Installer und externe Programme werden nur auf ausdrückliche Nutzeraktion gestartet.


3. Ergänzende Hinweise
----------------------

Zweck:
DevBox soll wiederkehrende und fehleranfällige Entwicklungsarbeit bündeln, standardisieren und sichtbar machen. Statt wichtige Abläufe nur als Erinnerung, lose Ordnerkonvention oder Einzelskript zu behalten, werden sie in einer Plattform festgehalten.

Die Anwendung dient insbesondere dazu:
- Projekt- und Produktstammdaten zentral zu pflegen.
- Dokumentationsinhalte in Deutsch und Englisch zu verwalten.
- Formulare, Markdown-Dateien und PDF-Dokumente aus gepflegten Daten zu erzeugen.
- die reale Projektordnerstruktur sichtbar zu machen und kontrolliert zu bearbeiten.
- benötigte Entwicklungswerkzeuge zu erkennen, zu installieren und zu starten.
- bereinigte, dokumentierte Repository-Stände vorzubereiten.
- Entwicklungsentscheidungen, Zustände und Fehler lokal nachvollziehbar zu protokollieren.

DevBox soll Routinearbeit nicht verstecken, sondern in verlässliche Bausteine überführen. Das Ziel ist keine starre All-in-one-Software, sondern eine wachsende Entwicklungszentrale, die mit den entstehenden Produkten und Diensten weiterentwickelt wird.


Kontext:
Die CYXnTrol Development Platform entstand aus praktischer Entwicklungsarbeit. Kleine Hilfsskripte konnten einzelne Aufgaben lösen, mussten aber selbst organisiert, aktualisiert und nachvollzogen werden. Mit zunehmender Zahl von Skripten, Datenquellen, Dokumenten, Testständen und geplanten Produkten wurde deutlich, dass auch die Entwicklungsumgebung eine eigene Struktur benötigt.

DevBox ist die sichtbare Schaltzentrale dieser Struktur. Sie verbindet lokale SQLite-Stammdaten, PySide6-Oberflächen, Dokumentationsformulare, Dateistrukturen, Build-nahe Werkzeuge und später auch Repository-Prozesse. Dabei bleibt die Plattform bewusst lokal orientiert: Der Entwicklungsbestand gehört dem Nutzer, liegt im Projektroot oder in lokalem AppData und wird nicht automatisch in eine Cloud übertragen.

Die Anwendung wird innerhalb der Dachmarke CYXLabs und der CYXnTrol Development Platform entwickelt. Sie dient zugleich als Arbeitswerkzeug, als Muster für weitere Entwicklungsplattformen und als nachvollziehbare Arbeitsprobe für modulare Softwareentwicklung.


Repository-Hinweis:
Das DevBox-Repository repräsentiert die CYXnTrol Development Platform selbst und nicht ein fertiges Endnutzerprodukt. Es dient als Entwicklungsbestand, als nachvollziehbare Arbeitsprobe und als Grundlage für die weitere Pflege der Plattform.

Der Repository-Stand wird nicht direkt aus dem produktiven Projektroot übernommen. Für DevBox wird ein separater, bereinigter root_dir-Stand erzeugt. Dieser erhält die vorgesehenen Quelltexte, Dokumente und Assets, lässt lokale Datenbanken, temporäre Reste, nicht benötigte Build-Ausgaben, Fontdateien und Installationsartefakte außerhalb des Veröffentlichungspakets und kann anschließend mit dem DevBox-Repository synchronisiert werden.

Produkte, Dienste oder Werke, die aus der Plattform entstehen, sollen eigene Repositories erhalten. Ihre Veröffentlichungsschemata werden getrennt von der DevBox-Sonderlogik entwickelt.


Copyright (c) 2026 Markus Walloner
