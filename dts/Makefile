dtbo = usb-bcm2708-pi4.dtbo

all: $(dtbo)

%.dtbo: %-overlay.dts
	dtc -I dts -O dtb -o $@ $<

clean:
	rm -f *.dtbo

