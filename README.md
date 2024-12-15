# Perf Analysis

## 1) **Launch the recording** 
```bash
sudo perf record -e cycles,instructions,cache-misses,page-faults,branch-misses,context-switches,cache-references,cpu-clock,branches -g -a
```
## 2) **Insert the test module**
```bash
sudo insmod test_module.ko 
```
## 3) **Stop the recording with CTRL+C and produce the report**
```bash
sudo perf report --kallsyms=/proc/kallsyms
```