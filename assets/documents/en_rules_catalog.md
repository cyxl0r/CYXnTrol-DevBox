RULES CATALOG
=============

Document status: Active proof of concept and development state.

DevBox already has a functioning local launcher, a graphical main interface, modular structure views, master-data and documentation maintenance, documentation snapshots, form imports, local tool detection, a repository page, and initial building blocks for the DevBox-specific repository process.

The application is not yet a finished end-user or release version. Interfaces, publication workflows, document templates, repository synchronization, and individual development modules are being revised continuously. The current documentation describes the present development state and must be maintained alongside functional changes.

First publication: 
Author / publisher: Markus Walloner
Country: Germany (DE)

1. Scope
--------

This rules catalog applies to the project described in the accompanying project documentation.

Short Description:
DevBox is the local development hub of the CYXnTrol Development Platform. It brings together recurring work around project structure, master data, documentation, build tools, external creative applications, and repository maintenance in a PySide6 interface.

DevBox is not an end-user product. It is an internal work environment for preparing, maintaining, and structuring development workflows for later publication.


2. Rules Catalog
----------------

DEVBOX RULES CATALOG

1. Project root and paths
- The project root is determined through the .root file.
- Implementations do not use hard-coded user or drive paths.
- Relative project paths, system variables, and the root determined through .root take priority.

2. Temporary workspaces
- Restructuring, exports, build steps, and repository preparation operate in unique subfolders of the system temporary directory.
- The actual project root remains unchanged during such operations.
- Success of a main operation and success of subsequent cleanup are evaluated separately.

3. Python startup
- Launchers and builders explicitly use python.exe.
- pythonw.exe is not used as an execution basis so that errors and console output remain traceable.

4. Databases and migration
- SQLite is the central data source for DevBox master data.
- Schema extensions must not delete existing tables or records.
- Missing columns are added through migration.

5. Logging and runtime data
- DevBox maintains local runtime data under AppData.
- Errors, startup states, and relevant process steps should be logged in a traceable way.
- Each DevBox building block should eventually be assigned to a clear log context.

6. Module boundaries
- Function scripts and subscripts should remain small, clearly named, and limited to one specific responsibility.
- New push-to-Git scripts must not exceed 300 lines each.
- Larger workflows are split into specialized subscripts.

7. Publication and repository
- The published DevBox state is created from a controlled root_dir desired state.
- README, license, documents, and images receive defined target locations and file names.
- Repository credentials are not stored in DevBox.
- Before a push, the local repository state is compared with root_dir; obsolete published files may be removed only under the defined protection rules.

8. External tools
- Paths to Inkscape and GIMP are checked and stored locally.
- Missing tools do not block all of DevBox, but can result in limited functionality.
- Installers and external programs are started only through explicit user action.


3. Supplementary Notes
----------------------

Purpose:
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


Context:
The CYXnTrol Development Platform emerged from practical development work. Small helper scripts could solve individual tasks, but they also had to be organized, updated, and kept traceable. As the number of scripts, data sources, documents, test states, and planned products grew, it became clear that the development environment itself needed a structure.

DevBox is the visible control center of that structure. It connects local SQLite master data, PySide6 interfaces, documentation forms, folder structures, build-related tools, and later repository processes. The platform deliberately remains locally oriented: the development state belongs to the user, resides in the project root or local AppData, and is not automatically transferred to a cloud service.

The application is developed within the CYXLabs umbrella and the CYXnTrol Development Platform. It serves as a work tool, as a pattern for further development platforms, and as a traceable portfolio example for modular software development.


Repository Note:
The DevBox repository represents the CYXnTrol Development Platform itself, not a finished end-user product. It serves as a development state, a traceable work sample, and a foundation for maintaining the platform.

The repository state is not copied directly from the productive project root. For DevBox, a separate cleaned root_dir state is generated. It receives the intended source code, documents, and assets, keeps local databases, temporary remnants, unnecessary build outputs, font files, and installation artifacts outside the publication package, and can then be synchronized with the DevBox repository.

Products, services, or works created from the platform are intended to receive separate repositories. Their publication schemes will be developed separately from the DevBox special logic.


Copyright (c) 2026 Markus Walloner
