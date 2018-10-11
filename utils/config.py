import json
import logging
import os
import sys
from collections import OrderedDict
from copy import copy

json.encoder.c_make_encoder = None


class Config:
    base_config = OrderedDict({
        # CORE
        'core': {
            'debug': True
        },
        # RUTORRENT
        'rutorrent': {
            'url': '',
            'download_folder': '',
            'path_mappings': {}
        }
    })

    def __init__(self, log: logging.getLoggerClass(),
                 config_path: str = os.path.join(os.path.dirname(sys.argv[0]), 'config.json')):
        self.log = log
        self.config_path = config_path
        self.config = OrderedDict({})
        self.load()
        self.log.setLevel(logging.DEBUG if self.config['core']['debug'] else logging.INFO)

    @property
    def default_config(self):
        example_config = self.base_config.copy()

        # CORE
        example_config['rutorrent']['url'] = 'https://user:pass@rutorrent.domain.com'
        example_config['rutorrent']['download_folder'] = '/mnt/local/downloads/torrents/rutorrent/completed'
        example_config['rutorrent']['path_mappings'] = {
            '/mnt/local/downloads/torrents/': [
                '/downloads/torrents/'
            ]
        }

        return example_config

    def __inner_upgrade(self, settings1, settings2, key=None, overwrite=False):
        sub_upgraded = False
        merged = copy(settings2)

        if isinstance(settings1, dict):
            for k, v in settings1.items():
                # missing k
                if k not in settings2:
                    merged[k] = v
                    sub_upgraded = True
                    if not key:
                        self.log.info("Added %r config option: %s", str(k), str(v))
                    else:
                        self.log.info("Added %r to config option %r: %s", str(k), str(key), str(v))
                    continue

                # iterate children
                if isinstance(v, dict) or isinstance(v, list):
                    merged[k], did_upgrade = self.__inner_upgrade(settings1[k], settings2[k], key=k,
                                                                  overwrite=overwrite)
                    sub_upgraded = did_upgrade if did_upgrade else sub_upgraded
                elif settings1[k] != settings2[k] and overwrite:
                    merged = settings1
                    sub_upgraded = True
        elif isinstance(settings1, list) and key:
            for v in settings1:
                if v not in settings2:
                    merged.append(v)
                    sub_upgraded = True
                    self.log.info("Added to config option %r: %s", str(key), str(v))
                    continue

        return merged, sub_upgraded

    def upgrade_settings(self, currents):
        # Do inner upgrade
        upgraded_settings, upgraded = self.__inner_upgrade(self.base_config, currents)
        return upgraded_settings, upgraded

    def dump(self):
        if not os.path.exists(self.config_path):
            with open(self.config_path, 'w') as fp:
                json.dump(self.default_config, fp, indent=2, sort_keys=False)
            self.log.warning(f"Default configuration was dumped to: {self.config_path}")
            self.log.warning("Please adjust before running again!")
            sys.exit(0)
        else:
            with open(self.config_path, 'w') as fp:
                json.dump(self.config, fp, indent=2, sort_keys=False)
        return

    def load(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as fp:
                self.config, upgraded = self.upgrade_settings(json.load(fp, object_hook=OrderedDict))
                # Save config if upgrade
                if upgraded:
                    self.dump()
                    self.log.warning("New configuration variables were added, please configure before running again!")
                    exit(0)

        else:
            self.dump()
        return
