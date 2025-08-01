# Contributing to Medium to WordPress Converter

Thank you for your interest in contributing to this project! This document outlines the process for contributing and provides guidelines for submitting changes.

## 🤝 How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. **Check existing issues** to see if it's already reported
2. **Create a new issue** with a clear title and description
3. **Include relevant details** such as:
   - Python version
   - Operating system
   - Error messages (if any)
   - Steps to reproduce the issue
   - Sample HTML files (if applicable)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:

1. **Check existing issues** for similar suggestions
2. **Create an issue** labeled as "enhancement"
3. **Describe the enhancement** in detail
4. **Explain the use case** and why it would be beneficial

### Contributing Code

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Test your changes** (`python test_setup.py`)
5. **Commit your changes** (`git commit -m 'Add amazing feature'`)
6. **Push to the branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

## 📝 Development Guidelines

### Code Style

- Follow **PEP 8** Python style guidelines
- Use **meaningful variable and function names**
- Add **docstrings** for all functions and classes
- Include **type hints** where appropriate
- Keep functions **focused and single-purpose**

### Testing

- Run the test suite before submitting: `python test_setup.py`
- Add tests for new features when applicable
- Ensure all existing tests pass
- Test with various HTML export formats

### Documentation

- Update the README if you add new features
- Add docstrings to new functions
- Update the changelog for significant changes
- Include examples in docstrings where helpful

## 🏗️ Project Structure

```
MediumToWordpressConverter/
├── medium_to_wordpress_optimized.py   # Main converter script
├── test_setup.py                      # Test suite
├── requirements.txt                   # Dependencies
├── setup.py                          # Package setup
├── config.example.py                 # Example configuration
├── README.md                         # Project documentation
├── CONTRIBUTING.md                   # This file
├── CHANGELOG.md                      # Version history
├── LICENSE                           # MIT License
├── Makefile                          # Development commands
└── blog_post.md                      # Example blog post
```

## 🧪 Testing Changes

Before submitting a pull request:

1. **Run the test suite**:
   ```bash
   python test_setup.py
   ```

2. **Test with real Medium exports** (if available):
   ```bash
   python medium_to_wordpress_optimized.py list
   ```

3. **Test edge cases**:
   - Empty HTML files
   - Files with unusual characters
   - Different date formats
   - Various image types

## 📋 Pull Request Process

1. **Ensure all tests pass**
2. **Update documentation** if needed
3. **Add a clear description** of what your PR does
4. **Reference any related issues**
5. **Be responsive to feedback** during code review

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Changes Made
- List specific changes
- Include any new features
- Mention any breaking changes

## Testing
Describe how you tested your changes.

## Related Issues
Fixes #(issue number)
```

## 🎯 Areas for Contribution

Here are some areas where contributions would be especially welcome:

### High Priority
- **Performance improvements** for large HTML files
- **Better error handling** for malformed HTML
- **Support for more image formats** and edge cases
- **Enhanced categorization** algorithms

### Medium Priority
- **Custom configuration** file support enhancement
- **WordPress plugin** for direct import
- **Batch processing** improvements
- **Progress indicators** for long operations

### Low Priority
- **Additional export formats** (JSON, etc.)
- **GUI interface** option
- **Docker containerization**
- **CI/CD pipeline** setup

## 🐛 Bug Report Template

When reporting bugs, please include:

```markdown
## Bug Description
A clear description of what the bug is.

## To Reproduce
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
What you expected to happen.

## Environment
- OS: [e.g. macOS, Windows, Linux]
- Python Version: [e.g. 3.9.0]
- Package Version: [e.g. 1.0.0]

## Additional Context
Any other context about the problem.
```

## 📞 Getting Help

If you need help with contributing:

1. **Check the README** for setup instructions
2. **Look at existing issues** for similar problems
3. **Create a new issue** with your question
4. **Be specific** about what you're trying to do

## 📜 Code of Conduct

This project follows a simple code of conduct:

- **Be respectful** to other contributors
- **Be constructive** in feedback and discussions
- **Focus on the project** and avoid personal attacks
- **Help newcomers** when you can

## 🎉 Recognition

Contributors will be recognized in:
- The project README
- Release notes for significant contributions
- GitHub's contributor graphs

Thank you for helping make this project better! 🚀
