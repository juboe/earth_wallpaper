#!/usr/bin/env python3
"""
Cleanup script for old wallpaper images.
Deletes wallpaper files older than a specified number of days.
"""

import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple


def parse_date_from_filename(filename: str) -> datetime | None:
    """Extract date from wallpaper filename format: wallpaper-device-YYYY-MM-DD.png"""
    pattern = r'wallpaper-[^-]+-(\d{4}-\d{2}-\d{2})\.png'
    match = re.match(pattern, filename)
    if match:
        try:
            return datetime.strptime(match.group(1), '%Y-%m-%d')
        except ValueError:
            return None
    return None


def find_old_wallpapers(directory: Path, max_age_days: int) -> List[Tuple[Path, datetime]]:
    """Find wallpaper files older than max_age_days."""
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    old_files = []
    
    for file_path in directory.glob('wallpaper-*.png'):
        file_date = parse_date_from_filename(file_path.name)
        if file_date and file_date < cutoff_date:
            old_files.append((file_path, file_date))
    
    return sorted(old_files, key=lambda x: x[1])  # Sort by date


def cleanup_old_wallpapers(directory: Path = None, max_age_days: int = 30, dry_run: bool = False) -> int:
    """
    Clean up old wallpaper files.
    
    Args:
        directory: Directory to search (default: current directory)
        max_age_days: Maximum age in days before deletion (default: 30)
        dry_run: If True, only show what would be deleted without actually deleting
    
    Returns:
        Number of files deleted (or would be deleted in dry_run mode)
    """
    if directory is None:
        directory = Path.cwd()
    
    old_files = find_old_wallpapers(directory, max_age_days)
    
    if not old_files:
        print(f"ℹ️  No wallpaper files older than {max_age_days} days found.")
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    action = "Would delete" if dry_run else "Deleting"
    print(f"🧹 {action} {len(old_files)} wallpaper files older than {cutoff_date.strftime('%Y-%m-%d')}:")
    
    deleted_count = 0
    for file_path, file_date in old_files:
        age_days = (datetime.now() - file_date).days
        print(f"  - {file_path.name} (from {file_date.strftime('%Y-%m-%d')}, {age_days} days old)")
        
        if not dry_run:
            try:
                file_path.unlink()
                deleted_count += 1
            except OSError as e:
                print(f"    ❌ Error deleting {file_path.name}: {e}")
        else:
            deleted_count += 1
    
    if not dry_run and deleted_count > 0:
        print(f"✅ Successfully deleted {deleted_count} old wallpaper files.")
    elif dry_run:
        print(f"🔍 Dry run complete. {deleted_count} files would be deleted.")
    
    return deleted_count


def main():
    """Main function with command line argument handling."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up old wallpaper images")
    parser.add_argument(
        "--max-age", 
        type=int, 
        default=30, 
        help="Maximum age in days before deletion (default: 30)"
    )
    parser.add_argument(
        "--directory", 
        type=Path, 
        default=None, 
        help="Directory to search (default: current directory)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Show what would be deleted without actually deleting"
    )
    parser.add_argument(
        "--quiet", 
        action="store_true", 
        help="Minimal output"
    )
    
    args = parser.parse_args()
    
    if args.directory and not args.directory.exists():
        print(f"❌ Directory {args.directory} does not exist.")
        sys.exit(1)
    
    try:
        deleted_count = cleanup_old_wallpapers(
            directory=args.directory,
            max_age_days=args.max_age,
            dry_run=args.dry_run
        )
        
        if args.quiet:
            print(deleted_count)
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n❌ Cleanup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()