def bytes_to_string(size_bytes):
    """
    reference: https://stackoverflow.com/a/6547474
    """
    try:
        if size_bytes == 1:
            # because I really hate unnecessary plurals
            return "1 B"

        suffixes_table = [('B', 0), ('KB', 0), ('MB', 1), ('GB', 2), ('TB', 2), ('PB', 2)]

        num = float(size_bytes)
        for suffix, precision in suffixes_table:
            if num < 1024.0:
                break
            num /= 1024.0

        if precision == 0:
            formatted_size = "%d" % num
        else:
            formatted_size = str(round(num, ndigits=precision))

        return "%s %s" % (formatted_size, suffix)
    except Exception:
        pass
    return "%d B" % size_bytes


def kbps_to_string(size_kbps):
    try:
        if size_kbps < 1024:
            return "%d Kbps" % size_kbps
        else:
            return "{:.2f} Mbps".format(size_kbps / 1024.)
    except Exception:
        pass
    return "%d Bbps" % size_kbps


def remap_file_paths(file_paths: list, path_mappings: dict) -> list:
    remapped_file_paths = []

    def _remap_single_path(file_path: str, _path_mappings: dict) -> str:
        for map_to_path, paths_to_remap in _path_mappings.items():
            for path_to_remap in paths_to_remap:
                if file_path.startswith(path_to_remap):
                    return file_path.replace(path_to_remap, map_to_path)
        return file_path

    for path in file_paths:
        remapped_file_paths.append(_remap_single_path(path, path_mappings))
    return remapped_file_paths
