# SPDX-License-Identifier: GPL-2.0

KDIR ?= /lib/modules/$(shell uname -r)/build
obj-m := list_benchmark.o 

# Add custom flags for debugging and preventing inlining
EXTRA_CFLAGS := -pg -fno-inline

# Build everything (both C and Rust code)
all:
	$(MAKE) LLVM=1 -C $(KDIR) M=$(PWD) modules
perf:
	$(MAKE) -s LLVM=1 -C $(KDIR) M=$(PWD) EXTRA_CFLAGS="$(EXTRA_CFLAGS)" modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
	
