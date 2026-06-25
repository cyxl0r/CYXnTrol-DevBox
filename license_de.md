LIZENZFORM

Lizenzbezeichnung: Zero-Clause BSD License 0BSD

Copyright (c) 2026 Markus Walloner
Autor / sichtbare Autorenangabe: Markus Walloner
Erstveröffentlichung: 
Projektbeginn: 2026
Land: Germany (DE)

1. Gegenstand

Diese Lizenzform bezieht sich auf die Software, die in der begleitenden Projektdokumentation beschrieben wird.

Kurzbeschreibung:
DevBox ist die lokale Entwicklungszentrale der CYXnTrol Development Platform. Sie bündelt wiederkehrende Arbeiten rund um Projektstruktur, Stammdaten, Dokumentation, Build-Werkzeuge, externe Kreativprogramme und Repository-Pflege in einer PySide6-Oberfläche.

DevBox ist kein Endnutzerprodukt. Die Anwendung dient als interne Arbeitsumgebung, mit der Entwicklungsabläufe nachvollziehbar vorbereitet, gepflegt und für spätere Veröffentlichungen strukturiert werden.


Langbeschreibung:
DevBox verbindet mehrere Entwicklungsaufgaben, die sonst über einzelne Skripte, Ordner, Tabellen, Konsolenfenster und externe Programme verteilt wären. Die Oberfläche stellt die Plattformdaten bereit, verwaltet Produktdaten und Dokumentationsinhalte, bereitet strukturierte Dokumente vor und bietet Werkzeuge für die Pflege eines kontrollierten Entwicklungsbestands.

Die Anwendung arbeitet lokal im Projektkontext. Ein Launcher ermittelt den Projektroot über die Datei .root, erstellt für die GUI eine temporäre Arbeitskopie und startet die grafische Oberfläche kontrolliert. Der echte Projektroot bleibt dabei die maßgebliche Quelle für Ressourcen, Datenbanken und Werkzeuge. Die DevBox verhindert parallele GUI-Instanzen und holt eine vorhandene Instanz beim erneuten Start in den Vordergrund.

Neben der Struktur-Werkstatt enthält DevBox eine Repository-Seite. Dort kann ein vorbereiteter Veröffentlichungsstand für die DevBox selbst erzeugt werden. Dieser Stand entsteht in einem temporären Arbeitsbereich, wird von nicht vorgesehenen Runtime-, Installer- und lokalen Daten bereinigt, erhält die gepflegten Dokumente und kann anschließend mit dem hinterlegten Repository verbunden werden. Dieser Sonderprozess gilt zunächst nur für DevBox; spätere Produkte erhalten eigene, passende Veröffentlichungsschemata.

DevBox erkennt außerdem lokale Installationsorte von Inkscape und GIMP, verwaltet diese Fundorte in einer lokalen SQLite-Datei und stellt für verfügbare Anwendungen Startbuttons bereit. Fehlende Fundorte werden beim Start erneut geprüft. Damit verbindet die Plattform ihre eigenen Daten, Skripte und Werkzeuge zu einer zentralen, lokal nachvollziehbaren Entwicklungsumgebung.


2. Lizenztext

Der nachfolgende Bereich muss mit dem unveränderten vollständigen Text der in den Produktdaten hinterlegten Lizenz "Zero-Clause BSD License 0BSD" gefüllt werden.

<<< VOLLSTÄNDIGEN UND UNVERÄNDERTEN LIZENZTEXT HIER EINFÜGEN >>>

3. Projektbezogene Hinweise

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


4. Dokumentationsstand

Status:
Aktiver Proof-of-Concept und Entwicklungsstand.

DevBox besitzt bereits einen funktionsfähigen lokalen Launcher, eine grafische Hauptoberfläche, modulare Strukturansichten, Stammdaten- und Dokumentationspflege, Dokumentations-Snapshots, Formularimporte, lokale Werkzeugerkennung, eine Repository-Seite sowie erste Bausteine für den DevBox-spezifischen Repository-Prozess.

Die Anwendung ist noch keine fertige Endnutzer- oder Release-Version. Oberflächen, Veröffentlichungsabläufe, Dokumentvorlagen, Repository-Synchronisation und einzelne Entwicklungsmodule werden fortlaufend überarbeitet. Die aktuelle Dokumentation beschreibt den derzeitigen Entwicklungsstand und muss bei funktionalen Änderungen mitgepflegt werden.


Veröffentlichungsjahr: 
