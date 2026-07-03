RULES CATALOG
=============

Document status: Active proof of concept and development state.

DevBox already has a functioning local launcher, a graphical main interface, modular structure views, master-data and documentation maintenance, documentation snapshots, local tool detection, a repository page, and initial building blocks for the DevBox-specific publication process.

The deskNode area is actively integrated into DevBox. Supervisor and daemon processes can be started and stopped from the GUI, and their console output is displayed in the deskNode log. The product version can be edited through master data. UX themes can be named, created, deleted, duplicated, renamed, and saved. Saving a theme refreshes the deskNode product data.

In the current proof of concept, deskNode has a coupled worker architecture. Tapo, FRITZ!DECT, and Shelly are discovered and monitored locally through their own venmods; supported devices process switching states and power values. The daemon synchronizes venmod data into a global device inventory, applies an initial safety read cycle, and opens the main interface only after the initial global synchronization. Structure management supports multiple building roots, one complete device pool per building, and additional additive assignments to rooms or other structure members.

Symbol management is available as a functional catalog interface. It manages deskNode device categories and consumer devices through selection menus and dialogs for creation, editing, and deletion. New devices receive one PNG source, stored under their record ID as symbol_source_<record_id>.png. After every successful catalog change, create_manufacturer_db.py is executed so mnfctr_db.r0b contains current theme, category, and device data.

The graphics-pack build is functional as a proof of concept. It creates prepared consumer-graphics states from symbol sources and UX themes. The current deskNode runtime already uses language, theme, and graphics data; asset selection, broader symbol coverage, and additional visual states are still being developed.

DevBox and deskNode are not finished end-user or release versions. Credential storage, long-term stability with larger device inventories, vendor-specific edge cases, testing, packaging, and cross-platform portability remain open development tasks.

First publication: 
Author / publisher: Markus Walloner
Country: Germany (DE)

1. Scope
--------

This rules catalog applies to the project described in the accompanying project documentation.

Short Description:
DevBox is the local development hub of the CYXnTrol Development Platform. Its PySide6 interface brings together project structure, master data, documentation, local tools, product modules, repository preparation, and recurring development workflows.

With deskNode, an active product module is integrated: a local device and structure hub for smart plugs and connected loads. deskNode is extended through replaceable venmods for supported vendors and protocols.

DevBox is not an end-user product. It is an internal working environment in which requirements, data models, UX decisions, interfaces, builds, and publication states are prepared and reviewed in a traceable way.


2. Rules Catalog
----------------

DEVBOX RULES CATALOG

1. Project root and paths
- The project root is determined through the .root file.
- Implementations do not use hard-coded user or drive paths.
- Relative project paths, system variables, and the root determined through .root take priority.

2. Temporary workspaces
- Exports, graphics builds, restructurings, repository preparation, and deskNode daemon runs use unique subfolders of the system temporary directory.
- The real project root is not used as a disposable working copy.
- Success of the main operation and success of subsequent cleanup are evaluated separately.

3. Python startup
- Launchers, builders, and product-specific processes explicitly use python.exe.
- pythonw.exe is not used as the execution basis so errors and console output remain traceable.

4. Databases and migrations
- SQLite is the central source for DevBox master data and local deskNode runtime data.
- Schema extensions must not delete existing tables or records unless a function explicitly recreates a derived product database.
- UX themes are stored centrally in ux-deskNode and product-locally in mnfctr_db.r0b as ux_themes.
- deskNode language resources are stored product-locally in lan.r0b; local user settings are kept separately in settings.r0b.
- The deskNode symbol catalog is stored centrally in desknode_consumer_device_categories and desknode_consumer_devices and product-locally in consumer_device_categories and consumer_devices.
- After every successful deskNode version, theme, category, or consumer-device change, mnfctr_db.r0b must be refreshed.

5. deskNode runtime and venmods
- Every venmod has a clear coupler contract and its own worker.
- A worker writes only its own temporary venmod database. Global device and structure state is not written directly by a venmod.
- The daemon validates coupler contracts, mirrors confirmed values into devices.r0b, and sends desired states back only through the downstream interface.
- Initial startup is read-only. Confirmed actual values and initial global synchronization release the main GUI.
- Externally observed switching states are adopted in a controlled way as actual and desired states; a venmod must not force unconfirmed switch-backs.
- Vendor logic remains inside the respective venmod. Working Tapo, FRITZ!DECT, and Shelly paths are not restructured without a concrete requirement.

6. Credentials and logs
- Credentials must not be materialized in console output, worker events, or error messages.
- The current local credential state is not a finished secure vault. A cross-platform encrypted vault must be developed as a shared platform component.
- Logging should include process role, product or venmod context, and traceable failure signals, but no secrets.

7. Symbol sources and graphics build
- A consumer device is referenced through a stable record_id and device_key, not through a rendered file name.
- New consumer devices require exactly one PNG source.
- The source PNG is stored as resources/graphics/symbol_source_<record_id>.png.
- Categories belong in the database, not in the source file name.
- The builder creates scaling, masks, theme variants, and final assets from symbol sources and UX themes.
- Inkscape and GIMP are used only through explicitly started build steps.

8. Module boundaries
- Subscripts should be clearly named and have a defined responsibility.
- In areas governed by the 300-line rule, larger workflows are split into specialized subscripts.
- Product-internal build scripts may be longer when their connected process logic remains clearer that way.

9. Publication and repository
- The published DevBox state is created from a controlled root_dir desired state.
- README, license, documents, and images receive defined target locations and file names.
- Repository credentials are not stored in DevBox.
- The current DevBox export deliberately includes applications/deskNode/resources/scripts but excludes __pycache__, .pyc, and .pyo content.
- Before a push, the local repository state is compared with root_dir; obsolete published files may be removed only under defined protection rules.

10. External tools
- Paths to Inkscape and GIMP are checked and stored locally.
- Missing tools do not block all of DevBox, but can limit individual functions.
- Installers and external programs are started only through explicit user action.


3. Supplementary Notes
----------------------

Purpose:
DevBox is intended to turn recurring and error-prone development work into traceable local tools. This includes maintaining product and manufacturer data, structured documentation, prepared publication steps, integration of local creative tools, and controlled execution of product-specific development functions.

The application provides a common working foundation for products of the CYXnTrol Development Platform. Instead of keeping workflows only as memory, folder convention, or a collection of console commands, they are retained as data, scripts, GUI functions, and verifiable process chains.

For deskNode, DevBox additionally serves as a development and configuration interface for product versions, UX themes, device categories, consumer symbols, language resources, and prepared graphics packages. The deskNode runtime is intended to receive reproducible data and prepared assets from this process. The venmod architecture should also allow new local device paths to be added without unnecessarily rebuilding the daemon or already working vendor paths.


Context:
The CYXnTrol Development Platform grew out of practical development work involving many small tools, data states, graphic files, documents, and test workflows. As the number of products and functions increases, it is no longer sufficient to keep information only in individual files or in memory. A stable project root, traceable data sources, repeatable temporary workspaces, and clearly separated product modules are needed.

DevBox is the response to this need. It acts as a local development center where manufacturer and product data, documentation, global structure rules, external tools, repository preparation, and specialized product functions are brought together.

deskNode is the first product integrated as its own active DevBox area. Its purpose is the local management, visualization, and switching of supported smart plugs. Tapo, FRITZ!DECT, and Shelly are not treated as special cases embedded directly into the interface; they are connected through venmods with a shared coupler and worker contract. Names, categories, stable technical IDs, PNG sources, theme data, and pre-rendered graphics states are brought into a reproducible workflow for connected loads.


Repository Note:
The DevBox repository represents the CYXnTrol Development Platform itself, not a finished end-user product. It serves as a development state, transparent work sample, and foundation for maintaining the platform.

The published state is not copied directly from the productive project root. DevBox generates a separate cleaned root_dir state. It contains intended source code, documents, and assets, while local runtime data, temporary leftovers, installers, database WAL files, and unpublished data remain outside the publication package.

The current DevBox push treats applications as a deliberate delivery window: the area is cleaned first. Afterwards, applications/deskNode/resources/scripts including contained files are copied into the publication state. __pycache__ folders and .pyc and .pyo files remain excluded. This current scope is a DevBox-specific publication process and not yet a complete deskNode product release. Before deskNode including GUI, logic, and venmods is published as its own repository or release, its export scope must be explicitly defined and tested.

DevBox is developed through an AI-assisted, iterative workflow. Requirements, architecture, data models, UX decisions, test cases, and acceptance are directed by the project owner. Implementation is created with AI-assisted development tools and checked against defined functional requirements.


Copyright (c) 2026 Markus Walloner
