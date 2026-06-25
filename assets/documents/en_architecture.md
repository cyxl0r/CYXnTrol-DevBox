ARCHITECTURE DOCUMENTATION
==========================

Document status: Active proof of concept and development state.

DevBox already has a functioning local launcher, a graphical main interface, modular structure views, master-data and documentation maintenance, documentation snapshots, form imports, local tool detection, a repository page, and initial building blocks for the DevBox-specific repository process.

The application is not yet a finished end-user or release version. Interfaces, publication workflows, document templates, repository synchronization, and individual development modules are being revised continuously. The current documentation describes the present development state and must be maintained alongside functional changes.

First publication: 
Project start: 2026
Author / publisher: Markus Walloner
Country: Germany (DE)

1. Overview
-----------

DevBox is the local development hub of the CYXnTrol Development Platform. It brings together recurring work around project structure, master data, documentation, build tools, external creative applications, and repository maintenance in a PySide6 interface.

DevBox is not an end-user product. It is an internal work environment for preparing, maintaining, and structuring development workflows for later publication.


2. Architecture Overview
------------------------

DevBox is modular in structure.

The launch chain begins with a DevBox launcher. It discovers the project root through the .root file, provides local runtime data under AppData, checks stored tool paths, and starts the graphical interface from a temporary copy. The temporary copy reduces the risk that a running GUI locks or changes files in the actual project root.

The main GUI resides in the functions area and uses several subscripts for pages, layout, data access, and specialized functions. The graphical interface uses PySide6. It accesses resources such as graphics, fonts, database files, installers, and function scripts through the actual project root.

The central master-data source is the SQLite file devbox_db.r0b under resources/organization. It contains, among other things, product data, repository fields, documentation fields, and structure information. For local runtime data, DevBox uses separate SQLite files under AppData: logfile.r0b for logs and locdata.r0b for verified paths to external tools.

Documentation forms are stored compressed in doc_forms.r0b. During an export, they are unpacked into a temporary docs folder, populated with data from the SQLite database, and then transferred as Markdown files, PDF documents, and repository-ready assets into a prepared root_dir state. That root_dir serves as the controlled desired state for DevBox repository maintenance.


3. Detailed Architecture
------------------------

DEVBOX ARCHITECTURE

1. System boundary
DevBox is a local Windows-oriented development environment within the CYXnTrol project root. It does not provide a general cloud platform or an embedded multi-user service. External services are used only when the user explicitly connects them through external tools or a repository push.

2. Launch and instance layer
The DevBox launcher discovers the project root through .root. It checks runtime requirements, creates local AppData structures, initializes or checks logfile.r0b and locdata.r0b, detects external tools, and prevents parallel GUI instances. If an instance is already open, it is activated.

3. GUI layer
The main GUI is based on PySide6. It contains the development platform page, the structure workshop, the repository page, and other areas that are partly marked as historic or future modules. The GUI uses a global background projection, modular pages, and icon-based actions.

4. Data layer
devbox_db.r0b is the central master database in the project. It contains, among other things, product, manufacturer, documentation, structure, and repository fields. logfile.r0b and locdata.r0b are stored separately under AppData and contain runtime information and local tool paths respectively.

5. Documentation layer
doc_forms.r0b contains the form templates. A documentation process unpacks the templates, populates them from language-dependent documentation tables, generates Markdown and PDF files, and places the results in a controlled export structure. PDF generation uses embedded fonts as well as header and footer graphics.

6. Publication layer
For DevBox, a temporary root_dir is generated. In this working state, non-publication data is removed, documents are placed in assets/documents, images are placed in assets/pictures, and README and license files are placed in the root. The resulting state is the desired state for repository synchronization.

7. Integration points
Git and Git Credential Manager handle repository authentication. Inkscape and GIMP are treated as external local programs. ReportLab and svglib support PDF generation. Further build, installer, and publication components remain modular and can be extended separately.

8. Security principle
DevBox separates the original state, temporary processing, and publication state. This allows cleanup, export, and repository synchronization without using the actual project root as the working copy.


4. Features and Goals
---------------------

Current functional scope:
- launch a single DevBox instance and activate an already running instance;
- provide a platform page with areas for the project platform, applications, and development software;
- detect and launch Inkscape and GIMP locally;
- launch installers for supported third-party tools when the installers are present in the project;
- provide a central SQLite master database for umbrella, product, documentation, and structure information;
- provide a structure workshop with navigation for umbrella data, product data, documentation, and the global app folder structure;
- export documentation snapshots and import fully revised German and English documentation content in a controlled manner;
- generate Markdown documents and PDF drafts for terms of use and privacy policies;
- provide a repository page with product selection, optional commit text, optional images, and log output;
- prepare a cleaned and documented DevBox repository state in a temporary workspace;
- maintain local log and tool-location databases under AppData.

Goals for the next expansion stages:
- further secure and improve the DevBox-specific push-to-Git process;
- maintain repository data per product;
- add further structured development tools as independent modules;
- separate later publication schemes for other products from the DevBox special logic;
- further standardize error states, logs, and status displays.


5. Configuration
----------------

Configuration is separated into several layers.

Project root:
The project root is discovered through the .root file. It is the authoritative source for scripts, resources, form archives, installers, and the central DevBox database.

Central master data:
resources/organization/devbox_db.r0b contains umbrella, product, documentation, structure, and repository information. Existing tables are not cleared when the schema is expanded; missing columns are intended to be added through migration.

Local runtime data:
%appdata%\CYXLabs\CYXnTrol\DevBox\logfile.r0b contains log data.
%appdata%\CYXLabs\CYXnTrol\DevBox\locdata.r0b contains verified paths for Inkscape and GIMP.

Tool detection:
Stored paths are checked at startup. Invalid paths are searched again first under Program Files and then under the system temporary area. If no supported program is found, DevBox displays a warning.

Repository data:
Repository URL and branch are maintained per product in product_credentials. Git credentials are not stored in DevBox; authentication and credential management remain with Git and the installed credential manager.


6. Technology
-------------

DevBox currently uses the following technologies in particular:

- Python as the core language for launchers, business logic, data preparation, and automation.
- PySide6 for the local graphical user interface.
- SQLite for central project master data as well as local runtime, log, and location data.
- openpyxl as a transitional or import tool for spreadsheets, not as the central master-data source.
- ReportLab and svglib for local generation of designed PDF documents.
- Git and Git Credential Manager for repository operations and authentication.
- Inkscape and GIMP as external locally launched creative tools.
- C# generation, the .NET SDK, WiX, and later additional packaging tools for build and installer processes.
- temporary workspaces under the system temporary directory for controlled copies, exports, and publication preparation.

The technical structure aims to clearly separate the GUI, function scripts, subscripts, data sources, and temporary work states.


7. Repository Note
------------------

The DevBox repository represents the CYXnTrol Development Platform itself, not a finished end-user product. It serves as a development state, a traceable work sample, and a foundation for maintaining the platform.

The repository state is not copied directly from the productive project root. For DevBox, a separate cleaned root_dir state is generated. It receives the intended source code, documents, and assets, keeps local databases, temporary remnants, unnecessary build outputs, font files, and installation artifacts outside the publication package, and can then be synchronized with the DevBox repository.

Products, services, or works created from the platform are intended to receive separate repositories. Their publication schemes will be developed separately from the DevBox special logic.


Copyright (c) 2026 Markus Walloner
