#include <linux/module.h>
#include <linux/export-internal.h>
#include <linux/compiler.h>

MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__section(".gnu.linkonce.this_module") = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

KSYMTAB_FUNC(mutex_benchmark_test, "", "");
KSYMTAB_FUNC(take_and_release, "", "");

MODULE_INFO(depends, "");


MODULE_INFO(srcversion, "3D01F3176B35DE932FC642B");
