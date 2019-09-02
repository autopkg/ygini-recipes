#!/usr/bin/env python
#
# Copyright 2018 Yoann Gini
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
"""See docstring for MunkiNormalizePath class"""

from __future__ import absolute_import

import re

from autopkglib import Processor

__all__ = ["MunkiNormalizePath"]


class MunkiNormalizePath(Processor):
    """Edit current munki pkginfo to normalize the 'MUNKI_REPO_SUBDIR' and 'NAME'
    to replace spaces with underscore and ensure everything is lowercase.
    Typically this would be run as a preprocessor."""
    input_variables = {
        "MUNKI_REPO_SUBDIR": {
            "required": False,
            "description": "The target munki subdirectory",
        },
        "repo_subdirectory": {
            "required": False,
            "description": "The target munki subdirectory",
        },
        "NAME": {
            "required": False,
            "description": "The target package name",
        }
    }
    output_variables = {
        "MUNKI_REPO_SUBDIR": {
            "description": "The updated target munki subdirectory if exist",
        },
        "repo_subdirectory": {
            "description": "The updated target munki subdirectory if exist",
        },
        "NAME": {
            "description": "The updated target package name",
        },
        "DISPLAYNAME": {
            "description": "The former NAME if this variable does not exist yet",
        },
        "display_name": {
            "description": "The former NAME if this variable and DISPLAYNAME does not exist yet",
        }
    }
    description = __doc__

    def main(self):
        if "pkginfo" not in self.env:
            self.env["pkginfo"] = {}
        original_name = self.env["NAME"] if "NAME" in self.env else None
        original_displayname = self.env["DISPLAYNAME"] if "DISPLAYNAME" in self.env else None
        original_displayname_munki = self.env["pkginfo"]["display_name"] if "display_name" in self.env["pkginfo"] else None
        original_subdir = self.env["MUNKI_REPO_SUBDIR"] if "MUNKI_REPO_SUBDIR" in self.env else None
        original_subdir_munki = self.env["repo_subdirectory"] if "repo_subdirectory" in self.env else None
        if original_name:
            self.env["NAME"] = re.sub('[^0-9a-zA-Z/]+', '_', original_name.lower())
            self.output("Updated NAME with %s" % self.env["NAME"])
            if original_displayname is None:
                self.output("No original DISPLAYNAME, adding one")
                self.env["DISPLAYNAME"] = original_name
                self.output("Updated DISPLAYNAME with %s" % original_name)
                if original_displayname_munki is None:
                    self.output("No original display_name in pkginfo, adding one")
                    self.env["pkginfo"]["display_name"] = original_name
                    self.output("Updated display_name with %s" % original_name)
        if original_subdir:
            self.env["MUNKI_REPO_SUBDIR"] = re.sub('[^0-9a-zA-Z/]+', '_', original_subdir.lower())
            self.output("Updated MUNKI_REPO_SUBDIR with %s" % self.env["MUNKI_REPO_SUBDIR"])
        if original_subdir_munki:
            self.env["repo_subdirectory"] = re.sub('[^0-9a-zA-Z/]+', '_', original_subdir_munki.lower())
            self.output("Updated repo_subdirectory with %s" % self.env["repo_subdirectory"])

if __name__ == "__main__":
    PROCESSOR = MunkiNormalizePath()
    PROCESSOR.execute_shell()
