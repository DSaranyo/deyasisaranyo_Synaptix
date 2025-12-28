#!/bin/bash

# Setup script for Agentic Pathway System

echo "🚀 Setting up Agentic Developer Workflow Agent"

# Create output directory
mkdir -p output
echo "✓ Created output directory"

# Create data directory if not exists
mkdir -p data
echo "✓ Verified data directory"

# Install dependencies
echo "📦 Installing dependencies..."
pip install --break-system-packages -q pathway litellm python-dotenv

echo "✓ Dependencies installed"

# Set up environment variables
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# LLM Configuration
ANTHROPIC_API_KEY=your_api_key_here

# Optional: Use OpenAI-compatible endpoint
# OPENAI_API_BASE=http://localhost:8000/v1
# OPENAI_API_KEY=your_key_here

# Pathway Configuration
PATHWAY_THREADS=4
PATHWAY_MONITORING=false
EOF
    echo "✓ Created .env template"
    echo "⚠️  Please add your API keys to .env file"
else
    echo "✓ .env file exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the agent:"
echo "  python agent.py"
echo ""
echo "To use with Claude API, set ANTHROPIC_API_KEY in .env"
