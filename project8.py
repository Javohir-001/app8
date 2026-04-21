#!/usr/bin/env python3
"""
File Organizer Script
Point it at a folder (e.g. Downloads), and it automatically sorts files 
into subfolders by type (Images/, PDFs/, Videos/, etc.). Logs what it moved.
"""

import os
import shutil
import time
from datetime import datetime
from typing import Dict, List, Tuple

# File type categories and their extensions
FILE_CATEGORIES = {
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico', '.heic', '.heif'],
    'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.mpg', '.mpeg'],
    'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx', '.odp', '.csv'],
    'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.tar.gz', '.tar.bz2'],
    'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.rb', '.go', '.rs', '.swift', '.kt'],
    'Executables': ['.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm', '.app', '.apk'],
    'Fonts': ['.ttf', '.otf', '.woff', '.woff2', '.eot', '.fon'],
    'Ebooks': ['.epub', '.mobi', '.azw', '.azw3', '.fb2', '.lit'],
    'Design': ['.psd', '.ai', '.sketch', '.fig', '.xd', '.indd', '.cdr'],
    'Spreadsheets': ['.xls', '.xlsx', '.csv', '.ods', '.numbers'],
    'Presentations': ['.ppt', '.pptx', '.odp', '.key', '.pdf'],
    'Scripts': ['.bat', '.sh', '.ps1', '.cmd', '.py', '.js', '.vbs'],
    'Data': ['.json', '.xml', '.yaml', '.yml', '.sql', '.db', '.sqlite', '.mdb'],
    'System': ['.log', '.tmp', '.bak', '.cache', '.ini', '.cfg', '.conf']
}

# Files to ignore
IGNORE_EXTENSIONS = ['.part', '.crdownload', '.download', '.temp', '.tmp']
IGNORE_FILES = {'desktop.ini', 'thumbs.db', '.ds_store', '.gitignore'}

class FileOrganizer:
    def __init__(self, target_folder: str, log_file: str = "file_organizer.log"):
        self.target_folder = os.path.abspath(target_folder)
        self.log_file = log_file
        self.moved_files = []
        self.errors = []
        self.start_time = datetime.now()
        
        # Create log file
        self.setup_logging()
    
    def setup_logging(self) -> None:
        """Setup logging to file."""
        log_message = f"\n{'='*60}\n"
        log_message += f"FILE ORGANIZER SESSION\n"
        log_message += f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        log_message += f"Target folder: {self.target_folder}\n"
        log_message += f"{'='*60}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message)
    
    def log_message(self, message: str, level: str = "INFO") -> None:
        """Log a message to file and console."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        print(log_entry)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def get_file_category(self, filename: str) -> str:
        """Determine the category for a file based on its extension."""
        _, ext = os.path.splitext(filename.lower())
        
        # Check if file should be ignored
        if ext in IGNORE_EXTENSIONS or filename.lower() in IGNORE_FILES:
            return "IGNORE"
        
        # Find category
        for category, extensions in FILE_CATEGORIES.items():
            if ext in extensions:
                return category
        
        return "Other"
    
    def create_category_folder(self, category: str) -> str:
        """Create category folder if it doesn't exist."""
        category_folder = os.path.join(self.target_folder, category)
        
        if not os.path.exists(category_folder):
            os.makedirs(category_folder)
            self.log_message(f"Created folder: {category}")
        
        return category_folder
    
    def get_unique_filename(self, destination: str, filename: str) -> str:
        """Generate a unique filename if file already exists."""
        base, ext = os.path.splitext(filename)
        counter = 1
        
        while os.path.exists(os.path.join(destination, filename)):
            filename = f"{base}_{counter}{ext}"
            counter += 1
        
        return filename
    
    def move_file(self, file_path: str, category: str) -> bool:
        """Move a file to its category folder."""
        try:
            filename = os.path.basename(file_path)
            category_folder = self.create_category_folder(category)
            
            # Get unique filename if needed
            unique_filename = self.get_unique_filename(category_folder, filename)
            destination_path = os.path.join(category_folder, unique_filename)
            
            # Move the file
            shutil.move(file_path, destination_path)
            
            # Log the move
            original_size = os.path.getsize(destination_path)
            self.moved_files.append({
                'original_path': file_path,
                'new_path': destination_path,
                'category': category,
                'size': original_size
            })
            
            self.log_message(f"Moved: {filename} -> {category}/ ({self.format_size(original_size)})")
            return True
            
        except Exception as e:
            error_msg = f"Error moving {file_path}: {str(e)}"
            self.errors.append(error_msg)
            self.log_message(error_msg, "ERROR")
            return False
    
    def format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def scan_and_organize(self, dry_run: bool = False) -> None:
        """Scan target folder and organize files."""
        if not os.path.exists(self.target_folder):
            self.log_message(f"Target folder does not exist: {self.target_folder}", "ERROR")
            return
        
        if not os.path.isdir(self.target_folder):
            self.log_message(f"Target is not a directory: {self.target_folder}", "ERROR")
            return
        
        self.log_message(f"Starting organization of: {self.target_folder}")
        if dry_run:
            self.log_message("DRY RUN MODE - No files will be moved")
        
        # Get all files in target folder (not subdirectories)
        files_to_process = []
        try:
            for item in os.listdir(self.target_folder):
                item_path = os.path.join(self.target_folder, item)
                
                if os.path.isfile(item_path):
                    files_to_process.append(item_path)
                elif os.path.isdir(item_path):
                    self.log_message(f"Skipping directory: {item}")
        
        except PermissionError:
            self.log_message(f"Permission denied accessing: {self.target_folder}", "ERROR")
            return
        
        if not files_to_process:
            self.log_message("No files to organize")
            return
        
        self.log_message(f"Found {len(files_to_process)} files to process")
        
        # Process each file
        for file_path in files_to_process:
            filename = os.path.basename(file_path)
            category = self.get_file_category(filename)
            
            if category == "IGNORE":
                self.log_message(f"Ignored: {filename}")
                continue
            
            if dry_run:
                self.log_message(f"Would move: {filename} -> {category}/ (DRY RUN)")
            else:
                self.move_file(file_path, category)
        
        # Print summary
        self.print_summary(dry_run)
    
    def print_summary(self, dry_run: bool = False) -> None:
        """Print organization summary."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        summary = f"\n{'='*60}\n"
        summary += f"ORGANIZATION SUMMARY\n"
        summary += f"{'='*60}\n"
        summary += f"Duration: {duration.total_seconds():.1f} seconds\n"
        summary += f"Target folder: {self.target_folder}\n"
        
        if dry_run:
            summary += f"Mode: DRY RUN (no files moved)\n"
        
        # Count files by category
        category_counts = {}
        total_size = 0
        
        for file_info in self.moved_files:
            category = file_info['category']
            category_counts[category] = category_counts.get(category, 0) + 1
            total_size += file_info['size']
        
        summary += f"\nFiles processed: {len(self.moved_files)}\n"
        summary += f"Total size: {self.format_size(total_size)}\n"
        summary += f"Errors: {len(self.errors)}\n"
        
        if category_counts:
            summary += f"\nFiles by category:\n"
            for category, count in sorted(category_counts.items()):
                summary += f"  {category}: {count} files\n"
        
        if self.errors:
            summary += f"\nErrors encountered:\n"
            for error in self.errors[:10]:  # Show first 10 errors
                summary += f"  - {error}\n"
            if len(self.errors) > 10:
                summary += f"  ... and {len(self.errors) - 10} more errors\n"
        
        summary += f"{'='*60}\n"
        
        self.log_message(summary)
        
        # Also write summary to separate file
        summary_file = f"organizer_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        self.log_message(f"Detailed summary saved to: {summary_file}")
    
    def undo_moves(self) -> None:
        """Undo the last organization session."""
        if not self.moved_files:
            self.log_message("No files to undo")
            return
        
        self.log_message("Undoing file moves...")
        
        undo_count = 0
        for file_info in reversed(self.moved_files):  # Reverse to handle duplicates
            try:
                # Check if source directory still exists
                source_dir = os.path.dirname(file_info['original_path'])
                if not os.path.exists(source_dir):
                    os.makedirs(source_dir)
                
                # Move file back
                shutil.move(file_info['new_path'], file_info['original_path'])
                undo_count += 1
                
                filename = os.path.basename(file_info['original_path'])
                self.log_message(f"Restored: {filename}")
                
            except Exception as e:
                error_msg = f"Error restoring {file_info['new_path']}: {str(e)}"
                self.log_message(error_msg, "ERROR")
        
        self.log_message(f"Undo complete. Restored {undo_count} files")
    
    def get_folder_stats(self) -> None:
        """Get statistics about the target folder."""
        if not os.path.exists(self.target_folder):
            self.log_message(f"Target folder does not exist: {self.target_folder}", "ERROR")
            return
        
        stats = {
            'total_files': 0,
            'total_size': 0,
            'categories': {},
            'largest_files': []
        }
        
        for root, dirs, files in os.walk(self.target_folder):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    stats['total_files'] += 1
                    stats['total_size'] += file_size
                    
                    # Track largest files
                    stats['largest_files'].append((file_path, file_size))
                    
                    # Categorize
                    category = self.get_file_category(file)
                    if category != "IGNORE":
                        stats['categories'][category] = stats['categories'].get(category, 0) + 1
                
                except (OSError, PermissionError):
                    continue
        
        # Sort largest files
        stats['largest_files'].sort(key=lambda x: x[1], reverse=True)
        
        # Print stats
        print(f"\nFolder Statistics: {self.target_folder}")
        print("=" * 50)
        print(f"Total files: {stats['total_files']}")
        print(f"Total size: {self.format_size(stats['total_size'])}")
        
        if stats['categories']:
            print(f"\nFiles by category:")
            for category, count in sorted(stats['categories'].items()):
                print(f"  {category}: {count} files")
        
        if stats['largest_files']:
            print(f"\nLargest files:")
            for file_path, size in stats['largest_files'][:10]:
                filename = os.path.basename(file_path)
                print(f"  {filename}: {self.format_size(size)}")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="File Organizer Script")
    parser.add_argument("folder", help="Target folder to organize")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be moved without actually moving")
    parser.add_argument("--stats", action="store_true", help="Show folder statistics only")
    parser.add_argument("--undo", action="store_true", help="Undo last organization session")
    parser.add_argument("--log", default="file_organizer.log", help="Log file name")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.folder):
        print(f"Error: Folder '{args.folder}' does not exist")
        return
    
    organizer = FileOrganizer(args.folder, args.log)
    
    if args.stats:
        organizer.get_folder_stats()
    elif args.undo:
        organizer.undo_moves()
    else:
        print(f"Organizing folder: {args.folder}")
        print("Press Ctrl+C to cancel...")
        time.sleep(2)
        
        try:
            organizer.scan_and_organize(dry_run=args.dry_run)
        except KeyboardInterrupt:
            print("\nOrganization cancelled by user")
        except Exception as e:
            print(f"Error during organization: {e}")

if __name__ == "__main__":
    main()
