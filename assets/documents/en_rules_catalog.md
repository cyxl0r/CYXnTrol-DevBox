RULES CATALOG
=============

Document status: Active proof of concept and development state.

DevBox already has a functioning local launcher, a graphical main interface, modular structure views, master-data and documentation maintenance, documentation snapshots, local tool detection, a repository page, and initial building blocks for the DevBox-specific publication process.

The deskNode area is actively integrated into DevBox. Supervisor and daemon processes can be started and stopped from the GUI, and their console output is displayed in the deskNode log. The product version can be edited through master data. UX themes can be named, created, deleted, duplicated, renamed, and saved. Saving a theme refreshes the deskNode manufacturer database.

Symbol management now exists as an initial functional catalog interface. It manages deskNode device categories and consumer devices through selection menus and dialogs for creation, editing, and deletion. New devices receive one PNG source, stored under their record ID as symbol_source_<record_id>.png. After every successful catalog change, create_manufacturer_db.py is executed so mnfctr_db.r0b contains current theme, category, and device data.

The graphics-pack build is functional as a proof of concept. It creates multiple prepared consumer-graphics states from symbol sources and UX themes. Actual deskNode runtime integration, asset selection, language packages, and complete state logic are still being developed.

DevBox is not a finished end-user or release version. Interfaces, database migrations, product modules, publication workflows, document templates, and tests are continuously being revised. This documentation describes the current state and must be updated alongside functional changes.

First publication: 
Author / publisher: Markus Walloner
Country: Germany (DE)

1. Scope
--------

This rules catalog applies to the project described in the accompanying project documentation.

Short Description:
DevBox is the local development hub of the CYXnTrol Development Platform. Its PySide6 interface brings together project structure, master data, documentation, local tools, product modules, repository preparation, and recurring development workflows.

DevBox is not an end-user product. It is an internal working environment in which technical requirements, data models, interfaces, build steps, and publication states are prepared, reviewed, and refined in a traceable manner.


2. Rules Catalog
----------------

DEVBOX RULES CATALOG

1. Project root and paths
- The project root is determined through the .root file.
- Implementations do not use hard-coded user or drive paths.
- Relative project paths, system variables, and the root determined through .root take priority.

2. Temporary workspaces
- Exports, graphics builds, restructuring, and repository preparation operate in unique subfolders of the system temporary directory.
- The actual project root is not used as a disposable working copy.
- Success of the main operation and success of a subsequent cleanup are evaluated separately.

3. Python startup
- Launchers, builders, and product-specific processes explicitly use python.exe.
- pythonw.exe is not used as an execution basis so that errors and console output remain traceable.

4. Databases and migration
- SQLite is the central data source for DevBox master data.
- Schema extensions must not delete existing tables or records unless a function explicitly recreates a derived product database.
- UX themes are stored centrally in "ux-deskNode" and product-locally in mnfctr_db.r0b as "ux_themes".
- The deskNode symbol catalog is stored centrally in desknode_consumer_device_categories and desknode_consumer_devices and product-locally in consumer_device_categories and consumer_devices.
- After every successful change to deskNode version, theme, category, or consumer device, mnfctr_db.r0b must be refreshed.

5. Symbol sources and graphics build
- A consumer device is referenced through a stable record_id and device_key, not through a rendered PNG file name.
- New consumer devices require exactly one PNG source.
- The source PNG is stored as resources/graphics/symbol_source_<record_id>.png.
- Categories belong in the database, not in the source file name.
- The builder creates scaling, masks, theme variants, and final assets from symbol sources and UX themes.
- Inkscape and GIMP are used only through explicitly started build steps.

6. Logging and runtime data
- DevBox maintains local runtime data under AppData.
- Errors, startup states, and relevant process steps should be logged in a traceable way.
- Each DevBox building block should eventually have a clear log context.

7. Module boundaries
- Subscripts should be clearly named and have a defined responsibility.
- In areas governed by the 300-line rule, larger workflows are split into specialized subscripts.
- Product-internal build scripts may be longer when their connected process logic remains clearer that way.

8. Publication and repository
- The published DevBox state is created from a controlled root_dir desired state.
- README, license, documents, and images receive defined target locations and file names.
- Repository credentials are not stored in DevBox.
- The publication export deliberately includes applications/deskNode/resources/scripts but excludes __pycache__, .pyc, and .pyo content.
- Before a push, the local repository state is compared with root_dir; obsolete published files may be removed only under defined protection rules.

9. External tools
- Paths to Inkscape and GIMP are checked and stored locally.
- Missing tools do not block all of DevBox, but can limit individual functions.
- Installers and external programs are started only through explicit user action.


3. Supplementary Notes
----------------------

Purpose:
DevBox is intended to turn recurring and error-prone development work into traceable local tools. This includes maintaining product and manufacturer data, structured documentation, prepared publication steps, integration of local creative applications, and controlled execution of product-specific development functions.

The application provides a shared working foundation for products of the CYXnTrol Development Platform. Instead of keeping workflows only as memory, folder conventions, or a collection of console commands, they are retained as data, scripts, GUI functions, and verifiable process chains.

For deskNode, DevBox additionally serves as a development and configuration interface for product versions, UX themes, device categories, consumer symbols, and prepared graphics packages. The later deskNode runtime is intended to receive reproducible data and pre-rendered assets from this process.


Context:
The CYXnTrol Development Platform emerged from practical development work involving many small tools, data states, graphics files, documents, and test workflows. As the number of products and functions grows, it is no longer sufficient to keep information only in individual files or in memory. A stable project root, traceable data sources, repeatable temporary workspaces, and clearly separated product modules are required.

DevBox is the response to this need. It provides a local development hub in which manufacturer and product data, documentation, global structure rules, external tools, repository preparation, and specialized product functions are brought together.

deskNode is the first product integrated as an active DevBox area. Its role is to manage and visualize smart plugs and their connected consumers. For those consumers, not only names but also categories, stable technical IDs, PNG sources, theme data, and pre-rendered graphical states are placed into a reproducible workflow. This removes the need to manually create symbol variants for every theme and state combination.


Repository Note:
The DevBox repository represents the CYXnTrol Development Platform itself, not a finished end-user product. It serves as a development record, a transparent work sample, and a foundation for maintaining the platform.

The published state is not copied directly from the productive project root. DevBox creates a separate cleaned root_dir state. It contains intended source code, documents, and assets, while local runtime data, temporary remnants, installers, unnecessary build output, and unpublished data remain outside the publication package.

The temporary publication root treats applications as a deliberate delivery window: the directory is cleaned first. It is then populated with applications/deskNode/resources/scripts and all contained files. __pycache__ directories as well as .pyc and .pyo files remain excluded. The real local product directory is not changed by this process.

DevBox is developed in an AI-assisted iterative workflow. Requirements, architecture, data models, UX decisions, test cases, and acceptance are directed by the project owner. Implementation is created with AI-assisted development tools and checked against defined functional requirements.


Copyright (c) 2026 Markus Walloner
