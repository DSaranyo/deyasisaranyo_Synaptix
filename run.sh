#!/bin/bash

# Run script for Agentic Pathway System

echo "🤖 Starting Agentic Developer Workflow Agent"
echo ""

# Check if dependencies are installed
if ! python3 -c "import pathway" 2>/dev/null; then
    echo "⚠️  Pathway not installed. Installing dependencies..."
    pip install --break-system-packages -q pathway litellm python-dotenv
    echo "✓ Dependencies installed"
fi

# Ensure output directory exists
mkdir -p output

# Run the agent
echo "🚀 Launching agent..."
echo ""

python3 agent_simple.py

echo ""
echo "✅ Agent execution complete"
echo ""
echo "📄 Output saved to: ./output/agent_actions.jsonl"
