# Example configuration for Medium to WordPress Converter
# Copy this file to config.py and customize as needed

# Default settings
DEFAULT_INPUT_DIR = "export_htmls"
DEFAULT_OUTPUT_DIR = "."
DEFAULT_IMAGES_DIR = "wordpress_images"

# WordPress settings
WORDPRESS_AUTHOR = "Admin"
WORDPRESS_LANGUAGE = "en-US"

# Image settings
IMAGE_DOWNLOAD_TIMEOUT = 30
IMAGE_CHUNK_SIZE = 8192

# Logging settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# Custom category mappings
# Add your own keyword-to-category mappings here
CUSTOM_CATEGORIES = {
    "ARTIFICIAL INTELLIGENCE": ["ai", "machine learning", "ml", "neural", "gpt", "llm"],
    "BLOCKCHAIN": ["blockchain", "cryptocurrency", "bitcoin", "ethereum", "web3"],
    "DATA SCIENCE": ["data science", "analytics", "pandas", "numpy", "jupyter"],
    # Add more as needed
}

# Custom tag keywords
# Add technology-specific keywords that should become tags
CUSTOM_TAGS = [
    "python", "django", "flask", "fastapi",
    "java", "spring", "hibernate",
    "go", "golang", "rust",
    "php", "laravel", "symfony",
    # Add more as needed
]

# URL patterns to replace in content
# Format: (pattern, replacement)
URL_REPLACEMENTS = [
    # Example: Replace old domain with new domain
    # ("old-domain.com", "new-domain.com"),
]
