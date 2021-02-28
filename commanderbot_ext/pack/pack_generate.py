import io
from typing import Dict
from zipfile import ZipFile

from beet import Context, run_beet
from lectern import Document


def generate_packs(project_name: str, message_source: str) -> Dict[str, bytes]:
    packs: Dict[str, bytes] = {}

    config = {
        "name": project_name,
        "pipeline": [__name__],
        "meta": {
            "source": message_source,
        },
    }

    with run_beet(config) as ctx:
        for pack in ctx.packs:
            if not pack:
                continue

            fp = io.BytesIO()

            with ZipFile(fp, mode="w") as output:
                pack.dump(output)
                output.writestr("source.md", message_source)

            packs[f"{pack.name}.zip"] = fp.getvalue()

    return packs


def beet_default(ctx: Context):
    document = ctx.inject(Document)
    document.add_markdown(ctx.meta["source"])
