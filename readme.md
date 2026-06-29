# README

## Short Description

DevBox is the local development hub of the CYXnTrol Development Platform. Its PySide6 interface brings together project structure, master data, documentation, local tools, product modules, repository preparation, and recurring development workflows.

DevBox is not an end-user product. It is an internal working environment in which technical requirements, data models, interfaces, build steps, and publication states are prepared, reviewed, and refined in a traceable manner.


## Long Description

DevBox connects tasks that would otherwise be distributed across individual scripts, folders, spreadsheets, console windows, and external programs. It manages central project and product data, provides documentation content, organizes global structure templates, detects local tools, and brings product-specific development functions together in one interface.

An active integrated product module is deskNode. Its page can start and stop the local supervisor and daemon, edit the product version from master data, maintain UX themes, and open symbol management. Themes are maintained through named records, RGBA colors, global font files, sizes, outline settings, and shape rules. After each successful theme change, the product-local deskNode manufacturer database is refreshed.

Symbol management is the central source for device categories and consumer symbols. Categories and devices can be created, edited, or deleted in the DevBox database. When a new consumer device is created, exactly one PNG source is accepted and stored in the global graphics directory as symbol_source_<record_id>.png, based on the stable record ID. The graphics-pack build creates pre-rendered variants for themes and states so the later deskNode runtime only has to select suitable assets.

DevBox operates locally in the project context. A launcher discovers the project root through the .root file, provides runtime data under AppData, checks external tools, and starts the GUI from a temporary working copy. The real project root remains the authoritative source for resources, databases, and function scripts. A single-instance mechanism prevents parallel DevBox windows and activates an existing instance on a repeated start request.

The project is developed through an AI-assisted iterative workflow. Functional requirements, process logic, data models, UX decisions, test cases, and acceptance decisions are directed by the project owner; implementation steps are created with AI-assisted tools, reviewed, and continuously refined.


## Purpose

DevBox is intended to turn recurring and error-prone development work into traceable local tools. This includes maintaining product and manufacturer data, structured documentation, prepared publication steps, integration of local creative applications, and controlled execution of product-specific development functions.

The application provides a shared working foundation for products of the CYXnTrol Development Platform. Instead of keeping workflows only as memory, folder conventions, or a collection of console commands, they are retained as data, scripts, GUI functions, and verifiable process chains.

For deskNode, DevBox additionally serves as a development and configuration interface for product versions, UX themes, device categories, consumer symbols, and prepared graphics packages. The later deskNode runtime is intended to receive reproducible data and pre-rendered assets from this process.


## Context

The CYXnTrol Development Platform emerged from practical development work involving many small tools, data states, graphics files, documents, and test workflows. As the number of products and functions grows, it is no longer sufficient to keep information only in individual files or in memory. A stable project root, traceable data sources, repeatable temporary workspaces, and clearly separated product modules are required.

DevBox is the response to this need. It provides a local development hub in which manufacturer and product data, documentation, global structure rules, external tools, repository preparation, and specialized product functions are brought together.

deskNode is the first product integrated as an active DevBox area. Its role is to manage and visualize smart plugs and their connected consumers. For those consumers, not only names but also categories, stable technical IDs, PNG sources, theme data, and pre-rendered graphical states are placed into a reproducible workflow. This removes the need to manually create symbol variants for every theme and state combination.


## Core Idea

The core idea of DevBox is that recurring development processes should not have to be reinvented each time. They should remain available as understandable tools, data structures, and workflows.

A single script can solve a specific task. Several scripts and products, however, need shared rules: a reliably discoverable project root, safe temporary workspaces, central master data, portable paths, traceable logs, separated runtime data, and an interface where functions remain discoverable.

A second key principle is the separation of design, source, and runtime. deskNode UX themes and the device and symbol catalog are maintained in DevBox, then transferred to the deskNode manufacturer database and used for builds. Product operation should use prepared, consistent data and assets without requiring the DevBox editor logic.


## Features and Goals

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


## Architecture Overview

DevBox is modular in structure.

The launch chain begins with a DevBox launcher. It discovers the project root through the .root file, provides local runtime data under AppData, checks stored tool paths, and starts the graphical interface from a temporary copy. The temporary copy reduces the risk that a running GUI locks or changes files in the actual project root.

The main GUI resides under resources/applications/devbox/functions and uses specialized subscripts for pages, layout, data access, process starts, and product modules. The graphical interface uses PySide6. It accesses graphics, fonts, database files, installers, and function scripts through the actual project root.

The central master-data source is resources/organization/devbox_db.r0b. It contains product data, repository fields, documentation fields, structure information, named deskNode UX themes, and the symbol-catalog tables desknode_consumer_device_categories and desknode_consumer_devices. For local runtime data, DevBox uses logfile.r0b and locdata.r0b under AppData.

deskNode additionally has applications/deskNode/data/mnfctr_db.r0b. It is recreated by create_manufacturer_db.py and contains master_data, ux_themes, consumer_device_categories, and consumer_devices. This keeps the deskNode runtime decoupled from the complete DevBox master database.

The graphics-pack build processes global symbol sources, scaling, masks, vectorization, and theme data in temporary work folders. Inkscape and GIMP are used as external local tools. The result is a compressed graphics package containing pre-rendered state variants that deskNode can later load.


## Project Status

Active proof of concept and development state.

DevBox already has a functioning local launcher, a graphical main interface, modular structure views, master-data and documentation maintenance, documentation snapshots, local tool detection, a repository page, and initial building blocks for the DevBox-specific publication process.

The deskNode area is actively integrated into DevBox. Supervisor and daemon processes can be started and stopped from the GUI, and their console output is displayed in the deskNode log. The product version can be edited through master data. UX themes can be named, created, deleted, duplicated, renamed, and saved. Saving a theme refreshes the deskNode manufacturer database.

Symbol management now exists as an initial functional catalog interface. It manages deskNode device categories and consumer devices through selection menus and dialogs for creation, editing, and deletion. New devices receive one PNG source, stored under their record ID as symbol_source_<record_id>.png. After every successful catalog change, create_manufacturer_db.py is executed so mnfctr_db.r0b contains current theme, category, and device data.

The graphics-pack build is functional as a proof of concept. It creates multiple prepared consumer-graphics states from symbol sources and UX themes. Actual deskNode runtime integration, asset selection, language packages, and complete state logic are still being developed.

DevBox is not a finished end-user or release version. Interfaces, database migrations, product modules, publication workflows, document templates, and tests are continuously being revised. This documentation describes the current state and must be updated alongside functional changes.


## Installation and Startup

DevBox is currently intended as a local Windows-oriented development environment.

Requirements for a development start:
- a complete CYXnTrol project root with a .root file containing project-root;
- a functioning Python installation for the development environment;
- the Python packages required for the GUI, in particular PySide6;
- ReportLab and svglib for PDF generation;
- optionally Git including Git Credential Manager for repository operations;
- optionally Inkscape and GIMP for graphics, mask, and asset-build functions;
- for deskNode, an existing applications/deskNode product folder with function, data, and resource files.

Startup is performed through the DevBox launcher or the resulting DevBox executable. The launcher finds the project root, provides local databases under AppData, checks external tool paths, and then starts the GUI. If a DevBox instance is already running, it is brought to the foreground instead of starting a second instance.

The deskNode buttons start product-specific scripts through python.exe. The graphics-pack build requires valid symbol_source_<record_id>.png files in the global resources/graphics directory. New sources are created through symbol management. The build additionally requires usable Inkscape and GIMP paths. A productive distribution path, portable edition, or installer package will later use separate packaging and signing processes.


## Configuration

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


## Technology

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


## Repository Note

The DevBox repository represents the CYXnTrol Development Platform itself, not a finished end-user product. It serves as a development record, a transparent work sample, and a foundation for maintaining the platform.

The published state is not copied directly from the productive project root. DevBox creates a separate cleaned root_dir state. It contains intended source code, documents, and assets, while local runtime data, temporary remnants, installers, unnecessary build output, and unpublished data remain outside the publication package.

The temporary publication root treats applications as a deliberate delivery window: the directory is cleaned first. It is then populated with applications/deskNode/resources/scripts and all contained files. __pycache__ directories as well as .pyc and .pyo files remain excluded. The real local product directory is not changed by this process.

DevBox is developed in an AI-assisted iterative workflow. Requirements, architecture, data models, UX decisions, test cases, and acceptance are directed by the project owner. Implementation is created with AI-assisted development tools and checked against defined functional requirements.


## License

This project is licensed under Zero-Clause BSD License 0BSD.

The complete license terms are included in the accompanying license file.

## Author / Publisher

Markus Walloner
Markus Walloner
Germany (DE)

Copyright (c) 2026 Markus Walloner
