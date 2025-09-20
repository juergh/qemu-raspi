# config_txt

from . import log


def parse(fname, model=None, tryboot=False):
    log.info(f"Parse: {fname} (model={model}, tryboot={tryboot})")

    model_filter = {
        "pi4": "[pi4]",
        "pi3": "[pi3]",
    }

    dtb = {
        "pi4": "bcm2711-rpi-4-b.dtb",
        "pi3": "bcm2710-rpi-3-b.dtb",
    }

    kernel = {
        "pi4": "kernel8.img",
        "pi3": "kernel7.img",
    }

    initramfs = {
        "pi4": "initramfs8",
        "pi3": "initramfs7",
    }

    config = {
        "model": model,
        "filter": model_filter[model],
        "os_prefix": "",
        "overlay_prefix": "overlays/",
        "kernel": kernel[model],
        "initramfs": initramfs[model],
        "dtb": dtb[model],
        "dtparam": [],
        "dtoverlay": [],
        "cmdline": "cmdline.txt",
        "misc": [],
    }

    parse = True
    with open(fname, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line == "[all]":
                log.info("Found: [all]")
                parse = True
                continue

            if line == "[tryboot]" and tryboot:
                log.info("Found: [tryboot]")
                parse = True
                continue

            if line in config["filter"]:
                log.info(f"Found: {line}")
                parse = True
                continue

            if (line[0], line[-1]) == ("[", "]"):
                log.info(f"Found: {line} (Ignored)")
                parse = False
                continue

            if not parse:
                continue

            # initramfs is special :-/
            if line.startswith("initramfs "):
                key = "initramfs"
                val = line.split(" ")[1]
            else:
                key, val = line.split("=", 1)

            # Boot assets
            if key in ("os_prefix", "kernel", "initramfs", "cmdline"):
                config[key] = val
                continue

            # dtparam and dtoverlay
            if key in ("dtparam", "dtoverlay"):
                config[key].append(val)
                continue

            # Miscellaneous relevant configs
            if key in ("enable_uart",):
                config["misc"].append(line)
                continue

            log.warn(f"Ignored line: {line}")

    return config
