#!/usr/bin/env python3
"""
Test script for Medium to WordPress Converter
Run this to verify your setup is working correctly.
"""

import os
import sys
import tempfile
from datetime import datetime

def test_imports():
    """Test that all required imports work."""
    print("🔍 Testing imports...")
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError:
        print("❌ requests not found - run: pip install requests")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup imported successfully")
    except ImportError:
        print("❌ BeautifulSoup not found - run: pip install beautifulsoup4")
        return False
    
    try:
        import lxml
        print("✅ lxml imported successfully")
    except ImportError:
        print("❌ lxml not found - run: pip install lxml")
        return False
    
    return True

def test_converter_import():
    """Test that the converter module can be imported."""
    print("\n🔍 Testing converter import...")
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from medium_to_wordpress_optimized import MediumToWordPressConverter
        print("✅ MediumToWordPressConverter imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Could not import converter: {e}")
        return False

def test_basic_functionality():
    """Test basic converter functionality."""
    print("\n🔍 Testing basic functionality...")
    try:
        from medium_to_wordpress_optimized import MediumToWordPressConverter
        
        # Create converter instance
        converter = MediumToWordPressConverter("test-domain.com", download_images=False)
        print("✅ Converter instance created successfully")
        
        # Test slug creation
        test_title = "Test Blog Post: How to Use This Tool!"
        slug = converter.create_slug(test_title)
        expected_slug = "test-blog-post-how-to-use-this-tool"
        if slug == expected_slug:
            print(f"✅ Slug creation works: '{test_title}' → '{slug}'")
        else:
            print(f"❌ Slug creation failed: expected '{expected_slug}', got '{slug}'")
            return False
        
        # Test date extraction
        test_filename = "2023-12-25_Christmas-Post-abc123.html"
        date = converter.extract_date_from_filename(test_filename)
        if date.year == 2023 and date.month == 12 and date.day == 25:
            print(f"✅ Date extraction works: '{test_filename}' → {date.strftime('%Y-%m-%d')}")
        else:
            print(f"❌ Date extraction failed: {date}")
            return False
        
        # Test categorization
        test_content = "This is a tutorial about Angular and TypeScript development"
        categories, tags = converter.extract_categories_and_tags("Angular Tutorial", test_content)
        if "WEB DEVELOPMENT" in categories or "TUTORIAL" in categories:
            print(f"✅ Categorization works: found categories {categories}")
        else:
            print(f"❌ Categorization failed: {categories}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_sample_html():
    """Test with a sample HTML structure."""
    print("\n🔍 Testing HTML processing...")
    try:
        from medium_to_wordpress_optimized import MediumToWordPressConverter
        
        # Create sample Medium-style HTML
        sample_html = """
        <section data-field="body">
            <div>
                <h2>Sample Heading</h2>
                <p>This is a sample paragraph with some <strong>bold text</strong>.</p>
                <figure>
                    <img src="https://example.com/image.jpg" alt="Sample image">
                </figure>
                <pre><code>console.log('Hello, World!');</code></pre>
            </div>
        </section>
        """
        
        converter = MediumToWordPressConverter("test-domain.com", download_images=False)
        processed_content = converter.process_content(sample_html, "test-post")
        
        if "<h2>Sample Heading</h2>" in processed_content:
            print("✅ HTML processing works: headings preserved")
        else:
            print("❌ HTML processing failed: headings not found")
            return False
        
        if "<strong>bold text</strong>" in processed_content:
            print("✅ HTML processing works: formatting preserved")
        else:
            print("❌ HTML processing failed: formatting not preserved")
            return False
        
        print("✅ HTML processing completed successfully")
        return True
    except Exception as e:
        print(f"❌ HTML processing test failed: {e}")
        return False

def test_directories():
    """Test directory structure and permissions."""
    print("\n🔍 Testing directory setup...")
    
    # Check if export_htmls directory exists or can be created
    export_dir = "export_htmls"
    if not os.path.exists(export_dir):
        try:
            os.makedirs(export_dir)
            print(f"✅ Created {export_dir} directory")
        except Exception as e:
            print(f"❌ Could not create {export_dir}: {e}")
            return False
    else:
        print(f"✅ {export_dir} directory exists")
    
    # Test write permissions
    try:
        test_file = "test_write_permissions.txt"
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("✅ Write permissions OK")
    except Exception as e:
        print(f"❌ Write permission test failed: {e}")
        return False
    
    return True

def test_link_processing():
    """Test the improved link processing functionality."""
    print("\n🔍 Testing link processing...")
    try:
        from medium_to_wordpress_optimized import MediumToWordPressConverter
        from bs4 import BeautifulSoup
        
        converter = MediumToWordPressConverter("example.de", download_images=False)
        
        # Test Medium post slug cleaning
        test_cases = [
            ("post-title-5691beba463e", "post-title"),
            ("angular-dependencies-and-versioning-abc123def456", "angular-dependencies-and-versioning"),
            ("simple-post", "simple-post"),
            ("post-with-numbers-123-abc456", "post-with-numbers-123"),
        ]
        
        for original, expected in test_cases:
            result = converter.clean_medium_post_slug(original)
            if result == expected:
                print(f"✅ Slug cleaning: '{original}' → '{result}'")
            else:
                print(f"❌ Slug cleaning failed: '{original}' → '{result}' (expected '{expected}')")
                return False
        
        # Test link processing with sample HTML
        sample_html = """
        <div>
            <p>Check out my <a href="https://medium.com/@username/great-post-abc123def456">other post</a>.</p>
            <p>Also see <a href="https://medium.com/publication/another-post-xyz789">this article</a>.</p>
            <p>Visit my <a href="https://www.example.de/old-link">website</a>.</p>
        </div>
        """
        
        soup = BeautifulSoup(sample_html, 'html.parser')
        div_element = soup.find('div')
        
        # Process links
        converter.process_links_in_element(div_element, "example.de")
        
        # Check results
        links = div_element.find_all('a')
        
        # First link should be converted to example.de domain with cleaned slug
        first_link = links[0].get('href')
        if "example.de/great-post/" in first_link:
            print(f"✅ Medium profile link processed: {first_link}")
        else:
            print(f"❌ Medium profile link failed: {first_link}")
            return False
        
        # Second link should be converted to example.de domain with cleaned slug
        second_link = links[1].get('href')
        if "example.de/another-post/" in second_link:
            print(f"✅ Medium publication link processed: {second_link}")
        else:
            print(f"❌ Medium publication link failed: {second_link}")
            return False
        
        # Third link should be updated to use example.de
        third_link = links[2].get('href')
        if "example.de" in third_link:
            print(f"✅ Domain reference updated: {third_link}")
        else:
            print(f"❌ Domain reference failed: {third_link}")
            return False
        
        print("✅ Link processing works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Link processing test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Medium to WordPress Converter - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_imports),
        ("Converter Import", test_converter_import),
        ("Basic Functionality", test_basic_functionality),
        ("HTML Processing", test_sample_html),
        ("Link Processing", test_link_processing),
        ("Directory Setup", test_directories),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready to use.")
        print("\n📖 Next steps:")
        print("1. Export your Medium posts (Settings → Download your information)")
        print("2. Place HTML files in the 'export_htmls' directory")
        print("3. Run: python medium_to_wordpress_optimized.py list")
    else:
        print("⚠️  Some tests failed. Please fix the issues above before proceeding.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
