import io
import os
from typing import Dict
from zipfile import ZipFile

from beet import Context, ProjectConfig, config_error_handler, run_beet
from beet.core.utils import JsonDict
from lectern import Document


def generate_packs(
    project_name: str,
    project_config: JsonDict,
    message_content: str,
) -> Dict[str, bytes]:
    project_directory = os.getcwd()
    packs: Dict[str, bytes] = {}

    message_config = {
        "name": project_name,
        "pipeline": [__name__],
        "meta": {
            "source": message_content,
        },
    }

    with config_error_handler():
        config = (
            ProjectConfig(**project_config)
            .resolve(project_directory)
            .with_defaults(ProjectConfig(**message_config).resolve(project_directory))
        )

    with run_beet(config) as ctx:
        for pack in ctx.packs:
            if not pack:
                continue

            fp = io.BytesIO()

            with ZipFile(fp, mode="w") as output:
                pack.dump(output)
                output.writestr("source.md", message_content)

            packs[f"{pack.name}.zip"] = fp.getvalue()

    return packs


def beet_default(ctx: Context):
    document = ctx.inject(Document)
    document.add_markdown(ctx.meta["source"])
