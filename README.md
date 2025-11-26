Simple scripts to run Raspberry Pi images with QEMU
----------------------------------------------------

*** This is very much work in progress and likely broken at the moment. ***

Rational: QEMU doesn't emulate the Pi bootloader and only supports direct boot
using -kernel, -dtb and -initrd, ... arguments. With that one has to first
extract these boot files from an image and supply them to QEMU via commandline
arguments. The collection of scripts in this repo aim to simplify that process.
In addition the scripts will (try to) parse config.txt and modify the DTB and
QEMU commandline arguments accordingly to emulated the Pi as closely as possible.

 1. Build dtmerge:

        $ make dtmerge

 2. Download a Raspberry Pi image, for example Ubuntu:

        $ wget https://cdimage.ubuntu.com/releases/questing/release/ubuntu-25.10-preinstalled-server-arm64+raspi.img.xz

    or Debian:

        $ wget https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2025-10-02/2025-10-01-raspios-trixie-arm64-lite.img.xz

 3. Uncompress and resize the image. The QEMU raspi machine wants the image size to be a power of 2.

        $ unxz <image>.xz
        $ qemu-img resize -f raw <image> 8G

 4. Run the image:

        $ ./run-qemu --model pi4 <image> --verbose


QEMU doesn't seem to like some of Ubuntu's kernel configs and the display stays blank until the
console switch. Be patient, takes ~60 secondss.


Example to specify the commandline explicitly and set the memory size to 2GB:

    $ ./run-qemu --model pi4 ubuntu-25.10-preinstalled-server-arm64+raspi.img --verbose --cmdline "console=tty1 root=LABEL=writable rootfstype=ext4 rootwait net.ifnames=0" -- -m 2048
