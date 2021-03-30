CFLAGS := -m32 -std=gnu99 -g -O0 -fno-stack-protector -z execstack

ALL := shellcode.bin target

all: $(ALL)

target: target.c
	$(CC) $(CFLAGS) -o $@ $<

%.o: %.S
	$(CC) -m32 -c -o $@ $<

%.bin: %.o
	objcopy -S -O binary -j .text $< $@

test: $(ALL)
	objdump -m i386 -D -b binary shellcode.bin
	bash -c '(cat shellcode.bin; echo; cat) | strace -e execve ./target'

readflag: $(ALL)
	bash -c 'echo "cat /proc/flag" | (cat shellcode.bin; echo; cat) | ./target'

clean:
	rm -f $(ALL) *.bin

.PHONY: all clean