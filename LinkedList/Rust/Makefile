# SPDX-License-Identifier: GPL-2.0
KDIR ?= /lib/modules/$(shell uname -r)/build

obj-m += rust_list_benchmark.o

# Build everything (both C and Rust code)
all:
	$(MAKE) LLVM=1 -C $(KDIR) M=$(PWD) CFLAGS_MODULE += -g modules 

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean

