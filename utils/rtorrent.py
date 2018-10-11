import logging
import os

from .xmlrpc import ServerProxy

log = logging.getLogger(__name__)


class Rtorrent:
    def __init__(self, url):
        self.url = "%s/RPC2" % url
        self.xmlrpc = ServerProxy(self.url)

    def get_torrents(self):
        torrent_list = {}
        try:
            with self.xmlrpc as proxy:
                torrent_list_raw = proxy.d.multicall2(
                    # List type
                    "",
                    # View
                    "",
                    # Attributes
                    "d.hash=",
                    "d.name=",
                    "d.is_multi_file=",
                    "d.base_path=",
                    "d.complete=",
                    "d.is_open=",
                    "d.custom1=",
                    "d.directory="
                )

                for t in torrent_list_raw:
                    # Get files if multifile torrent
                    files = None
                    if t[2]:
                        files = proxy.f.multicall(
                            # Hash
                            t[0],
                            # Pattern
                            "",
                            # Get files path
                            "f.path="
                        )
                        # Flatten list
                        files = [os.path.join(t[7], f) for subf in files for f in subf]
                    else:
                        files = [os.path.join(t[7], t[1])]

                    torrent_list[t[0]] = {
                        'hash': t[0],
                        'name': t[1],
                        'is_multi_file': t[2],
                        'base_path': t[3],
                        'files': files,
                        'complete': t[4],
                        'is_open': t[5],
                        'label': t[6],
                        'directory': t[7]
                    }

            return torrent_list

        except Exception:
            log.exception("Exception retrieving torrents: ")
        return {}
