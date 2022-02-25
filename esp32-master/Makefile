CC=arduino-cli
CFLAGS=-b esp32:esp32:esp32 -u -p /dev/cu.SLAB_USBtoUART

.PHONY: client demo_controls clean

client: client.ino
	$(CC) compile $(CFLAGS) -o client client.ino

demo_controls: demo_controls.ino
	$(CC) compile $(CFLAGS) -o demo_controls demo_controls.ino

clean:
	rm *.bin *.elf
