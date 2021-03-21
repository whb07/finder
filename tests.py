from .main import (
    serialized,
    get_all_files,
    Module,
    import_headers,
    get_file,
    get_module,
    File,
)
import itertools
from pathlib import Path


def test_serialized():
    path = "/tmp/bitcoin/src/crypto/ctaes"
    result = {path: ["COPYING", "README.md", "bench.c", "ctaes.c", "ctaes.h", "test.c"]}
    ctaes = serialized(path)
    assert set(result[path]) == set(ctaes[path])
    assert result.keys() == ctaes.keys()

    path = "/tmp/bitcoin/src/crypto"
    crypto = serialized(path)

    assert "crypto" in list(crypto.keys())[0]
    child = list(filter(lambda n: isinstance(n, dict), crypto[path]))
    assert child
    assert set(str(ctaes)) == set(str(child[0]))

    assert len(crypto[path]) == 34


def test_get_all_files():
    path = "/tmp/bitcoin/src"
    result = get_all_files(path)

    assert isinstance(result, dict)
    directories = [
        "/tmp/bitcoin/src/consensus",
        "/tmp/bitcoin/src/leveldb",
        "/tmp/bitcoin/src/bench",
        "/tmp/bitcoin/src/crypto",
        "/tmp/bitcoin/src/crc32c",
        "/tmp/bitcoin/src/compat",
        "/tmp/bitcoin/src/test",
        "/tmp/bitcoin/src/util",
        "/tmp/bitcoin/src/config",
        "/tmp/bitcoin/src/qt",
        "/tmp/bitcoin/src/script",
        "/tmp/bitcoin/src/primitives",
        "/tmp/bitcoin/src/secp256k1",
        "/tmp/bitcoin/src/support",
        "/tmp/bitcoin/src/wallet",
        "/tmp/bitcoin/src/index",
        "/tmp/bitcoin/src/node",
        "/tmp/bitcoin/src/rpc",
        "/tmp/bitcoin/src/univalue",
        "/tmp/bitcoin/src/logging",
        "/tmp/bitcoin/src/zmq",
        "/tmp/bitcoin/src/policy",
        "/tmp/bitcoin/src/interfaces",
    ]

    sub_dirs = list(
        itertools.chain(*[list(k.keys()) for k in result[path] if isinstance(k, dict)])
    )
    assert set(directories).issubset(sub_dirs)


def test_xmodule():
    module = Module(name="crypto", contents=list())
    assert module.name == "crypto"
    assert module.contents == []
    module.contents.append(File(name="crypto/sha256.h", imports=[]))
    assert module.owns_file("<crypto/sha256.h>")
    assert module.owns_file("crypto/sha256.h")

    assert module.get_file("crypto/sha256.h") is module.contents[0]


def test_import_headers():
    assert set(["ctaes.h", "<stdio.h>", "<string.h>", "<assert.h>"]) == set(
        import_headers(Path("/tmp/bitcoin/src/crypto/ctaes/test.c").read_text())
    )
    headers = import_headers(
        Path("/tmp/bitcoin/src/leveldb/port/port_stdcxx.h").read_text()
    )
    should_have = [
        "port/port_config.h",
        "<crc32c/crc32c.h>",
        "<snappy.h>",
        "<cassert>",
        "<condition_variable>",
        "<cstddef>",
        "<cstdint>",
        "<mutex>",
        "<string>",
        "port/thread_annotations.h",
    ]
    assert set(headers) == set(should_have)


def test_get_file():
    path = "/tmp/bitcoin/src/crypto/ctaes/test.c"
    test_file = get_file(path)
    assert test_file.name == path
    assert len(test_file.imports) == 4


def test_module():
    path = "/tmp/bitcoin/src/crypto"
    result = get_module(get_all_files(path))
    assert result.name == path
    assert len(result.contents) == 34
    subdirs = [k for k in result.contents if isinstance(k, Module)]
    assert len(subdirs) == 1
    assert "ctaes" in subdirs[0].name
    assert len(subdirs[0].contents) == 6
