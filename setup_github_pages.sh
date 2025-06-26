#!/bin/bash

# GitHub Pages Setup Script for Singapore Policy Impact Assessment Framework
# This script helps configure your repository for GitHub Pages deployment

echo "🚀 Setting up GitHub Pages for Singapore Policy Impact Assessment Framework"
echo "=================================================================="

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "docs" ]; then
    echo "❌ Error: Please run this script from the root of your repository"
    echo "   Make sure you have README.md and docs/ directory"
    exit 1
fi

echo "✅ Repository structure verified"

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Error: Git is not installed or not in PATH"
    exit 1
fi

echo "✅ Git found"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    echo "   Please initialize git first: git init"
    exit 1
fi

echo "✅ Git repository detected"

# Create .gitattributes if it doesn't exist
if [ ! -f ".gitattributes" ]; then
    echo "📝 Creating .gitattributes for proper GitHub language detection"
    cat > .gitattributes << 'EOF'
# GitHub language detection
*.py linguist-language=Python
*.html linguist-language=HTML
*.css linguist-language=CSS
*.js linguist-language=JavaScript
*.md linguist-documentation=true
*.txt linguist-documentation=true
docs/* linguist-documentation=false
docs/*.html linguist-language=HTML
docs/assets/css/* linguist-language=CSS
docs/assets/js/* linguist-language=JavaScript
EOF
    echo "✅ .gitattributes created"
else
    echo "✅ .gitattributes already exists"
fi

# Create or update .github/workflows directory for GitHub Actions
mkdir -p .github/workflows

# Create GitHub Pages deployment workflow
if [ ! -f ".github/workflows/pages.yml" ]; then
    echo "📝 Creating GitHub Actions workflow for automated deployment"
    cat > .github/workflows/pages.yml << 'EOF'
name: Deploy GitHub Pages

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        
      - name: Setup Pages
        uses: actions/configure-pages@v4
        
      - name: Build with Jekyll
        uses: actions/jekyll-build-pages@v1
        with:
          source: ./docs
          destination: ./_site
          
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
EOF
    echo "✅ GitHub Actions workflow created"
else
    echo "✅ GitHub Actions workflow already exists"
fi

# Update main README.md to include GitHub Pages link
echo "📝 Updating main README.md with GitHub Pages information"

# Create a backup of the current README
cp README.md README.md.backup

# Add GitHub Pages section to README if it doesn't exist
if ! grep -q "GitHub Pages" README.md; then
    cat >> README.md << 'EOF'

## 🌐 GitHub Pages Website

**Live Demo:** [Singapore Policy Impact Assessment Framework](https://yourusername.github.io/Policy_Impact_Score_Singapore)

### 📊 Interactive Features
- **Comprehensive Dashboard** with policy analysis results
- **International Validation** from 16 independent sources  
- **Scientific Methodology** documentation
- **87.6/100 Transparency Score** achievement
- **Responsive Design** optimized for all devices

### 🚀 Quick Access
- [**Main Overview**](https://yourusername.github.io/Policy_Impact_Score_Singapore) - Executive summary and key findings
- [**Methodology**](https://yourusername.github.io/Policy_Impact_Score_Singapore/pages/methodology.html) - Detailed MCDA framework
- [**Reports**](https://yourusername.github.io/Policy_Impact_Score_Singapore/pages/reports.html) - All research documentation

> **Note:** Replace `yourusername` with your actual GitHub username in the URLs above.

### 📱 Mobile Optimized
The GitHub Pages site is fully responsive and optimized for:
- Desktop computers and laptops
- Tablets and mobile devices  
- Screen readers and accessibility tools
- Fast loading with compressed assets

EOF
    echo "✅ GitHub Pages information added to README.md"
else
    echo "✅ GitHub Pages information already in README.md"
fi

# Check current git status
echo "📋 Current Git Status:"
git status --porcelain

# Provide setup instructions
echo ""
echo "🎯 SETUP COMPLETE!"
echo "=================================================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. 📝 UPDATE CONFIGURATION:"
echo "   - Edit docs/_config.yml and replace 'yourusername' with your GitHub username"
echo "   - Update repository URL and other personal details"
echo ""
echo "2. 🔗 UPDATE LINKS:"
echo "   - Replace placeholder links in docs/index.html"
echo "   - Update email addresses and contact information"
echo ""
echo "3. 📤 COMMIT AND PUSH:"
echo "   git add ."
echo "   git commit -m \"Add GitHub Pages setup with comprehensive policy analysis site\""
echo "   git push origin main"
echo ""
echo "4. 🚀 ENABLE GITHUB PAGES:"
echo "   - Go to your repository on GitHub"
echo "   - Navigate to Settings > Pages"
echo "   - Source: Deploy from a branch"
echo "   - Branch: main"
echo "   - Folder: /docs"
echo "   - Click Save"
echo ""
echo "5. 🌐 ACCESS YOUR SITE:"
echo "   Your site will be available at:"
echo "   https://yourusername.github.io/Policy_Impact_Score_Singapore"
echo "   (Replace 'yourusername' with your actual GitHub username)"
echo ""
echo "⏱️  GitHub Pages typically takes 5-10 minutes to build and deploy"
echo "✨ Your comprehensive policy analysis will then be live!"
echo ""
echo "📊 FEATURES INCLUDED:"
echo "   ✅ Interactive dashboard with Chart.js visualizations"
echo "   ✅ 87.6/100 transparency score presentation"
echo "   ✅ 16 international sources validation"
echo "   ✅ Responsive design for all devices"
echo "   ✅ SEO optimized with proper meta tags"
echo "   ✅ Professional Singapore-themed styling"
echo ""
echo "🎉 Ready to showcase your policy impact assessment research!"
