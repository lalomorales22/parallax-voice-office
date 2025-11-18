# Voice Interface Guide

Welcome to the Parallax Voice Office voice interface! This guide will help you master voice-first task management and get the most out of your AI assistant.

## 🎙️ Getting Started with Voice

### Prerequisites

Before using voice commands, ensure you have:

1. **Microphone Access**: Your browser needs permission to access your microphone
2. **Supported Browser**: Chrome, Edge, or Safari (Firefox has limited support)
3. **Secure Connection**: Voice API requires HTTPS or localhost
4. **Network Connection**: For web search features (optional)

### First-Time Setup

1. **Launch Parallax Voice Office**:
   ```bash
   python obp-GUI.py
   ```

2. **Access the Web Interface**:
   - Local: http://localhost:5001
   - Network: http://your-ip:5001 (shown in terminal)

3. **Grant Microphone Permission**:
   - Click the 🎤 microphone button
   - Allow microphone access when prompted
   - You only need to do this once per device

4. **Test Your Voice**:
   - Click the microphone button
   - Speak: "Search for Python best practices"
   - Review the extracted task
   - Click "Add to Queue"

## 🗣️ How to Speak Tasks

### Basic Voice Command Structure

The most effective voice commands follow this pattern:

```
[Action] [Details] [Options]
```

**Examples:**

- **Action**: "Search for", "Create a", "Write a", "Process"
- **Details**: The main task description
- **Options**: Tone, format, filename, etc.

### Task Type Commands

#### Search Tasks

Use these phrases to trigger search tasks:

- "Search for [topic]"
- "Look up [topic]"
- "Research [topic]"
- "Find information about [topic]"

**Examples:**
```
"Search for the latest AI developments in 2025"
"Look up Python async programming best practices"
"Research renewable energy trends and save to energy_report.md"
"Find information about quantum computing breakthroughs"
```

#### Create Tasks

Use these phrases for content creation:

- "Create a [type]"
- "Write a [type]"
- "Draft a [type]"
- "Generate a [type]"

**Examples:**
```
"Create a professional email about the quarterly meeting"
"Write a blog post about remote work productivity"
"Draft a friendly message to the team about the holiday schedule"
"Generate a social media post for our new product launch"
```

#### Process Tasks

Use these phrases to transform existing content:

- "Process [content] and [instruction]"
- "Simplify [content]"
- "Summarize [content]"
- "Convert [content] to [format]"

**Examples:**
```
"Process this report and make it more concise"
"Simplify this technical document for non-technical readers"
"Summarize this article in bullet points"
"Convert this email to a professional tone"
```

#### Code Tasks

Use these phrases for code generation:

- "Write a [language] [type]"
- "Create a [language] script to [purpose]"
- "Build a [language] function for [purpose]"
- "Generate code to [purpose]"

**Examples:**
```
"Write a Python function to validate email addresses"
"Create a JavaScript script to fetch API data with error handling"
"Build a Python class for database connections with documentation"
"Generate code to parse CSV files using pandas"
```

#### File Operations

Use these phrases for file management:

- "Search all [file type] for [text]"
- "List all [file type] in [location]"
- "Find files containing [text]"
- "Create a file called [name]"

**Examples:**
```
"Search all Python files for TODO comments"
"List all JavaScript files in the workspace"
"Find markdown files containing 'project update'"
"Create a new file called meeting_notes.md"
```

## 🎯 Adding Metadata Through Voice

### Specifying Filenames

Include the filename in your command using these phrases:

- "and save to [filename]"
- "and save as [filename]"
- "save the output to [filename]"
- "output to [filename]"

**Examples:**
```
"Search for React hooks and save to react_hooks_guide.md"
"Create a script and save as data_analyzer.py"
```

### Setting Tone

Specify the tone using these keywords:

- **Professional**: "professional", "formal", "business"
- **Casual**: "casual", "informal", "relaxed"
- **Friendly**: "friendly", "warm", "approachable"
- **Technical**: "technical", "detailed", "in-depth"

**Examples:**
```
"Write a professional email to the board"
"Create a casual blog post about our team"
"Draft a friendly message to new users"
"Generate a technical documentation for the API"
```

### Including Documentation and Tests

Add these keywords for code tasks:

- "with documentation"
- "with tests"
- "with examples"
- "with error handling"

**Examples:**
```
"Write a Python function to process images with documentation"
"Create a JavaScript API client with tests and error handling"
"Build a data validator with documentation and examples"
```

### Specifying Format

Include format preferences:

- "in bullet points"
- "as markdown"
- "in JSON format"
- "as a CSV"

**Examples:**
```
"Summarize this report in bullet points"
"Create a guide as markdown"
"Generate the data in JSON format"
```

### Targeting Audience

Specify the target audience:

- "for executives"
- "for developers"
- "for general audience"
- "for beginners"

**Examples:**
```
"Create a presentation for executives about our Q4 results"
"Write a tutorial for beginners on Python basics"
"Generate documentation for developers"
```

## 💡 Best Practices

### Do's ✅

1. **Speak Clearly**: Enunciate and speak at a normal pace
2. **Be Specific**: Include as many details as possible
3. **Use Complete Sentences**: Full sentences work better than fragments
4. **Include Filenames**: Always specify output filename when possible
5. **Review Before Queuing**: Check the extracted metadata for accuracy
6. **Use Natural Language**: Speak conversationally, the system understands variations

**Good Examples:**
```
✅ "Search for Python testing best practices and create a comprehensive guide with examples, save to testing_guide.md"
✅ "Write a professional Python script to validate email addresses with documentation and tests, save as email_validator.py"
✅ "Create a friendly blog post about productivity tips for remote workers, 1000 words, save to productivity_blog.md"
```

### Don'ts ❌

1. **Don't Be Vague**: Avoid unclear or too-brief commands
2. **Don't Rush**: Speaking too fast reduces accuracy
3. **Don't Skip Review**: Always check extracted metadata
4. **Don't Ignore Errors**: If recognition fails, try rephrasing
5. **Don't Use Jargon Without Context**: Define acronyms and technical terms

**Bad Examples:**
```
❌ "Write code" (too vague)
❌ "Search stuff about AI" (unclear)
❌ "Make a thing" (no details)
❌ "Python" (incomplete command)
```

## 🔧 Voice Settings

### Configuring Your Voice Interface

Access voice settings in the Settings panel:

1. **Language Selection**:
   - Choose your preferred language
   - Supports: English, Spanish, French, German, Italian, Portuguese, and more
   - Default: English (US)

2. **Auto-Detection**:
   - Enable automatic task type detection
   - System analyzes your speech to determine task type
   - Recommended: ON

3. **Voice Feedback**:
   - Enable spoken confirmations
   - System will read back task details
   - Useful for hands-free operation

4. **Microphone Sensitivity**:
   - Adjust based on your microphone quality
   - Low: For sensitive/high-quality mics
   - Medium: For standard mics (recommended)
   - High: For low-quality or distant mics

### Browser-Specific Settings

#### Chrome/Edge
1. Click the lock icon in the address bar
2. Ensure "Microphone" is set to "Allow"
3. Select the correct microphone from the dropdown

#### Safari
1. Go to Safari → Settings → Websites
2. Click "Microphone" in the left sidebar
3. Set permissions for localhost

#### Firefox (Limited Support)
- Firefox has limited Web Speech API support
- For best experience, use Chrome, Edge, or Safari

## 🎤 Advanced Voice Techniques

### Multi-Step Tasks (Chaining)

Create complex workflows with a single command:

```
"Search for Python testing best practices, then create a comprehensive guide based on the results with examples, and save to testing_guide.md"
```

This creates a chain task that:
1. Searches the web for information
2. Processes the results
3. Generates a guide with examples
4. Saves to the specified file

### Conditional Instructions

Add conditions to your tasks:

```
"Search for JavaScript frameworks, compare React and Vue, and create a decision guide for executives"
```

The system extracts:
- Task type: search
- Comparison: true
- Topics: React, Vue
- Audience: executives
- Output: decision guide

### Batch Commands

Queue multiple tasks by speaking them one after another:

```
1. "Search for Python best practices and save to python_guide.md" → Add to Queue
2. "Create a blog post about AI ethics and save to ai_ethics.md" → Add to Queue
3. "Write a JavaScript function to validate forms with tests" → Add to Queue
```

Then process all at once when ready.

## 🐛 Troubleshooting Voice Issues

### Microphone Not Working

**Problem**: Browser can't access microphone

**Solutions**:
1. Check browser permissions (see Browser-Specific Settings above)
2. Verify microphone is connected and working
3. Test microphone in system settings
4. Close other apps using the microphone
5. Try a different browser

### Poor Recognition Accuracy

**Problem**: Voice commands are misunderstood

**Solutions**:
1. Speak more slowly and clearly
2. Reduce background noise
3. Move closer to the microphone
4. Adjust microphone sensitivity in settings
5. Use a better quality microphone
6. Rephrase your command with clearer keywords

### Voice Button Doesn't Activate

**Problem**: Clicking microphone does nothing

**Solutions**:
1. **Check HTTPS**: Voice requires HTTPS or localhost
   - If accessing from network, you may need HTTPS setup
   - Localhost (127.0.0.1 or localhost) works without HTTPS
2. **Browser Compatibility**: Switch to Chrome, Edge, or Safari
3. **Refresh the page**: Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
4. **Check console**: Open browser console (F12) for error messages

### Metadata Not Extracted Correctly

**Problem**: System misinterprets your intent

**Solutions**:
1. **Be More Explicit**: Include keywords like "professional", "save to", etc.
2. **Review and Edit**: Always review extracted metadata before queuing
3. **Use GUI**: Manually add/edit metadata in the interface
4. **Learn Patterns**: See what works and refine your phrasing
5. **Check Examples**: Refer to this guide for working patterns

### Voice Stops Working Mid-Session

**Problem**: Voice works initially but stops later

**Solutions**:
1. **Timeout**: Click the microphone button again to reactivate
2. **Browser Tab**: Ensure tab has focus (click on the tab)
3. **Permissions**: Check if permission was revoked accidentally
4. **Memory**: Refresh the page if browser is using too much memory

## 🌐 Network Access and Voice

### Using Voice from Phone/Tablet

1. **Connect to Same Network**: Ensure mobile device is on same WiFi
2. **Access Network URL**: Use the IP address shown in terminal
   - Example: http://192.168.1.100:5001
3. **Grant Mic Permission**: Allow microphone access on mobile browser
4. **Use Supported Browser**: Safari (iOS) or Chrome (Android)

**Mobile Tips**:
- Hold phone close to mouth for better recognition
- Speak slightly slower than normal
- Use quieter environments
- Review metadata carefully on small screens

### HTTPS Setup for Network Access

Voice API requires HTTPS on non-localhost connections. Two options:

#### Option 1: Use Localhost
- Only access from host machine
- URL: http://localhost:5001
- No HTTPS needed

#### Option 2: Set Up HTTPS
For network access with voice:

1. **Generate Self-Signed Certificate**:
   ```bash
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
   ```

2. **Update Application** to use HTTPS (modify obp-GUI.py)

3. **Accept Certificate** on each device (browser will warn about self-signed cert)

## 📱 Platform-Specific Tips

### macOS
- **Best Browser**: Safari or Chrome
- **Mic Permissions**: System Preferences → Security & Privacy → Microphone
- **Quality**: Built-in MacBook mics work well
- **Tip**: Use Dictation keyboard shortcut (fn fn) to test mic

### Windows
- **Best Browser**: Edge or Chrome
- **Mic Permissions**: Settings → Privacy → Microphone
- **Quality**: External USB mic recommended
- **Tip**: Test mic in Sound settings before using voice

### Linux
- **Best Browser**: Chrome or Chromium
- **Mic Permissions**: May vary by distribution
- **Quality**: Check PulseAudio/ALSA settings
- **Tip**: Test with `arecord` to verify mic works

### iOS (iPhone/iPad)
- **Best Browser**: Safari (only option for Web Speech API)
- **Mic Permissions**: Settings → Safari → Microphone
- **Quality**: Built-in mic works well
- **Tip**: Hold device 6-12 inches from mouth

### Android
- **Best Browser**: Chrome
- **Mic Permissions**: Chrome → Settings → Site Settings → Microphone
- **Quality**: Most built-in mics work well
- **Tip**: Reduce background noise for better accuracy

## 🎯 Voice Command Examples Library

### Research & Analysis

```
"Search for the latest machine learning frameworks and compare TensorFlow and PyTorch"
"Research climate change impact on coastal cities and create a detailed report"
"Look up blockchain use cases in supply chain and save to blockchain_supply.md"
"Find information about quantum computing applications with references"
```

### Content Creation

```
"Write a professional 1500-word blog post about productivity tips for remote workers"
"Create a casual social media post announcing our new feature launch"
"Draft a friendly welcome email for new customers with company overview"
"Generate a technical white paper on distributed systems architecture"
```

### Code Generation

```
"Write a Python script to process CSV files with pandas, include error handling and documentation"
"Create a JavaScript React component for user authentication with TypeScript"
"Build a Python API client for REST endpoints with async support and tests"
"Generate a SQL query to analyze user behavior patterns with comments"
```

### Document Processing

```
"Process this technical documentation and simplify it for non-technical audience"
"Summarize this research paper in bullet points with key findings"
"Convert this meeting transcript to action items and decisions"
"Improve the clarity of this email and make it more professional"
```

### File Management

```
"Search all Python files for TODO and FIXME comments and create a summary"
"List all markdown files modified in the last week"
"Find all JavaScript files containing 'deprecated' and create a migration guide"
"Search project files for API keys or secrets and generate a security report"
```

### Multi-Step Workflows

```
"Search for React hooks best practices, analyze the patterns, create a comprehensive guide with examples, and save to react_hooks_complete_guide.md"

"Research Python async programming, compare asyncio and trio frameworks, generate example code with documentation, and save to async_python_guide.md"

"Search all TODO comments in the codebase, categorize by priority, create a markdown report with sections, and save to project_todos.md"
```

## 🚀 Tips for Power Users

### 1. Create Voice Templates

Develop personal patterns for common tasks:

**Template**: "Search for [topic], create [output type] for [audience], save to [filename]"

**Example**: "Search for Kubernetes best practices, create a setup guide for developers, save to k8s_guide.md"

### 2. Use Consistent Filenames

Develop a naming convention:

- Research: `topic_research.md`
- Guides: `topic_guide.md`
- Code: `functionality_module.py`
- Reports: `topic_report_YYYY-MM-DD.md`

### 3. Batch Similar Tasks

Queue multiple related tasks together:

```
1. "Search for Python testing and save to python_testing.md"
2. "Search for Python logging and save to python_logging.md"
3. "Search for Python packaging and save to python_packaging.md"
```

Then process all at once for efficient completion.

### 4. Learn Metadata Extraction Patterns

Understand how the system interprets your words:

- "professional" → `tone: "professional"`
- "with tests" → `include_tests: true`
- "save to X.md" → `filename: "X.md"`
- "for developers" → `audience: "developers"`

### 5. Combine Voice with GUI

Use voice for quick task creation, then use GUI to:
- Fine-tune metadata
- Reorder tasks
- Edit task descriptions
- Monitor processing

## 📊 Voice vs. Text Input Comparison

| Feature | Voice Input | Text Input | Best For |
|---------|------------|------------|----------|
| Speed | ⭐⭐⭐⭐⭐ Fast | ⭐⭐⭐ Moderate | Quick capture |
| Precision | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent | Detailed tasks |
| Hands-Free | ⭐⭐⭐⭐⭐ Yes | ❌ No | Multitasking |
| Complex Metadata | ⭐⭐⭐ Moderate | ⭐⭐⭐⭐⭐ Excellent | Complex configs |
| Mobile Use | ⭐⭐⭐⭐ Great | ⭐⭐ Difficult | On-the-go |
| Accuracy | ⭐⭐⭐⭐ Very Good | ⭐⭐⭐⭐⭐ Perfect | Critical tasks |

**Recommendation**: Use voice for most tasks, switch to text for complex metadata requirements.

## 🎓 Learning Curve

### Week 1: Basics
- Learn basic commands for each task type
- Practice speaking clearly
- Review extracted metadata
- Get comfortable with the microphone button

### Week 2: Refinement
- Add filenames to commands
- Specify tone and format
- Start using multi-step commands
- Develop personal patterns

### Week 3: Mastery
- Chain complex workflows
- Use all metadata options via voice
- Batch tasks efficiently
- Rarely need to edit extracted metadata

### Week 4+: Power User
- Create personal voice templates
- Seamlessly combine voice and GUI
- Optimize workflow with voice shortcuts
- Teach others your techniques

---

## 📚 Additional Resources

- **[README.md](README.md)**: Full application documentation
- **[HOW-IT-WORKS.md](HOW-IT-WORKS.md)**: System architecture explained
- **[METADATA_GUIDE.md](METADATA_GUIDE.md)**: Complete metadata reference
- **Web Speech API**: [MDN Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)

---

**Happy voice commanding!** 🎤 The more you use Parallax Voice Office, the more natural it becomes. Start simple, build confidence, and soon you'll be managing complex AI workflows entirely by voice.
