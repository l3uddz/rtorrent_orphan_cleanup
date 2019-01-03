# rtorrent orphan cleanup

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-blue.svg)](https://www.python.org/)
[![License: GPL 3](https://img.shields.io/badge/License-GPL%203-blue.svg)](https://github.com/l3uddz/rutorrent_orphan_cleanup/blob/master/LICENSE.md)
[![Discord](https://img.shields.io/discord/381077432285003776.svg?colorB=177DC1&label=Discord)](https://discord.io/cloudbox)

---

<!-- TOC depthFrom:1 depthTo:2 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Introduction](#introduction)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
	- [config.json](#configjson)
	- [core](#core)
	- [cleanup](#cleanup)
	- [rutorrent](#rutorrent)
- [Usage](#usage)


<!-- /TOC -->

---



# Introduction

 Builds a list of files in all of the torrents reported in the rtorrent client and compares it with list of local files in the torrent download folder. When it finds files that are not in the torrent client (i.e. orphan files), it will offer the option to remove them.


# Requirements

1. Ubuntu/Debian

2. Python 3.5 or higher (`sudo apt install python3 python3-pip`).


# Installation

1. `cd /opt`

1. `sudo git clone https://github.com/l3uddz/rtorrent_orphan_cleanup`

1. `sudo chown -R user:group rtorrent_orphan_cleanup` (run `id` to find your user / group)

1. `cd rtorrent_orphan_cleanup`

1. `python3 cleanup.py` - run once to generate a default `config.json` file.

1. `nano config.json` - edit preferences.


# Configuration


## config.json

```json
{
  "core": {
    "debug": true
  },
  "cleanup": {
    "auto_remove": false,
    "show_total_orphans_size": true
  },
  "rutorrent": {
    "download_folder": "/mnt/local/downloads/torrents/rutorrent/completed",
    "url": "https://user:pass@rutorrent.domain.com",
    "path_mappings": {
      "/mnt/local/downloads/torrents/": [
        "/downloads/torrents/"
      ]
    }
  },
}
```


## core

```json
"core": {
  "debug": false
},
```

`debug` - Toggle debug messages in the log. Default is `false`.

  - Set to `true`, if you are having issues and want to diagnose why.

## cleanup

```json
"cleanup": {
  "auto_remove": false
},
```

`auto_remove` - To automatically delete orphan files.

  - If `false`, you will get a list of orphan files and you will be prompted to either delete them one-by-one or exit.

  - If `true`, you will get a list of orphan files and it will delete them all.

  - Default is `false`.

`show_total_orphans_size` - show total size of all orphan files. Default is `true`.

## rutorrent


```json
"rutorrent": {
  "download_folder": "/mnt/local/downloads/torrents/rutorrent/completed",
  "url": "https://user:pass@rutorrent.domain.com",
  "path_mappings": {
    "/mnt/local/downloads/torrents/": [
      "/downloads/torrents/"
    ]
  }
},
```

`download_folder` - Where all the completed downloads go.

  - If this is a Docker ruTorrent container, this will be the location on the host.

`url` - Your ruTorrent URL.

  - This can be in the form of `https://user:pass@ipaddress`


### path mappings

List of paths that will be remapped ruTorrent's download folder to the actual path on the host.

This section is relevant for ruTorrent docker containers.

#### Native Install

Format:
```json
"path_mappings": {
    "/path/to/downloads/on/host": [
        "/path/to/downloads/on/host"
    ]
},
```

Example:

```json
"path_mappings": {
    "/mnt/local/downloads/torrents/": [
        "/mnt/local/downloads/torrents/"
    ]
},
```

#### Docker Install

Format:

```json
"path_mappings": {
    "/path/to/downloads/on/host/": [
        "/path/to/downlods/in/rutorrent/container"
    ]
},
```

Example:

```json
"path_mappings": {
  "/mnt/local/downloads/torrents/": [
    "/downloads/torrents/"
  ]
}
```


# Usage


Command:
```
python3 cleanup.py
```

***

_If you find this project helpful, feel free to make a small donation via [Monzo](https://monzo.me/jamesbayliss9) (Credit Cards, Apple Pay, Google Pay, and others; no fees), [Paypal](https://www.paypal.me/l3uddz) (l3uddz@gmail.com), and Bitcoin (3CiHME1HZQsNNcDL6BArG7PbZLa8zUUgjL)._
