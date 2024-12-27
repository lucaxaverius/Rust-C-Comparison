savedcmd_rust_list_benchmark.mod := printf '%s\n'   rust_list_benchmark.o | awk '!x[$$0]++ { print("./"$$0) }' > rust_list_benchmark.mod
