# README

## Kurzbeschreibung

DevBox ist die lokale Entwicklungszentrale der CYXnTrol Development Platform. Sie bündelt wiederkehrende Arbeiten rund um Projektstruktur, Stammdaten, Dokumentation, Build-Werkzeuge, externe Kreativprogramme und Repository-Pflege in einer PySide6-Oberfläche.

DevBox ist kein Endnutzerprodukt. Die Anwendung dient als interne Arbeitsumgebung, mit der Entwicklungsabläufe nachvollziehbar vorbereitet, gepflegt und für spätere Veröffentlichungen strukturiert werden.


## Langbeschreibung

DevBox verbindet mehrere Entwicklungsaufgaben, die sonst über einzelne Skripte, Ordner, Tabellen, Konsolenfenster und externe Programme verteilt wären. Die Oberfläche stellt die Plattformdaten bereit, verwaltet Produktdaten und Dokumentationsinhalte, bereitet strukturierte Dokumente vor und bietet Werkzeuge für die Pflege eines kontrollierten Entwicklungsbestands.

Die Anwendung arbeitet lokal im Projektkontext. Ein Launcher ermittelt den Projektroot über die Datei .root, erstellt für die GUI eine temporäre Arbeitskopie und startet die grafische Oberfläche kontrolliert. Der echte Projektroot bleibt dabei die maßgebliche Quelle für Ressourcen, Datenbanken und Werkzeuge. Die DevBox verhindert parallele GUI-Instanzen und holt eine vorhandene Instanz beim erneuten Start in den Vordergrund.

Neben der Struktur-Werkstatt enthält DevBox eine Repository-Seite. Dort kann ein vorbereiteter Veröffentlichungsstand für die DevBox selbst erzeugt werden. Dieser Stand entsteht in einem temporären Arbeitsbereich, wird von nicht vorgesehenen Runtime-, Installer- und lokalen Daten bereinigt, erhält die gepflegten Dokumente und kann anschließend mit dem hinterlegten Repository verbunden werden. Dieser Sonderprozess gilt zunächst nur für DevBox; spätere Produkte erhalten eigene, passende Veröffentlichungsschemata.

DevBox erkennt außerdem lokale Installationsorte von Inkscape und GIMP, verwaltet diese Fundorte in einer lokalen SQLite-Datei und stellt für verfügbare Anwendungen Startbuttons bereit. Fehlende Fundorte werden beim Start erneut geprüft. Damit verbindet die Plattform ihre eigenen Daten, Skripte und Werkzeuge zu einer zentralen, lokal nachvollziehbaren Entwicklungsumgebung.


## Zweck

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


## Einordnung

Die CYXnTrol Development Platform entstand aus praktischer Entwicklungsarbeit. Kleine Hilfsskripte konnten einzelne Aufgaben lösen, mussten aber selbst organisiert, aktualisiert und nachvollzogen werden. Mit zunehmender Zahl von Skripten, Datenquellen, Dokumenten, Testständen und geplanten Produkten wurde deutlich, dass auch die Entwicklungsumgebung eine eigene Struktur benötigt.

DevBox ist die sichtbare Schaltzentrale dieser Struktur. Sie verbindet lokale SQLite-Stammdaten, PySide6-Oberflächen, Dokumentationsformulare, Dateistrukturen, Build-nahe Werkzeuge und später auch Repository-Prozesse. Dabei bleibt die Plattform bewusst lokal orientiert: Der Entwicklungsbestand gehört dem Nutzer, liegt im Projektroot oder in lokalem AppData und wird nicht automatisch in eine Cloud übertragen.

Die Anwendung wird innerhalb der Dachmarke CYXLabs und der CYXnTrol Development Platform entwickelt. Sie dient zugleich als Arbeitswerkzeug, als Muster für weitere Entwicklungsplattformen und als nachvollziehbare Arbeitsprobe für modulare Softwareentwicklung.


## Kernidee

Die Kernidee von DevBox lautet: Wiederkehrende Entwicklungsprozesse sollen nicht jedes Mal neu erfunden werden. Sie werden als verständliche Werkzeuge, Datenstrukturen und Abläufe festgehalten.

Ein einzelnes Skript kann eine konkrete Aufgabe lösen. Mehrere Skripte benötigen jedoch gemeinsame Regeln: Sie brauchen einen Projektroot, sichere temporäre Arbeitsbereiche, nachvollziehbare Datenquellen, konsistente Dateinamen, Fehlerprotokolle und eine Oberfläche, in der ihre Funktionen auffindbar bleiben. DevBox schafft diese gemeinsame Ebene.

Daraus folgt ein wichtiges Prinzip: Der echte Projektroot bleibt geschützt. Vorgänge mit Umbauten, Dokumentexporten, Bereinigungen oder Repository-Vorbereitung arbeiten mit temporären Kopien. Erst ein erfolgreich vorbereiteter Stand wird als Veröffentlichungskandidat weitergegeben. So bleiben Entwicklungsstand und veröffentlichter Stand klar voneinander getrennt.


## Funktionen und Ziele

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


## Architekturüberblick

DevBox ist modular aufgebaut.

Die Startkette beginnt mit einem DevBox-Launcher. Dieser ermittelt den Projektroot über die .root-Datei, stellt lokale Laufzeitdaten unter AppData bereit, prüft gespeicherte Werkzeugpfade und startet die grafische Oberfläche aus einer temporären Kopie. Die temporäre Kopie reduziert das Risiko, dass eine laufende GUI Dateien im echten Projektroot sperrt oder verändert.

Die Haupt-GUI liegt im Bereich functions und nutzt mehrere Subscripts für Seiten, Layout, Datenzugriff und Spezialfunktionen. Die grafische Oberfläche verwendet PySide6. Sie greift über den echten Projektroot auf Ressourcen wie Grafiken, Fonts, Datenbankdateien, Installer und Funktionsskripte zu.

Die zentrale Stammdatenquelle ist die SQLite-Datei devbox_db.r0b unter resources/organization. Dort liegen unter anderem Produktdaten, Repository-Felder, Dokumentationsfelder und Strukturinformationen. Für lokale Laufzeitdaten verwendet DevBox separate SQLite-Dateien unter AppData: logfile.r0b für Protokolle und locdata.r0b für geprüfte Pfade zu externen Werkzeugen.

Dokumentationsformulare liegen komprimiert in doc_forms.r0b. Für einen Export werden sie in einen temporären docs-Ordner entpackt, mit Daten aus der SQLite-Datenbank befüllt und anschließend als Markdown-Dateien, PDF-Dokumente und Repository-taugliche Assets in einen vorbereiteten root_dir-Stand überführt. Dieser root_dir dient als kontrollierter Soll-Zustand für die DevBox-Repository-Pflege.


## Projektstatus

Aktiver Proof-of-Concept und Entwicklungsstand.

DevBox besitzt bereits einen funktionsfähigen lokalen Launcher, eine grafische Hauptoberfläche, modulare Strukturansichten, Stammdaten- und Dokumentationspflege, Dokumentations-Snapshots, Formularimporte, lokale Werkzeugerkennung, eine Repository-Seite sowie erste Bausteine für den DevBox-spezifischen Repository-Prozess.

Die Anwendung ist noch keine fertige Endnutzer- oder Release-Version. Oberflächen, Veröffentlichungsabläufe, Dokumentvorlagen, Repository-Synchronisation und einzelne Entwicklungsmodule werden fortlaufend überarbeitet. Die aktuelle Dokumentation beschreibt den derzeitigen Entwicklungsstand und muss bei funktionalen Änderungen mitgepflegt werden.


## Installation und Start

DevBox ist derzeit für Windows als lokale Entwicklungsumgebung vorgesehen.

Voraussetzungen für einen Entwicklungsstart:
- ein vollständiger CYXnTrol-Projektroot mit einer .root-Datei, deren Inhalt project-root lautet;
- eine funktionsfähige Python-Installation für die Entwicklungsumgebung;
- die für die GUI benötigten Python-Pakete, insbesondere PySide6;
- für PDF-Erzeugung die Python-Pakete reportlab und svglib;
- optional Git inklusive Git Credential Manager für Repository-Vorgänge;
- optional Inkscape und GIMP für die entsprechenden Werkzeugfunktionen.

Der Start erfolgt über den DevBox-Launcher oder über die daraus erzeugte DevBox-EXE. Der Launcher sucht den Projektroot, stellt die erforderlichen lokalen Datenbanken unter AppData bereit, prüft externe Werkzeugpfade und startet anschließend die GUI. Falls bereits eine DevBox-Instanz läuft, wird diese in den Vordergrund geholt statt eine zweite Instanz zu starten.

Für einen produktiven Distributionsweg, eine portable Variante oder ein Installationspaket gelten später eigene Packaging- und Signierungsprozesse.


## Konfiguration

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


## Technologie

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


## Repository-Hinweis

Das DevBox-Repository repräsentiert die CYXnTrol Development Platform selbst und nicht ein fertiges Endnutzerprodukt. Es dient als Entwicklungsbestand, als nachvollziehbare Arbeitsprobe und als Grundlage für die weitere Pflege der Plattform.

Der Repository-Stand wird nicht direkt aus dem produktiven Projektroot übernommen. Für DevBox wird ein separater, bereinigter root_dir-Stand erzeugt. Dieser erhält die vorgesehenen Quelltexte, Dokumente und Assets, lässt lokale Datenbanken, temporäre Reste, nicht benötigte Build-Ausgaben, Fontdateien und Installationsartefakte außerhalb des Veröffentlichungspakets und kann anschließend mit dem DevBox-Repository synchronisiert werden.

Produkte, Dienste oder Werke, die aus der Plattform entstehen, sollen eigene Repositories erhalten. Ihre Veröffentlichungsschemata werden getrennt von der DevBox-Sonderlogik entwickelt.


## Lizenz

Dieses Projekt steht unter Zero-Clause BSD License 0BSD.

Die vollständigen Lizenzbedingungen befinden sich in der mitgelieferten Lizenzdatei.

## Autor / Herausgeber

Markus Walloner
Markus Walloner
Germany (DE)

Copyright (c) 2026 Markus Walloner
