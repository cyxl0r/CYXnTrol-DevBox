ARCHITECTURE DOCUMENTATION
==========================

Document status: Active proof of concept and development state.

DevBox already has a functioning local launcher, a graphical main interface, modular structure views, master-data and documentation maintenance, documentation snapshots, local tool detection, a repository page, and initial building blocks for the DevBox-specific publication process.

The deskNode area is actively integrated into DevBox. Supervisor and daemon processes can be started and stopped from the GUI, and their console output is displayed in the deskNode log. The product version can be edited through master data. UX themes can be named, created, deleted, duplicated, renamed, and saved. Saving a theme refreshes the deskNode product data.

In the current proof of concept, deskNode has a coupled worker architecture. Tapo, FRITZ!DECT, and Shelly are discovered and monitored locally through their own venmods; supported devices process switching states and power values. The daemon synchronizes venmod data into a global device inventory, applies an initial safety read cycle, and opens the main interface only after the initial global synchronization. Structure management supports multiple building roots, one complete device pool per building, and additional additive assignments to rooms or other structure members.

Symbol management is available as a functional catalog interface. It manages deskNode device categories and consumer devices through selection menus and dialogs for creation, editing, and deletion. New devices receive one PNG source, stored under their record ID as symbol_source_<record_id>.png. After every successful catalog change, create_manufacturer_db.py is executed so mnfctr_db.r0b contains current theme, category, and device data.

The graphics-pack build is functional as a proof of concept. It creates prepared consumer-graphics states from symbol sources and UX themes. The current deskNode runtime already uses language, theme, and graphics data; asset selection, broader symbol coverage, and additional visual states are still being developed.

DevBox and deskNode are not finished end-user or release versions. Credential storage, long-term stability with larger device inventories, vendor-specific edge cases, testing, packaging, and cross-platform portability remain open development tasks.

First publication: 
Project start: 2026
Author / publisher: Markus Walloner
Country: Germany (DE)

1. Overview
-----------

DevBox is the local development hub of the CYXnTrol Development Platform. Its PySide6 interface brings together project structure, master data, documentation, local tools, product modules, repository preparation, and recurring development workflows.

With deskNode, an active product module is integrated: a local device and structure hub for smart plugs and connected loads. deskNode is extended through replaceable venmods for supported vendors and protocols.

DevBox is not an end-user product. It is an internal working environment in which requirements, data models, UX decisions, interfaces, builds, and publication states are prepared and reviewed in a traceable way.


2. Architecture Overview
------------------------

DevBox is modular in structure.

The launch chain begins with a DevBox launcher. It discovers the project root through the .root file, provides local runtime data under AppData, checks stored tool paths, and starts the graphical interface from a temporary copy. The temporary copy reduces the risk that a running GUI locks or changes files in the real project root.

The main GUI resides under resources/applications/devbox/functions and uses specialized subscripts for pages, layout, data access, process starts, and product modules. The graphical interface uses PySide6. It accesses graphics, fonts, database files, installers, and function scripts through the actual project root.

The central master-data source is resources/organization/devbox_db.r0b. It contains product data, repository fields, documentation fields, structure information, named deskNode UX themes, and the symbol-catalog tables desknode_consumer_device_categories and desknode_consumer_devices. For local DevBox runtime data, the application uses logfile.r0b and locdata.r0b under AppData.

deskNode has its own derived product data under applications/deskNode/data, particularly mnfctr_db.r0b for manufacturer and theme data and lan.r0b for language resources. For every run, the supervisor creates a unique temporary context. The daemon couples available venmods through coupler.py, validates their contracts, provides a local worker-control hub, and starts one worker for each accepted venmod. Workers write only their own temporary venmod database. The daemon consolidates confirmed data in the global AppData database devices.r0b and logs resolved power values separately.

The current deskNode integration contains venmods for Tapo, FRITZ!DECT, and Shelly. During startup, the product GUI waits for the confirmed initial cycle of all coupled venmods and then shows the synchronized device inventory. Structure assignments, UX settings, and rendering remain separate from vendor-specific worker data.

The graphics-pack build processes global symbol sources, scaling, masks, vectorization, and theme data in temporary work folders. Inkscape and GIMP are used as external local tools. The result is a compressed graphics package with pre-rendered state variants that deskNode can load at runtime.


3. Detailed Architecture
------------------------

DEVBOX ARCHITECTURE

1. System boundary
DevBox is a local, Windows-oriented development environment inside the CYXnTrol project root. It does not provide a general cloud platform or a built-in multi-user service. External services are used only when the user explicitly connects them through external tools or a repository push. In the current proof of concept, deskNode communicates with supported devices through the local network and does not operate its own cloud service.

2. Startup and instance layer
The DevBox launcher determines the project root through .root. It checks runtime requirements, creates local AppData structures, initializes or checks logfile.r0b and locdata.r0b, detects external tools, and prevents parallel GUI instances. If an instance is already open, it is activated. The GUI starts from a temporary copy.

3. GUI and module layer
The main GUI is based on PySide6. It contains development-platform, structure, repository, and product-specific pages. deskNode is integrated as its own tab. It bundles product starts, log output, version editing, interface design, and symbol management. The graphics-pack build is started from symbol management because relevant categories, consumer devices, and PNG sources are maintained there.

4. Central data layer
Devbox_db.r0b is the central master database in the project. It contains manufacturer, product, documentation, structure, and repository data. The ux-deskNode table manages multiple named UX themes with stable record_id values. The desknode_consumer_device_categories and desknode_consumer_devices tables manage the deskNode symbol catalog. logfile.r0b and locdata.r0b are stored separately under AppData and contain runtime information and local tool paths.

5. deskNode product-data layer
deskNode receives derived product data: mnfctr_db.r0b contains master_data, UX themes, and category and device data; lan.r0b contains the language package. fonts.r0b and graphic_items.r0b are runtime archives. settings.r0b, devices.r0b, and log_device_power.r0b are located in the deskNode AppData area. The GUI keeps language and theme separate from manufacturer data, while devices.r0b manages global inventory, desired and actual states, presentation, and additive structure assignments.

6. deskNode runtime layer
The deskNode supervisor creates a unique temporary context for each run and starts the daemon. The daemon finds coupler.py files under venmod, validates the respective coupling contracts, merges the global device structure, and starts one worker per accepted venmod. A local worker-control hub handles commands and events. Every worker writes only its own temporary SQLite database. The daemon mirrors confirmed data into devices.r0b and records resolved power values in log_device_power.r0b.

7. Venmod layer
Tapo, FRITZ!DECT, and Shelly are connected as separate venmods. Tapo uses the local python-kasa path. FRITZ!DECT uses a FRITZ!Box and its local AHA interface. Shelly uses the local RPC path for supported switch channels. Vendor paths follow the same outer coupler, worker, and synchronization contract while keeping their specific discovery, authentication, and monitoring logic separate. A venmod must not write the global device inventory directly.

8. Safety and synchronization principle
At the beginning of a new daemon run, old global desired and actual states are reset safely. Venmods first read the real state and report their initial cycle. The main GUI leaves the loading screen only after all coupled venmods have completed and their data has been mirrored globally. Explicit switching requests use desired states, vendor-specific execution, and confirmed read-back. The central live-value logic cushions short monitor failures so individual faulty samples do not immediately create offline states.

9. Device and structure layer
An installation contains at least one building. Multiple independent building roots are possible. Every building has a fixed device pool as a complete overview; a device can belong to the pool and additionally to a room, area, desk, rack, or another structure member. The tree view shows spatial or functional structure members; the device pool acts as a separate overall access point for the relevant building.

10. Symbol catalog and graphics-build layer
A category has record_id, category_key, translation_key, and timestamps. A consumer device has record_id, device_key, category_id, translation_key, and timestamps. category_id refers to the stable category record_id. When a new device is created, exactly one PNG is accepted and stored as resources/graphics/symbol_source_<record_id>.png. graphic_items_bulder.py processes these sources in a temporary workspace, creates masks, theme and state variants, and provides the graphics package for deskNode.

11. Documentation and publication layer
doc_forms.r0b contains form templates. A document process unpacks them, fills them from language-specific tables, creates Markdown and PDF files, and moves them into a controlled export structure. For DevBox, a temporary root_dir is generated as the desired state for repository synchronization. The current DevBox publication state deliberately contains applications/deskNode/resources/scripts including subfolders, but excludes __pycache__ folders and Python bytecode.

12. Known security boundary
Current credential handling is a development state and not yet a cross-platform encrypted vault. Credentials must not be logged; the planned shared vault component is required before productive or public use. DevBox separates original files, temporary processing, derived product databases, and publication state so heavy operations do not work uncontrolled on the real project root.


4. Features and Goals
---------------------

Current functional scope:
- Start of a single DevBox instance and activation of an already-running instance.
- Platform page with areas for the project platform, applications, development software, and product modules.
- Local detection and launch capability for Inkscape and GIMP as well as explicit launch of available third-party installers.
- Central SQLite master database for roof, manufacturer, product, documentation, structure, repository, UX-theme, and deskNode symbol-catalog data.
- Structure workshop with navigation for roof data, product data, documentation, and global app-folder structure.
- Initialization of only completely empty product folders from the global structure template.
- Export of documentation snapshots and controlled import of completely revised German and English documentation.
- Generation of Markdown documents and PDF drafts for terms of use and privacy notices.
- Repository page with product selection, optional commit text, optional images, and log output.
- Preparation of a cleaned DevBox publication state in a temporary workspace.
- deskNode tab for starting and stopping the supervisor and daemon with live console output.
- Editing of the deskNode version and refresh of derived product databases.
- Interface design with multiple named UX themes, RGBA colors, global font files, font formats, radii, and outlines.
- Symbol management for device categories and consumer devices with stable record_id, category_key, and device_key references.
- Acceptance of one PNG source for new consumer devices and storage as symbol_source_<record_id>.png.
- Graphics-pack build from symbol sources, UX themes, GIMP masks, Inkscape vectorization, and prepared state variants.
- deskNode proof of concept with supervisor, daemon, separate venmod workers, global device inventory, power-value logging, and local device paths for Tapo, FRITZ!DECT, and Shelly.
- deskNode structure with multiple independent building trees, building device pools, and additive device assignments.

Goals:
- repeatable development steps instead of manual one-off solutions;
- clear separation between DevBox master data, deskNode runtime data, venmod data, temporary builds, and repository export;
- stable technical references for themes, languages, categories, consumer devices, and assets;
- local device integration without a deskNode-operated cloud service;
- extensibility for further CYXnTrol products and venmods without turning DevBox into an arbitrary script collection.


5. Configuration
----------------

Configuration is separated into several layers.

Project root:
The project root is found through the .root file. It is the authoritative source for scripts, resources, form archives, installers, global fonts, and the central DevBox database.

Central DevBox master data:
resources/organization/devbox_db.r0b contains manufacturer, product, documentation, structure, repository, UX-theme, and symbol-catalog information. The ux-deskNode table contains named theme records with record_id and theme_name. The desknode_consumer_device_categories and desknode_consumer_devices tables contain persistent technical categories and consumer devices. Schema extensions should retain existing records and add missing fields through migration.

deskNode product data:
applications/deskNode/data/mnfctr_db.r0b contains master_data, ux_themes, consumer_device_categories, and consumer_devices. applications/deskNode/data/lan.r0b contains the language_package. fonts.r0b and graphic_items.r0b are product archives for runtime use. create_manufacturer_db.py refreshes the derived manufacturer database after successful version, theme, category, or consumer-device changes.

deskNode AppData and runtime:
The local AppData path is built from master_data, currently typically %APPDATA%/CYXLabs/CYXnTrol/deskNode. settings.r0b stores the selected UI language and active UX theme as well as runtime information needed by the supervisor. devices.r0b contains the global device inventory and additive structure assignments. log_device_power.r0b logs resolved power values. Every active daemon run also has a unique temporary folder containing runtime_state.r0b and separate temporary venmod databases.

Device structure:
A fresh installation receives at least one building root. Every building has an internal, fixed device pool as its complete building-wide overview. Devices can remain in the pool and also be assigned to spatial or functional members. Structure management supports multiple independent building roots.

Venmods:
A venmod is found through coupler.py and must report a valid coupling contract. This describes its name, worker start, temporary database, device table, and upstream and downstream column mappings. The daemon validates these values before starting a worker. Tapo, FRITZ!DECT, and Shelly are the currently integrated local paths.

Credentials and security status:
Credentials are required only by vendor paths that need login. They are not written to logs. The current proof of concept does not yet have a cross-platform encrypted credential vault; locally persisted development data must therefore not be treated as a hardened secret store. The planned vault solution is intended as a shared platform component rather than a venmod-specific special case.

Interface design:
Colors are stored as eight-digit RGBA hexadecimal values without #, for example 00e4ffff. Font files are read recursively from resources/fonts and stored as project-root-relative paths. Font roles include large headlines, section headlines, body text, button text, input text, status messages, and log text. Further theme values cover font sizes, font styles, underlining, outlines, radii, and state colors.

Tool detection and repository data:
Stored paths are checked at startup. Invalid Inkscape or GIMP paths are searched again. Repository URL and branch are maintained per product in product_credentials. Git credentials are not stored in DevBox. For a DevBox push, a temporary publication root is created; the current export scope is defined by the controlled push process.


6. Technology
-------------

DevBox currently uses the following technologies in particular:

- Python as the core language for launchers, process logic, data preparation, automation, and product-specific tools.
- PySide6 for the local graphical interfaces of DevBox and deskNode.
- SQLite for central project master data, deskNode product data, and local runtime, device, settings, language, and log data.
- python-kasa for local Tapo discovery and device communication in the Tapo venmod.
- Local HTTP, XML, and RPC communication for FRITZ!DECT/AHA and Shelly paths where implemented by the respective venmod.
- A local worker-control hub and separate worker processes for venmod integration.
- openpyxl as a transitional or import tool for spreadsheets, not as the central master-data source.
- ReportLab and svglib for local generation of designed PDF documents.
- Git and Git Credential Manager for repository operations and authentication.
- Inkscape for scaling, SVG work, and vectorization of masks.
- GIMP 3 for non-interactive image processing and preparatory mask stages.
- XML/SVG processing through Python standard libraries for cleanup of generated masks.
- C# generation, the .NET SDK, WiX, and later additional packaging tools for build and installer processes.
- temporary workspaces under the system temporary directory for controlled copies, graphics builds, exports, daemon runtimes, and publication preparation.

The technical structure aims to clearly separate GUI, function scripts, subscripts, data sources, product databases, external tools, global device storage, and venmod-specific runtime. The deskNode symbol catalog links SQLite records to PNG sources through stable record_id values, while the graphics-pack build creates the resulting visual variants.


7. Repository Note
------------------

The DevBox repository represents the CYXnTrol Development Platform itself, not a finished end-user product. It serves as a development state, transparent work sample, and foundation for maintaining the platform.

The published state is not copied directly from the productive project root. DevBox generates a separate cleaned root_dir state. It contains intended source code, documents, and assets, while local runtime data, temporary leftovers, installers, database WAL files, and unpublished data remain outside the publication package.

The current DevBox push treats applications as a deliberate delivery window: the area is cleaned first. Afterwards, applications/deskNode/resources/scripts including contained files are copied into the publication state. __pycache__ folders and .pyc and .pyo files remain excluded. This current scope is a DevBox-specific publication process and not yet a complete deskNode product release. Before deskNode including GUI, logic, and venmods is published as its own repository or release, its export scope must be explicitly defined and tested.

DevBox is developed through an AI-assisted, iterative workflow. Requirements, architecture, data models, UX decisions, test cases, and acceptance are directed by the project owner. Implementation is created with AI-assisted development tools and checked against defined functional requirements.


Copyright (c) 2026 Markus Walloner
