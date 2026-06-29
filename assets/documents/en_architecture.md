ARCHITECTURE DOCUMENTATION
==========================

Document status: Active proof of concept and development state.

DevBox already has a functioning local launcher, a graphical main interface, modular structure views, master-data and documentation maintenance, documentation snapshots, local tool detection, a repository page, and initial building blocks for the DevBox-specific publication process.

The deskNode area is actively integrated into DevBox. Supervisor and daemon processes can be started and stopped from the GUI, and their console output is displayed in the deskNode log. The product version can be edited through master data. UX themes can be named, created, deleted, duplicated, renamed, and saved. Saving a theme refreshes the deskNode manufacturer database.

Symbol management now exists as an initial functional catalog interface. It manages deskNode device categories and consumer devices through selection menus and dialogs for creation, editing, and deletion. New devices receive one PNG source, stored under their record ID as symbol_source_<record_id>.png. After every successful catalog change, create_manufacturer_db.py is executed so mnfctr_db.r0b contains current theme, category, and device data.

The graphics-pack build is functional as a proof of concept. It creates multiple prepared consumer-graphics states from symbol sources and UX themes. Actual deskNode runtime integration, asset selection, language packages, and complete state logic are still being developed.

DevBox is not a finished end-user or release version. Interfaces, database migrations, product modules, publication workflows, document templates, and tests are continuously being revised. This documentation describes the current state and must be updated alongside functional changes.

First publication: 
Project start: 2026
Author / publisher: Markus Walloner
Country: Germany (DE)

1. Overview
-----------

DevBox is the local development hub of the CYXnTrol Development Platform. Its PySide6 interface brings together project structure, master data, documentation, local tools, product modules, repository preparation, and recurring development workflows.

DevBox is not an end-user product. It is an internal working environment in which technical requirements, data models, interfaces, build steps, and publication states are prepared, reviewed, and refined in a traceable manner.


2. Architecture Overview
------------------------

DevBox is modular in structure.

The launch chain begins with a DevBox launcher. It discovers the project root through the .root file, provides local runtime data under AppData, checks stored tool paths, and starts the graphical interface from a temporary copy. The temporary copy reduces the risk that a running GUI locks or changes files in the actual project root.

The main GUI resides under resources/applications/devbox/functions and uses specialized subscripts for pages, layout, data access, process starts, and product modules. The graphical interface uses PySide6. It accesses graphics, fonts, database files, installers, and function scripts through the actual project root.

The central master-data source is resources/organization/devbox_db.r0b. It contains product data, repository fields, documentation fields, structure information, named deskNode UX themes, and the symbol-catalog tables desknode_consumer_device_categories and desknode_consumer_devices. For local runtime data, DevBox uses logfile.r0b and locdata.r0b under AppData.

deskNode additionally has applications/deskNode/data/mnfctr_db.r0b. It is recreated by create_manufacturer_db.py and contains master_data, ux_themes, consumer_device_categories, and consumer_devices. This keeps the deskNode runtime decoupled from the complete DevBox master database.

The graphics-pack build processes global symbol sources, scaling, masks, vectorization, and theme data in temporary work folders. Inkscape and GIMP are used as external local tools. The result is a compressed graphics package containing pre-rendered state variants that deskNode can later load.


3. Detailed Architecture
------------------------

DEVBOX ARCHITECTURE

1. System boundary
DevBox is a local Windows-oriented development environment within the CYXnTrol project root. It does not provide a general cloud platform or an embedded multi-user service. External services are used only when the user explicitly connects them through external tools or a repository push.

2. Launch and instance layer
The DevBox launcher discovers the project root through .root. It checks runtime requirements, creates local AppData structures, initializes or checks logfile.r0b and locdata.r0b, detects external tools, and prevents parallel GUI instances. If an instance is already open, it is activated. The GUI is started from a temporary copy.

3. GUI and module layer
The main GUI is based on PySide6. It contains development-platform, structure, repository, and product-specific pages. deskNode is integrated as its own tab. It combines product starts, log output, version editing, surface design, and symbol management. The graphics-pack build is started from symbol management because that is also where the relevant categories, consumer devices, and PNG sources are maintained.

4. Central data layer
devbox_db.r0b is the central master database in the project. It contains manufacturer, product, documentation, structure, and repository data. The "ux-deskNode" table manages multiple named UX themes with stable record_id values. The desknode_consumer_device_categories and desknode_consumer_devices tables manage the deskNode symbol catalog. logfile.r0b and locdata.r0b are kept separately under AppData and hold runtime information and local tool paths.

5. Symbol-catalog layer
A category has record_id, category_key, translation_key, and timestamps. A consumer device has record_id, device_key, category_id, translation_key, and timestamps. category_id points to the stable record_id of the category. When a new device is created, exactly one PNG is accepted and stored as resources/graphics/symbol_source_<record_id>.png. Source file names therefore contain no category hierarchy and remain stable through the technical ID.

6. deskNode product data layer
deskNode receives a derived manufacturer database named mnfctr_db.r0b. create_manufacturer_db.py creates master_data and copies from devbox_db.r0b the tables ux-deskNode as ux_themes, desknode_consumer_device_categories as consumer_device_categories, and desknode_consumer_devices as consumer_devices. Every successful change to version, UX theme, or symbol catalog must trigger this update after the database commit.

7. Graphics build layer
graphic_items_bulder.py processes symbol sources in a temporary workspace. It copies source graphics, scales and centers them, creates contrast masks in GIMP, vectorizes them with Inkscape, cleans the resulting SVG files, and generates multiple glow and state variants for every UX theme. The final files are provided as a graphics package for deskNode.

8. Documentation and publication layer
doc_forms.r0b contains form templates. A documentation process unpacks them, fills them from language-dependent tables, generates Markdown and PDF files, and moves the results into a controlled export structure. For DevBox, a temporary root_dir is generated as the desired state for repository synchronization. The publication state deliberately includes applications/deskNode/resources/scripts and its files, while excluding __pycache__ directories and Python bytecode.

9. Integration points and security principle
Git and Git Credential Manager handle repository authentication. Inkscape and GIMP are treated as external local programs. ReportLab and svglib support PDF generation. DevBox separates original state, temporary processing, derived product databases, and publication state so complex operations do not run uncontrolled on the real project root.


4. Features and Goals
---------------------

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


5. Configuration
----------------

Configuration is separated into several layers.

Project root:
The project root is discovered through the .root file. It is the authoritative source for scripts, resources, form archives, installers, global fonts, and the central DevBox database.

Central master data:
resources/organization/devbox_db.r0b contains manufacturer, product, documentation, structure, repository, UX-theme, and symbol-catalog information. The "ux-deskNode" table contains multiple named theme records with record_id and theme_name. The desknode_consumer_device_categories and desknode_consumer_devices tables contain permanent technical categories and consumer devices. Schema extensions are intended to preserve existing records and add missing fields through migration.

Symbol catalog:
Categories are maintained through category_key and an automatically derived translation_key. Devices are maintained through device_key, category_id, and an automatically derived translation_key. When a device is created, one PNG is selected or dropped and copied to resources/graphics/symbol_source_<record_id>.png. Category association is stored through category_id, not through a file name.

deskNode runtime data:
applications/deskNode/data/mnfctr_db.r0b is recreated by create_manufacturer_db.py. It contains master_data, ux_themes, consumer_device_categories, and consumer_devices. This refresh is executed after every successful change to version, theme, category, or consumer device.

Surface design:
Colors are stored as eight-character RGBA hexadecimal values without #, for example 00e4ffff. Font files are read recursively from resources/fonts and stored as project-root-relative paths. Font roles include large headings, section headings, body text, button text, input text, status messages, and log text. Additional theme values cover font size, font style, underlining, outlines, radii, and state colors.

Local runtime data:
%appdata%/CYXLabs/CYXnTrol/DevBox/logfile.r0b contains log data.
%appdata%/CYXLabs/CYXnTrol/DevBox/locdata.r0b contains verified paths for Inkscape and GIMP.

Tool detection:
Stored paths are checked at startup. Invalid paths are searched again, first under Program Files and then in the system temporary area. Missing tools limit only the related functions.

Repository data:
Repository URL and branch are maintained per product in product_credentials. Git credentials are not stored in DevBox. For the DevBox push, a temporary publication root is created; its applications directory is cleaned and then selectively filled with applications/deskNode/resources/scripts without __pycache__ content.


6. Technology
-------------

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


7. Repository Note
------------------

The DevBox repository represents the CYXnTrol Development Platform itself, not a finished end-user product. It serves as a development record, a transparent work sample, and a foundation for maintaining the platform.

The published state is not copied directly from the productive project root. DevBox creates a separate cleaned root_dir state. It contains intended source code, documents, and assets, while local runtime data, temporary remnants, installers, unnecessary build output, and unpublished data remain outside the publication package.

The temporary publication root treats applications as a deliberate delivery window: the directory is cleaned first. It is then populated with applications/deskNode/resources/scripts and all contained files. __pycache__ directories as well as .pyc and .pyo files remain excluded. The real local product directory is not changed by this process.

DevBox is developed in an AI-assisted iterative workflow. Requirements, architecture, data models, UX decisions, test cases, and acceptance are directed by the project owner. Implementation is created with AI-assisted development tools and checked against defined functional requirements.


Copyright (c) 2026 Markus Walloner
