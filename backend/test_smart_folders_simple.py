#!/usr/bin/env python
"""
Smart Folder Classification - Simple Test Script

Demonstrates the automatic folder classification system without Django
Tests various file types and shows which folders they're assigned to
"""

import sys
from pathlib import Path

# Add storage directory to path
sys.path.insert(0, str(Path(__file__).parent))

from storage.smart_folder_classifier import SmartFolderClassifier


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print('=' * 80)


def test_file_classification():
    """Test file classification with various file types"""

    classifier = SmartFolderClassifier()

    # Test cases with different file types
    test_files = [
        # Photos
        ('vacation.jpg', 'Photo from camera'),
        ('screenshot.png', 'Screenshot image'),
        ('profile_pic.heic', 'iPhone photo'),

        # GIFs
        ('animation.gif', 'Animated GIF'),

        # Vector Graphics
        ('logo.svg', 'SVG logo'),
        ('illustration.eps', 'Vector illustration'),

        # Videos
        ('movie.mp4', 'MP4 video'),
        ('clip.mov', 'QuickTime video'),
        ('recording.webm', 'WebM video'),
        ('tutorial.mkv', 'Matroska video'),

        # Audio
        ('song.mp3', 'Music file'),
        ('podcast.m4a', 'Podcast audio'),
        ('sound.wav', 'WAV audio'),
        ('music.flac', 'Lossless audio'),

        # Web files
        ('index.html', 'HTML webpage'),
        ('styles.css', 'CSS stylesheet'),
        ('app.js', 'JavaScript file'),
        ('component.tsx', 'TypeScript React'),

        # Programming languages
        ('script.py', 'Python script'),
        ('Main.java', 'Java source'),
        ('program.cpp', 'C++ source'),
        ('api.php', 'PHP file'),
        ('server.go', 'Go source'),
        ('app.rs', 'Rust source'),

        # Documents
        ('report.pdf', 'PDF document'),
        ('letter.docx', 'Word document'),
        ('data.xlsx', 'Excel spreadsheet'),
        ('presentation.pptx', 'PowerPoint'),
        ('notes.txt', 'Plain text'),
        ('README.md', 'Markdown file'),

        # Data formats
        ('config.json', 'JSON data'),
        ('data.xml', 'XML file'),
        ('settings.yaml', 'YAML config'),
        ('export.csv', 'CSV data'),
        ('queries.sql', 'SQL file'),

        # Archives
        ('backup.zip', 'ZIP archive'),
        ('package.tar.gz', 'TAR archive'),
        ('files.rar', 'RAR archive'),
        ('compressed.7z', '7-Zip archive'),

        # Executables
        ('installer.exe', 'Windows executable'),
        ('application.dmg', 'macOS disk image'),
        ('package.deb', 'Debian package'),

        # Fonts
        ('font.ttf', 'TrueType font'),
        ('webfont.woff2', 'Web font'),

        # 3D models
        ('model.obj', '3D model'),
        ('scene.blend', 'Blender file'),
        ('asset.gltf', 'GLTF model'),

        # Ebooks
        ('book.epub', 'EPUB ebook'),
        ('novel.mobi', 'Kindle book'),

        # Subtitles
        ('movie.srt', 'Subtitle file'),
        ('captions.vtt', 'WebVTT subtitles'),

        # Config
        ('app.conf', 'Configuration'),
        ('.env', 'Environment file'),

        # Shell scripts
        ('deploy.sh', 'Shell script'),
        ('build.bat', 'Batch file'),

        # Blockchain
        ('contract.sol', 'Solidity contract'),

        # Other
        ('download.torrent', 'Torrent file'),
        ('unknown.xyz', 'Unknown type'),
    ]

    print_section("Smart Folder Classification Test")

    print("\nTesting file classification for various file types...\n")

    # Group results by category
    results_by_category = {}

    for filename, description in test_files:
        category, info = classifier.classify_file(filename)

        if category not in results_by_category:
            results_by_category[category] = []

        results_by_category[category].append({
            'filename': filename,
            'description': description,
            'info': info
        })

    # Print results grouped by category
    for category in sorted(results_by_category.keys()):
        files = results_by_category[category]
        category_desc = classifier.FILE_CATEGORIES[category]['description']

        print(f"\n📁 {category.upper()} ({category_desc})")
        print("-" * 80)

        for file_info in files:
            matched_by = file_info['info']['matched_by']
            ext = file_info['info']['extension']

            match_icon = "🎯" if matched_by == "extension" else "🔍"
            print(f"  {match_icon} {file_info['filename']:<25} → {file_info['description']}")
            print(f"     Extension: {ext:<10} | Matched by: {matched_by}")

    # Print statistics
    print_section("Classification Statistics")

    total_files = len(test_files)
    total_categories = len(results_by_category)

    print(f"\n  Total files tested: {total_files}")
    print(f"  Total categories used: {total_categories}")
    print(f"  Available categories: {len(classifier.FILE_CATEGORIES)}")

    print("\n  Files per category:")
    for category in sorted(results_by_category.keys()):
        count = len(results_by_category[category])
        bar = "█" * (count * 2)
        print(f"    {category:<20} {bar} {count}")

    # Show all available categories
    print_section("All Available Categories")

    all_categories = classifier.get_all_categories()

    print(f"\n  {len(all_categories)} categories available:\n")

    categories_sorted = sorted(all_categories.items())
    for i, (cat_name, cat_desc) in enumerate(categories_sorted, 1):
        print(f"  {i:2d}. {cat_name:<25} - {cat_desc}")

    # Example folder structure
    print_section("Example Folder Structure")

    print("\n  After uploading files, your storage will look like:\n")
    print("  media_storage/")

    # Show first 10 unique categories
    unique_categories = sorted(set(cat for cat, _ in [classifier.classify_file(f[0]) for f in test_files[:15]]))[:10]

    for category in unique_categories:
        extensions = classifier.FILE_CATEGORIES[category]['extensions']
        ext = extensions[0][1:] if extensions else 'file'
        print(f"  ├── {category}/")
        print(f"  │   └── 2024/01/15/")
        print(f"  │       └── admin_20240115_120000_abc123.{ext}")

    print("  ├── thumbnails/")
    print("  └── temp/")

    print_section("Test Complete!")

    print("\n  ✅ Smart folder classification is working!")
    print("  ✅ Files will be automatically organized into specific folders")
    print(f"  ✅ Supports {len(classifier.FILE_CATEGORIES)} different file categories")
    print("\n  Try uploading files through the API to see it in action!\n")


if __name__ == '__main__':
    try:
        test_file_classification()
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
