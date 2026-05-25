from pathlib import Path
import re
from typing import Optional
import zipfile
import requests

def normalize_filename(filename: str) -> str:
    filename = filename.replace(".0", "")
    name = filename.split(".")[0]
    return name

def _get_filename_from_cd(cd):
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]

def download_file(url: str, download_dir: Path, timeout=30) -> tuple[bool, Optional[Path]]:
    response = requests.get(url, timeout=timeout, allow_redirects=True)
    if response.status_code != 200:
        return False, None
    
    filename = _get_filename_from_cd(response.headers.get('content-disposition'))
    
    if not filename:
        if 'file_id=' in url:
            filename = url.split('file_id=')[-1]
        else:
            return False, None
    
    filepath = download_dir / filename
    with open(filepath, 'wb') as f:
        f.write(response.content)
    
    return True, filepath

def download_archive_and_unzip(url: str, download_dir, timeout=30) -> tuple[bool, Optional[list[Path]]]:
    ok, filepath = download_file(url, download_dir, timeout)
    if not ok:
        return False, None
    
    extract_dir = download_dir / "extracted"
    extract_dir.mkdir(exist_ok=True)
    
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    extracted_files = list(extract_dir.glob("*"))
    
    filepath.unlink()
    
    return True, extracted_files