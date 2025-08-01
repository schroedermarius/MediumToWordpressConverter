# Medium to WordPress Converter

A Python tool to convert Medium blog posts (exported as HTML) to WordPress XML format for easy migration. This tool preserves your content structure, downloads images, processes links, and automatically categorizes posts based on content analysis.

## ✨ Features

- **🔄 Complete Migration**: Convert single posts or entire Medium exports
- **🖼️ Image Management**: Automatically download and organize images with WordPress-compatible paths
- **🧹 Content Cleaning**: Remove Medium-specific attributes and clean HTML for WordPress
- **🏷️ Smart Categorization**: Automatic categorization and tagging based on content analysis
- **🔗 Link Processing**: Update internal links to point to your new WordPress domain
- **📅 Date Preservation**: Extract and preserve original publication dates
- **🛡️ SEO-Friendly**: Generate URL-friendly slugs and proper WordPress structure

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Medium HTML export files
- Your target WordPress domain

### Installation

1. Clone this repository:
```bash
git clone https://github.com/schroedermarius/MediumToWordpressConverter.git
cd MediumToWordpressConverter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Export your Medium posts:
   - Go to Medium Settings → Account → Download your information
   - Extract the downloaded archive
   - Copy HTML files to the `export_htmls` folder

### Basic Usage

**List available posts:**
```bash
python medium_to_wordpress_optimized.py list
```

**Convert all posts:**
```bash
python medium_to_wordpress_optimized.py all yourdomain.com
```

**Convert a single post:**
```bash
python medium_to_wordpress_optimized.py single 1 yourdomain.com
# or
python medium_to_wordpress_optimized.py single "post-filename.html" yourdomain.com
```

## 📖 Detailed Usage

### Command Line Options

```bash
usage: medium_to_wordpress_optimized.py [-h] [--input-dir INPUT_DIR] [--no-images] [--verbose]
                                        {list,all,single} [target] [base_url]

Convert Medium blog posts to WordPress XML format

positional arguments:
  {list,all,single}     Command to execute
  target                Target file/number for single command, or base URL for all command
  base_url              Base URL for your WordPress site (e.g., yourdomain.com)

optional arguments:
  -h, --help            show this help message and exit
  --input-dir INPUT_DIR
                        Directory containing Medium HTML exports (default: export_htmls)
  --no-images           Skip downloading images
  --verbose, -v         Enable verbose logging
```

### Examples

**List all available posts with titles:**
```bash
python medium_to_wordpress_optimized.py list
```

**Convert all posts to yourdomain.com:**
```bash
python medium_to_wordpress_optimized.py all yourdomain.com
```

**Convert a specific post by number:**
```bash
python medium_to_wordpress_optimized.py single 3 yourdomain.com
```

**Convert a specific post by filename:**
```bash
python medium_to_wordpress_optimized.py single "2019-07-04_My-Great-Post.html" yourdomain.com
```

**Convert without downloading images:**
```bash
python medium_to_wordpress_optimized.py all yourdomain.com --no-images
```

**Use custom input directory:**
```bash
python medium_to_wordpress_optimized.py all yourdomain.com --input-dir my_medium_exports
```

## 📁 File Structure

```
MediumToWordpressConverter/
├── medium_to_wordpress_optimized.py   # Main converter script
├── requirements.txt                   # Python dependencies
├── export_htmls/                      # Place your Medium HTML exports here
├── wordpress_images/                  # Downloaded images (auto-created)
├── wordpress_export.xml               # Generated WordPress XML (for all posts)
└── [post-name].xml                   # Generated XML for single posts
```

## 🔧 How It Works

### 1. HTML Parsing
The tool parses Medium's HTML export format and extracts:
- Post titles
- Content structure (headings, paragraphs, lists, code blocks)
- Images and their metadata
- Publication dates from filenames

### 2. Content Processing
- Removes Medium-specific CSS classes and attributes
- Converts HTML to WordPress-compatible format
- Processes and updates internal links
- Escapes content properly for XML

### 3. Image Management
- Downloads images from Medium's CDN
- Generates unique filenames to avoid conflicts
- Creates WordPress-compatible paths (`/wp-content/uploads/YYYY/MM/`)
- Preserves image dimensions and alt text

### 4. Link Processing
- **Smart Medium Link Conversion**: Automatically converts Medium post links to your WordPress domain
- **Hash ID Removal**: Removes Medium's hash IDs (e.g., `post-title-abc123def` → `post-title`)
- **Domain Flexibility**: Works with any domain extension (.com, .de, .org, etc.)
- **Multiple URL Patterns**: Handles profile links, publication links, and direct Medium links
- **Existing Link Updates**: Updates existing domain references to new domain

### 5. Categorization & Tagging
Automatically assigns categories and tags based on content analysis:

**Categories:**
- WEB DEVELOPMENT
- .NET
- DEVOPS
- PROGRAMMING
- CLOUD
- MOBILE
- TUTORIAL

**Tags:** Extracted from technology keywords in content

### 6. WordPress XML Generation
Creates valid WordPress XML that includes:
- Post metadata (title, date, slug, categories, tags)
- Author information
- WordPress-specific fields
- Proper XML namespaces and structure

## � Advanced Link Processing

The converter includes sophisticated link processing to handle various Medium URL patterns:

### Medium Link Conversion Examples

**Profile Links:**
- `https://medium.com/@username/post-title-abc123def` → `https://yourdomain.com/post-title/`

**Publication Links:**
- `https://medium.com/publication/post-title-xyz789` → `https://yourdomain.com/post-title/`

**Direct Links:**
- `https://medium.com/post-title-123abc` → `https://yourdomain.com/post-title/`

### Domain Flexibility

Works with any domain extension:
- `.com` → `.de`, `.org`, `.io`, etc.
- Handles both www and non-www variants
- Preserves URL paths and query parameters

### Hash ID Removal

Medium appends hash IDs to post URLs for tracking. The converter automatically removes these:
- `angular-tutorial-5691beba463e` → `angular-tutorial`
- `react-guide-abc123def456` → `react-guide`

## �📋 Import to WordPress

1. **Generate XML file** using this tool
2. **Upload images** from `wordpress_images/` to your WordPress Media Library
3. **Import XML** in WordPress:
   - Go to Tools → Import
   - Choose "WordPress" importer
   - Upload the generated XML file
   - Map authors and import content

## 🎯 SEO & Canonical Links

This tool is perfect for migrating from Medium while maintaining SEO:

1. **Import posts** to WordPress using this tool
2. **Publish posts** on your WordPress site
3. **Update Medium posts** with canonical links pointing to your WordPress URLs
4. **Maintain SEO juice** while having content on your own domain

### Setting Canonical Links on Medium

After importing to WordPress:
1. Edit each post on Medium
2. Add canonical link in post settings
3. Point to your WordPress URL: `https://yourdomain.com/post-slug/`

## 🐛 Troubleshooting

### Common Issues

**"No HTML files found"**
- Ensure HTML files are in the `export_htmls` directory
- Check that files have `.html` extension

**"Could not parse HTML file"**
- Verify the HTML file is a valid Medium export
- Check file encoding (should be UTF-8)

**"Image download failed"**
- Check internet connection
- Some Medium images may have access restrictions
- Images will be skipped if download fails

**"Permission denied writing file"**
- Ensure you have write permissions in the current directory
- Check available disk space

### Debug Mode

Use verbose logging to troubleshoot issues:
```bash
python medium_to_wordpress_optimized.py all yourdomain.com --verbose
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Marius Schröder**
- Website: [marius-schroeder.de](https://marius-schroeder.de)
- GitHub: [@schroedermarius](https://github.com/schroedermarius)

## 🙏 Acknowledgments

- Built with [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- Uses [Requests](https://docs.python-requests.org/) for image downloading
- Inspired by the need to maintain content ownership while leveraging Medium's reach

## 🔮 Roadmap

- [ ] Support for more export formats
- [ ] Custom category mapping configuration
- [ ] Bulk image optimization
- [ ] WordPress plugin for direct import
- [ ] Support for Medium Publications

---

**Happy migrating! 🚀**

