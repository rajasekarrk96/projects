#!/usr/bin/env python3
"""
SafeGuard Pro - Professional Demo Setup Script
This script prepares the gas detection system for professional demonstrations
"""

import os
import sys
import subprocess
import json
from datetime import datetime

class SafeGuardProSetup:
    def __init__(self):
        self.project_name = "SafeGuard Pro - Industrial Gas Detection System"
        self.version = "1.0.0"
        self.author = "Professional IoT Developer"
        
    def print_banner(self):
        """Display professional banner"""
        banner = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    ███████╗ █████╗ ███████╗███████╗ ██████╗ ██╗   ██╗ █████╗ ██████╗ ██████╗ ║
║    ██╔════╝██╔══██╗██╔════╝██╔════╝██╔════╝ ██║   ██║██╔══██╗██╔══██╗██╔══██╗║
║    ███████╗███████║█████╗  █████╗  ██║  ███╗██║   ██║███████║██████╔╝██║  ██║║
║    ╚════██║██╔══██║██╔══╝  ██╔══╝  ██║   ██║██║   ██║██╔══██║██╔══██╗██║  ██║║
║    ███████║██║  ██║██║     ███████╗╚██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝║
║    ╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ║
║                                                                              ║
║                        Professional Demo Setup                              ║
║                              Version {self.version}                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def check_requirements(self):
        """Check if all requirements are met"""
        print("🔍 Checking system requirements...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            return False
            
        # Check required files
        required_files = [
            "Gas_Detection/app.py",
            "Gas_Detection/requirements.txt",
            "Gas_Detection/templates/index.html",
            "gas_detection.ino"
        ]
        
        for file in required_files:
            if not os.path.exists(file):
                print(f"❌ Missing required file: {file}")
                return False
                
        print("✅ All requirements met")
        return True
        
    def install_dependencies(self):
        """Install Python dependencies"""
        print("📦 Installing Python dependencies...")
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", 
                "Gas_Detection/requirements.txt"
            ], check=True, capture_output=True)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
            
    def create_env_template(self):
        """Create environment variables template"""
        print("🔧 Creating environment configuration...")
        
        env_content = """# SafeGuard Pro Environment Configuration
# Copy this file to .env and fill in your actual values

# Twilio Configuration (for SMS alerts)
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_FROM_NUMBER=your_twilio_phone_number_here
TWILIO_TO_NUMBER=recipient_phone_number_here

# ESP32 Configuration
ESP32_IP=192.168.1.100
GAS_THRESHOLD=800

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your_secret_key_here

# Database Configuration (for future expansion)
DATABASE_URL=sqlite:///safeguard_pro.db
"""
        
        with open("Gas_Detection/.env.template", "w") as f:
            f.write(env_content)
            
        print("✅ Environment template created")
        
    def create_demo_data(self):
        """Create demo data for presentation"""
        print("📊 Setting up demo data...")
        
        demo_data = {
            "system_info": {
                "name": "SafeGuard Pro",
                "version": self.version,
                "author": self.author,
                "created": datetime.now().isoformat(),
                "features": [
                    "Real-time gas detection",
                    "Temperature & humidity monitoring",
                    "SMS alert system",
                    "Professional web dashboard",
                    "Mobile responsive design",
                    "Industrial safety protocols"
                ]
            },
            "demo_scenarios": [
                {
                    "name": "Normal Operation",
                    "gas_value": 350,
                    "temperature": 24.5,
                    "humidity": 45.2,
                    "gas_detected": False
                },
                {
                    "name": "Warning Level",
                    "gas_value": 750,
                    "temperature": 26.8,
                    "humidity": 52.1,
                    "gas_detected": False
                },
                {
                    "name": "Critical Alert",
                    "gas_value": 950,
                    "temperature": 28.3,
                    "humidity": 58.7,
                    "gas_detected": True
                }
            ]
        }
        
        os.makedirs("Gas_Detection/demo", exist_ok=True)
        with open("Gas_Detection/demo/demo_data.json", "w") as f:
            json.dump(demo_data, f, indent=2)
            
        print("✅ Demo data created")
        
    def create_presentation_script(self):
        """Create presentation talking points"""
        print("📝 Creating presentation materials...")
        
        script_content = """# SafeGuard Pro - Presentation Script

## Opening (30 seconds)
"Good morning/afternoon! I'm excited to present SafeGuard Pro, an industrial IoT gas detection system I developed. This project showcases my full-stack development skills, combining embedded systems, web technologies, and real-time data processing."

## System Overview (1 minute)
"SafeGuard Pro is designed for industrial environments where gas monitoring is critical for worker safety. The system consists of:
- ESP32 microcontroller with MQ135 gas sensor and DHT11 environmental sensor
- Python Flask backend for data processing and SMS alerts
- Professional web dashboard for real-time monitoring"

## Live Demo Points (3 minutes)
1. **Professional Dashboard**: "Notice the enterprise-grade design with real-time status indicators"
2. **Responsive Design**: "The interface adapts perfectly to different screen sizes"
3. **Real-time Updates**: "Data refreshes every 2 seconds with smooth animations"
4. **Safety Features**: "When gas is detected, the system triggers visual alerts and SMS notifications"
5. **System Information**: "Comprehensive monitoring includes uptime, connection status, and technical details"

## Technical Highlights (2 minutes)
- **Modern Tech Stack**: "Built with current industry standards - Python Flask, modern JavaScript, responsive CSS"
- **Real-time Communication**: "Seamless data flow from hardware sensors to web interface"
- **Professional UI/UX**: "Enterprise-ready design with accessibility considerations"
- **Scalable Architecture**: "Designed for easy expansion to multiple sensors and locations"

## Code Quality (1 minute)
"The codebase demonstrates professional development practices:
- Clean, documented code structure
- Responsive design principles
- Error handling and user feedback
- Security considerations for production deployment"

## Closing (30 seconds)
"This project represents my ability to create complete, professional solutions that solve real-world problems. I'm excited to bring these skills to your team and contribute to your organization's success."

## Potential Questions & Answers

**Q: How would you scale this system?**
A: "I'd implement a microservices architecture with a central database, API gateway for multiple sensors, and cloud deployment for global accessibility."

**Q: What about security?**
A: "The system includes environment variable configuration, HTTPS support, and can integrate with enterprise authentication systems."

**Q: How long did this take to develop?**
A: "The core system took about 2 weeks, with additional time spent on professional UI design and documentation for presentation purposes."
"""
        
        with open("PRESENTATION_SCRIPT.md", "w") as f:
            f.write(script_content)
            
        print("✅ Presentation script created")
        
    def run_setup(self):
        """Run the complete setup process"""
        self.print_banner()
        
        if not self.check_requirements():
            print("\n❌ Setup failed - requirements not met")
            return False
            
        if not self.install_dependencies():
            print("\n❌ Setup failed - dependency installation failed")
            return False
            
        self.create_env_template()
        self.create_demo_data()
        self.create_presentation_script()
        
        print("\n" + "="*80)
        print("🎉 SafeGuard Pro setup completed successfully!")
        print("="*80)
        print("\n📋 Next Steps:")
        print("1. Copy .env.template to .env and configure your credentials")
        print("2. Upload gas_detection.ino to your ESP32 board")
        print("3. Update ESP32 IP address in app.py")
        print("4. Run: python Gas_Detection/app.py")
        print("5. Open browser to http://localhost:5000")
        print("\n📖 Documentation:")
        print("- README.md - Complete project documentation")
        print("- PROJECT_PRESENTATION.md - Interview presentation guide")
        print("- PRESENTATION_SCRIPT.md - Demo talking points")
        print("\n🚀 Your professional IoT project is ready for demonstration!")
        
        return True

if __name__ == "__main__":
    setup = SafeGuardProSetup()
    setup.run_setup()
