import os
from pathlib import Path

from fastapi import UploadFile


def save_upload_to_disk(upload: UploadFile, dest_dir: str) -> str:
    os.makedirs(dest_dir, exist_ok=True)
    suffix = Path(upload.filename).suffix
    # keep filename-ish, but avoid empty
    stem = Path(upload.filename).stem or "upload"
    out_path = os.path.join(dest_dir, f"{stem}{suffix}")
    with open(out_path, "wb") as f:
        f.write(upload.file.read())
    return out_path

