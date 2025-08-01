#!/usr/bin/env python3
"""
Medium to WordPress Converter

A tool to convert Medium blog posts (exported as HTML) to WordPress XML format.
Supports image downloading, link processing, and automatic categorization.

Author: Marius Schröder
License: MIT
"""

import os
import re
import sys
import html
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path
import argparse
import logging

# Funktion zum Herunterladen und Speichern von Bildern
def download_image(url, save_path):
    """Lädt ein Bild herunter und speichert es lokal."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"❌ Fehler beim Herunterladen von {url}: {e}")
        return False

# Funktion zum Extrahieren eines Bildnamens aus einer URL
def get_image_filename(image_url, post_slug):
    """Erstellt einen eindeutigen Bildnamen basierend auf URL und Post-Titel."""
    parsed_url = urlparse(image_url)
    original_filename = os.path.basename(parsed_url.path)
    
    # Falls kein Dateiname gefunden wird, verwende den Hash aus der URL
    if not original_filename or '.' not in original_filename:
        url_hash = hash(image_url) % 10000
        original_filename = f"image_{url_hash}.jpg"
    
    # Entferne URL-unfreundliche Zeichen wie Sterne
    original_filename = re.sub(r'[*<>:"/\\|?]', '', original_filename)
    
    # Füge Post-Slug als Präfix hinzu für Eindeutigkeit
    name, ext = os.path.splitext(original_filename)
    return f"{post_slug}_{name}{ext}"

# Funktion zum Erstellen eines URL-freundlichen Slugs
def create_slug(title):
    """Erstellt einen URL-freundlichen Slug aus dem Titel."""
    # Entferne HTML-Tags falls vorhanden
    clean_title = re.sub(r'<[^>]+>', '', title)
    # Ersetze Sonderzeichen und Leerzeichen, aber behalte Groß-/Kleinschreibung
    slug = re.sub(r'[^\w\s-]', '', clean_title)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-').lower()  # Nur für nicename lowercase verwenden

# Funktion zum Bereinigen von HTML-Elementen (entfernt Medium-spezifische Klassen)
def clean_html_content(element):
    """Bereinigt HTML-Inhalt von Medium-spezifischen Attributen und Klassen."""
    # Erstelle eine Kopie des Elements
    soup = BeautifulSoup(str(element), 'html.parser')
    
    # Entferne alle class-Attribute von allen Elementen
    for tag in soup.find_all(True):
        if tag.has_attr('class'):
            del tag['class']
        # Entferne auch andere Medium-spezifische Attribute
        for attr in ['data-action', 'data-action-type', 'data-action-value', 'data-anchor-type', 
                     'data-user-id', 'id', 'name']:
            if tag.has_attr(attr):
                del tag[attr]
    
    return soup

# Funktion zum Extrahieren und Verarbeiten des eigentlichen Inhalts
def process_content_simple(content_html, post_slug, images_dir, base_url):
    """Extrahiert sauberen HTML-Inhalt aus dem Medium-Format."""
    soup = BeautifulSoup(content_html, 'html.parser')
    
    # Sammle alle relevanten Content-Elemente in der richtigen Reihenfolge
    content_parts = []
    
    # Finde alle Content-Elemente
    for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figure', 'blockquote', 'pre', 'ul', 'ol', 'hr']):
        if element.name == 'figure':
            # Behandle Bilder
            img_tag = element.find('img')
            if img_tag:
                src = img_tag.get('src')
                if src and 'medium.com' in src:
                    # Erstelle Bildnamen und lade Bild herunter
                    image_filename = get_image_filename(src, post_slug)
                    image_path = os.path.join(images_dir, image_filename)
                    
                    if download_image(src, image_path):
                        # Erstelle WordPress-kompatiblen Bildpfad mit Jahr/Monat
                        current_year = datetime.now().year
                        current_month = datetime.now().strftime('%m')
                        # Ändere Dateiendung zu .webp
                        base_name = os.path.splitext(image_filename)[0]
                        webp_filename = f"{base_name}.webp"
                        src = f"/wp-content/uploads/{current_year}/{current_month}/{webp_filename}"
                        print(f"✅ Bild heruntergeladen: {webp_filename}")
                    else:
                        print(f"❌ Bild konnte nicht heruntergeladen werden: {src}")
                
                # Erstelle sauberes Figure-Element ohne Anführungszeichen bei src
                figure_html = f'<figure><img'
                if img_tag.get('data-width'):
                    figure_html += f' data-width={img_tag["data-width"]}'
                if img_tag.get('data-height'):
                    figure_html += f' data-height={img_tag["data-height"]}'
                figure_html += f' src={src}></figure>'
                
                content_parts.append(figure_html)
                
        elif element.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            # Erstelle eine saubere Kopie des Elements ohne CSS-Klassen
            element_copy = BeautifulSoup(str(element), 'html.parser').find(element.name)
            
            # Entferne alle CSS-Klassen und IDs
            for tag in element_copy.find_all(True):
                if tag.has_attr('class'):
                    del tag['class']
                if tag.has_attr('id'):
                    del tag['id']
                if tag.has_attr('name'):
                    del tag['name']
            
            # Verarbeite Links
            process_links_in_element(element_copy, base_url)
            
            # Hole den bereinigten Inhalt und entferne Anführungszeichen bei href
            inner_html = element_copy.decode_contents()
            # Entferne Anführungszeichen bei href-Attributen für WordPress-Kompatibilität
            inner_html = re.sub(r'href="([^"]+)"', r'href=\1', inner_html)
            inner_html = re.sub(r"href='([^']+)'", r'href=\1', inner_html)
            
            if inner_html.strip():
                content_parts.append(f'<{element.name}>{inner_html}</{element.name}>')
                
        elif element.name == 'blockquote':
            # Für Blockquotes extrahiere nur den Text
            text_content = element.get_text().strip()
            if text_content:
                content_parts.append(f'<blockquote>{text_content}</blockquote>')
                
        elif element.name == 'pre':
            # Für Code-Blöcke - extrahiere den eigentlichen Code
            code_content = element.get_text()
            if code_content.strip():
                lines = code_content.strip().split('\n')
                spans = []
                for line in lines:
                    if line.strip():
                        spans.append(f'<span>{html.escape(line)}</span>')
                    else:
                        spans.append('<br>')
                
                pre_content = ''.join(spans)
                content_parts.append(f'<pre>{pre_content}</pre>')
                
        elif element.name in ['ul', 'ol']:
            # Verarbeite Listen
            list_items = []
            for li in element.find_all('li'):
                li_text = li.get_text().strip()
                if li_text:
                    list_items.append(f'<li>{li_text}</li>')
            
            if list_items:
                list_html = ''.join(list_items)
                content_parts.append(f'<{element.name}>{list_html}</{element.name}>')
                
        elif element.name == 'hr':
            content_parts.append('<hr>')
    
    # Verbinde alle Teile
    return ''.join(content_parts)

# Hilfsfunktion zum Verarbeiten von Links in einem Element
def process_links_in_element(element, base_url):
    """Verarbeitet alle Links in einem gegebenen HTML-Element."""
    for link_tag in element.find_all('a'):
        # Entferne alle Medium-spezifischen Attribute
        for attr in ['data-action', 'data-action-type', 'data-action-value', 'data-anchor-type', 
                     'data-user-id', 'class', 'id', 'name']:
            if link_tag.has_attr(attr):
                del link_tag[attr]
        
        # Verarbeite href-Attribute
        href = link_tag.get('href')
        if href and ('medium.com/@mariusschroeder' in href or 'medium.com/medialesson' in href):
            # Extrahiere Post-ID oder Titel aus dem Link für eigene Posts
            match = re.search(r'/@mariusschroeder/([^?]+)', href)
            if match:
                post_path = match.group(1)
                link_tag['href'] = f"https://{base_url}/{post_path}"
                print(f"✅ href ersetzt: {href} → {link_tag['href']}")
            else:
                # Für medialesson Links
                match = re.search(r'/medialesson/([^?]+)', href)
                if match:
                    post_path = match.group(1)
                    link_tag['href'] = f"https://{base_url}/{post_path}"
                    print(f"✅ href ersetzt: {href} → {link_tag['href']}")
        elif href and 'www.marius-schroeder.de' in href:
            new_href = href.replace('www.marius-schroeder.de', base_url)
            link_tag['href'] = new_href
            print(f"✅ href angepasst: {href} → {new_href}")
        
        # Entferne data-href-Attribute komplett (wird in WordPress nicht benötigt)
        if link_tag.has_attr('data-href'):
            del link_tag['data-href']

# Legacy-Funktion für Rückwärtskompatibilität
def process_content(content_html, post_slug, images_dir, base_url):
    """Legacy-Funktion - verwendet neue einfache Content-Verarbeitung."""
    return process_content_simple(content_html, post_slug, images_dir, base_url)

# Funktion zum Extrahieren des Datums aus dem Dateinamen
def extract_date_from_filename(filename):
    """Extrahiert das Publikationsdatum aus dem Medium-Dateinamen."""
    # Format: 2019-07-04_Title-hash.html
    match = re.search(r'^(\d{4}-\d{2}-\d{2})_', filename)
    if match:
        date_str = match.group(1)
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            pass
    
    # Fallback auf aktuelles Datum
    return datetime.now()

# Funktion zum Extrahieren von Kategorien und Tags
def extract_categories_and_tags(title, content):
    """Extrahiert intelligente Kategorien und Tags aus Titel und Inhalt."""
    # Kombiniere Titel und Inhalt für die Analyse
    text = f"{title} {content}".lower()
    
    # Definiere Kategorie-Mapping basierend auf Schlüsselwörtern
    category_keywords = {
        'WEB DEVELOPMENT': ['angular', 'react', 'vue', 'javascript', 'typescript', 'html', 'css', 'web', 'frontend', 'backend', 'blazor', 'asp.net', 'mvc'],
        '.NET': ['.net', 'c#', 'csharp', 'asp.net', 'entity framework', 'blazor', 'mvc', 'web api', 'dotnet'],
        'DEVOPS': ['docker', 'kubernetes', 'azure', 'aws', 'deployment', 'ci/cd', 'pipeline', 'devops', 'terraform'],
        'PROGRAMMING': ['code', 'programming', 'development', 'software', 'algorithm', 'design pattern', 'best practices'],
        'CLOUD': ['azure', 'aws', 'cloud', 'serverless', 'microservices', 'container'],
        'MOBILE': ['ionic', 'xamarin', 'mobile', 'android', 'ios', 'app development'],
        'TUTORIAL': ['tutorial', 'guide', 'how to', 'step by step', 'getting started', 'introduction']
    }
    
    # Definiere Tags basierend auf spezifischen Technologien
    tag_keywords = [
        'angular', 'react', 'vue', 'javascript', 'typescript', 'html', 'css', 'sass', 'scss',
        '.net', 'c#', 'asp.net', 'blazor', 'mvc', 'web api', 'entity framework',
        'docker', 'kubernetes', 'azure', 'aws', 'git', 'github', 'visual studio',
        'npm', 'node.js', 'webpack', 'vite', 'ionic', 'xamarin', 'sql', 'database',
        'api', 'rest', 'graphql', 'json', 'xml', 'microservices', 'architecture',
        'testing', 'unit testing', 'integration testing', 'debugging', 'performance',
        'security', 'authentication', 'authorization', 'oauth', 'jwt'
    ]
    
    # Finde passende Kategorie
    categories = []
    for category, keywords in category_keywords.items():
        if any(keyword in text for keyword in keywords):
            categories.append(category)
    
    # Fallback auf "PROGRAMMING" wenn keine spezifische Kategorie gefunden
    if not categories:
        categories = ['PROGRAMMING']
    
    # Finde passende Tags
    tags = []
    for tag in tag_keywords:
        if tag in text:
            tags.append(tag.upper())
    
    # Füge zusätzliche Tags basierend auf Titel hinzu
    title_words = re.findall(r'\b\w+\b', title.lower())
    for word in title_words:
        if len(word) > 3 and word not in [tag.lower() for tag in tags]:
            if word in ['dependencies', 'versioning', 'tutorial', 'guide', 'introduction']:
                tags.append(word.upper())
    
    # Limitiere auf maximal 5 Tags
    tags = tags[:5]
    
    return categories[:2], tags  # Maximal 2 Kategorien

# Template für ein WordPress-Post mit korrekter Formatierung
def build_wp_item(title, content, date, base_url="example.com", author="Marius", post_id=None):
    post_slug = create_slug(title)
    if post_id is None:
        post_id = hash(title) % 10000
    
    # WordPress-konformes Datum
    wp_date = date.strftime('%Y-%m-%d %H:%M:%S')
    pub_date = date.strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    # Extrahiere Kategorien und Tags
    categories, tags = extract_categories_and_tags(title, content)
    
    # Erstelle Kategorie-XML
    category_xml = ""
    for i, category in enumerate(categories):
        category_slug = create_slug(category)
        category_xml += f'\n\t\t<category domain="category" nicename="{category_slug}"><![CDATA[{category}]]></category>'
    
    # Erstelle Tag-XML
    tag_xml = ""
    for tag in tags:
        tag_slug = tag.replace(' ', '-').replace('.', '').replace('#', '').lower()  # Für nicename
        tag_xml += f'\n\t\t<category domain="post_tag" nicename="{tag_slug}"><![CDATA[{tag}]]></category>'
    
    return f"""
	<item>
		<title><![CDATA[{title}]]></title>
		<link>https://{base_url}/{post_slug}/</link>
		<pubDate>{pub_date}</pubDate>
		<dc:creator><![CDATA[{author}]]></dc:creator>
		<guid isPermaLink="false">https://{base_url}/?p={post_id}</guid>
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

# XML Kopf mit korrekter WordPress-Formatierung
def build_wp_xml(items):
    return f"""<?xml version="1.0" encoding="UTF-8" ?>
<!-- This is a WordPress eXtended RSS file generated by WordPress as an export of your site. -->
<!-- It contains information about your site's posts, pages, comments, categories, and other content. -->
<!-- You may use this file to transfer that content from one site to another. -->
<!-- This file is not intended to serve as a complete backup of your site. -->

<!-- To import this information into a WordPress site follow these steps: -->
<!-- 1. Log in to that site as an administrator. -->
<!-- 2. Go to Tools: Import in the WordPress admin panel. -->
<!-- 3. Install the "WordPress" importer from the list. -->
<!-- 4. Activate & Run Importer. -->
<!-- 5. Upload this file using the form provided on that page. -->
<!-- 6. You will first be asked to map the authors in this export file to users -->
<!--    on the site. For each author, you may choose to map to an -->
<!--    existing user on the site or to create a new user. -->
<!-- 7. WordPress will then import each of the posts, pages, comments, categories, etc. -->
<!--    contained in this file into your site. -->

	<!-- generator="Medium to WordPress Migration Script" created="{datetime.now().strftime('%Y-%m-%d %H:%M')}" -->
<rss version="2.0"
	xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
	xmlns:content="http://purl.org/rss/1.0/modules/content/"
	xmlns:wfw="http://wellformedweb.org/CommentAPI/"
	xmlns:dc="http://purl.org/dc/elements/1.1/"
	xmlns:wp="http://wordpress.org/export/1.2/"
>

<channel>
	<title>Marius Schröder</title>
	<link>https://www.marius-schroeder.de</link>
	<description>Senior developer thoughts. Straight from the stack.</description>
	<pubDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
	<language>en-US</language>
	<wp:wxr_version>1.2</wp:wxr_version>
	<wp:base_site_url>https://www.marius-schroeder.de</wp:base_site_url>
	<wp:base_blog_url>https://www.marius-schroeder.de</wp:base_blog_url>

	<wp:author><wp:author_id>1</wp:author_id><wp:author_login><![CDATA[Marius]]></wp:author_login><wp:author_email><![CDATA[wordpress@marius-schroeder.de]]></wp:author_email><wp:author_display_name><![CDATA[Marius]]></wp:author_display_name><wp:author_first_name><![CDATA[]]></wp:author_first_name><wp:author_last_name><![CDATA[]]></wp:author_last_name></wp:author>

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

	<generator>Medium to WordPress Migration Script</generator>
{"".join(items)}
</channel>
</rss>"""

# Medium HTML-Dateien parsen
def parse_medium_html(file_path):
    with open(file_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")
        title_tag = soup.find("h1")
        body_section = soup.find("section", {"data-field": "body"})
        if not title_tag or not body_section:
            return None
        title = title_tag.text.strip()
        content_html = str(body_section)
        return title, content_html

# Hilfsfunktion zum Auflisten verfügbarer Blog Posts
def list_available_posts(folder_path):
    """Listet alle verfügbaren HTML-Dateien mit ihren Titeln auf."""
    print("📋 Verfügbare Blog Posts:")
    print("=" * 60)
    
    html_files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
    
    for i, file_name in enumerate(html_files, 1):
        file_path = os.path.join(folder_path, file_name)
        result = parse_medium_html(file_path)
        if result:
            title, _ = result
            print(f"{i:2d}. {title}")
            print(f"    📁 {file_name}")
        else:
            print(f"{i:2d}. ❌ Konnte nicht geparst werden")
            print(f"    📁 {file_name}")
        print()
    
    print(f"Gesamt: {len(html_files)} HTML-Dateien gefunden")
    return html_files

# Funktion zum Exportieren eines einzelnen Blog Posts
def convert_single_medium_post_to_wordpress_xml(file_path, output_file="single_post_export.xml", base_url="example.com", download_images=True):
    """Exportiert einen einzelnen Medium Blog Post zu WordPress XML."""
    
    if not os.path.exists(file_path):
        print(f"❌ Datei nicht gefunden: {file_path}")
        return False
    
    if not file_path.endswith(".html"):
        print(f"❌ Datei muss eine HTML-Datei sein: {file_path}")
        return False
    
    # Erstelle Bilder-Ordner
    images_dir = "wordpress_images"
    if download_images and not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"📁 Bilder-Ordner erstellt: {images_dir}")
    
    print(f"🔄 Verarbeite: {os.path.basename(file_path)}")
    result = parse_medium_html(file_path)
    
    if not result:
        print(f"❌ Konnte HTML-Datei nicht parsen: {file_path}")
        return False
    
    title, content = result
    post_slug = create_slug(title)
    
    # Verarbeite Bilder und Links nur wenn gewünscht
    if download_images:
        content = process_content(content, post_slug, images_dir, base_url)
    
    # Extrahiere Datum aus Dateiname
    filename = os.path.basename(file_path)
    date = extract_date_from_filename(filename)
    post_id = hash(title) % 100000  # Größerer Bereich für Post-IDs
    
    wp_item = build_wp_item(title, content, date, base_url, post_id=post_id)
    
    full_xml = build_wp_xml([wp_item])
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_xml)
    
    print(f"✅ Post verarbeitet: {title}")
    print(f"\n🎉 Einzelner Post exportiert!")
    print(f"📄 WordPress XML: {output_file}")
    if download_images:
        print(f"🖼️  Bilder-Ordner: {images_dir}")
        print(f"💡 Tipp: Lade alle Bilder aus '{images_dir}' in deine WordPress Media Library hoch")
    
    return True

# Hauptfunktion
def convert_medium_folder_to_wordpress_xml(folder_path, output_file="wordpress_export.xml", base_url="example.com", download_images=True):
    items = []
    
    # Erstelle Bilder-Ordner
    images_dir = "wordpress_images"
    if download_images and not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"📁 Bilder-Ordner erstellt: {images_dir}")
    
    for file_name in os.listdir(folder_path):
        if not file_name.endswith(".html"):
            continue
        
        print(f"🔄 Verarbeite: {file_name}")
        result = parse_medium_html(os.path.join(folder_path, file_name))
        if result:
            title, content = result
            post_slug = create_slug(title)
            
            # Verarbeite Bilder und Links nur wenn gewünscht
            if download_images:
                content = process_content(content, post_slug, images_dir, base_url)
            
            # Extrahiere Datum aus Dateiname
            date = extract_date_from_filename(file_name)
            post_id = hash(title) % 100000  # Größerer Bereich für Post-IDs
            
            wp_item = build_wp_item(title, content, date, base_url, post_id=post_id)
            items.append(wp_item)
            print(f"✅ Post verarbeitet: {title}")

    full_xml = build_wp_xml(items)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_xml)
    
    print(f"\n🎉 Export abgeschlossen!")
    print(f"📄 WordPress XML: {output_file}")
    print(f"📊 {len(items)} Blog Posts exportiert")
    if download_images:
        print(f"🖼️  Bilder-Ordner: {images_dir}")
        print(f"💡 Tipp: Lade alle Bilder aus '{images_dir}' in deine WordPress Media Library hoch")

# Beispielaufrufe (auskommentiert):

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("📋 Verfügbare Blog Posts:")
        print("=" * 60)
        list_available_posts("export_htmls")
        print("\n💡 Verwendung:")
        print("  python medium_to_wordpress.py all <base_url>")
        print("  python medium_to_wordpress.py single <datei_oder_nummer> <base_url>")
        print("  python medium_to_wordpress.py list")
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_available_posts("export_htmls")
    
    elif command == "all":
        if len(sys.argv) < 3:
            print("❌ Base URL fehlt")
            print("💡 Verwendung: python medium_to_wordpress.py all <base_url>")
            sys.exit(1)
        
        base_url = sys.argv[2]
        print(f"🚀 Exportiere alle Posts nach {base_url}...")
        convert_medium_folder_to_wordpress_xml("export_htmls", "wordpress_export.xml", base_url, download_images=True)
    
    elif command == "single":
        if len(sys.argv) < 4:
            print("📋 Verfügbare Blog Posts:")
            print("=" * 60)
            list_available_posts("export_htmls")
            print("\n💡 Verwendung: python medium_to_wordpress.py single <datei_oder_nummer> <base_url>")
            sys.exit(1)
        
        file_or_number = sys.argv[2]
        base_url = sys.argv[3]
        
        # Prüfe ob es eine Nummer ist
        if file_or_number.isdigit():
            # Hole Liste der HTML-Dateien
            html_files = []
            export_dir = "export_htmls"
            
            for filename in sorted(os.listdir(export_dir)):
                if filename.endswith(".html"):
                    html_files.append(filename)
            
            post_number = int(file_or_number)
            if 1 <= post_number <= len(html_files):
                selected_file = html_files[post_number - 1]
                file_path = os.path.join(export_dir, selected_file)
                
                # Erstelle Output-Dateiname basierend auf dem Original
                base_name = os.path.splitext(selected_file)[0]
                output_file = f"{base_name}.xml"
                
                print(f"🚀 Exportiere Post #{post_number}: {selected_file}")
                convert_single_medium_post_to_wordpress_xml(file_path, output_file, base_url, download_images=True)
            else:
                print(f"❌ Ungültige Post-Nummer: {post_number}")
                print(f"   Verfügbare Posts: 1-{len(html_files)}")
                sys.exit(1)
        else:
            # Behandle als Dateiname
            if not file_or_number.startswith("export_htmls/"):
                file_path = os.path.join("export_htmls", file_or_number)
            else:
                file_path = file_or_number
            
            if not os.path.exists(file_path):
                print(f"❌ Datei nicht gefunden: {file_path}")
                sys.exit(1)
            
            # Erstelle Output-Dateiname basierend auf dem Original
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_file = f"{base_name}.xml"
            
            print(f"🚀 Exportiere Post: {os.path.basename(file_path)}")
            convert_single_medium_post_to_wordpress_xml(file_path, output_file, base_url, download_images=True)
    
    else:
        print(f"❌ Unbekannter Befehl: {command}")
        print("💡 Verfügbare Befehle: list, all, single")

# Beispielaufrufe (auskommentiert):

# 1. Alle verfügbaren Posts auflisten
# list_available_posts("export_htmls")

# 2. Alle Blog Posts aus einem Ordner exportieren (einfaches HTML Format)
# convert_medium_folder_to_wordpress_xml("export_htmls", "wordpress_export.xml", "www.marius-schroeder.de", download_images=True)

# 3. Nur einen einzelnen Blog Post exportieren (einfaches HTML Format)
# convert_single_medium_post_to_wordpress_xml("export_htmls/2019-07-04_Angular--Dependencies-and-Versioning-5691beba463e.html", "single_post.xml", "www.marius-schroeder.de", download_images=True)
