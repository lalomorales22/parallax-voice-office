# Parallax Voice Office

**Your intelligent voice-enabled task management assistant powered by distributed computing.**

A voice-first AI office assistant that helps you manage tasks, process information, and get work done using a multi-node cluster of computers in your home. Speak naturally to add tasks, then run processing across your distributed compute network.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Parallax](https://img.shields.io/badge/parallax-powered-purple.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Voice](https://img.shields.io/badge/voice-enabled-green.svg)

## The Core Concept

Transform your home computers into a distributed AI assistant you can talk to. Using Parallax's multi-node cluster technology, multiple machines work together to share compute resources, making AI processing faster and more efficient.

Simply speak your tasks into the system, and they're queued for processing. When you're ready, trigger processing across your cluster. The voice interface means you can add tasks hands-free while working, and the distributed architecture means faster processing across multiple machines.

Perfect for busy professionals who want an AI assistant with the power of Claude Code or Gemini CLI, but running entirely on your own hardware with complete privacy.

## ✨ Key Features

- **🎙️ Voice Interface**: Speak naturally to add tasks with Web Speech API
  - Multi-language support (11 languages)
  - Smart task type and metadata extraction
  - Optional text-to-speech feedback

- **🔗 Multi-Node Cluster**: Distributed processing across multiple home computers using Parallax SDK

- **🛠️ Tool Capabilities**: MCP (Model Context Protocol) integration
  - File operations (15+ tools)
  - Web search (Serper/Tavily APIs)
  - JSON/YAML parsing and HTTP client

- **⚡ Lightweight & Fast**: Starts with qwen3:1b model, expandable as needed

- **🎛️ Web Control Panel**: Beautiful dark-themed GUI with:
  - Task prioritization and tagging
  - Real-time progress tracking
  - Bulk operations
  - Advanced gallery with pagination and filtering
  - Server-Sent Events for live updates

- **📱 Mobile-Responsive**: Queue tasks from anywhere on your network

- **🔒 Production Ready**:
  - HTTPS support with SSL certificates
  - Automated backups and recovery
  - Database optimization tools
  - Configuration validation
  - Comprehensive test suite

- **100% Local & Private**: Your data never leaves your machines

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Parallax SDK installed and configured
- One or more Linux/CPU machines for your cluster
- Microphone for voice input

### 2. Install Parallax

Follow the [Parallax installation guide](https://parallax.xyz/docs) to set up your multi-node cluster:

```bash
# On your host machine
parallax init

# On each additional node (optional)
parallax node join <host-ip>
```

### 3. Install Parallax Voice Office

```bash
git clone https://github.com/lalomorales22/parallax-voice-office
cd parallax-voice-office

# Run the interactive installer
python install.py
```

### 4. Download AI Model

```bash
# Start with lightweight qwen3:1b
parallax pull qwen3:1b

# Or use a more powerful model
parallax pull llama3.2:3b
```

### 5. Start Parallax

```bash
parallax serve
```

### 6. Launch Voice Office

```bash
python obp-GUI.py
```

Access the GUI at **http://localhost:5001** or from your phone using the network URL shown in the startup message.

## How It Works

### Voice-First Workflow

1. **Speak Your Tasks**: Click 🎤 and speak naturally
   - "Search for the latest AI safety research"
   - "Write a blog post about quantum computing"
   - "Create a Python script to analyze CSV files"

2. **Task Queue**: Tasks are added with intelligent metadata extraction

3. **Distributed Processing**: Your Parallax cluster distributes work across nodes

4. **Tool Integration**: Through MCP, the assistant can:
   - Search the web for real-time information
   - Manage files in your workspace
   - Execute code and validate results

5. **Results & History**: View completed tasks in the gallery and export results

### Task Types

- **search**: Research and compile information with web search
- **create**: Generate articles, documentation, code, or creative writing
- **process**: Transform content—summarize, rephrase, change tone
- **code**: Generate, debug, or document software code
- **chain**: Multi-step workflows with dependent steps
- **file_ops**: File operations like search, create, update, delete

## Configuration

### Web Search (Optional)

Get a free API key from [serper.dev](https://serper.dev) or [tavily.com](https://tavily.com) and add to `.env`:

```bash
SERPER_API_KEY=your_key_here
# or
TAVILY_API_KEY=your_key_here
```

### Parallax Cluster

Configure in `processor_config.yaml`:

```yaml
parallax:
  host: "localhost"
  port: 50051
  model: "qwen3:1b"
  max_workers: 4
  timeout: 600
```

### HTTPS Setup (For Network Voice Access)

```bash
python setup_https.py --self-signed
```

## Docker Deployment

```bash
# Build and start
docker-compose up --build -d

# With auto-backup service
docker-compose --profile backup up -d
```

Access at http://localhost:5001

## Utilities

### Backup Management
```bash
# Create backup
python backup_manager.py create

# List backups
python backup_manager.py list

# Restore backup
python backup_manager.py restore --name backup_20250118_120000
```

### Database Optimization
```bash
# Analyze database
python db_optimizer.py --analyze

# Full optimization
python db_optimizer.py --optimize

# Clean up old tasks
python db_optimizer.py --cleanup-old --days 30
```

### Configuration Validation
```bash
python config_validator.py
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## Project Structure

```
parallax-voice-office/
├── obp-GUI.py              # Main web interface with voice
├── processor_config.yaml   # Parallax configuration
├── mcp_config.json         # Model Context Protocol servers
├── task_configs/           # Task workflow definitions
├── backup_manager.py       # Backup and recovery
├── db_optimizer.py         # Database optimization
├── config_validator.py     # Configuration validation
├── setup_https.py          # HTTPS certificate setup
├── install.py              # Interactive installer
├── tests/                  # Test suite
├── workspace/              # File operations workspace
├── results/                # Completed task outputs
└── data/                   # SQLite database storage
```

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript with Web Speech API
- **Backend**: Python 3.8+, Flask
- **AI Engine**: Parallax SDK with qwen3:1b (or custom models)
- **Database**: SQLite
- **Tools**: Model Context Protocol (MCP)

## Troubleshooting

### Quick Diagnosis
```bash
python config_validator.py
```

### Common Issues

**Parallax Connection:**
- Verify Parallax is running: `parallax status`
- Check model is loaded: `parallax models list`
- Test connection: `parallax chat "Hello"`

**Voice Issues:**
- Use Chrome, Edge, or Safari (Firefox has limited support)
- Check browser microphone permissions
- For network access, HTTPS may be required

**Network Access:**
- Ensure devices are on same Wi-Fi
- Allow port 5001 in firewall
- Run `python network_test.py` for diagnostics

## License

MIT License - See LICENSE file for details

## Learn More

- [Voice Interface Guide](VOICE_GUIDE.md)
- [How It Works](HOW-IT-WORKS.md)
- [Metadata Guide](METADATA_GUIDE.md)
- [Task Roadmap](TASKS.md)
- [Parallax SDK Documentation](https://parallax.xyz/docs)
- [Model Context Protocol](https://modelcontextprotocol.io)

---

**Built with ❤️ for distributed AI computing and voice-first productivity**
