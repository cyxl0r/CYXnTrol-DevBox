TODO LIST
=========

Document status: Active proof of concept and development state.

DevBox already has a functioning local launcher, a graphical main interface, modular structure views, master-data and documentation maintenance, documentation snapshots, local tool detection, a repository page, and initial building blocks for the DevBox-specific publication process.

The deskNode area is actively integrated into DevBox. Supervisor and daemon processes can be started and stopped from the GUI, and their console output is displayed in the deskNode log. The product version can be edited through master data. UX themes can be named, created, deleted, duplicated, renamed, and saved. Saving a theme refreshes the deskNode manufacturer database.

Symbol management now exists as an initial functional catalog interface. It manages deskNode device categories and consumer devices through selection menus and dialogs for creation, editing, and deletion. New devices receive one PNG source, stored under their record ID as symbol_source_<record_id>.png. After every successful catalog change, create_manufacturer_db.py is executed so mnfctr_db.r0b contains current theme, category, and device data.

The graphics-pack build is functional as a proof of concept. It creates multiple prepared consumer-graphics states from symbol sources and UX themes. Actual deskNode runtime integration, asset selection, language packages, and complete state logic are still being developed.

DevBox is not a finished end-user or release version. Interfaces, database migrations, product modules, publication workflows, document templates, and tests are continuously being revised. This documentation describes the current state and must be updated alongside functional changes.

First publication: 
Project start: 2026
Author / publisher: Markus Walloner

1. Project Context
------------------

Short Description:
DevBox is the local development hub of the CYXnTrol Development Platform. Its PySide6 interface brings together project structure, master data, documentation, local tools, product modules, repository preparation, and recurring development workflows.

DevBox is not an end-user product. It is an internal working environment in which technical requirements, data models, interfaces, build steps, and publication states are prepared, reviewed, and refined in a traceable manner.


Long Description:
DevBox connects tasks that would otherwise be distributed across individual scripts, folders, spreadsheets, console windows, and external programs. It manages central project and product data, provides documentation content, organizes global structure templates, detects local tools, and brings product-specific development functions together in one interface.

An active integrated product module is deskNode. Its page can start and stop the local supervisor and daemon, edit the product version from master data, maintain UX themes, and open symbol management. Themes are maintained through named records, RGBA colors, global font files, sizes, outline settings, and shape rules. After each successful theme change, the product-local deskNode manufacturer database is refreshed.

Symbol management is the central source for device categories and consumer symbols. Categories and devices can be created, edited, or deleted in the DevBox database. When a new consumer device is created, exactly one PNG source is accepted and stored in the global graphics directory as symbol_source_<record_id>.png, based on the stable record ID. The graphics-pack build creates pre-rendered variants for themes and states so the later deskNode runtime only has to select suitable assets.

DevBox operates locally in the project context. A launcher discovers the project root through the .root file, provides runtime data under AppData, checks external tools, and starts the GUI from a temporary working copy. The real project root remains the authoritative source for resources, databases, and function scripts. A single-instance mechanism prevents parallel DevBox windows and activates an existing instance on a repeated start request.

The project is developed through an AI-assisted iterative workflow. Functional requirements, process logic, data models, UX decisions, test cases, and acceptance decisions are directed by the project owner; implementation steps are created with AI-assisted tools, reviewed, and continuously refined.


2. Open Items
-------------

CURRENT TODO LIST

deskNode and UX themes
- Continue testing saving, migration, and refreshing of multiple UX themes under real GUI conditions.
- Ensure that every successful theme-save operation is considered complete only after mnfctr_db.r0b has been refreshed.
- Connect theme selection in the later deskNode runtime through stable record_id values rather than renameable theme names.
- Handle missing font files, invalid RGBA values, and corrupted theme records robustly.
- Define additional visual states for offline, warning, error, unknown devices, and consumption thresholds.

Symbol catalog
- Continue filling symbol management with real categories and consumer symbols.
- Create language packages for categories and devices using the automatically generated translation_key values.
- Define searching in the later deskNode symbol picker through localized names and search terms.
- Define how renamed category_key or device_key values are handled without breaking existing smart-plug assignments.
- Add PNG replacement for existing devices as a dedicated editing workflow.
- Define how deskNode stores consumer_device_id and optionally consumer_device_key in smart-plug assignments.

Graphics-pack build
- Test generated graphics packages with more symbols, more themes, and longer file names.
- Fully align the builder with record-ID-named symbol_source_<record_id>.png sources.
- Validate build output against expected numbers of themes, symbols, masks, and state files.
- Further secure cleanup, archiving, and installation of the final graphics package.
- Optionally develop an incremental build so a small change does not rebuild every asset.
- Extend error handling for missing symbol sources, Inkscape, GIMP, and unsupported SVG/PNG files.

Repository and publication
- Fully test the DevBox push-to-Git process in the GUI.
- Verify that applications/deskNode/resources/scripts is included completely and without __pycache__ content in the publication root.
- Verify repository URL and branch setup with a real remote repository.
- Further secure desired-versus-actual synchronization, protection rules, and removal of obsolete repository files.
- Continue to evaluate push success and temporary cleanup success separately.

Documentation and quality
- Update form texts when functionality changes.
- Have terms of use and privacy notices legally reviewed and adapted to actual data flows before public use.
- Test the PDF layout with different text lengths, page breaks, and special characters.
- Further standardize logging across all DevBox components.
- Verify multi-monitor behavior, single-instance focus, structure views, and deskNode views at different resolutions.
- Add automated tests for database migration, theme saving, symbol catalog, graphics builds, document export, snapshot structure, and repository synchronization.


3. Target State
---------------

Current functional scope:
- launch a single DevBox instance and activate an already running instance;
- provide a platform page with areas for the project platform, applications, development software, and product modules;
- detect and launch Inkscape and GIMP locally;
- launch installers for supported third-party tools when installers are present in the project;
- provide a central SQLite master database for umbrella, manufacturer, product, documentation, structure, repository, UX-theme, and deskNode symbol-catalog information;
- provide a structure workshop with navigation for umbrella data, product data, documentation, and the global app folder structure;
- initialize only completely empty product folders from the global structure template;
- export documentation snapshots and import fully revised German and English documentation content in a controlled manner;
- generate Markdown documents and PDF drafts for terms of use and privacy policies;
- provide a repository page with product selection, optional commit text, optional images, and log output;
- prepare a cleaned DevBox publication state in a temporary workspace;
- provide a deskNode tab for starting and stopping supervisor and daemon with live console output;
- edit the deskNode version and then refresh mnfctr_db.r0b;
- provide surface design with multiple named UX themes, RGBA colors, global font files, font formats, radii, and outlines;
- provide symbol management for device categories and consumer devices through selection menus and create, edit, and delete dialogs;
- automatically derive category and device keys as well as translation keys from user input;
- accept exactly one PNG source for a new consumer device and store it as symbol_source_<record_id>.png;
- refresh the deskNode manufacturer database after every successful change to a theme or symbol catalog;
- build a graphics package from symbol sources, UX themes, GIMP masks, Inkscape vectorization, and pre-rendered state variants.

Goals:
- repeatable development steps rather than manual one-off solutions;
- clear separation between DevBox master data, deskNode runtime data, temporary builds, and repository export;
- stable technical references for themes, categories, consumer devices, and assets;
- extensibility for additional CYXnTrol products without treating DevBox as an arbitrary script collection.


4. Technical Context
--------------------

DevBox is modular in structure.

The launch chain begins with a DevBox launcher. It discovers the project root through the .root file, provides local runtime data under AppData, checks stored tool paths, and starts the graphical interface from a temporary copy. The temporary copy reduces the risk that a running GUI locks or changes files in the actual project root.

The main GUI resides under resources/applications/devbox/functions and uses specialized subscripts for pages, layout, data access, process starts, and product modules. The graphical interface uses PySide6. It accesses graphics, fonts, database files, installers, and function scripts through the actual project root.

The central master-data source is resources/organization/devbox_db.r0b. It contains product data, repository fields, documentation fields, structure information, named deskNode UX themes, and the symbol-catalog tables desknode_consumer_device_categories and desknode_consumer_devices. For local runtime data, DevBox uses logfile.r0b and locdata.r0b under AppData.

deskNode additionally has applications/deskNode/data/mnfctr_db.r0b. It is recreated by create_manufacturer_db.py and contains master_data, ux_themes, consumer_device_categories, and consumer_devices. This keeps the deskNode runtime decoupled from the complete DevBox master database.

The graphics-pack build processes global symbol sources, scaling, masks, vectorization, and theme data in temporary work folders. Inkscape and GIMP are used as external local tools. The result is a compressed graphics package containing pre-rendered state variants that deskNode can later load.


DevBox currently uses the following technologies in particular:

- Python as the core language for launchers, process logic, data preparation, automation, and product-specific tools.
- PySide6 for the local graphical user interface.
- SQLite for central project master data, deskNode manufacturer data, and local runtime, log, and location data.
- openpyxl as a transitional or import tool for spreadsheets, not as the central master-data source.
- ReportLab and svglib for local generation of designed PDF documents.
- Git and Git Credential Manager for repository operations and authentication.
- Inkscape for scaling, SVG work, and vectorization of masks.
- GIMP 3 for non-interactive image processing and preparatory mask stages.
- XML/SVG processing through Python standard libraries for cleanup of generated masks.
- C# generation, the .NET SDK, WiX, and later additional packaging tools for build and installer processes.
- temporary workspaces under the system temporary directory for controlled copies, graphics builds, exports, and publication preparation.

The technical structure aims to clearly separate GUI, function scripts, subscripts, data sources, product databases, external tools, and temporary work states. The deskNode symbol catalog links SQLite records to PNG sources through stable record_id values, while the graphics-pack build creates the resulting visual variants.


Copyright (c) 2026 Markus Walloner
