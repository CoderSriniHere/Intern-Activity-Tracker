import json
import os

try:
    import aiofiles
except ImportError:
    aiofiles = None

JSON_FILE = "intern_data.json"

"""The actual database of the interns where it is stored 
in an json file, and after storing it can also read the data 
for further uses"""

async def read_data():
    if not os.path.exists(JSON_FILE):
        return []
    if aiofiles:
        async with aiofiles.open(JSON_FILE, "r") as f:
            content = await f.read()
    else:
        with open(JSON_FILE, "r") as f:
            content = f.read()
    if not content.strip():
        return []
    return json.loads(content)


async def write_data(data):
    content = json.dumps(data, indent=4)
    if aiofiles:
        async with aiofiles.open(JSON_FILE, "w") as f:
            await f.write(content)
    else:
        with open(JSON_FILE, "w") as f:
            f.write(content)
