# Parallax Voice Office

<img width="1185" height="1037" alt="Screenshot 2025-08-18 at 12 01 57 AM" src="https://github.com/user-attachments/assets/b768c716-bd5f-406b-b528-20aecb3a3dfb" />
<img width="1791" height="1188" alt="Screenshot 2025-08-18 at 12 02 06 AM" src="https://github.com/user-attachments/assets/33fd47b5-855e-4de6-89ac-4882329cd73d" />

**Your intelligent voice-enabled task management assistant powered by distributed computing.**

A voice-first AI office assistant that helps you manage tasks, process information, and get work done using a multi-node cluster of computers in your home. Speak naturally to add tasks, then run processing across your distributed compute network when you're ready.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Parallax](https://img.shields.io/badge/parallax-powered-purple.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Voice](https://img.shields.io/badge/voice-enabled-green.svg)





## The Core Concept

**Parallax Voice Office** transforms your home computers into a distributed AI assistant you can talk to. Using Parallax's multi-node cluster technology, multiple machines work together to share compute resources, making AI processing faster and more efficient.

Simply speak your tasks into the system, and they're queued for processing. When you're ready, trigger processing across your cluster. The voice interface means you can add tasks hands-free while working, and the distributed architecture means faster processing across multiple machines.

Perfect for busy professionals who want an AI assistant with the power of Claude Code or Gemini CLI, but running entirely on your own hardware with complete privacy.

## ✨ Key Features

- **🎙️ Voice Interface**: Speak naturally to add tasks, get responses, and control the system
- **🔗 Multi-Node Cluster**: Distributed processing across multiple home computers using Parallax SDK
- **🛠️ Tool Capabilities**: MCP (Model Context Protocol) integration for file operations, web search, and more
- **⚡ Lightweight & Fast**: Starts with qwen3:1b model, expandable to larger models as needed
- **🎛️ Web Control Panel**: Beautiful dark-themed GUI for task management, cluster monitoring, and results
- **📱 Phone & Tablet Access**: Queue tasks from anywhere on your network with a mobile-responsive interface
- **Universal Task Engine**: Handles a wide variety of tasks:
  - **search**: In-depth research and report generation with web search
  - **create**: Generate new content like articles, documentation, or creative writing
  - **process**: Transform existing content—summarize, rephrase, or change its tone
  - **code**: Generate, debug, or document software code
  - **chain**: Execute multi-step workflows where the output of one step feeds into the next
- **Full File Management**: Complete file CRUD (Create, Read, Update, Delete) with 15+ operations
- **Visual Gallery**: Stunning dark-themed, filterable gallery view to browse and export completed tasks
- **100% Local & Private**: Your data never leaves your machines (unless you enable optional web search)

## Quick Start Guide

### 1. Prerequisites

Before starting, ensure you have:
- Python 3.8 or higher
- Parallax SDK installed and configured
- One or more Linux/CPU machines for your cluster
- Microphone for voice input (built-in or USB)

### 2. Install Parallax

Follow the [Parallax installation guide](https://parallax.xyz/docs) to set up your multi-node cluster:

```bash
# On your host machine
parallax init

# On each additional node machine (optional but recommended)
parallax node join <host-ip>
```

### 3. Clone and Install Parallax Voice Office

```bash
# Clone the repository
git clone https://github.com/lalomorales22/parallax-voice-office
cd parallax-voice-office

# We recommend 'uv' for fast package management
# Install uv if you don't have it:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create a virtual environment and activate it
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run the interactive installer (Recommended)
python install.py
```

The installer will check your dependencies, verify your Parallax connection, and help you get set up.

### 4. Download the AI Model

```bash
# Start with the lightweight qwen3:1b model (recommended for testing)
parallax pull qwen3:1b

# Or use a more powerful model if you have the resources
parallax pull llama3.2:3b
```

### 5. Start Parallax

Ensure Parallax is running on your host machine:

```bash
# Terminal 1: Start the Parallax server
parallax run qwen3:1b
```

### 6. Launch the Voice Office

```bash
# Terminal 2: Start the web application
python obp-GUI.py
```

Access the GUI on your computer at **http://localhost:5001**.

To access from your phone or another device, use the "Network Access" URL shown in the startup message (e.g., http://192.168.0.64:5001).

## How It Works

### Voice-First Task Management

1. **Speak Your Tasks**: Click the 🎤 microphone button in the web interface and speak naturally:
   - "Search for the latest AI safety research"
   - "Write a blog post about quantum computing"
   - "Create a Python script to analyze CSV files"

2. **Task Queue**: Tasks are added to your queue with intelligent metadata extraction from your voice input. Review and edit any details before queuing.

3. **Distributed Processing**: When you're ready, start processing. Your Parallax cluster distributes work across nodes for faster completion. Multiple machines work together to process tasks efficiently.

4. **Tool Integration**: Through MCP (Model Context Protocol), the assistant can:
   - Search the web for real-time information
   - Manage files in your workspace
   - Execute code and validate results
   - Perform complex multi-step operations

5. **Results & History**: View completed tasks in the gallery, export results, and track your work history. All results are saved to both a database and individual files.

### Task Types & Metadata

You can create tasks either by voice or through the GUI's metadata builder. The system supports several task types:

**Task Types:**

```text
{search}
Search for and compile research on any topic with optional web search integration.

{create}
Generate new content like articles, documentation, code, or creative writing.

{process}
Transform existing content—summarize, rephrase, change tone, or reformat.

{code}
Generate, debug, or document software code in any programming language.

{chain}
Execute multi-step workflows where outputs feed into subsequent steps.

{file_ops}
Perform file operations like search, list, create, update, or delete files.
```

**Example Voice Commands:**

- "Search for renewable energy trends in 2025"
- "Create a professional email about the project deadline"
- "Process this report and make it more concise"
- "Write a Python function to validate email addresses"
- "Search all Python files for TODO comments"

### Metadata Guide

Metadata customizes how tasks are processed. You can add metadata through:

**GUI Method** (Recommended):
1. Select your task type
2. Use the "Add Metadata" button to add key-value pairs
3. The system automatically converts to JSON

**Voice Method**:
The system extracts metadata from your spoken request automatically.

**Common Metadata Options:**

For Search Tasks:
```json
{
  "search_query": "AI safety 2025",
  "comparison": true,
  "filename": "research_report.md"
}
```

For Content Creation:
```json
{
  "tone": "professional",
  "audience": "executives",
  "format": "bullet_points",
  "filename": "content.md"
}
```

For Code Generation:
```json
{
  "language": "python",
  "filename": "analyzer.py",
  "include_docs": true,
  "include_tests": true
}
```

See [METADATA_GUIDE.md](METADATA_GUIDE.md) for comprehensive metadata options.

## Parallax Cluster Setup

### Single Machine (Development)

Start with just your main computer for testing:

```bash
parallax run qwen3:1b
```

The Voice Office application will automatically connect to your local Parallax instance.

### Multi-Node Cluster (Recommended for Production)

Set up multiple machines to share compute and process tasks faster:

**On Host Machine:**
```bash
# Start Parallax server with network access
parallax serve --host 0.0.0.0
```

**On Each Node Machine:**
```bash
# Join the cluster (replace with your host IP)
parallax node join 192.168.1.100:50051
```

**Verify Your Cluster:**
```bash
parallax nodes list
# Should show all connected nodes and their status
```

The application automatically detects and uses your entire Parallax cluster for distributed processing. Tasks are intelligently distributed across available nodes for optimal performance.

### Cluster Configuration

Configure your cluster settings in `processor_config.yaml`:

```yaml
parallax:
  host: "localhost"
  port: 50051
  model: "qwen3:1b"
  max_workers: 4
  timeout: 600
```

## Model Context Protocol (MCP)

Parallax Voice Office uses Model Context Protocol to provide tool capabilities similar to Claude Desktop and Gemini CLI.

### Available Tools

- **File Operations**: Create, read, update, delete, search, and manage files
- **Web Search**: Real-time information via Serper or Tavily APIs
- **Code Execution**: Run and test generated code safely
- **Workspace Management**: Browse, organize, and export results

### Adding MCP Servers

Configure additional MCP servers in `mcp_config.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "mcp-server-filesystem",
      "args": ["--workspace", "./workspace"]
    },
    "web-search": {
      "command": "mcp-server-tavily",
      "env": {
        "TAVILY_API_KEY": "your_key_here"
      }
    }
  }
}
```

See the [MCP documentation](https://modelcontextprotocol.io) for more servers and capabilities.

## Advanced Setup & Configuration

### Web Search Integration (Optional but Recommended)

Enable real-time information access for your tasks:

**Get a Free API Key:**

- **Serper**: [serper.dev](https://serper.dev) (2,500 free searches/month)
- **Tavily**: [tavily.com](https://tavily.com) (1,000 free searches/month)

**Configure:**

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file and add your key
SERPER_API_KEY=your_serper_key_here
# or TAVILY_API_KEY=your_tavily_key_here
```

Restart the application to enable web search capabilities.

### Custom Workflows (YAML)

Define or modify task processing steps by editing YAML files in the `task_configs/` directory:

**Example (search_tasks.yaml):**

```yaml
type: search
steps:
  - name: web_search
    plugin: web_search
    optional: true
  - name: summarize
    prompt: "Summarize these search results: {web_search_result}"
  - name: create_report
    prompt: "Create a detailed report: {summarize_result}"
  - name: save_report
    plugin: file_operations
    operation: create
    filename_template: "search_{task_id}.md"
```

### Bulk Task Import

You can still import multiple tasks at once using a text file:

**Create a tasks.txt file:**

```text
{search}
search_query=AI safety 2025::Research the latest developments in AI safety.

{create}
tone=professional,filename=blog_post.md::Write a blog post about quantum computing.

{code}
language=python,filename=analyzer.py::Create a data visualization script using pandas.
```

**Import via GUI:**

1. Go to the "Import Tasks" section
2. Upload your tasks.txt file
3. Review and queue all tasks at once

## Using Voice Commands

### Adding Tasks by Voice

1. Click the 🎤 **microphone button** in the web interface
2. Speak your task naturally:
   - "Create a Python script to analyze CSV files"
   - "Search for renewable energy trends and create a report"
   - "Process this text and make it more professional"
3. The system extracts task type and metadata automatically
4. Review the generated task and click "Add to Queue"

### Voice Settings

Configure voice recognition in the Settings panel:

- **Language**: Set your preferred language (English, Spanish, French, etc.)
- **Auto-detect**: Automatically determine task type from speech
- **Voice Feedback**: Enable spoken confirmations
- **Sensitivity**: Adjust microphone sensitivity

### Voice Tips

- Speak clearly and at a normal pace
- Include key details like "and save to filename.md"
- Specify the task type explicitly for best results: "Search for...", "Create a...", "Write code to..."
- Use the preview before adding to queue to ensure accuracy

## Docker Deployment (Recommended for Production)

Docker provides an isolated and consistent environment for running Parallax Voice Office.

**Run Setup Script:**

```bash
./docker-setup.sh
```

**Start with Docker Compose:**

```bash
# Build and start the containers
docker-compose up --build -d
```

**Access the Application:**
- Web GUI: http://localhost:5001
- Network Access: http://your-server-ip:5001

**Manage:**

- **View logs**: `docker-compose logs -f`
- **Stop**: `docker-compose down`
- **Restart**: `docker-compose restart`

**Docker + Parallax:**

Ensure your `docker-compose.yml` points to your Parallax host:

```yaml
environment:
  - PARALLAX_HOST=host.docker.internal
  - PARALLAX_PORT=50051
```

For Linux, you may need to use `172.17.0.1` instead of `host.docker.internal`.

## Troubleshooting Guide

### 1. Quick Diagnosis

Run the connection test script to diagnose common issues:

```bash
python test_connection.py
```

### 2. Parallax Connection Issues

If the application can't connect to Parallax:

- **Verify Parallax is running**: `parallax status`
- **Check the model is loaded**: `parallax models list`
- **Test connection**: `parallax chat "Hello"` should respond
- **Check configuration**: Ensure `processor_config.yaml` has correct host/port
- **Firewall**: Ensure port 50051 is open for cluster communication

### 3. Voice Recognition Issues

If voice input isn't working:

- **Microphone permissions**: Ensure browser has microphone access
- **HTTPS**: Voice requires HTTPS or localhost (use localhost for testing)
- **Browser compatibility**: Use Chrome, Edge, or Safari for best results
- **Audio settings**: Check system audio input settings
- **Test microphone**: Use browser's built-in mic test

### 4. Mobile / Network Access Issues

If you can't access from your phone:

- **Same Network**: Ensure phone and computer are on the same Wi-Fi
- **Correct IP**: Use the "Network Access" URL from startup message
- **Firewall**:
  - **macOS**: System Preferences → Security & Privacy → Firewall → Allow Python
  - **Linux**: `sudo ufw allow 5001`
- **Network Test**: `python network_test.py` for detailed diagnostics

### 5. Docker Issues

If Docker container can't connect to Parallax:

- Ensure Parallax is running on host: `parallax serve`
- Check `docker-compose.yml` has correct `PARALLAX_HOST`
- Run `./docker-setup.sh` again if database errors occur
- Rebuild: `docker-compose up --build`

### 6. Cluster Node Issues

If nodes aren't joining the cluster:

- **Network connectivity**: Ensure nodes can ping the host
- **Firewall**: Open port 50051 on host machine
- **Correct IP**: Use host's local IP, not 127.0.0.1
- **Verify**: `parallax nodes list` should show all nodes

### 7. API Key / Web Search Issues

If web search isn't working:

- Verify `.env` file exists and contains actual API key
- Restart application after editing `.env`
- Check API key is valid at provider's dashboard
- Test with simple search task first

## 🎨 Design Philosophy

**Parallax Voice Office** features a carefully crafted dark theme optimized for professional use:

- Deep black backgrounds with subtle gradient overlays
- Vibrant accent colors for improved visibility
- Glassmorphic effects with backdrop blur for a modern feel
- Smooth animations and transitions
- Professional color-coded task status indicators
- Eye-friendly contrast ratios for extended use
- Voice-first interface design with clear visual feedback

## Project Information

### Project Structure

```
parallax-voice-office/
├── obp-GUI.py              # Main web interface with voice integration
├── processor_config.yaml   # Global configuration for Parallax
├── task_configs/           # Custom task workflow definitions
├── gallery_template.html   # Template for the /gallery view
├── install.py              # Interactive installer script
├── mcp_config.json         # Model Context Protocol server configuration
├── Dockerfile              # Docker container definition
├── docker-compose.yml      # Docker orchestration file
├── requirements.txt        # Python dependencies
├── .env.example            # Template for API keys
├── workspace/              # Default directory for file operations
├── results/                # Output directory for completed task files
└── data/                   # SQLite database storage
```

### Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript with Web Speech API
- **Backend**: Python 3.8+, Flask
- **AI Engine**: Parallax SDK with qwen3:1b (or custom models)
- **Database**: SQLite for task and result storage
- **Tools**: Model Context Protocol (MCP) for extensibility
- **Voice**: Web Speech API for recognition and synthesis

### Recommended Models

- **qwen3:1b**: Lightweight, fast, perfect for basic tasks (recommended)
- **llama3.2:3b**: More capable, still runs well on modest hardware
- **mistral:7b**: High quality for complex tasks, needs more resources
- **Custom models**: Any Parallax-compatible model can be used

## Contributing

Pull requests are welcome! Please see CONTRIBUTING.md for guidelines.

To set up a development environment:

```bash
# Install development and testing tools
pip install -r requirements-dev.txt

# Run tests
make test

# Check code formatting
make lint
```

## Roadmap

Future enhancements planned:

- [ ] Always-on voice activation with wake word
- [ ] Voice output for task completion notifications
- [ ] Multi-language voice support
- [ ] Mobile app for iOS/Android
- [ ] Advanced cluster load balancing
- [ ] Real-time task streaming results
- [ ] Integration with calendar/email tools
- [ ] Plugin marketplace for custom MCP servers

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Learn More

- [Parallax SDK Documentation](https://parallax.xyz/docs)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Voice Interface Guide](VOICE_GUIDE.md)
- [How It Works](HOW-IT-WORKS.md)
- [Metadata Guide](METADATA_GUIDE.md)

---

**Built with ❤️ for distributed AI computing and voice-first productivity**
