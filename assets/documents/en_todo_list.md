TODO LIST
=========

Document status: Active proof of concept and development state.

DevBox already has a functioning local launcher, a graphical main interface, modular structure views, master-data and documentation maintenance, documentation snapshots, form imports, local tool detection, a repository page, and initial building blocks for the DevBox-specific repository process.

The application is not yet a finished end-user or release version. Interfaces, publication workflows, document templates, repository synchronization, and individual development modules are being revised continuously. The current documentation describes the present development state and must be maintained alongside functional changes.

First publication: 
Project start: 2026
Author / publisher: Markus Walloner

1. Project Context
------------------

Short Description:
DevBox is the local development hub of the CYXnTrol Development Platform. It brings together recurring work around project structure, master data, documentation, build tools, external creative applications, and repository maintenance in a PySide6 interface.

DevBox is not an end-user product. It is an internal work environment for preparing, maintaining, and structuring development workflows for later publication.


Long Description:
DevBox combines development tasks that would otherwise be spread across individual scripts, folders, tables, console windows, and external applications. Its interface provides platform data, manages product and documentation content, prepares structured documents, and offers tools for maintaining a controlled development state.

The application operates locally in the project context. A launcher discovers the project root through the .root file, creates a temporary working copy for the GUI, and starts the graphical interface in a controlled manner. The actual project root remains the authoritative source for resources, databases, and tools. DevBox prevents parallel GUI instances and brings an existing instance to the foreground when it is started again.

In addition to the structure workshop, DevBox contains a repository page. There, a prepared publication state for DevBox itself can be generated. That state is created in a temporary workspace, cleaned of non-public runtime, installer, and local data, enriched with maintained documentation, and then connected to the configured repository. This special process currently applies only to DevBox; later products will receive their own suitable publication schemes.

DevBox also detects local installation locations of Inkscape and GIMP, stores those locations in a local SQLite file, and provides launch buttons for available applications. Missing locations are checked again at startup. This brings the platform’s own data, scripts, and tools together in one locally traceable development environment.


2. Open Items
-------------

CURRENT TODO LIST

Repository and publication
- Fully test the DevBox push-to-Git process in the GUI.
- Verify repository URL and branch setup with a real remote repository.
- Further secure desired-versus-actual synchronization, protection rules, and removal of obsolete repository files.
- Continue to evaluate push success and temporary cleanup success separately.
- Further refine repository log output and error presentation.
- Plan publication schemes for later products separately from DevBox.

Documentation
- Update form texts when functionality changes.
- Have terms of use and privacy notices legally reviewed and adapted to real data flows before public use.
- Test the PDF layout with different text lengths, page breaks, and special characters.
- Add the complete unmodified license text to license forms before publication.

DevBox architecture
- Further standardize logging across all DevBox components.
- Document the locdata and logfile structure over time.
- Add further structure-workshop areas as configurable modules.
- Review and clean up legacy and unused scripts in a controlled way.
- Reintegrate the compiler and packaging chain as a clearly defined DevBox area.

Tools and quality
- Further test launch, installation, and error handling for external tools.
- Verify multi-monitor behavior, single-instance focus, and the structure view at different resolutions.
- Add automated tests for database migration, documentation export, snapshot structure, and repository synchronization.


3. Target State
---------------

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


4. Technical Context
--------------------

DevBox is modular in structure.

The launch chain begins with a DevBox launcher. It discovers the project root through the .root file, provides local runtime data under AppData, checks stored tool paths, and starts the graphical interface from a temporary copy. The temporary copy reduces the risk that a running GUI locks or changes files in the actual project root.

The main GUI resides in the functions area and uses several subscripts for pages, layout, data access, and specialized functions. The graphical interface uses PySide6. It accesses resources such as graphics, fonts, database files, installers, and function scripts through the actual project root.

The central master-data source is the SQLite file devbox_db.r0b under resources/organization. It contains, among other things, product data, repository fields, documentation fields, and structure information. For local runtime data, DevBox uses separate SQLite files under AppData: logfile.r0b for logs and locdata.r0b for verified paths to external tools.

Documentation forms are stored compressed in doc_forms.r0b. During an export, they are unpacked into a temporary docs folder, populated with data from the SQLite database, and then transferred as Markdown files, PDF documents, and repository-ready assets into a prepared root_dir state. That root_dir serves as the controlled desired state for DevBox repository maintenance.


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


Copyright (c) 2026 Markus Walloner
