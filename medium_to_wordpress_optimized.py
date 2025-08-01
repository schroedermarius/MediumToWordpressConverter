#!/usr/bin/env python3
"""
Medium to WordPress Converter

A tool to convert Medium blog posts (exported as HTML) to WordPress XML format.
Supports image downloading, link processing, and automatic categorization.

Features:
- Convert single or multiple Medium HTML exports to WordPress XML
- Download and organize images with proper WordPress paths
- Clean HTML content from Medium-specific attributes
- Automatic categorization and tagging based on content
- SEO-friendly slug generation
- Preserve publication dates from filenames

Requirements:
- beautifulsoup4
- requests
- lxml (optional, for better HTML parsing)

Usage:
    python medium_to_wordpress.py list
    python medium_to_wordpress.py all <base_url>
    python medium_to_wordpress.py single <file_or_number> <base_url>

Author: Marius Schröder
License: MIT
"""

import os
import re
import sys
import html
import requests
import argparse
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path
from typing import Optional, Tuple, List, Dict


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class MediumToWordPressConverter:
    """Main converter class for Medium to WordPress migration."""
    
    def __init__(self, base_url: str = "example.com", download_images: bool = True):
        """
        Initialize the converter.
        
        Args:
            base_url: Target WordPress site domain
            download_images: Whether to download images locally
        """
        self.base_url = base_url
        self.download_images = download_images
        self.images_dir = "wordpress_images"
        
        # Create images directory if needed
        if self.download_images and not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
            logger.info(f"📁 Created images directory: {self.images_dir}")
    
    def download_image(self, url: str, save_path: str) -> bool:
        """
        Download an image from URL and save it locally.
        
        Args:
            url: Image URL to download
            save_path: Local path to save the image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, stream=True, headers=headers, timeout=30)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            logger.warning(f"❌ Failed to download {url}: {e}")
            return False
    
    def get_image_filename(self, image_url: str, post_slug: str) -> str:
        """
        Generate a unique filename for an image based on URL and post slug.
        
        Args:
            image_url: Original image URL
            post_slug: Post slug for uniqueness
            
        Returns:
            Generated filename
        """
        parsed_url = urlparse(image_url)
        original_filename = os.path.basename(parsed_url.path)
        
        # Generate filename if none found
        if not original_filename or '.' not in original_filename:
            url_hash = abs(hash(image_url)) % 10000
            original_filename = f"image_{url_hash}.jpg"
        
        # Clean filename of problematic characters
        original_filename = re.sub(r'[*<>:"/\\|?]', '', original_filename)
        
        # Add post slug prefix for uniqueness
        name, ext = os.path.splitext(original_filename)
        return f"{post_slug}_{name}{ext}"
    
    def create_slug(self, title: str) -> str:
        """
        Create a URL-friendly slug from title.
        
        Args:
            title: Post title
            
        Returns:
            URL-friendly slug
        """
        # Remove HTML tags if present
        clean_title = re.sub(r'<[^>]+>', '', title)
        # Replace special characters and spaces
        slug = re.sub(r'[^\w\s-]', '', clean_title)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-').lower()
    
    def clean_medium_post_slug(self, post_path: str) -> str:
        """
        Clean Medium post slug by removing hash-like IDs and normalizing.
        
        Args:
            post_path: Raw post path from Medium URL
            
        Returns:
            Cleaned slug suitable for WordPress
        """
        # Remove query parameters first
        post_path = post_path.split('?')[0]
        
        # Medium post URLs typically end with a hash like: post-title-5691beba463e
        # We want to remove this hash part (usually 6+ alphanumeric characters)
        # Pattern: Remove trailing dash followed by 6+ alphanumeric characters
        post_path = re.sub(r'-[a-zA-Z0-9]{6,}$', '', post_path)
        
        # Additional cleanup: remove any remaining weird characters
        post_path = re.sub(r'[^a-zA-Z0-9\-]', '', post_path)
        
        # Remove multiple consecutive dashes and trim
        post_path = re.sub(r'-+', '-', post_path).strip('-')
        
        return post_path.lower()

    def process_links_in_element(self, element, base_url: str):
        """
        Process and clean links in an HTML element.
        
        Args:
            element: BeautifulSoup element containing links
            base_url: Target base URL for internal links (without protocol, e.g., 'yourdomain.com' or 'yourdomain.de')
        """
        for link_tag in element.find_all('a'):
            # Remove Medium-specific attributes
            attrs_to_remove = ['data-action', 'data-action-type', 'data-action-value', 
                             'data-anchor-type', 'data-user-id', 'class', 'id', 'name']
            for attr in attrs_to_remove:
                if link_tag.has_attr(attr):
                    del link_tag[attr]
            
            # Process href attributes
            href = link_tag.get('href')
            if href:
                # Handle Medium profile/publication links
                if 'medium.com/' in href:
                    # Pattern 1: Profile posts - medium.com/@username/post-title-hash
                    profile_match = re.search(r'medium\.com/@[^/]+/([^?/#]+)', href)
                    # Pattern 2: Publication posts - medium.com/publication/post-title-hash  
                    publication_match = re.search(r'medium\.com/[^/@][^/]*/([^?/#]+)', href)
                    # Pattern 3: Direct posts - medium.com/post-title-hash
                    direct_match = re.search(r'medium\.com/([^/@?#][^/?#]*)', href)
                    
                    if profile_match:
                        raw_post_path = profile_match.group(1)
                        clean_slug = self.clean_medium_post_slug(raw_post_path)
                        new_url = f"https://{base_url}/{clean_slug}/"
                        link_tag['href'] = new_url
                        logger.info(f"✅ Updated Medium profile link: {href} → {new_url}")
                    elif publication_match:
                        raw_post_path = publication_match.group(1)
                        clean_slug = self.clean_medium_post_slug(raw_post_path)
                        new_url = f"https://{base_url}/{clean_slug}/"
                        link_tag['href'] = new_url
                        logger.info(f"✅ Updated Medium publication link: {href} → {new_url}")
                    elif direct_match:
                        raw_post_path = direct_match.group(1)
                        # Skip if this looks like a Medium system path
                        if not any(system_path in raw_post_path.lower() for system_path in 
                                 ['about', 'help', 'settings', 'membership', 'partner', 'creators']):
                            clean_slug = self.clean_medium_post_slug(raw_post_path)
                            new_url = f"https://{base_url}/{clean_slug}/"
                            link_tag['href'] = new_url
                            logger.info(f"✅ Updated Medium direct link: {href} → {new_url}")
                
                # Handle existing domain references (could be .com, .de, .org, etc.)
                elif any(domain_ref in href for domain_ref in [base_url, f'www.{base_url}']):
                    # Clean up any www prefix and ensure correct protocol
                    if href.startswith('http'):
                        # Extract path and rebuild URL
                        parsed_url = urlparse(href)
                        clean_path = parsed_url.path.rstrip('/')
                        query_string = f"?{parsed_url.query}" if parsed_url.query else ""
                        fragment = f"#{parsed_url.fragment}" if parsed_url.fragment else ""
                        new_url = f"https://{base_url}{clean_path}{query_string}{fragment}"
                    else:
                        # Relative URL, just ensure it starts with /
                        new_url = href if href.startswith('/') else f"/{href}"
                    
                    if new_url != href:
                        link_tag['href'] = new_url
                        logger.info(f"✅ Updated domain reference: {href} → {new_url}")
            
            # Remove data-href attributes
            if link_tag.has_attr('data-href'):
                del link_tag['data-href']
    
    def process_content(self, content_html: str, post_slug: str) -> str:
        """
        Process and clean HTML content from Medium format.
        
        Args:
            content_html: Raw HTML content from Medium
            post_slug: Post slug for image naming
            
        Returns:
            Cleaned HTML content for WordPress
        """
        soup = BeautifulSoup(content_html, 'html.parser')
        content_parts = []
        
        # Find all content elements in order
        elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figure', 
                                'blockquote', 'pre', 'ul', 'ol', 'hr'])
        
        for element in elements:
            if element.name == 'figure':
                # Process images
                img_tag = element.find('img')
                if img_tag:
                    src = img_tag.get('src')
                    if src and 'medium.com' in src:
                        if self.download_images:
                            # Download and process image
                            image_filename = self.get_image_filename(src, post_slug)
                            image_path = os.path.join(self.images_dir, image_filename)
                            
                            if self.download_image(src, image_path):
                                # Create WordPress-compatible image path
                                current_year = datetime.now().year
                                current_month = datetime.now().strftime('%m')
                                src = f"/wp-content/uploads/{current_year}/{current_month}/{image_filename}"
                                logger.info(f"✅ Downloaded image: {image_filename}")
                            else:
                                logger.warning(f"❌ Could not download image: {src}")
                    
                    # Create clean figure element
                    figure_html = '<figure><img'
                    if img_tag.get('data-width'):
                        figure_html += f' data-width="{img_tag["data-width"]}"'
                    if img_tag.get('data-height'):
                        figure_html += f' data-height="{img_tag["data-height"]}"'
                    if img_tag.get('alt'):
                        figure_html += f' alt="{html.escape(img_tag["alt"])}"'
                    figure_html += f' src="{src}"></figure>'
                    
                    content_parts.append(figure_html)
            
            elif element.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # Process text elements
                element_copy = BeautifulSoup(str(element), 'html.parser').find(element.name)
                
                # Remove CSS classes and IDs
                for tag in element_copy.find_all(True):
                    attrs_to_remove = ['class', 'id', 'name']
                    for attr in attrs_to_remove:
                        if tag.has_attr(attr):
                            del tag[attr]
                
                # Process links
                self.process_links_in_element(element_copy, self.base_url)
                
                # Get cleaned content
                inner_html = element_copy.decode_contents()
                if inner_html.strip():
                    content_parts.append(f'<{element.name}>{inner_html}</{element.name}>')
            
            elif element.name == 'blockquote':
                # Process blockquotes
                text_content = element.get_text().strip()
                if text_content:
                    content_parts.append(f'<blockquote>{html.escape(text_content)}</blockquote>')
            
            elif element.name == 'pre':
                # Process code blocks
                code_content = element.get_text()
                if code_content.strip():
                    escaped_code = html.escape(code_content)
                    content_parts.append(f'<pre><code>{escaped_code}</code></pre>')
            
            elif element.name in ['ul', 'ol']:
                # Process lists
                list_items = []
                for li in element.find_all('li'):
                    li_text = li.get_text().strip()
                    if li_text:
                        list_items.append(f'<li>{html.escape(li_text)}</li>')
                
                if list_items:
                    list_html = ''.join(list_items)
                    content_parts.append(f'<{element.name}>{list_html}</{element.name}>')
            
            elif element.name == 'hr':
                content_parts.append('<hr>')
        
        return ''.join(content_parts)
    
    def extract_date_from_filename(self, filename: str) -> datetime:
        """
        Extract publication date from Medium filename.
        
        Args:
            filename: Medium export filename
            
        Returns:
            Parsed datetime or current datetime as fallback
        """
        # Format: 2019-07-04_Title-hash.html
        match = re.search(r'^(\d{4}-\d{2}-\d{2})_', filename)
        if match:
            date_str = match.group(1)
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                pass
        
        logger.warning(f"Could not extract date from {filename}, using current date")
        return datetime.now()
    
    def extract_categories_and_tags(self, title: str, content: str) -> Tuple[List[str], List[str]]:
        """
        Extract intelligent categories and tags from title and content.
        
        Args:
            title: Post title
            content: Post content
            
        Returns:
            Tuple of (categories, tags)
        """
        text = f"{title} {content}".lower()
        
        # Category mapping based on keywords
        category_keywords = {
            'WEB DEVELOPMENT': ['angular', 'react', 'vue', 'javascript', 'typescript', 'html', 'css', 'web', 'frontend', 'backend'],
            '.NET': ['.net', 'c#', 'csharp', 'asp.net', 'entity framework', 'blazor', 'mvc', 'web api', 'dotnet'],
            'DEVOPS': ['docker', 'kubernetes', 'azure', 'aws', 'deployment', 'ci/cd', 'pipeline', 'devops', 'terraform'],
            'PROGRAMMING': ['code', 'programming', 'development', 'software', 'algorithm', 'design pattern'],
            'CLOUD': ['azure', 'aws', 'cloud', 'serverless', 'microservices', 'container'],
            'MOBILE': ['ionic', 'xamarin', 'mobile', 'android', 'ios', 'app development'],
            'TUTORIAL': ['tutorial', 'guide', 'how to', 'step by step', 'getting started', 'introduction']
        }
        
        # Tag keywords
        tag_keywords = [
            'angular', 'react', 'vue', 'javascript', 'typescript', 'html', 'css', 'sass',
            '.net', 'c#', 'asp.net', 'blazor', 'mvc', 'web api', 'entity framework',
            'docker', 'kubernetes', 'azure', 'aws', 'git', 'github', 'visual studio',
            'npm', 'node.js', 'webpack', 'vite', 'ionic', 'xamarin', 'sql', 'database',
            'api', 'rest', 'graphql', 'json', 'microservices', 'architecture',
            'testing', 'unit testing', 'debugging', 'performance', 'security'
        ]
        
        # Find matching categories
        categories = []
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                categories.append(category)
        
        # Default to PROGRAMMING if no specific category found
        if not categories:
            categories = ['PROGRAMMING']
        
        # Find matching tags
        tags = []
        for tag in tag_keywords:
            if tag in text:
                tags.append(tag.upper())
        
        # Limit results
        return categories[:2], tags[:5]
    
    def build_wp_item(self, title: str, content: str, date: datetime, post_id: Optional[int] = None) -> str:
        """
        Build a WordPress XML item from post data.
        
        Args:
            title: Post title
            content: Post content (HTML)
            date: Publication date
            post_id: Unique post ID
            
        Returns:
            WordPress XML item string
        """
        post_slug = self.create_slug(title)
        if post_id is None:
            post_id = abs(hash(title)) % 100000
        
        # WordPress-compatible date formatting
        wp_date = date.strftime('%Y-%m-%d %H:%M:%S')
        pub_date = date.strftime('%a, %d %b %Y %H:%M:%S +0000')
        
        # Extract categories and tags
        categories, tags = self.extract_categories_and_tags(title, content)
        
        # Build category XML
        category_xml = ""
        for category in categories:
            category_slug = self.create_slug(category)
            category_xml += f'\n\t\t<category domain="category" nicename="{category_slug}"><![CDATA[{category}]]></category>'
        
        # Build tag XML
        tag_xml = ""
        for tag in tags:
            tag_slug = tag.replace(' ', '-').replace('.', '').replace('#', '').lower()
            tag_xml += f'\n\t\t<category domain="post_tag" nicename="{tag_slug}"><![CDATA[{tag}]]></category>'
        
        return f"""
	<item>
		<title><![CDATA[{title}]]></title>
		<link>https://{self.base_url}/{post_slug}/</link>
		<pubDate>{pub_date}</pubDate>
		<dc:creator><![CDATA[Admin]]></dc:creator>
		<guid isPermaLink="false">https://{self.base_url}/?p={post_id}</guid>
		<description></description>
		<content:encoded><![CDATA[{content}]]></content:encoded>
		<excerpt:encoded><![CDATA[]]></excerpt:encoded>
		<wp:post_id>{post_id}</wp:post_id>
		<wp:post_date><![CDATA[{wp_date}]]></wp:post_date>
		<wp:post_date_gmt><![CDATA[{wp_date}]]></wp:post_date_gmt>
		<wp:post_modified><![CDATA[{wp_date}]]></wp:post_modified>
		<wp:post_modified_gmt><![CDATA[{wp_date}]]></wp:post_modified_gmt>
		<wp:comment_status><![CDATA[open]]></wp:comment_status>
		<wp:ping_status><![CDATA[open]]></wp:ping_status>
		<wp:post_name><![CDATA[{post_slug}]]></wp:post_name>
		<wp:status><![CDATA[publish]]></wp:status>
		<wp:post_parent>0</wp:post_parent>
		<wp:menu_order>0</wp:menu_order>
		<wp:post_type><![CDATA[post]]></wp:post_type>
		<wp:post_password><![CDATA[]]></wp:post_password>
		<wp:is_sticky>0</wp:is_sticky>{category_xml}{tag_xml}
	</item>"""
    
    def build_wp_xml(self, items: List[str]) -> str:
        """
        Build complete WordPress XML export with items.
        
        Args:
            items: List of WordPress XML items
            
        Returns:
            Complete WordPress XML export
        """
        return f"""<?xml version="1.0" encoding="UTF-8" ?>
<!-- This is a WordPress eXtended RSS file generated by Medium to WordPress Converter -->
<!-- It contains information about your site's posts, categories, and other content -->
<!-- To import this information into a WordPress site follow these steps: -->
<!-- 1. Log in to that site as an administrator -->
<!-- 2. Go to Tools: Import in the WordPress admin panel -->
<!-- 3. Install the "WordPress" importer from the list -->
<!-- 4. Activate & Run Importer -->
<!-- 5. Upload this file using the form provided on that page -->

<rss version="2.0"
	xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
	xmlns:content="http://purl.org/rss/1.0/modules/content/"
	xmlns:wfw="http://wellformedweb.org/CommentAPI/"
	xmlns:dc="http://purl.org/dc/elements/1.1/"
	xmlns:wp="http://wordpress.org/export/1.2/"
>

<channel>
	<title>Medium to WordPress Import</title>
	<link>https://{self.base_url}</link>
	<description>Imported from Medium</description>
	<pubDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
	<language>en-US</language>
	<wp:wxr_version>1.2</wp:wxr_version>
	<wp:base_site_url>https://{self.base_url}</wp:base_site_url>
	<wp:base_blog_url>https://{self.base_url}</wp:base_blog_url>

	<wp:author>
		<wp:author_id>1</wp:author_id>
		<wp:author_login><![CDATA[admin]]></wp:author_login>
		<wp:author_email><![CDATA[admin@{self.base_url}]]></wp:author_email>
		<wp:author_display_name><![CDATA[Admin]]></wp:author_display_name>
		<wp:author_first_name><![CDATA[]]></wp:author_first_name>
		<wp:author_last_name><![CDATA[]]></wp:author_last_name>
	</wp:author>

	<!-- Categories -->
	<wp:category>
		<wp:term_id>1</wp:term_id>
		<wp:category_nicename><![CDATA[web-development]]></wp:category_nicename>
		<wp:category_parent><![CDATA[]]></wp:category_parent>
		<wp:cat_name><![CDATA[WEB DEVELOPMENT]]></wp:cat_name>
	</wp:category>

	<wp:category>
		<wp:term_id>2</wp:term_id>
		<wp:category_nicename><![CDATA[dotnet]]></wp:category_nicename>
		<wp:category_parent><![CDATA[]]></wp:category_parent>
		<wp:cat_name><![CDATA[.NET]]></wp:cat_name>
	</wp:category>

	<wp:category>
		<wp:term_id>3</wp:term_id>
		<wp:category_nicename><![CDATA[devops]]></wp:category_nicename>
		<wp:category_parent><![CDATA[]]></wp:category_parent>
		<wp:cat_name><![CDATA[DEVOPS]]></wp:cat_name>
	</wp:category>

	<wp:category>
		<wp:term_id>4</wp:term_id>
		<wp:category_nicename><![CDATA[programming]]></wp:category_nicename>
		<wp:category_parent><![CDATA[]]></wp:category_parent>
		<wp:cat_name><![CDATA[PROGRAMMING]]></wp:cat_name>
	</wp:category>

	<wp:category>
		<wp:term_id>5</wp:term_id>
		<wp:category_nicename><![CDATA[cloud]]></wp:category_nicename>
		<wp:category_parent><![CDATA[]]></wp:category_parent>
		<wp:cat_name><![CDATA[CLOUD]]></wp:cat_name>
	</wp:category>

	<wp:category>
		<wp:term_id>6</wp:term_id>
		<wp:category_nicename><![CDATA[mobile]]></wp:category_nicename>
		<wp:category_parent><![CDATA[]]></wp:category_parent>
		<wp:cat_name><![CDATA[MOBILE]]></wp:cat_name>
	</wp:category>

	<wp:category>
		<wp:term_id>7</wp:term_id>
		<wp:category_nicename><![CDATA[tutorial]]></wp:category_nicename>
		<wp:category_parent><![CDATA[]]></wp:category_parent>
		<wp:cat_name><![CDATA[TUTORIAL]]></wp:cat_name>
	</wp:category>

	<generator>Medium to WordPress Converter</generator>
{"".join(items)}
</channel>
</rss>"""
    
    def parse_medium_html(self, file_path: str) -> Optional[Tuple[str, str]]:
        """
        Parse a Medium HTML export file.
        
        Args:
            file_path: Path to Medium HTML file
            
        Returns:
            Tuple of (title, content_html) or None if parsing failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                
                title_tag = soup.find('h1')
                body_section = soup.find('section', {'data-field': 'body'})
                
                if not title_tag or not body_section:
                    logger.error(f"Could not find title or body in {file_path}")
                    return None
                
                title = title_tag.get_text().strip()
                content_html = str(body_section)
                
                return title, content_html
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return None
    
    def list_available_posts(self, folder_path: str) -> List[str]:
        """
        List all available HTML files with their titles.
        
        Args:
            folder_path: Path to folder containing HTML files
            
        Returns:
            List of HTML filenames
        """
        if not os.path.exists(folder_path):
            logger.error(f"Folder not found: {folder_path}")
            return []
        
        print("📋 Available Blog Posts:")
        print("=" * 60)
        
        html_files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
        html_files.sort()
        
        for i, file_name in enumerate(html_files, 1):
            file_path = os.path.join(folder_path, file_name)
            result = self.parse_medium_html(file_path)
            if result:
                title, _ = result
                print(f"{i:2d}. {title}")
                print(f"    📁 {file_name}")
            else:
                print(f"{i:2d}. ❌ Could not parse")
                print(f"    📁 {file_name}")
            print()
        
        print(f"Total: {len(html_files)} HTML files found")
        return html_files
    
    def convert_single_post(self, file_path: str, output_file: str) -> bool:
        """
        Convert a single Medium post to WordPress XML.
        
        Args:
            file_path: Path to Medium HTML file
            output_file: Output XML file path
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
        
        if not file_path.endswith('.html'):
            logger.error(f"File must be HTML: {file_path}")
            return False
        
        logger.info(f"🔄 Processing: {os.path.basename(file_path)}")
        result = self.parse_medium_html(file_path)
        
        if not result:
            logger.error(f"Could not parse HTML file: {file_path}")
            return False
        
        title, content_html = result
        post_slug = self.create_slug(title)
        
        # Process content
        content = self.process_content(content_html, post_slug)
        
        # Extract date from filename
        filename = os.path.basename(file_path)
        date = self.extract_date_from_filename(filename)
        post_id = abs(hash(title)) % 100000
        
        wp_item = self.build_wp_item(title, content, date, post_id)
        full_xml = self.build_wp_xml([wp_item])
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_xml)
            
            logger.info(f"✅ Post processed: {title}")
            logger.info(f"🎉 Single post exported to: {output_file}")
            if self.download_images:
                logger.info(f"🖼️  Images saved to: {self.images_dir}")
            return True
        except Exception as e:
            logger.error(f"Error writing output file {output_file}: {e}")
            return False
    
    def convert_folder(self, folder_path: str, output_file: str) -> bool:
        """
        Convert all Medium posts in a folder to WordPress XML.
        
        Args:
            folder_path: Path to folder containing HTML files
            output_file: Output XML file path
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(folder_path):
            logger.error(f"Folder not found: {folder_path}")
            return False
        
        items = []
        html_files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
        
        if not html_files:
            logger.error(f"No HTML files found in {folder_path}")
            return False
        
        for file_name in sorted(html_files):
            logger.info(f"🔄 Processing: {file_name}")
            file_path = os.path.join(folder_path, file_name)
            result = self.parse_medium_html(file_path)
            
            if result:
                title, content_html = result
                post_slug = self.create_slug(title)
                
                # Process content
                content = self.process_content(content_html, post_slug)
                
                # Extract date from filename
                date = self.extract_date_from_filename(file_name)
                post_id = abs(hash(title)) % 100000
                
                wp_item = self.build_wp_item(title, content, date, post_id)
                items.append(wp_item)
                logger.info(f"✅ Post processed: {title}")
            else:
                logger.warning(f"❌ Skipped: {file_name}")
        
        if not items:
            logger.error("No posts were successfully processed")
            return False
        
        # Write output
        try:
            full_xml = self.build_wp_xml(items)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_xml)
            
            logger.info(f"\n🎉 Export completed!")
            logger.info(f"📄 WordPress XML: {output_file}")
            logger.info(f"📊 {len(items)} blog posts exported")
            if self.download_images:
                logger.info(f"🖼️  Images directory: {self.images_dir}")
                logger.info(f"💡 Upload all images from '{self.images_dir}' to your WordPress Media Library")
            return True
        except Exception as e:
            logger.error(f"Error writing output file {output_file}: {e}")
            return False


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description='Convert Medium blog posts to WordPress XML format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list
  %(prog)s all https://yourdomain.com
  %(prog)s single 1 https://yourdomain.com
  %(prog)s single post.html https://yourdomain.com
        """
    )
    
    parser.add_argument('command', choices=['list', 'all', 'single'],
                       help='Command to execute')
    parser.add_argument('target', nargs='?',
                       help='Target file/number for single command, or base URL for all command')
    parser.add_argument('base_url', nargs='?', 
                       help='Base URL for your WordPress site (e.g., yourdomain.com)')
    parser.add_argument('--input-dir', default='export_htmls',
                       help='Directory containing Medium HTML exports (default: export_htmls)')
    parser.add_argument('--no-images', action='store_true',
                       help='Skip downloading images')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Handle list command
    if args.command == 'list':
        converter = MediumToWordPressConverter()
        converter.list_available_posts(args.input_dir)
        return
    
    # Validate base URL for other commands
    if not args.base_url:
        if args.command == 'all':
            logger.error("Base URL is required for 'all' command")
            logger.info("Usage: python medium_to_wordpress.py all <base_url>")
        elif args.command == 'single':
            logger.error("Base URL is required for 'single' command")
            logger.info("Usage: python medium_to_wordpress.py single <file_or_number> <base_url>")
        return
    
    # Clean base URL
    base_url = args.base_url.replace('https://', '').replace('http://', '').strip('/')
    
    # Initialize converter
    converter = MediumToWordPressConverter(
        base_url=base_url,
        download_images=not args.no_images
    )
    
    if args.command == 'all':
        logger.info(f"🚀 Exporting all posts to {base_url}...")
        success = converter.convert_folder(args.input_dir, 'wordpress_export.xml')
        sys.exit(0 if success else 1)
    
    elif args.command == 'single':
        if not args.target:
            logger.error("Target file or number is required for 'single' command")
            converter.list_available_posts(args.input_dir)
            logger.info("Usage: python medium_to_wordpress.py single <file_or_number> <base_url>")
            return
        
        # Handle numeric input (post number)
        if args.target.isdigit():
            html_files = converter.list_available_posts(args.input_dir)
            post_number = int(args.target)
            
            if 1 <= post_number <= len(html_files):
                selected_file = html_files[post_number - 1]
                file_path = os.path.join(args.input_dir, selected_file)
                base_name = os.path.splitext(selected_file)[0]
                output_file = f"{base_name}.xml"
                
                logger.info(f"🚀 Exporting post #{post_number}: {selected_file}")
                success = converter.convert_single_post(file_path, output_file)
            else:
                logger.error(f"Invalid post number: {post_number}")
                logger.error(f"Available posts: 1-{len(html_files)}")
                success = False
        else:
            # Handle filename input
            if not args.target.startswith(args.input_dir):
                file_path = os.path.join(args.input_dir, args.target)
            else:
                file_path = args.target
            
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_file = f"{base_name}.xml"
            
            logger.info(f"🚀 Exporting post: {os.path.basename(file_path)}")
            success = converter.convert_single_post(file_path, output_file)
        
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
