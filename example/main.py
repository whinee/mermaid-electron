import base64
import json
import multiprocessing.dummy as mp
import shlex
import subprocess
from collections.abc import Callable, Collection
from io import BytesIO
from typing import Any

from PIL import Image, ImageOps

try:
    from .validate import validate_mermaid_config
except ImportError:
    from example.validate import validate_mermaid_config

# Types
CONFIG_TYPE = bool | int | str | dict[str, bool | int | str]
MMD_LS_TYPE = list[dict[str, str | Collection[str] | CONFIG_TYPE]]

# Constants
CMD = "./dist/mermaid-electron.AppImage"
# CMD = "yarn -s electron --trace-warnings src/electron.js"


def b64_2_image(vdata: dict[str, Any]) -> Callable[..., None]:
    margin = vdata["config"]["margin"]

    margin2 = margin * 2

    def inner(idx: int, img_b64: str) -> None:
        # Decode base64 and open image in Pillow
        img = Image.open(BytesIO(base64.b64decode(img_b64)))

        # Get inverted grayscale copy of the image
        img_gray = img.convert("L")
        img_inv = ImageOps.invert(img_gray)

        # Then get the bounding box of the non-zero region in the image
        bbox = img_inv.getbbox()

        # And afterwards crop the image using the bounding box tuple
        cropped_img = img.crop(bbox)

        # If the margin is not set, then do not apply one, and just save it
        if not margin:
            cropped_img.save(f"screenshot-{idx}.png")
            return

        # Otherwise, make a new image `2 * margin` larger than the size of the
        # original screenshot
        bordered_img = Image.new(
            "RGB",
            (cropped_img.width + margin2, cropped_img.height + margin2),
            color="white",
        )

        # Then paste the image in the center, and afterwards save the image
        bordered_img.paste(cropped_img, (margin, margin))
        bordered_img.save(f"screenshot-{idx}.png")

    return inner


def run_mermaid_electron(cmd: str, data: dict[str, Any]) -> None:
    vdata = validate_mermaid_config(data)

    img_fn = b64_2_image(vdata)
    data_str = json.dumps(vdata)

    process = subprocess.Popen(
        shlex.split(cmd),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    stdout, stderr = process.communicate(data_str)

    if stderr:
        raise Exception(stderr)

    img_ls: list[str] = json.loads(stdout)

    p = mp.Pool(10)
    p.starmap(img_fn, enumerate(img_ls))
    p.close()
    p.join()


mmd_ls = [
    {
        "code": """gantt
    title A Gantt Diagram
    dateFormat YYYY-MM-DD
    section Section
    A task :a1, 2014-01-01, 30d
    Another task :after a1 , 20d
    section Another
    Task in sec :2014-01-12 , 12d
    another task : 24d
""",
        "config": {"theme": "forest"},
    },
    {
        "code": """flowchart TD
        intro --> tt
    """,
        "config": {"theme": "forest"},
    },
    {
        "code": """flowchart TD
        intro --> tt
    """,
    },
]

data = {
    "mmd": mmd_ls,
    "mmd_config": {
        "theme": "dark",
    },
    "config": {
        "width": 1200,
        "zoom": 1.5,
    },
}


run_mermaid_electron(CMD, data)
