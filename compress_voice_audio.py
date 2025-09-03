#!/usr/bin/env python3
import argparse
import shutil
import subprocess
from pathlib import Path

SUPPORTED_INPUT_EXTS = {".m4a", ".aifc"}

def have_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None

def build_output_path(src: Path, outdir: Path, overwrite: bool) -> Path:
    """
    - For .m4a inputs: keep .m4a, add "_compressed" before extension unless overwriting.
    - For .aifc inputs: convert to .m4a.
    - Preserve relative directory structure under outdir.
    """
    rel = src.relative_to(root_in)
    base = rel.stem
    if src.suffix.lower() == ".aifc":
        target_name = f"{base}.m4a"
    else:
        target_name = f"{base}.m4a" if overwrite else f"{base}_compressed.m4a"
    return outdir / rel.parent / target_name

def compress_file(src: Path, dst: Path, bitrate: str, samplerate: int, dry_run: bool, extra_ffmpeg_args: list[str]) -> int:
    dst.parent.mkdir(parents=True, exist_ok=True)

    # ffmpeg command:
    # -ac 1            -> mono (voice)
    # -ar <samplerate> -> sample rate (e.g., 24000 for voice)
    # -c:a aac         -> AAC encoder
    # -b:a <bitrate>   -> target bitrate (e.g., 32k)
    # -movflags +faststart -> better streaming/startup for m4a
    # -map_metadata 0  -> copy source metadata
    # -y               -> overwrite destination file if exists (we control via logic)
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-i", str(src),
        "-ac", "1",
        "-ar", str(samplerate),
        "-c:a", "aac",
        "-b:a", bitrate,
        "-movflags", "+faststart",
        "-map_metadata", "0",
        "-y",
        *extra_ffmpeg_args,
        str(dst),
    ]

    if dry_run:
        print("[DRY RUN] Would run:", " ".join(cmd))
        return 0

    print(f"Compressing: {src}  ->  {dst}")
    try:
        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            print(f"  ❌ ffmpeg failed for: {src} (exit {result.returncode})")
        else:
            print(f"  ✅ Done: {dst}")
        return result.returncode
    except FileNotFoundError:
        print("❌ ffmpeg not found. Please install ffmpeg and try again.")
        return 127

def scan_inputs(root: Path) -> list[Path]:
    files = []
    for ext in SUPPORTED_INPUT_EXTS:
        files.extend(root.rglob(f"*{ext}"))
        files.extend(root.rglob(f"*{ext.upper()}"))
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for f in files:
        if f not in seen:
            unique.append(f)
            seen.add(f)
    return unique

def parse_args():
    p = argparse.ArgumentParser(
        description="Compress voice audio in a folder (.aifc, .m4a) using ffmpeg (AAC)."
    )
    p.add_argument(
        "input_dir",
        type=Path,
        help="Folder to scan (recursively) for audio files."
    )
    p.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=None,
        help="Where to write compressed files. Defaults to '<input_dir>/compressed'."
    )
    p.add_argument(
        "--bitrate",
        default="32k",
        help="Audio bitrate (e.g., 24k, 32k, 48k). Default: 32k"
    )
    p.add_argument(
        "--samplerate",
        type=int,
        default=24000,
        help="Sample rate in Hz (e.g., 16000, 24000, 32000). Default: 24000"
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite original file names (writes .m4a with same base name)."
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without writing files."
    )
    p.add_argument(
        "--extra-ffmpeg-args",
        nargs=argparse.REMAINDER,
        default=[],
        help="Anything after this flag is passed straight to ffmpeg (advanced use)."
    )
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()

    global root_in  # used by build_output_path
    root_in = args.input_dir.expanduser().resolve()
    if not root_in.exists() or not root_in.is_dir():
        raise SystemExit(f"Input directory does not exist or is not a directory: {root_in}")

    if not have_ffmpeg():
        raise SystemExit("ffmpeg is required but was not found in PATH. Install it (e.g., 'brew install ffmpeg').")

    outdir = (args.output_dir or (root_in / "compressed")).expanduser().resolve()

    inputs = scan_inputs(root_in)
    if not inputs:
        print(f"No .aifc or .m4a files found under: {root_in}")
        raise SystemExit(0)

    print(f"Found {len(inputs)} input file(s). Output dir: {outdir}")
    failures = 0

    for src in inputs:
        dst = build_output_path(src, outdir, args.overwrite)
        # Skip if destination exists and not overwriting originals
        if dst.exists() and not args.dry_run:
            print(f"Skipping (already exists): {dst}")
            continue
        rc = compress_file(
            src=src,
            dst=dst,
            bitrate=args.bitrate,
            samplerate=args.samplerate,
            dry_run=args.dry_run,
            extra_ffmpeg_args=args.extra_ffmpeg_args,
        )
        if rc != 0:
            failures += 1

    if failures:
        print(f"\nCompleted with {failures} failure(s).")
    else:
        print("\nAll files processed successfully.")
