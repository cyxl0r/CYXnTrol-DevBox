ARCHITEKTURDOKUMENTATION
========================

Dokumentstand: Aktiver Proof-of-Concept und Entwicklungsstand.

DevBox besitzt bereits einen funktionsfähigen lokalen Launcher, eine grafische Hauptoberfläche, modulare Strukturansichten, Stammdaten- und Dokumentationspflege, Dokumentations-Snapshots, Formularimporte, lokale Werkzeugerkennung, eine Repository-Seite sowie erste Bausteine für den DevBox-spezifischen Repository-Prozess.

Die Anwendung ist noch keine fertige Endnutzer- oder Release-Version. Oberflächen, Veröffentlichungsabläufe, Dokumentvorlagen, Repository-Synchronisation und einzelne Entwicklungsmodule werden fortlaufend überarbeitet. Die aktuelle Dokumentation beschreibt den derzeitigen Entwicklungsstand und muss bei funktionalen Änderungen mitgepflegt werden.

Erstveröffentlichung: 
Projektbeginn: 2026
Autor / Herausgeber: Markus Walloner
Land: Germany (DE)

1. Kurzüberblick
----------------

DevBox ist die lokale Entwicklungszentrale der CYXnTrol Development Platform. Sie bündelt wiederkehrende Arbeiten rund um Projektstruktur, Stammdaten, Dokumentation, Build-Werkzeuge, externe Kreativprogramme und Repository-Pflege in einer PySide6-Oberfläche.

DevBox ist kein Endnutzerprodukt. Die Anwendung dient als interne Arbeitsumgebung, mit der Entwicklungsabläufe nachvollziehbar vorbereitet, gepflegt und für spätere Veröffentlichungen strukturiert werden.


2. Architekturüberblick
-----------------------

DevBox ist modular aufgebaut.

Die Startkette beginnt mit einem DevBox-Launcher. Dieser ermittelt den Projektroot über die .root-Datei, stellt lokale Laufzeitdaten unter AppData bereit, prüft gespeicherte Werkzeugpfade und startet die grafische Oberfläche aus einer temporären Kopie. Die temporäre Kopie reduziert das Risiko, dass eine laufende GUI Dateien im echten Projektroot sperrt oder verändert.

Die Haupt-GUI liegt im Bereich functions und nutzt mehrere Subscripts für Seiten, Layout, Datenzugriff und Spezialfunktionen. Die grafische Oberfläche verwendet PySide6. Sie greift über den echten Projektroot auf Ressourcen wie Grafiken, Fonts, Datenbankdateien, Installer und Funktionsskripte zu.

Die zentrale Stammdatenquelle ist die SQLite-Datei devbox_db.r0b unter resources/organization. Dort liegen unter anderem Produktdaten, Repository-Felder, Dokumentationsfelder und Strukturinformationen. Für lokale Laufzeitdaten verwendet DevBox separate SQLite-Dateien unter AppData: logfile.r0b für Protokolle und locdata.r0b für geprüfte Pfade zu externen Werkzeugen.

Dokumentationsformulare liegen komprimiert in doc_forms.r0b. Für einen Export werden sie in einen temporären docs-Ordner entpackt, mit Daten aus der SQLite-Datenbank befüllt und anschließend als Markdown-Dateien, PDF-Dokumente und Repository-taugliche Assets in einen vorbereiteten root_dir-Stand überführt. Dieser root_dir dient als kontrollierter Soll-Zustand für die DevBox-Repository-Pflege.


3. Detaillierte Architektur
---------------------------

DEVBOX-ARCHITEKTUR

1. Systemgrenze
DevBox ist eine lokale Windows-orientierte Entwicklungsumgebung innerhalb des CYXnTrol-Projektroots. Sie stellt keine allgemeine Cloud-Plattform und keinen eingebauten Mehrbenutzer-Dienst bereit. Externe Dienste werden nur genutzt, wenn der Nutzer sie ausdrücklich über externe Werkzeuge oder einen Repository-Push einbindet.

2. Start- und Instanzebene
Der DevBox-Launcher ermittelt den Projektroot über .root. Er prüft Laufzeitvoraussetzungen, erstellt lokale AppData-Strukturen, initialisiert beziehungsweise prüft logfile.r0b und locdata.r0b, erkennt externe Werkzeuge und verhindert parallele GUI-Instanzen. Ist eine Instanz bereits geöffnet, wird sie aktiviert.

3. GUI-Ebene
Die Haupt-GUI basiert auf PySide6. Sie enthält die Entwicklungsplattformseite, die Struktur-Werkstatt, die Repository-Seite und weitere Bereiche, die teilweise als historische oder zukünftige Module markiert sind. Die GUI nutzt eine globale Hintergrundprojektion, modulare Seiten und Icon-basierte Aktionen.

4. Datenebene
devbox_db.r0b ist die zentrale Stammdatenbank im Projekt. Sie enthält unter anderem Produkt-, Hersteller-, Dokumentations-, Struktur- und Repository-Felder. logfile.r0b und locdata.r0b liegen getrennt unter AppData und enthalten Laufzeitinformationen beziehungsweise lokale Werkzeugpfade.

5. Dokumentationsebene
doc_forms.r0b enthält die Formularvorlagen. Ein Dokumentprozess entpackt die Vorlagen, füllt sie aus den sprachabhängigen Dokumenttabellen, erzeugt Markdown- und PDF-Dateien und ordnet die Ergebnisse in eine kontrollierte Exportstruktur ein. Die PDF-Erzeugung verwendet eingebettete Fonts sowie Header- und Footer-Grafiken.

6. Veröffentlichungsebene
Für DevBox wird ein temporärer root_dir erzeugt. In diesem Arbeitsstand werden nicht veröffentlichungsrelevante Daten entfernt, Dokumente in assets/documents und Bilder in assets/pictures eingeordnet und README- sowie Lizenzdateien im Root abgelegt. Der resultierende Stand ist der Soll-Zustand für die Repository-Synchronisation.

7. Integrationspunkte
Git und Git Credential Manager übernehmen Repository-Authentifizierung. Inkscape und GIMP werden als externe lokale Programme behandelt. ReportLab und svglib unterstützen die PDF-Generierung. Weitere Build-, Installer- und Veröffentlichungsbausteine bleiben modular und können getrennt erweitert werden.

8. Sicherheitsprinzip
DevBox trennt Originalbestand, temporäre Verarbeitung und Veröffentlichungsstand. Dadurch können Bereinigung, Export und Repository-Abgleich durchgeführt werden, ohne den echten Projektroot als Arbeitskopie zu missbrauchen.


4. Funktionen und Ziele
-----------------------

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


5. Konfiguration
----------------

Die Konfiguration ist in mehrere Ebenen getrennt.

Projektroot:
Der Projektroot wird über die Datei .root erkannt. Er ist die maßgebliche Quelle für Skripte, Ressourcen, Formulararchive, Installer und die zentrale DevBox-Datenbank.

Zentrale Stammdaten:
resources/organization/devbox_db.r0b enthält Dach-, Produkt-, Dokumentations-, Struktur- und Repository-Informationen. Bereits vorhandene Tabellen werden bei Schema-Erweiterungen nicht geleert; fehlende Spalten sollen per Migration ergänzt werden.

Lokale Laufzeitdaten:
%appdata%\CYXLabs\CYXnTrol\DevBox\logfile.r0b enthält Logdaten.
%appdata%\CYXLabs\CYXnTrol\DevBox\locdata.r0b enthält geprüfte Pfade für Inkscape und GIMP.

Werkzeugerkennung:
Gespeicherte Pfade werden beim Start geprüft. Ungültige Pfade werden zuerst unter Program Files und anschließend unter dem System-Temp-Bereich erneut gesucht. Werden keine unterstützten Programme gefunden, zeigt DevBox eine Warnung an.

Repository-Daten:
Repository-URL und Branch werden produktbezogen in product_credentials gepflegt. Git-Zugangsdaten werden nicht in DevBox gespeichert; Authentifizierung und Credential-Verwaltung bleiben bei Git und dem installierten Credential Manager.


6. Technologie
-------------

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


7. Repository-Hinweis
---------------------

Das DevBox-Repository repräsentiert die CYXnTrol Development Platform selbst und nicht ein fertiges Endnutzerprodukt. Es dient als Entwicklungsbestand, als nachvollziehbare Arbeitsprobe und als Grundlage für die weitere Pflege der Plattform.

Der Repository-Stand wird nicht direkt aus dem produktiven Projektroot übernommen. Für DevBox wird ein separater, bereinigter root_dir-Stand erzeugt. Dieser erhält die vorgesehenen Quelltexte, Dokumente und Assets, lässt lokale Datenbanken, temporäre Reste, nicht benötigte Build-Ausgaben, Fontdateien und Installationsartefakte außerhalb des Veröffentlichungspakets und kann anschließend mit dem DevBox-Repository synchronisiert werden.

Produkte, Dienste oder Werke, die aus der Plattform entstehen, sollen eigene Repositories erhalten. Ihre Veröffentlichungsschemata werden getrennt von der DevBox-Sonderlogik entwickelt.


Copyright (c) 2026 Markus Walloner
