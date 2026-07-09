# Decompyle++ (pycdc) — decompile Python 3.7 .pyc from PyInstaller games.
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates build-essential cmake \
 && git clone --depth 1 https://github.com/zrax/pycdc /pycdc \
 && cd /pycdc && cmake . && make -j"$(nproc)" \
 && apt-get purge -y git cmake && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
WORKDIR /work
ENTRYPOINT ["/pycdc/pycdc"]
