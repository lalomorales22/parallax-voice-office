#!/usr/bin/env python3
"""
HTTPS Setup Script for Parallax Voice Office
Generates self-signed SSL certificates or helps configure Let's Encrypt
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HTTPSSetup:
    """Manages HTTPS/SSL certificate setup"""

    def __init__(self, cert_dir: str = "certs"):
        self.cert_dir = Path(cert_dir)
        self.cert_dir.mkdir(exist_ok=True, mode=0o700)

        self.cert_file = self.cert_dir / "server.crt"
        self.key_file = self.cert_dir / "server.key"
        self.csr_file = self.cert_dir / "server.csr"

    def check_openssl(self) -> bool:
        """Check if OpenSSL is installed"""
        try:
            result = subprocess.run(
                ['openssl', 'version'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info(f"OpenSSL found: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            logger.error("OpenSSL not found. Please install OpenSSL first.")
        return False

    def generate_self_signed_cert(self, domain: str = "localhost", days: int = 365):
        """Generate a self-signed SSL certificate"""
        if not self.check_openssl():
            return False

        try:
            logger.info(f"Generating self-signed certificate for {domain}...")

            # Generate private key
            subprocess.run([
                'openssl', 'genrsa',
                '-out', str(self.key_file),
                '2048'
            ], check=True, capture_output=True)

            logger.info("✓ Private key generated")

            # Generate certificate
            subprocess.run([
                'openssl', 'req',
                '-new',
                '-x509',
                '-key', str(self.key_file),
                '-out', str(self.cert_file),
                '-days', str(days),
                '-subj', f'/CN={domain}/O=Parallax Voice Office/C=US'
            ], check=True, capture_output=True)

            logger.info("✓ Certificate generated")

            # Set proper permissions
            os.chmod(self.key_file, 0o600)
            os.chmod(self.cert_file, 0o644)

            # Display certificate info
            self.show_cert_info()

            logger.info(f"\n✓ Self-signed certificate created successfully!")
            logger.info(f"  Certificate: {self.cert_file}")
            logger.info(f"  Private Key: {self.key_file}")
            logger.info(f"  Valid for: {days} days")
            logger.info(f"\n⚠️  Note: This is a self-signed certificate.")
            logger.info("  Browsers will show a security warning.")
            logger.info("  For production, use Let's Encrypt (see --letsencrypt option).")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate certificate: {e}")
            return False

    def generate_csr(self, domain: str, email: str):
        """Generate a Certificate Signing Request for Let's Encrypt"""
        if not self.check_openssl():
            return False

        try:
            logger.info(f"Generating CSR for {domain}...")

            # Generate private key if it doesn't exist
            if not self.key_file.exists():
                subprocess.run([
                    'openssl', 'genrsa',
                    '-out', str(self.key_file),
                    '2048'
                ], check=True, capture_output=True)

            # Generate CSR
            subprocess.run([
                'openssl', 'req',
                '-new',
                '-key', str(self.key_file),
                '-out', str(self.csr_file),
                '-subj', f'/CN={domain}/O=Parallax Voice Office/emailAddress={email}/C=US'
            ], check=True, capture_output=True)

            logger.info("✓ CSR generated successfully")
            logger.info(f"  CSR file: {self.csr_file}")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate CSR: {e}")
            return False

    def show_cert_info(self):
        """Display certificate information"""
        if not self.cert_file.exists():
            logger.error("Certificate file not found")
            return

        try:
            result = subprocess.run([
                'openssl', 'x509',
                '-in', str(self.cert_file),
                '-noout',
                '-subject',
                '-issuer',
                '-dates'
            ], capture_output=True, text=True, check=True)

            logger.info("\nCertificate Information:")
            logger.info(result.stdout)

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to read certificate: {e}")

    def setup_letsencrypt_instructions(self, domain: str, email: str):
        """Provide instructions for Let's Encrypt setup"""
        logger.info("\n" + "="*70)
        logger.info("Let's Encrypt Setup Instructions")
        logger.info("="*70)
        logger.info("\nLet's Encrypt provides free, automated SSL certificates.")
        logger.info("Follow these steps to set up Let's Encrypt:\n")

        logger.info("1. Install Certbot:")
        logger.info("   Ubuntu/Debian: sudo apt-get install certbot")
        logger.info("   CentOS/RHEL:   sudo yum install certbot")
        logger.info("   macOS:         brew install certbot\n")

        logger.info("2. Stop Parallax Voice Office (ports 80/443 must be free):")
        logger.info("   docker-compose down\n")

        logger.info("3. Run Certbot in standalone mode:")
        logger.info(f"   sudo certbot certonly --standalone -d {domain} --email {email}\n")

        logger.info("4. Copy certificates to the certs directory:")
        logger.info(f"   sudo cp /etc/letsencrypt/live/{domain}/fullchain.pem {self.cert_file}")
        logger.info(f"   sudo cp /etc/letsencrypt/live/{domain}/privkey.pem {self.key_file}")
        logger.info(f"   sudo chown $USER:$USER {self.cert_dir}/*\n")

        logger.info("5. Set ENABLE_HTTPS=true in your .env file")
        logger.info("6. Restart Parallax Voice Office:")
        logger.info("   docker-compose up -d\n")

        logger.info("7. Set up auto-renewal (add to crontab):")
        logger.info("   0 0 * * * certbot renew --quiet --post-hook 'docker-compose restart'\n")

        logger.info("="*70)

    def verify_setup(self) -> bool:
        """Verify that certificates are properly set up"""
        if not self.cert_file.exists():
            logger.error("✗ Certificate file not found")
            return False

        if not self.key_file.exists():
            logger.error("✗ Private key file not found")
            return False

        # Check file permissions
        cert_perms = oct(os.stat(self.cert_file).st_mode)[-3:]
        key_perms = oct(os.stat(self.key_file).st_mode)[-3:]

        logger.info("✓ Certificate file exists")
        logger.info("✓ Private key file exists")
        logger.info(f"  Certificate permissions: {cert_perms}")
        logger.info(f"  Private key permissions: {key_perms}")

        if key_perms != '600':
            logger.warning(f"⚠️  Private key permissions should be 600, found {key_perms}")
            logger.info("  Fixing permissions...")
            os.chmod(self.key_file, 0o600)

        self.show_cert_info()

        return True

def main():
    parser = argparse.ArgumentParser(
        description="HTTPS/SSL Setup for Parallax Voice Office",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate self-signed certificate for testing
  python setup_https.py --self-signed

  # Generate self-signed certificate with custom domain
  python setup_https.py --self-signed --domain myserver.local

  # Get Let's Encrypt setup instructions
  python setup_https.py --letsencrypt --domain example.com --email admin@example.com

  # Verify current certificate setup
  python setup_https.py --verify
        """
    )

    parser.add_argument('--self-signed', action='store_true',
                       help='Generate self-signed certificate (for development)')
    parser.add_argument('--letsencrypt', action='store_true',
                       help='Show Let\'s Encrypt setup instructions')
    parser.add_argument('--domain', default='localhost',
                       help='Domain name for certificate (default: localhost)')
    parser.add_argument('--email', default='admin@localhost',
                       help='Email address for Let\'s Encrypt')
    parser.add_argument('--days', type=int, default=365,
                       help='Certificate validity in days (default: 365)')
    parser.add_argument('--cert-dir', default='certs',
                       help='Certificate directory (default: certs)')
    parser.add_argument('--verify', action='store_true',
                       help='Verify certificate setup')

    args = parser.parse_args()

    setup = HTTPSSetup(cert_dir=args.cert_dir)

    if args.verify:
        if setup.verify_setup():
            logger.info("\n✓ HTTPS setup is valid")
            sys.exit(0)
        else:
            logger.error("\n✗ HTTPS setup has issues")
            sys.exit(1)

    elif args.self_signed:
        if setup.generate_self_signed_cert(domain=args.domain, days=args.days):
            logger.info("\n✓ Setup complete!")
            logger.info("\nNext steps:")
            logger.info("1. Set ENABLE_HTTPS=true in your .env file")
            logger.info("2. Restart the application")
            logger.info("3. Access via https://localhost:5443")
            sys.exit(0)
        else:
            sys.exit(1)

    elif args.letsencrypt:
        setup.setup_letsencrypt_instructions(domain=args.domain, email=args.email)
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(0)

if __name__ == '__main__':
    main()
