#!/usr/bin/env python3
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
    os.path.join(os.path.dirname(sys.argv[0]), 'activity.log'),
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

def remove_file(file_path):
    log.warning("Do you want to remove: %s (y/n)", file_path)
    yn = input()
    if yn.lower() == 'y':
        # delete the file
        if path.delete(file_path):
            # the file/folder was removed
            folder_path = os.path.dirname(file_path)
            left_over_files = path.find_files(folder_path)
            if not len(left_over_files):
                log.warning("Do you want to remove the orphaned folder: %s (y/n)", folder_path)
                yn = input()
                if yn.lower() == 'y':
                    path.delete(folder_path)


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
    log.info("Built file list with %d total files from %d torrents", len(torrent_files), len(torrents))

    # build list of files that are no longer in the torrent client
    orphaned_files = set(local_files) - set(torrent_files)
    if not len(orphaned_files):
        log.info("There were no orphaned files found!")
        sys.exit(0)
    log.info("Found %d orphaned files that existed locally, but were not associated with a torrent!",
             len(orphaned_files))

    log.info(orphaned_files)

    # delete files
    log.info("Do you want to delete the files, one by one? (y/n)")
    yn = input()
    if yn.lower() == 'y':
        for orphaned_file in orphaned_files:
            remove_file(orphaned_file)

    log.info("Finished!")
