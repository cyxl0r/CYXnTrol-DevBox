from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
DEVBOX_CODE_ROOT = SCRIPT_PATH.parent.parent

if str(DEVBOX_CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(DEVBOX_CODE_ROOT))

from subscripts.push_to_git_schema_devbox_cleanup import cleanup_workspace
from subscripts.push_to_git_schema_devbox_context import (
    build_context,
    parse_request,
)
from subscripts.push_to_git_schema_devbox_documents import build_documents
from subscripts.push_to_git_schema_devbox_export import prepare_publish_root
from subscripts.push_to_git_schema_devbox_git import sync_and_push
from subscripts.push_to_git_schema_devbox_log import ProcessReporter
from subscripts.push_to_git_schema_devbox_media import copy_repository_images
from subscripts.push_to_git_schema_devbox_repository import ensure_repository_settings


REPORTER = ProcessReporter(__file__)


def run() -> int:
    request = parse_request()
    context = None
    operation_success = False

    try:
        REPORTER.info("DevBox repository schema started.")
        context = build_context(request)
        REPORTER.info("Temporary publish workspace created.", str(context.temp_path))

        repository = ensure_repository_settings(
            database_file=context.source_database_file,
            product_slug=request.product_slug,
            reporter=REPORTER,
        )
        REPORTER.info(
            "Repository settings ready.",
            f"url={repository.url}; branch={repository.branch}",
        )

        prepare_publish_root(context, REPORTER)
        build_documents(context, REPORTER)
        copied_images = copy_repository_images(
            image_paths=request.image_paths,
            pictures_path=context.pictures_path,
            timestamp=context.timestamp,
            reporter=REPORTER,
        )
        REPORTER.info(
            "Optional repository images prepared.",
            f"count={len(copied_images)}",
        )

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
            REPORTER.info("DevBox repository push finished successfully.")
            return 0

        REPORTER.info("Repository content was already current; no push was needed.")
        return 0

    except KeyboardInterrupt:
        REPORTER.warning("DevBox repository schema cancelled by user.")
        return 130
    except Exception as error:
        REPORTER.exception("DevBox repository schema failed.", error)
        return 1
    finally:
        if context is not None:
            cleanup_ok = cleanup_workspace(context.temp_path, REPORTER)
            if not cleanup_ok:
                REPORTER.warning(
                    "Publish workspace cleanup failed after main operation.",
                    str(context.temp_path),
                )
            elif operation_success:
                REPORTER.info("Temporary publish workspace cleaned up.")


if __name__ == "__main__":
    raise SystemExit(run())
