# device_tree

import os
import shutil
from subprocess import check_call

from . import log


class DeviceTreeError(Exception):
    pass


def merge(indtb, outdtb, dtmerge, overlays_dir="overlays", dtmerge_bin="dtmerge"):
    """Merge DTB overlays and params"""
    shutil.copy(indtb, outdtb)
    if not dtmerge:
        return

    tmpdtb = outdtb + ".tmp"
    for key, val in dtmerge:
        shutil.copy(outdtb, tmpdtb)
        if key == "dtparam":
            log.info(f"Merge dtparam: {val}")
            check_call([dtmerge_bin, tmpdtb, outdtb, "-", val])
            continue

        if key == "dtoverlay":
            if val.startswith("vc4-kms"):
                log.warn(f"Ignore dtoverlay: {val}")
                continue

            log.info(f"Merge dtoverlay: {val}")
            dtbo = f"{overlays_dir}/{val}.dtbo"
            if not os.path.exists(dtbo):
                raise DeviceTreeError(f"dtoverlay does not exist: {dtbo}")
            check_call([dtmerge_bin, tmpdtb, outdtb, dtbo])
            continue

        log.warn(f"Unknown dtmerge entry: {key} {val}")

    os.remove(tmpdtb)
