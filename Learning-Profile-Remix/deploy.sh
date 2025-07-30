#!/bin/bash

echo "🚀 Begin Learning Profile - Web Deployment Setup"
echo "=============================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: Begin Learning Profile - Day 1 Back to School MVP"
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

echo ""
echo "🌐 Deployment Options:"
echo ""
echo "1. STREAMLIT CLOUD (Recommended for demos)"
echo "   • Go to: https://share.streamlit.io"
echo "   • Connect your GitHub account"
echo "   • Select this repository"
echo "   • Main file: main.py"
echo "   • Click Deploy"
echo ""
echo "2. REPLIT (Instant deploy)"
echo "   • Go to: https://replit.com"
echo "   • Import from GitHub or upload files"
echo "   • Run command: streamlit run main.py --server.port 8080"
echo ""
echo "3. RAILWAY (Production-ready)"
echo "   • Go to: https://railway.app"
echo "   • Connect GitHub repository"
echo "   • Automatic deployment"
echo ""

echo "📋 Files ready for deployment:"
echo "   ✅ main.py (main application)"
echo "   ✅ requirements.txt (dependencies)"
echo "   ✅ .streamlit/config.toml (theme configuration)"
echo "   ✅ README.md (documentation)"
echo "   ✅ All utility files and assets"
echo ""

echo "🎯 Next Steps:"
echo "1. Push this repository to GitHub"
echo "2. Deploy on your chosen platform"
echo "3. Share the public URL for demos!"
echo ""

echo "💡 Pro Tip: The app works perfectly without a database for demos."
echo "   All teacher assignment and results functionality will work!"
echo ""

echo "🔗 Your app will be available at URLs like:"
echo "   Homepage: https://your-app.streamlit.app"
echo "   Teacher Dashboard: https://your-app.streamlit.app?page=teacher_register"
echo "   Assignment Links: https://your-app.streamlit.app?token=xyz123"