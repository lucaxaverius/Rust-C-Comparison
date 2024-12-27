savedcmd_rust_list_benchmark.o := OBJTREE=/home/rustxave/Scrivania/6.13/linux RUST_MODFILE=./rust_list_benchmark rustc --edition=2021 -Zbinary_dep_depinfo=y -Astable_features -Dnon_ascii_idents -Dunsafe_op_in_unsafe_fn -Wmissing_docs -Wrust_2018_idioms -Wunreachable_pub -Wclippy::all -Wclippy::ignored_unit_patterns -Wclippy::mut_mut -Wclippy::needless_bitwise_bool -Wclippy::needless_continue -Aclippy::needless_lifetimes -Wclippy::no_mangle_with_rust_abi -Wclippy::undocumented_unsafe_blocks -Wclippy::unnecessary_safety_comment -Wclippy::unnecessary_safety_doc -Wrustdoc::missing_crate_level_docs -Wrustdoc::unescaped_backticks -Cpanic=abort -Cembed-bitcode=n -Clto=n -Cforce-unwind-tables=n -Ccodegen-units=1 -Csymbol-mangling-version=v0 -Crelocation-model=static -Zfunction-sections=n -Wclippy::float_arithmetic --target=/home/rustxave/Scrivania/6.13/linux/scripts/target.json -Ctarget-feature=-sse,-sse2,-sse3,-ssse3,-sse4.1,-sse4.2,-avx,-avx2 -Ztune-cpu=generic -Cno-redzone=y -Ccode-model=kernel -Copt-level=2 -Cdebug-assertions=n -Coverflow-checks=n -Cforce-frame-pointers=y -Zdwarf-version=5 -Cdebuginfo=2 -C debuginfo=2  --cfg MODULE  @/home/rustxave/Scrivania/6.13/linux/include/generated/rustc_cfg -Zallow-features=asm_const,asm_goto,arbitrary_self_types,lint_reasons -Zcrate-attr=no_std -Zcrate-attr='feature(asm_const,asm_goto,arbitrary_self_types,lint_reasons)' -Zunstable-options --extern kernel --crate-type rlib -L /home/rustxave/Scrivania/6.13/linux/rust/ --crate-name rust_list_benchmark --sysroot=/dev/null --out-dir ./ --emit=dep-info=./.rust_list_benchmark.o.d --emit=obj=rust_list_benchmark.o rust_list_benchmark.rs  ; /home/rustxave/Scrivania/6.13/linux/tools/objtool/objtool --hacks=jump_label --hacks=noinstr --mcount --mnop --retpoline --stackval --static-call --uaccess   --module rust_list_benchmark.o

source_rust_list_benchmark.o := rust_list_benchmark.rs

deps_rust_list_benchmark.o := \
  /home/rustxave/Scrivania/6.13/linux/rust/libcore.rmeta \
  /home/rustxave/Scrivania/6.13/linux/rust/libcompiler_builtins.rmeta \
  /home/rustxave/Scrivania/6.13/linux/rust/libkernel.rmeta \
  /home/rustxave/Scrivania/6.13/linux/rust/libffi.rmeta \
  /home/rustxave/Scrivania/6.13/linux/rust/libmacros.so \
  /home/rustxave/Scrivania/6.13/linux/rust/libbindings.rmeta \
  /home/rustxave/Scrivania/6.13/linux/rust/libuapi.rmeta \
  /home/rustxave/Scrivania/6.13/linux/rust/libbuild_error.rmeta \

rust_list_benchmark.o: $(deps_rust_list_benchmark.o)

$(deps_rust_list_benchmark.o):

rust_list_benchmark.o: $(wildcard /home/rustxave/Scrivania/6.13/linux/tools/objtool/objtool)
