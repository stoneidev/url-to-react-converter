#!/bin/bash

# URL to React Converter - Setup Script

echo "🚀 Setting up URL to React Converter..."

# 1. Check Python version
echo ""
echo "📋 Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# 2. Create virtual environment
echo ""
echo "🐍 Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping..."
else
    python -m venv venv
    echo "✅ Virtual environment created"
fi

# 3. Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# 4. Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# 5. Install requirements
echo ""
echo "📦 Installing Python packages..."
pip install -r requirements.txt

# 6. Install Playwright browsers
echo ""
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# 7. Check AWS configuration
echo ""
echo "☁️  Checking AWS configuration..."
if command -v aws &> /dev/null; then
    echo "AWS CLI found"
    aws configure list
else
    echo "⚠️  AWS CLI not found. Please install it: https://aws.amazon.com/cli/"
fi

# 8. Create .env file if not exists
echo ""
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your AWS settings."
else
    echo "✅ .env file already exists"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Edit .env file with your AWS settings"
echo "   3. Verify AWS Bedrock access: aws bedrock list-foundation-models --region us-east-1"
echo "   4. Start coding! 🚀"
echo ""
