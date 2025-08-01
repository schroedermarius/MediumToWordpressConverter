#!/usr/bin/env python3
"""
Demo script showing the improved link processing capabilities
"""

from medium_to_wordpress_optimized import MediumToWordPressConverter
from bs4 import BeautifulSoup

def demo_link_processing():
    """Demonstrate the link processing improvements."""
    print("🔗 Medium to WordPress Link Processing Demo")
    print("=" * 50)
    
    # Create converter for a German domain (.de)
    converter = MediumToWordPressConverter("marius-schroeder.de", download_images=False)
    
    # Test slug cleaning
    print("\n1. 📝 Medium Slug Cleaning:")
    test_slugs = [
        "angular-dependencies-and-versioning-5691beba463e",
        "react-tutorial-for-beginners-abc123def456",
        "simple-post-xyz789",
        "devops-best-practices-123abc456def"
    ]
    
    for slug in test_slugs:
        clean_slug = converter.clean_medium_post_slug(slug)
        print(f"   {slug}")
        print(f"   → {clean_slug}")
        print()
    
    # Test link processing
    print("2. 🌐 Link Processing:")
    sample_html = """
    <div>
        <p>Check out my previous post about <a href="https://medium.com/@mariusschroeder/angular-dependencies-and-versioning-5691beba463e">Angular dependencies</a>.</p>
        <p>Also read this <a href="https://medium.com/medialesson/react-tutorial-abc123def456">React tutorial</a>.</p>
        <p>Visit my <a href="https://www.marius-schroeder.com/about">old website</a>.</p>
        <p>See this <a href="https://medium.com/simple-post-xyz789">direct Medium link</a>.</p>
    </div>
    """
    
    soup = BeautifulSoup(sample_html, 'html.parser')
    div_element = soup.find('div')
    
    print("   Before processing:")
    for link in div_element.find_all('a'):
        print(f"   - {link.get('href')}")
    
    # Process the links
    converter.process_links_in_element(div_element, "marius-schroeder.de")
    
    print("\n   After processing:")
    for link in div_element.find_all('a'):
        print(f"   - {link.get('href')}")
    
    print("\n✅ Demo completed! As you can see:")
    print("   • Medium hash IDs are removed")
    print("   • Links point to your domain")
    print("   • Works with any domain extension (.de, not just .com)")
    print("   • Handles profile, publication, and direct links")

if __name__ == "__main__":
    demo_link_processing()
