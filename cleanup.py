#!/usr/bin/env python3
import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from utils import path, misc
from utils.config import Config
from utils.rtorrent import Rtorrent

############################################################
# INIT
############################################################

# Logging
logFormatter = logging.Formatter('%(asctime)24s - %(levelname)8s - %(name)50s - %(funcName)30s '
                                 '[%(thread)5d]: %(message)s')
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)

# Console logger, log to stdout instead of stderr
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

# File logger
fileHandler = RotatingFileHandler(
    os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'activity.log'),
    maxBytes=1024 * 1024 * 5,
    backupCount=5,
    encoding='utf-8'
)

fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

# Config
cfg = Config(rootLogger)

# Logger
log = rootLogger.getChild("rtorrent_orphan_cleanup")

# Rtorrent
rtorrent = None


############################################################
# FUNCTIONS
############################################################

def remove_path(file_path, auto_remove=False):
    if not auto_remove:
        log.warning("Do you want to remove: %s (y/n)", file_path)
        yn = input()
    else:
        yn = 'y'
    if yn.lower() == 'y':
        # delete the path
        is_folder = os.path.isdir(file_path)
        if path.delete(file_path):
            # the file/folder was removed
            if not is_folder:
                folder_path = os.path.dirname(file_path)
                left_over_files = path.find_files(folder_path)
                if not len(left_over_files):
                    if not auto_remove:
                        log.warning("Do you want to remove the orphaned folder: %s (y/n)", folder_path)
                        yn = input()
                    else:
                        yn = 'y'
                    if yn.lower() == 'y':
                        path.delete(folder_path)


def existing_folder(folder_path, torrent_files):
    for file_path in torrent_files:
        if file_path.lower().startswith(folder_path.lower()):
            return True
    return False


############################################################
# MAIN
############################################################

if __name__ == "__main__":
    log.debug("Initialized")

    # build list of files in download path
    local_files = path.find_files(cfg.config['rutorrent']['download_folder'])
    if not len(local_files):
        log.error("Failed to build files list for: %s", cfg.config['rutorrent']['download_folder'])
        sys.exit(1)
    log.info("Built file list with %d files from: %s", len(local_files), cfg.config['rutorrent']['download_folder'])

    # build list of folders in download path
    local_folders = path.find_folders(cfg.config['rutorrent']['download_folder'])
    if not len(local_folders):
        log.error("Failed to build folders list for: %s", cfg.config['rutorrent']['download_folder'])
        sys.exit(1)
    log.info("Built folder list with %d folders from: %s", len(local_folders),
             cfg.config['rutorrent']['download_folder'])

    # fetch torrent list
    rtorrent = Rtorrent(cfg.config['rutorrent']['url'])
    torrents = rtorrent.get_torrents()

    if not len(torrents):
        log.error("Failed to retrieve torrent list...")
        sys.exit(1)
    else:
        log.info("Fetched %d torrents", len(torrents))

    # turn torrent list into file list
    torrent_files = []
    for k, v in torrents.items():
        remapped_files = misc.remap_file_paths(v['files'], cfg.config['rutorrent']['path_mappings'])
        if len(remapped_files):
            torrent_files.extend(remapped_files)
            log.debug("Added %5s files from torrent: %s", len(remapped_files), v['name'])
    log.info("Built file list with %d files from %d torrents", len(torrent_files), len(torrents))

    # build list of files that are no longer in the torrent client
    orphaned_paths = set(local_files) - set(torrent_files)

    # add list of folders to orphaned_files
    for folder in local_folders:
        if not existing_folder(folder, torrent_files):
            orphaned_paths.add(folder)

    if not len(orphaned_paths):
        log.info("There were no orphaned files found!")
        sys.exit(0)
    log.info("Found %d orphaned paths that existed locally, but were not associated with a torrent!",
             len(orphaned_paths))

    sorted_orphaned_paths = path.sort_path_list(orphaned_paths)
    log.info(json.dumps(sorted_orphaned_paths, indent=2))

    # delete paths
    if not cfg.config['cleanup']['auto_remove']:
        log.info("Do you want to delete the paths, one by one? (y/n)")
        yn = input()
    else:
        yn = 'y'

    if yn.lower() == 'y':
        for orphaned_path in sorted_orphaned_paths:
            remove_path(orphaned_path, cfg.config['cleanup']['auto_remove'])

    log.info("Finished!")
