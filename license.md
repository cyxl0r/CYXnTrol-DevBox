LICENSE FORM

License name: Zero-Clause BSD License 0BSD

Copyright (c) 2026 Markus Walloner
Author / public author attribution: Markus Walloner
First publication: 
Project start: 2026
Country: Germany (DE)

1. Subject Matter

This license form applies to the software described in the accompanying project documentation.

Short Description:
DevBox is the local development hub of the CYXnTrol Development Platform. It brings together recurring work around project structure, master data, documentation, build tools, external creative applications, and repository maintenance in a PySide6 interface.

DevBox is not an end-user product. It is an internal work environment for preparing, maintaining, and structuring development workflows for later publication.


Long Description:
DevBox combines development tasks that would otherwise be spread across individual scripts, folders, tables, console windows, and external applications. Its interface provides platform data, manages product and documentation content, prepares structured documents, and offers tools for maintaining a controlled development state.

The application operates locally in the project context. A launcher discovers the project root through the .root file, creates a temporary working copy for the GUI, and starts the graphical interface in a controlled manner. The actual project root remains the authoritative source for resources, databases, and tools. DevBox prevents parallel GUI instances and brings an existing instance to the foreground when it is started again.

In addition to the structure workshop, DevBox contains a repository page. There, a prepared publication state for DevBox itself can be generated. That state is created in a temporary workspace, cleaned of non-public runtime, installer, and local data, enriched with maintained documentation, and then connected to the configured repository. This special process currently applies only to DevBox; later products will receive their own suitable publication schemes.

DevBox also detects local installation locations of Inkscape and GIMP, stores those locations in a local SQLite file, and provides launch buttons for available applications. Missing locations are checked again at startup. This brings the platform’s own data, scripts, and tools together in one locally traceable development environment.


2. License Text

The following section must be filled with the complete, unmodified text of the license "Zero-Clause BSD License 0BSD" stored in the product data.

<<< INSERT THE COMPLETE AND UNMODIFIED LICENSE TEXT HERE >>>

3. Project-Specific Notes

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


4. Documentation Status

Status:
Active proof of concept and development state.

DevBox already has a functioning local launcher, a graphical main interface, modular structure views, master-data and documentation maintenance, documentation snapshots, form imports, local tool detection, a repository page, and initial building blocks for the DevBox-specific repository process.

The application is not yet a finished end-user or release version. Interfaces, publication workflows, document templates, repository synchronization, and individual development modules are being revised continuously. The current documentation describes the present development state and must be maintained alongside functional changes.


Publication year: 
