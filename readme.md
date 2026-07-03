# README

## Short Description

DevBox is the local development hub of the CYXnTrol Development Platform. Its PySide6 interface brings together project structure, master data, documentation, local tools, product modules, repository preparation, and recurring development workflows.

With deskNode, an active product module is integrated: a local device and structure hub for smart plugs and connected loads. deskNode is extended through replaceable venmods for supported vendors and protocols.

DevBox is not an end-user product. It is an internal working environment in which requirements, data models, UX decisions, interfaces, builds, and publication states are prepared and reviewed in a traceable way.


## Long Description

DevBox combines work that would otherwise be scattered across individual scripts, folders, spreadsheets, console windows, and external applications. It manages central project and product data, provides documentation content, organizes global structure templates, detects local tools, and brings product-specific development functions together in one interface.

The first active product module is deskNode. deskNode is a local control and structure environment for smart plugs and connected loads. A supervisor starts a daemon; the daemon couples discovered venmods through a common contract and starts one worker per venmod. The current proof of concept contains local paths for Tapo, FRITZ!DECT, and Shelly. Devices are maintained in a global inventory database, while every worker writes only its own temporary runtime database. The daemon synchronizes confirmed live values, desired states, and device identities between the layers.

deskNode additionally organizes devices in independent building trees. Every building has a device pool as its complete building-wide overview and can contain spatial or functional structure members. A device can remain in a building pool and also be assigned to a room, area, desk, or other structure member. The graphical interface visualizes this structure, device and power values, and local switching states.

The DevBox page for deskNode starts and stops the supervisor and daemon, shows their console output, and maintains product versions, UX themes, and the symbol catalog. Themes are managed through named records, RGBA colors, global font files, sizes, outlines, and shape rules. Categories and consumer symbols are maintained through stable technical IDs and PNG sources. The graphics-pack build creates prepared variants for themes and states.

DevBox works locally in the project context. A launcher discovers the project root through the .root file, provides runtime data under AppData, checks external tools, and starts the GUI from a temporary working copy. The real project root remains the authoritative source for resources, databases, and function scripts. A single-instance mechanism prevents parallel DevBox windows and activates the already-open instance when started again.

The project is developed through an AI-assisted, iterative workflow. Requirements, process logic, data models, UX decisions, test cases, and acceptance are directed by the project owner; implementation steps are created, reviewed, and refined with AI-assisted development tools.


## Purpose

DevBox is intended to turn recurring and error-prone development work into traceable local tools. This includes maintaining product and manufacturer data, structured documentation, prepared publication steps, integration of local creative tools, and controlled execution of product-specific development functions.

The application provides a common working foundation for products of the CYXnTrol Development Platform. Instead of keeping workflows only as memory, folder convention, or a collection of console commands, they are retained as data, scripts, GUI functions, and verifiable process chains.

For deskNode, DevBox additionally serves as a development and configuration interface for product versions, UX themes, device categories, consumer symbols, language resources, and prepared graphics packages. The deskNode runtime is intended to receive reproducible data and prepared assets from this process. The venmod architecture should also allow new local device paths to be added without unnecessarily rebuilding the daemon or already working vendor paths.


## Context

The CYXnTrol Development Platform grew out of practical development work involving many small tools, data states, graphic files, documents, and test workflows. As the number of products and functions increases, it is no longer sufficient to keep information only in individual files or in memory. A stable project root, traceable data sources, repeatable temporary workspaces, and clearly separated product modules are needed.

DevBox is the response to this need. It acts as a local development center where manufacturer and product data, documentation, global structure rules, external tools, repository preparation, and specialized product functions are brought together.

deskNode is the first product integrated as its own active DevBox area. Its purpose is the local management, visualization, and switching of supported smart plugs. Tapo, FRITZ!DECT, and Shelly are not treated as special cases embedded directly into the interface; they are connected through venmods with a shared coupler and worker contract. Names, categories, stable technical IDs, PNG sources, theme data, and pre-rendered graphics states are brought into a reproducible workflow for connected loads.


## Core Idea

The core idea of DevBox is that recurring development processes should not have to be reinvented every time. They should remain available as understandable tools, data structures, and workflows.

A single script can solve one specific task. Multiple scripts and products, however, need shared rules: a determinable project root, safe temporary workspaces, central master data, portable paths, traceable logs, separated runtime data, and an interface where functions remain discoverable.

A second central principle is the separation of design, source, and runtime. deskNode UX themes, language resources, and device and symbol catalogs are maintained in DevBox and then transferred into product-specific data sets. During operation, deskNode separates global inventory, temporary venmod databases, and controlled worker communication. This should make it possible to add new device paths without uncontrolled mixing of existing vendor integrations or user data.


## Features and Goals

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


## Architecture Overview

DevBox is modular in structure.

The launch chain begins with a DevBox launcher. It discovers the project root through the .root file, provides local runtime data under AppData, checks stored tool paths, and starts the graphical interface from a temporary copy. The temporary copy reduces the risk that a running GUI locks or changes files in the real project root.

The main GUI resides under resources/applications/devbox/functions and uses specialized subscripts for pages, layout, data access, process starts, and product modules. The graphical interface uses PySide6. It accesses graphics, fonts, database files, installers, and function scripts through the actual project root.

The central master-data source is resources/organization/devbox_db.r0b. It contains product data, repository fields, documentation fields, structure information, named deskNode UX themes, and the symbol-catalog tables desknode_consumer_device_categories and desknode_consumer_devices. For local DevBox runtime data, the application uses logfile.r0b and locdata.r0b under AppData.

deskNode has its own derived product data under applications/deskNode/data, particularly mnfctr_db.r0b for manufacturer and theme data and lan.r0b for language resources. For every run, the supervisor creates a unique temporary context. The daemon couples available venmods through coupler.py, validates their contracts, provides a local worker-control hub, and starts one worker for each accepted venmod. Workers write only their own temporary venmod database. The daemon consolidates confirmed data in the global AppData database devices.r0b and logs resolved power values separately.

The current deskNode integration contains venmods for Tapo, FRITZ!DECT, and Shelly. During startup, the product GUI waits for the confirmed initial cycle of all coupled venmods and then shows the synchronized device inventory. Structure assignments, UX settings, and rendering remain separate from vendor-specific worker data.

The graphics-pack build processes global symbol sources, scaling, masks, vectorization, and theme data in temporary work folders. Inkscape and GIMP are used as external local tools. The result is a compressed graphics package with pre-rendered state variants that deskNode can load at runtime.


## Project Status

Active proof of concept and development state.

DevBox already has a functioning local launcher, a graphical main interface, modular structure views, master-data and documentation maintenance, documentation snapshots, local tool detection, a repository page, and initial building blocks for the DevBox-specific publication process.

The deskNode area is actively integrated into DevBox. Supervisor and daemon processes can be started and stopped from the GUI, and their console output is displayed in the deskNode log. The product version can be edited through master data. UX themes can be named, created, deleted, duplicated, renamed, and saved. Saving a theme refreshes the deskNode product data.

In the current proof of concept, deskNode has a coupled worker architecture. Tapo, FRITZ!DECT, and Shelly are discovered and monitored locally through their own venmods; supported devices process switching states and power values. The daemon synchronizes venmod data into a global device inventory, applies an initial safety read cycle, and opens the main interface only after the initial global synchronization. Structure management supports multiple building roots, one complete device pool per building, and additional additive assignments to rooms or other structure members.

Symbol management is available as a functional catalog interface. It manages deskNode device categories and consumer devices through selection menus and dialogs for creation, editing, and deletion. New devices receive one PNG source, stored under their record ID as symbol_source_<record_id>.png. After every successful catalog change, create_manufacturer_db.py is executed so mnfctr_db.r0b contains current theme, category, and device data.

The graphics-pack build is functional as a proof of concept. It creates prepared consumer-graphics states from symbol sources and UX themes. The current deskNode runtime already uses language, theme, and graphics data; asset selection, broader symbol coverage, and additional visual states are still being developed.

DevBox and deskNode are not finished end-user or release versions. Credential storage, long-term stability with larger device inventories, vendor-specific edge cases, testing, packaging, and cross-platform portability remain open development tasks.


## Installation and Startup

DevBox is currently intended as a local, Windows-oriented development environment.

Requirements for a development start:
- a complete CYXnTrol project root with a .root file whose content is project-root;
- a working Python installation for the development environment;
- Python packages required for the GUI, especially PySide6;
- ReportLab and svglib for PDF generation;
- optionally Git including Git Credential Manager for repository operations;
- optionally Inkscape and GIMP for graphics, masks, and asset-build functions;
- for deskNode, an existing applications/deskNode product directory with function, data, venmod, and resource files;
- for the Tapo venmod, a Python environment with python-kasa; for FRITZ!DECT and Shelly, reachable local devices or gateways on the same network.

Startup occurs through the DevBox launcher or a DevBox executable built from it. The launcher finds the project root, provides local databases under AppData, checks external tool paths, and then starts the GUI. If a DevBox instance is already open, it is brought to the foreground instead of opening a second instance.

deskNode controls start product-specific scripts through python.exe. The deskNode supervisor creates a temporary runtime context for every run and starts the daemon. The daemon couples available venmods. For devices that require login, the deskNode GUI requests local credentials and waits for vendor-specific validation. The main interface appears after the confirmed initial cycle and global synchronization.

For the graphics-pack build, valid symbol_source_<record_id>.png files must exist in the global resources/graphics folder. New sources are created through symbol management. The build also requires usable Inkscape and GIMP paths. A productive distribution, portable edition, or installer package will require separate packaging and signing processes later.


## Configuration

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


## Technology

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


## Repository Note

The DevBox repository represents the CYXnTrol Development Platform itself, not a finished end-user product. It serves as a development state, transparent work sample, and foundation for maintaining the platform.

The published state is not copied directly from the productive project root. DevBox generates a separate cleaned root_dir state. It contains intended source code, documents, and assets, while local runtime data, temporary leftovers, installers, database WAL files, and unpublished data remain outside the publication package.

The current DevBox push treats applications as a deliberate delivery window: the area is cleaned first. Afterwards, applications/deskNode/resources/scripts including contained files are copied into the publication state. __pycache__ folders and .pyc and .pyo files remain excluded. This current scope is a DevBox-specific publication process and not yet a complete deskNode product release. Before deskNode including GUI, logic, and venmods is published as its own repository or release, its export scope must be explicitly defined and tested.

DevBox is developed through an AI-assisted, iterative workflow. Requirements, architecture, data models, UX decisions, test cases, and acceptance are directed by the project owner. Implementation is created with AI-assisted development tools and checked against defined functional requirements.


## License

This project is licensed under Zero-Clause BSD License 0BSD.

The complete license terms are included in the accompanying license file.

## Author / Publisher

Markus Walloner
Markus Walloner
Germany (DE)

Copyright (c) 2026 Markus Walloner
