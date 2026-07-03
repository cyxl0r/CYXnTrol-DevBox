TODO LIST
=========

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

1. Project Context
------------------

Short Description:
DevBox is the local development hub of the CYXnTrol Development Platform. Its PySide6 interface brings together project structure, master data, documentation, local tools, product modules, repository preparation, and recurring development workflows.

With deskNode, an active product module is integrated: a local device and structure hub for smart plugs and connected loads. deskNode is extended through replaceable venmods for supported vendors and protocols.

DevBox is not an end-user product. It is an internal working environment in which requirements, data models, UX decisions, interfaces, builds, and publication states are prepared and reviewed in a traceable way.


Long Description:
DevBox combines work that would otherwise be scattered across individual scripts, folders, spreadsheets, console windows, and external applications. It manages central project and product data, provides documentation content, organizes global structure templates, detects local tools, and brings product-specific development functions together in one interface.

The first active product module is deskNode. deskNode is a local control and structure environment for smart plugs and connected loads. A supervisor starts a daemon; the daemon couples discovered venmods through a common contract and starts one worker per venmod. The current proof of concept contains local paths for Tapo, FRITZ!DECT, and Shelly. Devices are maintained in a global inventory database, while every worker writes only its own temporary runtime database. The daemon synchronizes confirmed live values, desired states, and device identities between the layers.

deskNode additionally organizes devices in independent building trees. Every building has a device pool as its complete building-wide overview and can contain spatial or functional structure members. A device can remain in a building pool and also be assigned to a room, area, desk, or other structure member. The graphical interface visualizes this structure, device and power values, and local switching states.

The DevBox page for deskNode starts and stops the supervisor and daemon, shows their console output, and maintains product versions, UX themes, and the symbol catalog. Themes are managed through named records, RGBA colors, global font files, sizes, outlines, and shape rules. Categories and consumer symbols are maintained through stable technical IDs and PNG sources. The graphics-pack build creates prepared variants for themes and states.

DevBox works locally in the project context. A launcher discovers the project root through the .root file, provides runtime data under AppData, checks external tools, and starts the GUI from a temporary working copy. The real project root remains the authoritative source for resources, databases, and function scripts. A single-instance mechanism prevents parallel DevBox windows and activates the already-open instance when started again.

The project is developed through an AI-assisted, iterative workflow. Requirements, process logic, data models, UX decisions, test cases, and acceptance are directed by the project owner; implementation steps are created, reviewed, and refined with AI-assisted development tools.


2. Open Items
-------------

CURRENT TODO LIST

deskNode runtime and venmods
- Test the shared venmod contract with further vendor paths and multiple simultaneous devices.
- Continue measuring and stabilizing Tapo operations with larger device inventories, longer runs, 403 errors, reauthentication, and fast switching sequences.
- Reduce Tapo monitoring to the actually required local minimum and use vendor-specific detail queries only where needed.
- Test FRITZ!DECT with multiple FRITZ!Boxes, changing gateways, offline devices, and AHA edge cases.
- Extend Shelly with documented authentication, HTTPS, where applicable Gen1 compatibility, and additional device categories without destabilizing the existing RPC path.
- Make polling capacities, backoff, discovery frequencies, and switching-command priority configurable based on reliable measurements.
- Add end-to-end logging for desired state, downstream command, worker execution, read-back, confirmation, and timeout.

Credentials and security
- Design and implement a shared DevBox/deskNode credential-vault component.
- Define audited cryptographic building blocks, a master-password or key model, migration, password change, and safe runtime transfer for the portable vault.
- Do not develop custom cryptography and do not retain clear-text credentials in global device, venmod, or runtime tables.
- Add optional auto-unlock through native key stores only after a platform-neutral vault format exists.

deskNode structure and GUI
- Test building pools, direct assignment counts, drag-and-drop, and multi-building views with real data inventories.
- Define visual states for offline, warning, error, unknown devices, pending commands, and consumption thresholds.
- Design filters, search, dense operator view, and scalable behavior with many devices.
- Check structure and device views at different screen sizes, zoom levels, and long labels.
- Further develop language and theme selection through stable record_id references instead of renameable names.

UX themes and symbol catalog
- Continue testing persistence, migration, and refresh of multiple UX themes under real GUI conditions.
- Handle missing font files, invalid RGBA values, and corrupted theme records robustly.
- Continue filling symbol management with real categories and consumer symbols.
- Create language packages for categories and devices using automatically generated translation keys.
- Define search in the deskNode symbol picker through localized names and search terms.
- Add PNG replacement for existing devices as a dedicated editing workflow.
- Define how consumer_device_id and optional consumer_device_key are stored with device assignments.

Graphics-pack build
- Test generated graphics packages with more symbols, more themes, and longer file names.
- Fully align the builder with record-ID-named symbol_source_<record_id>.png sources.
- Validate build output against expected numbers of themes, symbols, masks, and state files.
- Further secure cleanup, archiving, and installation of the final graphics package.
- Optionally develop an incremental build so a small change does not rebuild every asset.
- Extend error handling for missing symbol sources, Inkscape, GIMP, and unsupported SVG/PNG files.

Repository, documentation, and quality
- Fully test the DevBox push-to-Git process in the GUI.
- Define the complete export scope for an independent deskNode repository; the current DevBox export includes only resources/scripts and is not a product release.
- Verify repository URL and branch setup with a real remote repository.
- Further secure desired-versus-actual synchronization, protection rules, and removal of obsolete repository files.
- Update form texts when functionality changes.
- Have terms of use and privacy notices legally reviewed and adapted to actual data flows before public use.
- Add automated tests for database migration, theme persistence, symbol catalog, graphics build, document export, snapshot structure, repository synchronization, venmod coupling, and device workflows.
- Plan and validate packaging, signing, and later macOS and Linux portability separately.


3. Target State
---------------

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


4. Technical Context
--------------------

DevBox is modular in structure.

The launch chain begins with a DevBox launcher. It discovers the project root through the .root file, provides local runtime data under AppData, checks stored tool paths, and starts the graphical interface from a temporary copy. The temporary copy reduces the risk that a running GUI locks or changes files in the real project root.

The main GUI resides under resources/applications/devbox/functions and uses specialized subscripts for pages, layout, data access, process starts, and product modules. The graphical interface uses PySide6. It accesses graphics, fonts, database files, installers, and function scripts through the actual project root.

The central master-data source is resources/organization/devbox_db.r0b. It contains product data, repository fields, documentation fields, structure information, named deskNode UX themes, and the symbol-catalog tables desknode_consumer_device_categories and desknode_consumer_devices. For local DevBox runtime data, the application uses logfile.r0b and locdata.r0b under AppData.

deskNode has its own derived product data under applications/deskNode/data, particularly mnfctr_db.r0b for manufacturer and theme data and lan.r0b for language resources. For every run, the supervisor creates a unique temporary context. The daemon couples available venmods through coupler.py, validates their contracts, provides a local worker-control hub, and starts one worker for each accepted venmod. Workers write only their own temporary venmod database. The daemon consolidates confirmed data in the global AppData database devices.r0b and logs resolved power values separately.

The current deskNode integration contains venmods for Tapo, FRITZ!DECT, and Shelly. During startup, the product GUI waits for the confirmed initial cycle of all coupled venmods and then shows the synchronized device inventory. Structure assignments, UX settings, and rendering remain separate from vendor-specific worker data.

The graphics-pack build processes global symbol sources, scaling, masks, vectorization, and theme data in temporary work folders. Inkscape and GIMP are used as external local tools. The result is a compressed graphics package with pre-rendered state variants that deskNode can load at runtime.


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


Copyright (c) 2026 Markus Walloner
