"""
Rules for data collection
"""
from __future__ import absolute_import
import logging
import six
import os
from six.moves import configparser as ConfigParser
from .constants import InsightsConstants as constants

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)
net_logger = logging.getLogger('network')


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

            # add tokens to limit regex handling (for now)
            #   core parses blacklist for files and commands as regex
            for idx, f in enumerate(rm_conf['files']):
                rm_conf['files'][idx] = '^' + f + '$'

            for idx, c in enumerate(rm_conf['commands']):
                rm_conf['commands'][idx] = '^' + c + '$'

            return rm_conf
        except ConfigParser.Error as e:
            raise RuntimeError('ERROR: Could not parse the remove.conf file. ' + str(e))


if __name__ == '__main__':
    from .config import InsightsConfig
    print(InsightsUploadConf(InsightsConfig().load_all()))
