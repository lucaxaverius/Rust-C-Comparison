# SPDX-License-Identifier: GPL-2.0
KDIR ?= /lib/modules/$(shell uname -r)/build

obj-m += rust_mutex_benchmark.o

# Build everything (both C and Rust code)
all:
	$(MAKE) -s LLVM=1 -C $(KDIR) M=$(PWD) EXTRA_CFLAGS=-g modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean

