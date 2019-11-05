#!/Library/AutoPkg/Python3/Python.framework/Versions/Current/bin/python3
#
# Copyright 2010 Per Olofsson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""See docstring for PraatURLProvider class"""


import re
from urllib.parse import urlopen  # For Python 3

from autopkglib import Processor, ProcessorError

__all__ = ["PraatURLProvider"]


PRAAT_BASE_URL = "http://www.fon.hum.uva.nl/praat/download_mac.html"
PRAAT_DEFAULT_ARCH = "32"
PRAAT_DMG_RE = r'a href="?(?P<url>praat\d+_mac{0}\.dmg)"?'


class PraatURLProvider(Processor):
    """Provides URL to the latest release of Praat."""

    description = __doc__
    input_variables = {
        "arch_edition": {
            "required": False,
            "description": (
                "Build architecture to retrieve. Can be either ",
                f"'32' or '64'. Default is {PRAAT_DEFAULT_ARCH}",
            ),
        },
        "base_url": {
            "required": False,
            "description": f"Default is '{PRAAT_BASE_URL}'.",
        },
    }
    output_variables = {"url": {"description": "URL to the latest release of Praat."}}

    def get_praat_dmg_url(self, base_url):
        """Find the download URL in the HTML returned from the base_url"""
        arch = self.env.get("arch_edition", "32")
        re_praat_dmg = re.compile(PRAAT_DMG_RE.format(arch))
        # Read HTML index.
        try:
            fref = urlopen(base_url)
            html = fref.read()
            fref.close()
        except Exception as err:
            raise ProcessorError(f"Can't download {base_url}: {err}")

        # Search for download link.
        match = re_praat_dmg.search(html)
        if not match:
            raise ProcessorError(f"Couldn't find Praat download URL in {base_url}")

        # Return URL.
        url = PRAAT_BASE_URL.rsplit("/", 1)[0] + "/" + match.group("url")
        return url

    def main(self):
        # Determine base_url.
        base_url = self.env.get("base_url", PRAAT_BASE_URL)

        self.env["url"] = self.get_praat_dmg_url(base_url)
        self.output(f"Found URL {self.env['url']}")


if __name__ == "__main__":
    PROCESSOR = PraatURLProvider()
    PROCESSOR.execute_shell()
