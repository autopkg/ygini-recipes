#!/usr/bin/python

from __future__ import absolute_import
from HTMLParser import HTMLParser
import re
import urllib2
import urlparse

from distutils.version import LooseVersion, StrictVersion

from autopkglib import Processor, ProcessorError

__all__ = ["PHPComposerURLProvider"]

class ComposerURLFinder(HTMLParser):
    urls = []
    def handle_starttag(self, tag, attrs):
        # Only parse the 'anchor' tag.
        if tag == "a":
           # Check the list of defined attributes.
            for name, value in attrs:
                # If href is defined, print it.
                if name == "href":
                    self.urls.append(value)

class PHPComposerURLProvider(Processor):
    """Provides a version and dmg download for Composer command line tool."""
    description = __doc__
    source_url = "https://getcomposer.org/download/"
    url_pattern = "/download/([0-9.]+)/composer.phar"
    input_variables = {
    }
    output_variables = {
        "source_url": {
            "required": False,
            "description":
                "URL that will be parsed for the final download URL."
                "Default value is https://getcomposer.org/download/"
        },
        "url_pattern": {
            "required": False,
            "description":
                "Regex pattern that will applied to all URLs found on the"
                "composer's download page. Used to find the last version."
                "You might change it to allow RC, beta or alpha version. "
                "Extracted version number will be evaluated by distutils' "
                "LooseVersion."
                "Default value is '/download/([0-9.]+)/composer.phar'"
        },
        "version": {
            "description": "Version of the product.",
        },
        "url": {
            "description": "Download URL.",
        },
    }


    def get_all_download_URLs_per_version(self):
        '''Return a list of download URLs.'''
        try:
            html_content = urllib2.urlopen(self.source_url).read()
            parser = ComposerURLFinder()
            parser.feed(html_content)
            url_pattern = re.compile(self.url_pattern )
            urls = parser.urls
            download_urls = {}
            for url in urls:
                m = url_pattern.search(url)
                if m is not None:
                    version = m.group(1)
                    download_urls[version] = url

        except urllib2.HTTPError as ValueError:
            raise ProcessorError("Could not parse downloads metadata.")
        return download_urls

    def get_highest_version(self, all_versions):
        '''Extract the highest version using LooseVersions'''
        has_changed = True
        selected_version = all_versions[0]
        while has_changed:
            has_changed = False
            for a_version in all_versions:
                if LooseVersion(selected_version) < LooseVersion(a_version):
                    has_changed = True
                    selected_version = a_version
        return selected_version

    def main(self):
        '''Find the last version number and URL'''

        if 'source_url' in self.env:
            self.source_url = self.env['source_url']

        if 'url_pattern' in self.env:
            self.url_pattern = self.env['url_pattern']

        try:
            all_download_URLs_per_version = self.get_all_download_URLs_per_version()

            last_version = self.get_highest_version(all_download_URLs_per_version)
            last_version_url = all_download_URLs_per_version[last_version]
        except Exception as e:
            raise ProcessorError("Could not get a download URL: %s" % e)

        self.env["version"] = last_version
        self.env["url"] = urlparse.urljoin(self.source_url, last_version_url)
        self.output("Found download URL for version %s: %s" % (self.env["version"], self.env["url"]))

if __name__ == "__main__":
    PROCESSOR = PHPComposerURLProvider()
    PROCESSOR.execute_shell()
