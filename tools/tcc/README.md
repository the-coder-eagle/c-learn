# TCC (Tiny C Compiler) Setup

TCC is a tiny (~300KB) but fully functional C compiler. It compiles and runs
C code in milliseconds — no Docker, no installation, just a single executable.

## Download

1. Go to: https://download.savannah.gnu.org/releases/tinycc/
2. Download the latest Windows binary: `tcc-0.9.27-win64-bin.zip`
3. Extract `tcc.exe` into this directory (`tools/tcc/`)

Or on Linux/Mac:
```bash
# Ubuntu/Debian
sudo apt install tcc

# macOS
brew install tcc

# Or download binary from savannah
```

## Verify

```bash
tools/tcc/tcc -version
# Should print: tcc version 0.9.27 (x86_64 Windows)

echo '#include <stdio.h>
int main() { printf("Hello from TCC!\n"); return 0; }' | tools/tcc/tcc -run -
# Should print: Hello from TCC!
```

## How it works in C Learn

When `tools/tcc/tcc.exe` (Windows) or `tcc` (Linux/Mac) is found,
the compiler service automatically uses it as the first-choice backend.

Priority chain:
1. **TCC** — fastest, real C11 compiler, works everywhere
2. **Docker sandbox (GCC)** — most secure, sandboxed execution
3. **Local GCC** — system compiler
4. **Mock simulation** — last resort (Windows without any compiler)

## Security note

TCC executes code directly on the host machine (no sandbox). For production
environments handling untrusted code, use the Docker sandbox path instead.
You can force Docker-only by setting `DOCKER_ENABLED=true` and removing `tcc.exe`.
