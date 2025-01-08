savedcmd_mutex_benchmark.mod := printf '%s\n'   mutex_benchmark.o | awk '!x[$$0]++ { print("./"$$0) }' > mutex_benchmark.mod
