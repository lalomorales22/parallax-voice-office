# Metadata Usage Guide

## 🎯 What is Metadata?

Metadata allows you to customize how tasks are processed. Think of it as configuration options that tell the system exactly how you want your task handled. Metadata can be added through the GUI interface or extracted automatically from your voice commands.

## 🔧 How to Use Metadata

### Method 1: Voice Input (Recommended)
1. Click the 🎤 microphone button
2. Speak your task naturally with details
3. The system automatically extracts relevant metadata
4. Review and adjust before queuing

**Example Voice Commands:**
- "Search for Python best practices and save to python_guide.md"
  - Auto-extracts: `search_query: "Python best practices"`, `filename: "python_guide.md"`
- "Create a professional email about the quarterly meeting"
  - Auto-extracts: `tone: "professional"`, task type: `create`
- "Write a Python function to validate email addresses with documentation"
  - Auto-extracts: `language: "python"`, `include_docs: true`

### Method 2: Key-Value Builder (GUI)
1. Select your task type
2. Use the "Add Metadata" button to add key-value pairs
3. The system will automatically convert to JSON
4. Click "Add to Queue"

### Method 3: Direct JSON Input
Enter JSON directly in the metadata field:
```json
{"filename": "my_report.md", "language": "python"}
```

### Method 4: Bulk Import (Text File)
Use the tasks.txt format for importing multiple tasks:
```text
{search}
search_query=AI safety 2025,filename=ai_safety.md::Research latest AI safety developments
```

## 📝 Common Metadata Options

### 🔍 For Search Tasks
```json
{
  "search_query": "AI safety 2025",
  "comparison": true,
  "filename": "research_report.md"
}
```

**Voice Examples:**
- "Search for AI safety 2025 and compare different approaches"
- "Look up renewable energy trends and save the results"
- "Research quantum computing breakthroughs"

### ✏️ For Content Creation
```json
{
  "tone": "professional",
  "audience": "executives",
  "format": "bullet_points",
  "filename": "content.md"
}
```

**Voice Examples:**
- "Write a professional blog post for executives about cloud migration"
- "Create a casual social media post about our new feature"
- "Draft a friendly email to the team about the holiday schedule"

### ⚙️ For Processing Tasks
```json
{
  "format": "bullet_points",
  "improve_clarity": true,
  "simplify": true
}
```

**Voice Examples:**
- "Process this report and make it more concise"
- "Simplify this technical document for non-technical readers"
- "Convert this article to bullet points"

### 💻 For Code Generation
```json
{
  "language": "python",
  "filename": "analyzer.py",
  "include_docs": true,
  "include_tests": true
}
```

**Voice Examples:**
- "Write a Python script to analyze CSV files with documentation"
- "Create a JavaScript function to validate email addresses"
- "Build a Python class for database connections with tests"

### 📁 For File Operations
```json
{
  "operation": "search",
  "search_text": "TODO",
  "pattern": "*.py",
  "filename": "todo_summary.md"
}
```

**Voice Examples:**
- "Search all Python files for TODO comments"
- "List all JavaScript files in the workspace"
- "Find all markdown files containing 'project update'"

## 🎨 File Operations Available

### Basic CRUD:
- **operation**: `create`, `read`, `update`, `delete`
- **filename**: Target file name
- **file_content**: Content to write

### Advanced Operations:
- **operation**: `search` - Find text in files
- **search_text**: Text to search for
- **pattern**: File pattern like `*.py` or `*.js`
- **operation**: `list` - List files
- **recursive**: `true` for subdirectories
- **operation**: `backup` - Create backup

### Examples:

**Search for TODOs:**
```json
{
  "operation": "search",
  "search_text": "TODO",
  "pattern": "*.py"
}
```

**Voice:** "Search all Python files for TODO comments"

**Create a new file:**
```json
{
  "operation": "create",
  "filename": "my_notes.md",
  "file_content": "# My Notes\n\nContent here..."
}
```

**Voice:** "Create a new file called my_notes.md with a header"

**List all Python files:**
```json
{
  "operation": "list",
  "pattern": "*.py",
  "recursive": true
}
```

**Voice:** "List all Python files in the workspace recursively"

## 🌐 Web Search Options

All task types support optional web search integration:

```json
{
  "search_query": "latest React best practices",
  "filename": "react_guide.md"
}
```

**Voice Examples:**
- "Search for the latest React best practices"
- "Look up current TypeScript documentation"
- "Find information about Python 3.12 new features"

The system will:
1. Search the web for your query (via Serper or Tavily API)
2. Analyze the results
3. Use the information in your task

## 📊 Format Options

### Text Formats:
- `"format": "bullet_points"` - Convert to bullets
- `"format": "markdown"` - Structured markdown
- `"format": "json"` - JSON output
- `"format": "csv"` - Comma separated

### Code Formats:
- `"language": "python"` - Python code
- `"language": "javascript"` - JavaScript
- `"language": "typescript"` - TypeScript
- `"language": "sql"` - SQL queries
- `"style": "functional"` - Functional programming style

## 🎯 Task-Specific Examples

### Research Report:
```json
{
  "search_query": "renewable energy trends 2025",
  "comparison": true,
  "regions": "global",
  "filename": "energy_report.md",
  "format": "markdown"
}
```

**Voice:** "Search for renewable energy trends in 2025, compare different regions globally, and save as energy_report.md"

### Data Analysis Script:
```json
{
  "language": "python",
  "filename": "data_analyzer.py",
  "include_docs": true,
  "libraries": "pandas,matplotlib",
  "optimize": true
}
```

**Voice:** "Create a Python data analyzer script with pandas and matplotlib, include documentation and optimize it"

### Blog Post:
```json
{
  "tone": "conversational",
  "seo_optimized": true,
  "keywords": "productivity,remote work",
  "word_count": 1500,
  "filename": "blog_post.md"
}
```

**Voice:** "Write a conversational 1500-word blog post about productivity and remote work, SEO optimized"

### File Cleanup:
```json
{
  "operation": "search",
  "search_text": "deprecated",
  "pattern": "*.js",
  "create_backup": true,
  "filename": "cleanup_report.md"
}
```

**Voice:** "Search all JavaScript files for deprecated code, create a backup, and save a cleanup report"

## 🎙️ Voice-Specific Metadata Extraction

When you speak tasks, the system automatically extracts metadata from your words:

**Tone Detection:**
- "professional" → tone: "professional"
- "casual" → tone: "casual"
- "friendly" → tone: "friendly"
- "formal" → tone: "formal"
- "technical" → tone: "technical"

**File Detection:**
- "save to X" → filename: "X"
- "save as X" → filename: "X"
- "output to X" → filename: "X"

**Language Detection:**
- "Python script" → language: "python"
- "JavaScript function" → language: "javascript"
- "SQL query" → language: "sql"

**Format Detection:**
- "bullet points" → format: "bullet_points"
- "markdown format" → format: "markdown"
- "as JSON" → format: "json"

**Documentation Detection:**
- "with documentation" → include_docs: true
- "with tests" → include_tests: true
- "with examples" → include_examples: true

## 💡 Pro Tips

1. **Be Specific in Voice Commands**: The more details you provide, the better the metadata extraction
   - ✅ "Write a professional Python script to validate emails with tests and save to validator.py"
   - ❌ "Write some code"

2. **Use Natural Language**: Speak conversationally, the system understands variations
   - "Create a..." / "Write a..." / "Build a..." all work
   - "Search for..." / "Look up..." / "Find..." all work

3. **Review Before Queuing**: Always check the extracted metadata to ensure accuracy

4. **Combine Options**: Mix search, format, and file options for powerful tasks
   ```json
   {
     "search_query": "best practices",
     "format": "bullet_points",
     "filename": "guide.md",
     "tone": "professional"
   }
   ```

5. **File Extensions Matter**: Match the content type (.md, .py, .js, .json)

## 🚨 Common Mistakes

❌ **Wrong**: `{"include_docs": "true"}`
✅ **Right**: `{"include_docs": true}`

❌ **Wrong**: `{filename: "test.md"}`
✅ **Right**: `{"filename": "test.md"}`

❌ **Wrong**: Missing quotes around keys
✅ **Right**: All keys in quotes

❌ **Wrong**: "Write code" (too vague)
✅ **Right**: "Write a Python function to calculate prime numbers with documentation"

## 🔄 Dynamic Metadata

The GUI provides smart defaults based on task type. When you select:
- **Search**: Adds filename, search_query options
- **Create**: Adds tone, format options
- **Code**: Adds language, filename options
- **Process**: Adds format, audience options

Just modify the suggested values or add your own!

## 🎯 Advanced Voice Patterns

### Chain Tasks
**Voice:** "Search for Python testing best practices, then create a testing guide based on the results"

**Extracted Metadata:**
```json
{
  "task_type": "chain",
  "steps": [
    {
      "type": "search",
      "search_query": "Python testing best practices"
    },
    {
      "type": "create",
      "input_from_previous": true,
      "format": "guide"
    }
  ]
}
```

### Multi-step File Operations
**Voice:** "Search all Python files for TODO comments, then create a summary report and save it as todos.md"

**Extracted Metadata:**
```json
{
  "operation": "search",
  "pattern": "*.py",
  "search_text": "TODO",
  "create_report": true,
  "filename": "todos.md"
}
```

## 📚 Complete Metadata Reference

### All Available Keys:

**General:**
- `filename`: Output file name
- `format`: Output format (markdown, json, bullet_points, csv)
- `tone`: Writing tone (professional, casual, friendly, technical)
- `audience`: Target audience (executives, developers, general)

**Search Tasks:**
- `search_query`: What to search for
- `comparison`: Compare multiple sources (true/false)
- `regions`: Geographic focus
- `depth`: Research depth (brief, standard, comprehensive)

**Content Creation:**
- `word_count`: Target word count
- `seo_optimized`: Optimize for SEO (true/false)
- `keywords`: Keywords to include
- `style`: Writing style (conversational, formal, technical)

**Code Tasks:**
- `language`: Programming language
- `include_docs`: Include documentation (true/false)
- `include_tests`: Include unit tests (true/false)
- `include_examples`: Include usage examples (true/false)
- `libraries`: Libraries to use (comma-separated)
- `optimize`: Optimize code (true/false)

**File Operations:**
- `operation`: File operation type
- `pattern`: File pattern (*.py, *.js, etc.)
- `search_text`: Text to search for
- `recursive`: Search recursively (true/false)
- `create_backup`: Create backup before changes (true/false)

**Processing Tasks:**
- `simplify`: Simplify language (true/false)
- `improve_clarity`: Improve clarity (true/false)
- `expand`: Expand content (true/false)
- `target_length`: Target length (shorter, longer, same)

This comprehensive guide should help you get the most out of Parallax Voice Office's metadata system, whether you're using voice, GUI, or bulk import methods!
