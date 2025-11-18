#!/usr/bin/env python3
"""
Parallax Voice Office - Installation Helper
Comprehensive installation wizard with system checks and validation
"""

import subprocess
import sys
import os
import socket
import shutil
from pathlib import Path

def print_banner():
    print("""
    ╔══════════════════════════════════════════════════╗
    ║     Parallax Voice Office - Installer            ║
    ║     Voice-Enabled AI Assistant                   ║
    ╚══════════════════════════════════════════════════╝
    """)

def run_command(cmd):
    """Run a shell command and return success status"""
    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8+ is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def check_pip():
    """Check if pip is installed"""
    if not run_command("pip --version > /dev/null 2>&1"):
        print("❌ Error: pip is not installed")
        print("   Install pip: https://pip.pypa.io/en/stable/installation/")
        sys.exit(1)
    print("✅ pip is installed")

def check_parallax():
    """Check if Parallax is accessible"""
    try:
        # Check if parallax command exists
        result = subprocess.run(['which', 'parallax'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Parallax CLI is installed")

            # Try to check if Parallax server is running
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', 50051))
            sock.close()

            if result == 0:
                print("✅ Parallax server is running (port 50051)")
            else:
                print("⚠️  Parallax server not running")
                print("   Start it with: parallax serve")
        else:
            print("⚠️  Parallax CLI not found")
            print("   Install from: https://parallax.xyz/docs")
    except Exception as e:
        print(f"⚠️  Could not check Parallax: {e}")
        print("   Install from: https://parallax.xyz/docs")

def check_openssl():
    """Check if OpenSSL is installed (for HTTPS)"""
    try:
        result = subprocess.run(['openssl', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ OpenSSL is installed: {result.stdout.strip()}")
            return True
        return False
    except FileNotFoundError:
        print("⚠️  OpenSSL not found (needed for HTTPS)")
        print("   Install: apt-get install openssl (Ubuntu) or brew install openssl (macOS)")
        return False

def install_minimal():
    """Install minimal requirements"""
    print("\n📦 Installing minimal requirements...")
    if run_command("pip install requests PyYAML Flask Flask-Cors"):
        print("✅ Minimal installation complete!")
        return True
    return False

def install_recommended():
    """Install recommended requirements"""
    print("\n📦 Installing recommended requirements...")
    requirements = [
        "requests>=2.31.0",
        "PyYAML>=6.0.1", 
        "Flask>=3.0.0",
        "Flask-Cors>=4.0.0",
        "python-dotenv>=1.0.0",
        "colorlog>=6.8.0",
        "schedule>=1.2.0",
        "watchdog>=3.0.0"
    ]
    
    if run_command(f"pip install {' '.join(requirements)}"):
        print("✅ Recommended installation complete!")
        return True
    return False

def install_full():
    """Install full requirements including optional features"""
    print("\n📦 Installing full requirements...")
    if os.path.exists("requirements.txt"):
        if run_command("pip install -r requirements.txt"):
            print("✅ Full installation complete!")
            return True
    else:
        print("❌ requirements.txt not found")
    return False

def install_dev():
    """Install development requirements"""
    print("\n📦 Installing development requirements...")
    if os.path.exists("requirements-dev.txt"):
        run_command("pip install -r requirements.txt")
        if run_command("pip install -r requirements-dev.txt"):
            print("✅ Development installation complete!")
            return True
    else:
        print("❌ requirements-dev.txt not found")
    return False

def create_env_file():
    """Create .env file template"""
    if not os.path.exists(".env"):
        print("\n📝 Creating .env file template...")
        with open(".env", "w") as f:
            f.write("""# Parallax Voice Office Environment Variables

# Web Search API Keys (optional - get free keys at serper.dev or tavily.com)
# SERPER_API_KEY=your_serper_api_key_here
# TAVILY_API_KEY=your_tavily_api_key_here

# Parallax Settings
# PARALLAX_HOST=localhost
# PARALLAX_PORT=50051

# Security Settings
# ENABLE_HTTPS=false
# RATE_LIMIT_ENABLED=true
# MAX_REQUESTS_PER_MINUTE=60

# Backup Settings
# MAX_BACKUPS=30
# BACKUP_INTERVAL=86400
# COMPRESS_BACKUPS=true
""")
        print("✅ Created .env file template")
    else:
        print("ℹ️  .env file already exists")

def create_directories():
    """Create necessary directories"""
    dirs = ["results", "task_configs", "workspace", "logs", "data", ".backups", "certs"]
    print("\n📁 Creating directories...")
    for dir_name in dirs:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True, mode=0o755)

        # Special permissions for certs directory
        if dir_name == "certs":
            dir_path.chmod(0o700)

        print(f"   ✅ {dir_name}/")

def run_validation():
    """Run configuration validation"""
    print("\n🔍 Running configuration validation...")
    try:
        if Path("config_validator.py").exists():
            result = subprocess.run([sys.executable, "config_validator.py"],
                                 capture_output=True, text=True)
            print(result.stdout)
            if result.returncode == 0:
                print("✅ Configuration validation passed")
            else:
                print("⚠️  Configuration has warnings (see above)")
        else:
            print("⚠️  config_validator.py not found, skipping validation")
    except Exception as e:
        print(f"⚠️  Could not run validation: {e}")

def offer_https_setup():
    """Offer to set up HTTPS"""
    print("\n🔒 HTTPS Setup (optional)")
    print("   HTTPS is required for voice features on network access")
    choice = input("   Set up HTTPS with self-signed certificate? (y/N): ").strip().lower()

    if choice == 'y':
        print("\n   Generating self-signed SSL certificate...")
        try:
            result = subprocess.run([
                sys.executable, "setup_https.py", "--self-signed"
            ], capture_output=False)

            if result.returncode == 0:
                print("✅ HTTPS certificate generated")
            else:
                print("⚠️  HTTPS setup had issues")
        except Exception as e:
            print(f"⚠️  Could not set up HTTPS: {e}")
    else:
        print("   Skipping HTTPS setup (you can run 'python setup_https.py' later)")

def offer_initial_backup():
    """Offer to create initial backup"""
    print("\n💾 Initial Backup")
    if Path("data/task_processor.db").exists():
        choice = input("   Create initial backup of database? (Y/n): ").strip().lower()
        if choice != 'n':
            try:
                result = subprocess.run([
                    sys.executable, "backup_manager.py", "create",
                    "--description", "Initial backup after installation"
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    print("✅ Initial backup created")
                else:
                    print("⚠️  Backup creation had issues")
            except Exception as e:
                print(f"⚠️  Could not create backup: {e}")
    else:
        print("   No database found yet, skipping backup")

def main():
    print_banner()

    # System checks
    print("🔍 Checking system requirements...\n")
    check_python_version()
    check_pip()
    check_openssl()

    # Installation options
    print("\n📋 Installation Options:\n")
    print("  1. Minimal      - Just the essentials (fastest)")
    print("  2. Recommended  - Includes helpful extras (best for most users)")
    print("  3. Full         - All features from requirements.txt")
    print("  4. Developer    - Full + development tools + test suite")
    print("  5. Cancel\n")

    choice = input("Select installation type (1-5): ").strip()

    success = False
    if choice == "1":
        success = install_minimal()
    elif choice == "2":
        success = install_recommended()
    elif choice == "3":
        success = install_full()
    elif choice == "4":
        success = install_dev()
    elif choice == "5":
        print("Installation cancelled")
        sys.exit(0)
    else:
        print("Invalid choice")
        sys.exit(1)

    if success:
        # Post-installation setup
        create_env_file()
        create_directories()

        print("\n" + "="*60)
        print("🎉 Installation Complete!")
        print("="*60)

        # Check Parallax
        print("\n🔍 Checking Parallax...")
        check_parallax()

        # Run validation
        run_validation()

        # Optional setups
        offer_https_setup()
        offer_initial_backup()

        # Next steps
        print("\n" + "="*60)
        print("📖 Next Steps:")
        print("="*60)
        print("\n1️⃣  Start Parallax:")
        print("   parallax serve")
        print("\n2️⃣  Pull a model:")
        print("   parallax pull qwen3:1b")
        print("\n3️⃣  Start Parallax Voice Office:")
        print("   python obp-GUI.py")
        print("\n4️⃣  Access the interface:")
        print("   • Local:   http://localhost:5001")
        print("   • Network: Check startup message for network URL")
        print("\n5️⃣  Optional: Run tests")
        print("   pytest tests/ -v")

        print("\n💡 Tips:")
        print("  • Use the voice button (🎤) to add tasks by speaking")
        print("  • Visit the Gallery tab to see completed tasks")
        print("  • Check the Cluster tab to monitor your Parallax nodes")

        print("\n🛠️  Utilities:")
        print("  • Validate config:  python config_validator.py")
        print("  • Create backup:    python backup_manager.py create")
        print("  • Optimize DB:      python db_optimizer.py --optimize")
        print("  • Setup HTTPS:      python setup_https.py --self-signed")

        print("\n📚 Documentation:")
        print("  • README.md        - Overview and quick start")
        print("  • VOICE_GUIDE.md   - Voice interface guide")
        print("  • HOW-IT-WORKS.md  - Architecture details")
        print("  • METADATA_GUIDE.md - Task metadata reference")

        print("\n" + "="*60)
        print("✨ Happy processing! ✨")
        print("="*60)
    else:
        print("\n❌ Installation failed. Please check error messages above.")
        print("   Try manual installation: pip install -r requirements.txt")

if __name__ == "__main__":
    main()