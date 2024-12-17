# Perf Analysis

## 0) **Initialize the module**
Compile the kernel module, then copy it with:
```bash
sudo cp test_module.ko /lib/modules/$(uname -r)/extra/
```

Then update the dependency:
```bash
sudo depmod -a
```

## 1) **Launch the recording** 
```bash
sudo perf record -e cycles,instructions,cache-misses,page-faults,branch-misses,context-switches,cache-references,cpu-clock,branches -g -a
```
## 2) **Insert the test module**
```bash
sudo modprobe test_module 
```
## 3) **Stop the recording with CTRL+C and produce the report**
```bash
sudo perf report --kallsyms=/proc/kallsyms
```