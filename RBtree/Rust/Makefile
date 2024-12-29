# SPDX-License-Identifier: GPL-2.0
KDIR ?= /lib/modules/$(shell uname -r)/build

obj-m += rust_rbtree_benchmark.o

# Add custom flags for debugging and preventing inlining
EXTRA_CFLAGS := -pg -g -fno-inline
RUSTFLAGS := -C debuginfo=2 

# Build everything (both C and Rust code)
all: 
	$(MAKE) LLVM=1 -C $(KDIR) M=$(PWD) modules

perf:
	$(MAKE) -s LLVM=1 -C $(KDIR) M=$(PWD) \
	EXTRA_CFLAGS="$(EXTRA_CFLAGS)" \
	KRUSTFLAGS="$(RUSTFLAGS)" \
	modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
