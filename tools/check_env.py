import importlib.util
import glob
import os
from PIL import Image

for m in ("numpy", "scipy", "cv2"):
    print(m, "OK" if importlib.util.find_spec(m) else "MISSING")

files = sorted(glob.glob(r"C:/Project/Workbuddy/equ-us-ci/产品资料/fengtu_*.jpg"))
print("--- sizes ---")
for f in files:
    im = Image.open(f)
    print(os.path.basename(f), im.size, str(os.path.getsize(f) // 1024) + "KB")
