# qemu-raspi

import argparse
import json
import os
from subprocess import check_call

from . import device_tree, log


def qemu(
    model,
    dtb,
    kernel,
    initrd=None,
    image=None,
    cmdline=None,
    earlycon=False,
    console=[],
    config=[],
    dry_run=False,
    qemu_args=[],
    overlays_dir=".",
    dtmerge_bin="dtmerge",
    qemu_bin="qemu-system-aarch64",
):
    """Call QEMU"""
    # Model specifics
    if model == "pi3":
        machine = "raspi3b"
        earlycon_opts = "earlycon=pl011,mmio32,0x3f215040"
    else:
        machine = "raspi4b"
        earlycon_opts = "earlycon=pl011,mmio32,0xfe201000"

    # (Pre-) assemble the kernel commandline
    # TODO: Use bootargs from the DTB?
    if cmdline:
        cmdline = cmdline.split(" ")
    else:
        cmdline = ["ignore_loglevel"]
    if earlycon:
        cmdline.append(earlycon_opts)
    if console:
        # Remove existing console arguments before adding explicit ones
        cmdline = [c for c in cmdline if not c.startswith("console=")]
        cmdline.extend([f"console={c}" for c in console])

    # Process config
    dtmerge = []
    for cfg in config:
        if cfg.startswith("dtparam=") or cfg.startswith("dtoverlay="):
            dtmerge.append(cfg.split("=", 1))
            continue
        if cfg == "enable_uart=1":
            cmdline.append("8250.nr_uarts=1")
            continue
        log.warn(f"Ignored config: {cfg}")

    # Create the DTB to use with QEMU
    qemu_dtb = dtb.replace(".dtb", "-qemu.dtb")
    dtmerge_bin = os.path.join(os.path.dirname(__file__), os.pardir, "dtmerge", "dtmerge")
    device_tree.merge(dtb, qemu_dtb, dtmerge, overlays_dir=overlays_dir, dtmerge_bin=dtmerge_bin)

    # Assemble the QEMU command
    # fmt: off
    cmd = [
        qemu_bin,
        "-machine", machine,
        "-dtb", qemu_dtb,
        "-kernel", kernel,
        "-append", " ".join(cmdline),
        "-device", "usb-kbd",
        "-device", "usb-mouse",
        "-device", "usb-net,netdev=net0",
        "-netdev", "user,id=net0,hostfwd=tcp::5022-:22",
        "-drive", f"file={image},if=sd,format=raw,index=0"
    ]
    # fmt: on
    if initrd:
        cmd.extend(["-initrd", initrd])
    cmd.extend(qemu_args)

    log.info(cmd)
    if not dry_run:
        check_call(cmd)


def merge_config_json(args):
    if not args.config_json:
        return args

    log.info(f"Load config from: {args.config_json}")
    with open(args.config_json, encoding="utf-8") as fh:
        config = json.load(fh)

    config_dir = os.path.dirname(args.config_json)

    if not args.model:
        args.model = config["model"]
    if not args.dtb:
        args.dtb = os.path.join(config_dir, config["dtb"])
    if not args.kernel:
        args.kernel = os.path.join(config_dir, config["kernel"])
    if not args.initrd:
        args.initrd = os.path.join(config_dir, config["initramfs"])
    if not args.overlays:
        args.overlays = os.path.join(config_dir, "overlays")

    if not args.config:
        for x in config["dtparam"]:
            args.config.append(f"dtparam={x}")
        for x in config["dtoverlay"]:
            args.config.append(f"dtoverlay={x}")
        for x in config["misc"]:
            args.config.append(x)

    if not args.cmdline:
        cmdline_txt = os.path.join(config_dir, config["cmdline"])
        with open(cmdline_txt, encoding="utf-8") as fh:
            args.cmdline = fh.readline().strip()

    return args


#
# Main entry point
#


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["pi3", "pi4"], help="Raspberry Pi model")
    parser.add_argument("--dtb", help="DTB file")
    parser.add_argument("--kernel", help="Kernel file")
    parser.add_argument("--initrd", help="Initramfs file")
    parser.add_argument("--overlays", help="Directory with the DTB overlays")
    parser.add_argument("--cmdline", help="Kernel commandline")
    parser.add_argument("--earlycon", action="store_true", help="Add 'earlycon=...' to the kernel commandline")
    parser.add_argument("--console", action="append", help="Add 'console=...' to the kernel commandline")
    parser.add_argument("--config", action="append", default=[], help="Specify config.txt settings")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--image", help="OS image file")
    parser.add_argument("--config-json", help="config.json config file")
    parser.add_argument("--qemu-bin", default="qemu-system-aarch64", help="QEMU binary")
    parser.add_argument("qemu_args", metavar="-- QEMU_ARG", nargs="*", help="Additional QEMU arguments")
    args = parser.parse_args()

    log.enable_logging(verbose=args.verbose, debug=args.debug)

    for f in (args.dtb, args.kernel, args.initrd, args.overlays, args.image, args.config_json):
        if f and not os.path.exists(f):
            log.error(f"No such file or directory: {f}")
            return 1

    args = merge_config_json(args)

    qemu(
        args.model,
        args.dtb,
        args.kernel,
        initrd=args.initrd,
        image=args.image,
        cmdline=args.cmdline,
        earlycon=args.earlycon,
        console=args.console,
        config=args.config,
        overlays_dir=args.overlays,
        dry_run=args.dry_run,
        qemu_bin=args.qemu_bin,
        qemu_args=args.qemu_args,
    )

    return 0
