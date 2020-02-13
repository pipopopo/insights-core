"""
Categorize the commands, paths, and template strings used by datasources,
and parse the remove.conf file.
"""
from __future__ import absolute_import
import logging
import six
import os
from six.moves import configparser as ConfigParser
from .constants import InsightsConstants as constants
from collections import defaultdict
from insights import datasource, dr, parse_plugins, load_packages
from insights.core import spec_factory as sf

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)
net_logger = logging.getLogger('network')


def resolve(d):
    """
    Categorizes a datasource's command, path, or template information.

    The categorization ignores first_of, head, and find since they depend on other
    datasources that will get resolved anyway. Ignore the listdir helper and explicit
    @datasource functions since they're pure python.
    """
    if isinstance(d, sf.simple_file):
        return ("file_static", [d.path])

    if isinstance(d, sf.first_file):
        return ("file_static", d.paths)

    if isinstance(d, sf.glob_file):
        return ("file_glob", d.patterns)

    if isinstance(d, sf.foreach_collect):
        return ("file_template", [d.path])

    if isinstance(d, sf.simple_command):
        return ("command_static", [d.cmd])

    if isinstance(d, sf.command_with_args):
        return ("command_template", [d.cmd])

    if isinstance(d, sf.foreach_execute):
        return ("command_template", [d.cmd])

    return (None, None)


def categorize(ds):
    """
    Extracts commands, paths, and templates from datasources and cateorizes them
    based on their type.
    """
    results = defaultdict(set)
    for d in ds:
        (cat, res) = resolve(d)
        if cat is not None:
            results[cat] |= set(res)
    return {k: sorted(v) for k, v in results.items()}


def get_spec_report():
    """
    You'll need to already have the specs loaded, and then you can call this
    procedure to get a categorized dict of the commands we might run and files
    we might collect.
    """
    load("insights.specs.default")
    ds = dr.get_components_of_type(datasource)
    return categorize(ds)


# helpers for running the script directly
# def parse_args():
#     p = argparse.ArgumentParser()
#     p.add_argument("-p", "--plugins", default=)
#     return p.parse_args()


def load(p):
    plugins = parse_plugins(p)
    load_packages(plugins)


# def main():
#     args = parse_args()
#     load(args.plugins)
#     report = get_spec_report()
#     print(yaml.dump(report))


class InsightsUploadConf(object):
    """
    Insights spec configuration from uploader.json
    """

    def __init__(self, config):
        """
        Load config from parent
        """
        self.remove_file = config.remove_file

    def get_rm_conf(self):
        """
        Get excluded files config from remove_file.
        """
        if not os.path.isfile(self.remove_file):
            return None

        # Convert config object into dict
        parsedconfig = ConfigParser.RawConfigParser()
        try:
            parsedconfig.read(self.remove_file)
            rm_conf = {}

            for item, value in parsedconfig.items('remove'):
                if six.PY3:
                    rm_conf[item] = value.strip().encode('utf-8').decode('unicode-escape').split(',')
                else:
                    rm_conf[item] = value.strip().decode('string-escape').split(',')

            return rm_conf
        except ConfigParser.Error as e:
            raise RuntimeError('ERROR: Could not parse the remove.conf file. ' + str(e))


if __name__ == '__main__':
    from .config import InsightsConfig
    print(InsightsUploadConf(InsightsConfig().load_all()))
