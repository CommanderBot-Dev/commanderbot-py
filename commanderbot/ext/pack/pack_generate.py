import io
import os
from multiprocessing import Process, Queue
from queue import Empty
from typing import Dict, List, Tuple
from zipfile import ZipFile

from beet import (
    Context,
    FormattedPipelineException,
    ProjectConfig,
    config_error_handler,
    run_beet,
)
from beet.core.utils import JsonDict, normalize_string
from beet.toolchain.utils import format_exc
from jinja2 import TemplateError
from lectern import Document

BuildResult = Tuple[List[str], Dict[str, bytes]]


def generate_packs(
    project_config: JsonDict,
    build_timeout: float,
    show_stacktraces: bool,
    project_name: str,
    message_content: str,
) -> BuildResult:
    q: "Queue[BuildResult]" = Queue()

    p = Process(
        target=worker,
        args=(
            q,
            project_name,
            project_config,
            message_content,
            show_stacktraces,
        ),
    )

    p.start()
    p.join(timeout=build_timeout)

    try:
        return q.get_nowait()
    except Empty:
        p.kill()
        return [
            f"Timeout exceeded. The message took more than {build_timeout} seconds to process."
        ], {}


def worker(
    q: "Queue[BuildResult]",
    project_name: str,
    project_config: JsonDict,
    message_content: str,
    show_stacktraces: bool,
):
    project_directory = os.getcwd()

    base_config = {
        "name": normalize_string(project_name) or "untitled",
        "pipeline": [__name__],
        "meta": {
            "source": message_content,
            "build_output": [],
            "build_attachments": {},
        },
    }

    try:
        with config_error_handler():
            config = (
                ProjectConfig(**project_config)
                .resolve(project_directory)
                .with_defaults(ProjectConfig(**base_config).resolve(project_directory))
            )

        with run_beet(config) as ctx:
            build_output = ctx.meta["build_output"]
            attachments = ctx.meta["build_attachments"]

            for pack in ctx.packs:
                if pack:
                    fp = io.BytesIO()

                    with ZipFile(fp, mode="w") as output:
                        pack.dump(output)
                        output.writestr("source.md", message_content)

                    attachments[f"{pack.name}.zip"] = fp.getvalue()

            q.put((build_output, attachments))
            return
    except FormattedPipelineException as exc:
        build_output = [exc.message]
        exception = exc.__cause__ if exc.format_cause else None
    except Exception as exc:
        build_output = ["An unhandled exception occurred. This could be a bug."]
        exception = exc

    if exception:
        exc_name = type(exception).__name__

        if show_stacktraces:
            build_output.append(format_exc(exception))
        elif isinstance(
            exception,
            (
                TypeError,
                ValueError,
                AttributeError,
                LookupError,
                ArithmeticError,
                TemplateError,
            ),
        ):
            build_output.append(f"{exc_name}: {exception}")
        else:
            build_output.append(
                f'{exc_name}: Enable the "stacktraces" option to see the full traceback.'
            )

    q.put((build_output, {}))


def beet_default(ctx: Context):
    document = ctx.inject(Document)
    document.cache = None
    document.add_markdown(ctx.meta["source"])
