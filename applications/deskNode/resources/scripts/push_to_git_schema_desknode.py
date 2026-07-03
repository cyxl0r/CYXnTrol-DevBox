from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
SCRIPT_ROOT = SCRIPT_PATH.parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from subscripts.push_to_git_schema_desknode_cleanup import cleanup_workspace
from subscripts.push_to_git_schema_desknode_context import build_context, parse_request
from subscripts.push_to_git_schema_desknode_documents import build_documents
from subscripts.push_to_git_schema_desknode_export import prepare_publish_root
from subscripts.push_to_git_schema_desknode_git import sync_and_push
from subscripts.push_to_git_schema_desknode_log import ProcessReporter
from subscripts.push_to_git_schema_desknode_media import copy_repository_images
from subscripts.push_to_git_schema_desknode_repository import ensure_repository_settings


REPORTER = ProcessReporter(__file__)


def run() -> int:
    request = parse_request()
    context = None
    operation_success = False
    try:
        REPORTER.info("deskNode repository schema started.")
        context = build_context()
        REPORTER.info("Temporary deskNode publish workspace created.", str(context.temp_path))

        repository = ensure_repository_settings(context.source_database_file, REPORTER)
        REPORTER.info("deskNode repository settings ready.", f"url={repository.url}; branch={repository.branch}")

        prepare_publish_root(context, REPORTER)
        build_documents(context, REPORTER)
        copied_images = copy_repository_images(
            image_paths=request.image_paths,
            pictures_path=context.pictures_path,
            timestamp=context.timestamp,
            reporter=REPORTER,
        )
        REPORTER.info("Optional deskNode repository images prepared.", f"count={len(copied_images)}")

        result = sync_and_push(
            root_dir=context.root_dir,
            repository_url=repository.url,
            repository_branch=repository.branch,
            repository_workspace=context.repository_path,
            commit_text=request.commit_text,
            reporter=REPORTER,
        )
        operation_success = result.pushed
        if result.pushed:
            REPORTER.info("deskNode repository push finished successfully.")
        else:
            REPORTER.info("deskNode repository content was already current; no push was needed.")
        return 0
    except KeyboardInterrupt:
        REPORTER.warning("deskNode repository schema cancelled by user.")
        return 130
    except Exception as error:
        REPORTER.exception("deskNode repository schema failed.", error)
        return 1
    finally:
        if context is not None:
            cleanup_ok = cleanup_workspace(context.temp_path, REPORTER)
            if cleanup_ok:
                REPORTER.info("Temporary deskNode publish workspace cleaned up.")
            else:
                REPORTER.warning("Publish workspace cleanup failed after main operation.", str(context.temp_path))


if __name__ == "__main__":
    raise SystemExit(run())
