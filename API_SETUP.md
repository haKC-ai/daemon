# AI API Configuration Guide

## Overview

The Daemon Network system uses modern AI APIs (Claude and OpenAI) to provide autonomous decision-making capabilities. This guide shows you how to configure your API keys **securely** using environment variables.

![Security](https://img.shields.io/badge/Security-Best%20Practices-success.svg)
![Method](https://img.shields.io/badge/Method-.env%20File-blue.svg)

## 🔒 Security First

**CRITICAL: Never commit API keys to version control!**

This project uses `.env` files to keep your API keys secure and separate from your code.

## Required API Keys

You'll need at least one of the following:

### 1. Anthropic Claude API Key (Recommended)
![Claude](https://img.shields.io/badge/Claude-Sonnet%204-00A67E.svg)

- **Sign up**: https://console.anthropic.com/
- **Model**: Claude Sonnet 4
- **Pricing**: ~$3/M input tokens, ~$15/M output tokens
- **Best for**: Natural language understanding, complex reasoning

### 2. OpenAI API Key (Optional)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991.svg)

- **Sign up**: https://platform.openai.com/
- **Model**: GPT-4 Turbo
- **Pricing**: ~$10/M input tokens, ~$30/M output tokens
- **Best for**: Alternative to Claude, JSON formatting

---

## Quick Setup (3 Steps)

### Step 1: Get Your API Keys

**For Claude:**
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-`)

**For OpenAI:**
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)

### Step 2: Create Your .env File

```bash
# Copy the example file
cp .env.example .env
```

### Step 3: Add Your API Keys

Open `.env` in a text editor and replace the placeholder values:

```bash
# AI API Keys Configuration
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
OPENAI_API_KEY=sk-your-actual-key-here

# AI Configuration (optional - defaults are fine)
CLAUDE_MODEL=claude-sonnet-4-20250514
OPENAI_MODEL=gpt-4-turbo-preview
DEFAULT_AI=claude
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=4096

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-random-secret-key-here
```

**That's it!** The system will automatically load these values.

---

##  Verify Your Configuration

Test that your API keys are working:

```bash
source daemon_venv/bin/activate
python -c "from ai_integration import AICore; ai = AICore(); print('✓ API Keys configured!' if (ai.claude_client or ai.openai_client) else '✗ No API keys found')"
```

---

## Security Best Practices

### DO 

-  Use the `.env` file for API keys
-  Keep `.env` in your `.gitignore` (already configured)
-  Use different keys for development and production
-  Rotate keys every 90 days
-  Set up billing alerts in API dashboards
-  Monitor usage regularly
-  Use environment-specific keys

### DON'T 

- **NEVER** commit `.env` to git
- **NEVER** share your `.env` file
- **NEVER** hardcode API keys in source code
- **NEVER** post keys in issues or forums
- **NEVER** use production keys for testing
- **NEVER** commit `daemon_data/ai_config.json` with keys

---

## Cost Estimates

![Cost](https://img.shields.io/badge/Monthly%20Cost-%245--20-blue.svg)

### Typical Usage Costs

| Operation | Tokens | Claude Cost | OpenAI Cost |
|-----------|--------|-------------|-------------|
| Trigger evaluation | ~500 | ~$0.01 | ~$0.02 |
| Quest generation | ~1000 | ~$0.02 | ~$0.05 |
| Decision making | ~1500 | ~$0.03 | ~$0.08 |
| Strategic planning | ~3000 | ~$0.06 | ~$0.15 |

**For casual use (10-20 operations/day):**
- Claude: ~$5-10/month
- OpenAI: ~$10-20/month

**For heavy use (100+ operations/day):**
- Claude: ~$20-40/month
- OpenAI: ~$40-80/month

---

## 🔧 Configuration Options

### AI Models

You can change which models to use in your `.env` file:

```bash
# Use different Claude model
CLAUDE_MODEL=claude-3-opus-20240229

# Use different OpenAI model
OPENAI_MODEL=gpt-4

# Set default AI provider
DEFAULT_AI=openai  # or 'claude'
```

### AI Behavior

Adjust how the AI responds:

```bash
# Lower temperature = more focused/deterministic (0.0 - 1.0)
AI_TEMPERATURE=0.5

# More tokens = longer responses (1000 - 8000)
AI_MAX_TOKENS=8000
```

### Flask Security

Generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Add it to your `.env`:

```bash
SECRET_KEY=your-generated-key-here
```

---

## Alternative: Direct Environment Variables

If you prefer not to use a `.env` file, you can set environment variables directly:

### Linux/macOS

```bash
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
```

Make permanent by adding to `~/.bashrc` or `~/.zshrc`:

```bash
echo 'export ANTHROPIC_API_KEY="your-key"' >> ~/.bashrc
echo 'export OPENAI_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

### Windows (PowerShell)

```powershell
$env:ANTHROPIC_API_KEY="your-key-here"
$env:OPENAI_API_KEY="your-key-here"
```

Make permanent:

```powershell
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'your-key', 'User')
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'your-key', 'User')
```

---

## Troubleshooting

### "No API keys configured" Error

**Problem**: System can't find your API keys

**Solutions**:
1. Verify `.env` file exists in project root
2. Check keys are correctly formatted (no quotes needed)
3. Ensure no extra spaces around `=`
4. Restart your terminal/IDE after creating `.env`
5. Run from the correct directory (where `.env` is located)

**Test**:
```bash
cat .env | grep API_KEY
```

### "Invalid API key" Error

**Problem**: API key is incorrect or expired

**Solutions**:
1. Verify key is copied correctly from API dashboard
2. Check for extra spaces or newlines
3. Regenerate key in API dashboard
4. Ensure key hasn't been revoked

**Test**:
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY')[:10] + '...')"
```

### "Rate limit exceeded" Error

**Problem**: Too many API calls too quickly

**Solutions**:
1. Wait 60 seconds and try again
2. Check API dashboard for rate limits
3. Reduce frequency of operations
4. Upgrade API tier if needed

### Keys Not Loading

**Problem**: `.env` file exists but keys not loading

**Solutions**:
1. Ensure file is named `.env` (not `env` or `.env.txt`)
2. Place `.env` in project root directory
3. Restart Python process
4. Check file permissions: `chmod 600 .env`

**Verify**:
```bash
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('Loaded!' if os.getenv('ANTHROPIC_API_KEY') else 'Not loaded')"
```

---

## AI Capabilities Enabled

Once configured, the AI enables these autonomous features:

### 1. Natural Language Trigger Creation
- Parse English descriptions into executable triggers
- Automatic safety validation
- Structured trigger generation

### 2. Autonomous Quest Generation
- Context-aware quest creation
- Adaptive difficulty scaling
- Balanced reward systems

### 3. Intelligent Decision Making
- Complex condition evaluation
- Strategic planning
- Risk assessment

### 4. Automated Validation
- Quest completion evaluation
- Operative performance analysis
- Quality assessment

### 5. Network Analysis
- Anomaly detection
- Threat assessment
- Performance optimization

---

## Next Steps

After configuration:

1. **Test the Demo**:
   ```bash
   python demo_ai.py
   ```

2. **Start the System**:
   ```bash
   python web_interface.py
   ```

3. **Create Your First Trigger**:
   - Navigate to http://localhost:5000
   - Register as an operative
   - Reach Rank 3
   - Go to `/triggers` and create triggers in natural language

---

## Support

### API-Related Issues

- **Anthropic**: https://support.anthropic.com/
- **OpenAI**: https://help.openai.com/

### System Issues

- Check logs in `daemon_data/action_log.json`
- Enable debug mode: `FLASK_DEBUG=True` in `.env`
- Review error messages in terminal

### Security Concerns

If you accidentally committed your API keys:

1. **Immediately** revoke them in the API dashboard
2. Generate new keys
3. Update your `.env` file
4. Use `git filter-branch` or BFG Repo-Cleaner to remove from history

---

## 🔒 Final Security Reminder

Your `.env` file contains sensitive credentials. Treat it like a password:

- Never commit to version control (already in `.gitignore`)
- Never share publicly
- Never include in screenshots
- Rotate keys regularly
- Use different keys per environment

**The `.gitignore` file is already configured to protect your `.env` file and other sensitive data.**

---

## Monitoring Usage

Track your API usage to manage costs:

**Claude Dashboard**: https://console.anthropic.com/settings/usage

**OpenAI Dashboard**: https://platform.openai.com/usage

Set up billing alerts to avoid surprises!

---

