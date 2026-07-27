import msgpack
import os

INPUT_FILE = "graph-forfeits.msgpack"
OUTPUT_DIR = "graph_chunks"

MAX_SIZE_MB = 50
MAX_SIZE = MAX_SIZE_MB * 1024 * 1024

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading graph...")
with open(INPUT_FILE, "rb") as f:
    graph = msgpack.unpackb(
        f.read(),
        raw=False,
        strict_map_key=False
    )

print(f"Loaded {len(graph)} nodes")

chunk = {}
chunk_size = 0
chunk_num = 0

def save_chunk(data, num):
    output = os.path.join(
        OUTPUT_DIR,
        f"graph-{num:04}.msgpack"
    )

    with open(output, "wb") as f:
        f.write(msgpack.packb(data, use_bin_type=True))

    size = os.path.getsize(output) / 1024 / 1024
    print(f"Created {output} ({len(data)} nodes, {size:.2f} MB)")


for key, value in graph.items():
    packed_value = msgpack.packb(
        {key: value},
        use_bin_type=True
    )

    chunk[key] = value
    chunk_size += len(packed_value)

    if chunk_size >= MAX_SIZE:
        save_chunk(chunk, chunk_num)
        chunk_num += 1
        chunk = {}
        chunk_size = 0

if chunk:
    save_chunk(chunk, chunk_num)

print("Done")