"""Denoise one frame with Intel OIDN. Called by oidn_render.py (system Python, not Blender).
Usage: python3 -I oidn_denoise.py <prefix>
Reads <prefix>color.npy, albedo.npy, normal.npy (H x W x 3 float32, linear HDR),
writes <prefix>out.npy."""
import ctypes
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "oidn-py"))
import numpy as np  # noqa: E402
import oidn  # noqa: E402

pre = sys.argv[1]
c, a, n = (np.ascontiguousarray(np.load(pre + k + ".npy").astype(np.float32))
           for k in ("color", "albedo", "normal"))
h, w, _ = c.shape
out = np.zeros_like(c)
lib = ctypes.CDLL(os.path.join(os.path.dirname(oidn.__file__), "lib.linux.x64",
                               f"libOpenImageDenoise.so.{oidn.oidn_version}"))
lib.oidnSetFilter1b.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_bool]
lib.oidnGetDeviceError.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_char_p)]
dev = oidn.NewDevice()
oidn.CommitDevice(dev)
flt = oidn.NewFilter(dev, "RT")
for name, img in (("color", c), ("albedo", a), ("normal", n), ("output", out)):
    oidn.SetSharedFilterImage(flt, name, img, oidn.FORMAT_FLOAT3, w, h)
lib.oidnSetFilter1b(flt, b"hdr", True)
oidn.CommitFilter(flt)
oidn.ExecuteFilter(flt)
msg = ctypes.c_char_p()
if lib.oidnGetDeviceError(dev, ctypes.byref(msg)):
    sys.exit(f"OIDN error: {msg.value}")
oidn.ReleaseFilter(flt)
oidn.ReleaseDevice(dev)
np.save(pre + "out.npy", out)
