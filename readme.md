# README

## Short Description

DevBox is the local development hub of the CYXnTrol Development Platform. It brings together recurring work around project structure, master data, documentation, build tools, external creative applications, and repository maintenance in a PySide6 interface.

DevBox is not an end-user product. It is an internal work environment for preparing, maintaining, and structuring development workflows for later publication.


## Long Description

DevBox combines development tasks that would otherwise be spread across individual scripts, folders, tables, console windows, and external applications. Its interface provides platform data, manages product and documentation content, prepares structured documents, and offers tools for maintaining a controlled development state.

The application operates locally in the project context. A launcher discovers the project root through the .root file, creates a temporary working copy for the GUI, and starts the graphical interface in a controlled manner. The actual project root remains the authoritative source for resources, databases, and tools. DevBox prevents parallel GUI instances and brings an existing instance to the foreground when it is started again.

In addition to the structure workshop, DevBox contains a repository page. There, a prepared publication state for DevBox itself can be generated. That state is created in a temporary workspace, cleaned of non-public runtime, installer, and local data, enriched with maintained documentation, and then connected to the configured repository. This special process currently applies only to DevBox; later products will receive their own suitable publication schemes.

DevBox also detects local installation locations of Inkscape and GIMP, stores those locations in a local SQLite file, and provides launch buttons for available applications. Missing locations are checked again at startup. This brings the platform’s own data, scripts, and tools together in one locally traceable development environment.


## Purpose

DevBox is intended to bring together, standardize, and make visible recurring and error-prone development work. Instead of retaining important workflows only as memory, loose folder conventions, or isolated scripts, the platform records them in a structured form.

The application is intended in particular to:
- maintain platform and product master data centrally;
- manage documentation content in German and English;
- generate forms, Markdown files, and PDF documents from maintained data;
- visualize and edit the real project folder structure in a controlled way;
- detect, install, and launch required development tools;
- prepare cleaned and documented repository states;
- log development decisions, states, and errors locally in a traceable manner.

DevBox is not meant to hide routine work but to turn it into reliable building blocks. The goal is not a rigid all-in-one product, but a growing development hub that evolves alongside the products and services created from it.


## Context

The CYXnTrol Development Platform emerged from practical development work. Small helper scripts could solve individual tasks, but they also had to be organized, updated, and kept traceable. As the number of scripts, data sources, documents, test states, and planned products grew, it became clear that the development environment itself needed a structure.

DevBox is the visible control center of that structure. It connects local SQLite master data, PySide6 interfaces, documentation forms, folder structures, build-related tools, and later repository processes. The platform deliberately remains locally oriented: the development state belongs to the user, resides in the project root or local AppData, and is not automatically transferred to a cloud service.

The application is developed within the CYXLabs umbrella and the CYXnTrol Development Platform. It serves as a work tool, as a pattern for further development platforms, and as a traceable portfolio example for modular software development.


## Core Idea

DevBox is based on one core idea: recurring development processes should not have to be reinvented every time. They should be retained as understandable tools, data structures, and workflows.

A single script can solve a specific task. Several scripts, however, need common rules: they need a project root, safe temporary workspaces, traceable data sources, consistent file names, error logs, and an interface in which their functions remain discoverable. DevBox provides that shared layer.

This leads to an important principle: the real project root remains protected. Operations involving restructuring, documentation export, cleanup, or repository preparation work with temporary copies. Only a successfully prepared state is passed on as a publication candidate. This keeps the development state and the published state clearly separate.


## Features and Goals

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


## Architecture Overview

DevBox is modular in structure.

The launch chain begins with a DevBox launcher. It discovers the project root through the .root file, provides local runtime data under AppData, checks stored tool paths, and starts the graphical interface from a temporary copy. The temporary copy reduces the risk that a running GUI locks or changes files in the actual project root.

The main GUI resides in the functions area and uses several subscripts for pages, layout, data access, and specialized functions. The graphical interface uses PySide6. It accesses resources such as graphics, fonts, database files, installers, and function scripts through the actual project root.

The central master-data source is the SQLite file devbox_db.r0b under resources/organization. It contains, among other things, product data, repository fields, documentation fields, and structure information. For local runtime data, DevBox uses separate SQLite files under AppData: logfile.r0b for logs and locdata.r0b for verified paths to external tools.

Documentation forms are stored compressed in doc_forms.r0b. During an export, they are unpacked into a temporary docs folder, populated with data from the SQLite database, and then transferred as Markdown files, PDF documents, and repository-ready assets into a prepared root_dir state. That root_dir serves as the controlled desired state for DevBox repository maintenance.


## Project Status

Active proof of concept and development state.

DevBox already has a functioning local launcher, a graphical main interface, modular structure views, master-data and documentation maintenance, documentation snapshots, form imports, local tool detection, a repository page, and initial building blocks for the DevBox-specific repository process.

The application is not yet a finished end-user or release version. Interfaces, publication workflows, document templates, repository synchronization, and individual development modules are being revised continuously. The current documentation describes the present development state and must be maintained alongside functional changes.


## Installation and Startup

DevBox is currently intended as a local development environment for Windows.

Requirements for a development start:
- a complete CYXnTrol project root with a .root file containing project-root;
- a functioning Python installation for the development environment;
- the Python packages required for the GUI, in particular PySide6;
- the reportlab and svglib Python packages for PDF generation;
- optionally Git including Git Credential Manager for repository operations;
- optionally Inkscape and GIMP for the related tool functions.

Startup is performed through the DevBox launcher or the resulting DevBox executable. The launcher finds the project root, provides the required local databases under AppData, checks external tool paths, and then starts the GUI. If a DevBox instance is already running, it is brought to the foreground instead of starting a second instance.

A productive distribution path, portable edition, or installer package will later use separate packaging and signing processes.


## Configuration

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


## Technology

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


## Repository Note

The DevBox repository represents the CYXnTrol Development Platform itself, not a finished end-user product. It serves as a development state, a traceable work sample, and a foundation for maintaining the platform.

The repository state is not copied directly from the productive project root. For DevBox, a separate cleaned root_dir state is generated. It receives the intended source code, documents, and assets, keeps local databases, temporary remnants, unnecessary build outputs, font files, and installation artifacts outside the publication package, and can then be synchronized with the DevBox repository.

Products, services, or works created from the platform are intended to receive separate repositories. Their publication schemes will be developed separately from the DevBox special logic.


## License

This project is licensed under Zero-Clause BSD License 0BSD.

The complete license terms are included in the accompanying license file.

## Author / Publisher

Markus Walloner
Markus Walloner
Germany (DE)

Copyright (c) 2026 Markus Walloner
