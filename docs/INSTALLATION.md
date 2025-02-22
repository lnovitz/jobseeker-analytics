# Email Client Installation Guide

This guide will walk you through installing and setting up the Email Client on your computer.

## Table of Contents
- [Windows Installation](#windows-installation)
- [Mac Installation](#mac-installation)
- [Linux Installation](#linux-installation)
- [Email Setup Guide](#email-setup-guide)
- [Troubleshooting](#troubleshooting)

## Windows Installation

1. Download the installer
   - Go to the [Releases page](https://github.com/yourusername/email-client/releases)
   - Download `Email-Client-Setup.exe`
   ![Download Page](images/win-download.png)

2. Run the installer
   - Double-click the downloaded file
   - If you see a Windows security warning, click "More info" and then "Run anyway"
   ![Windows Security](images/win-security.png)

3. Choose installation options
   - Select installation location (or keep default)
   - Choose whether to create desktop shortcut
   ![Install Options](images/win-install-options.png)

4. Complete installation
   - Click "Install" and wait for the process to complete
   - Click "Finish" when done

## Mac Installation

1. Download the app
   - Go to the [Releases page](https://github.com/yourusername/email-client/releases)
   - Download `Email-Client.dmg`
   ![Download DMG](images/mac-download.png)

2. Install the app
   - Double-click the downloaded .dmg file
   - Drag the Email Client app to your Applications folder
   ![Mac Install](images/mac-install.png)

3. First launch
   - Find Email Client in your Applications folder or Launchpad
   - Right-click and select "Open"
   - Click "Open" in the security dialog
   ![Mac Security](images/mac-security.png)

## Linux Installation

### Ubuntu/Debian
1. Download the .deb package
   - Go to the [Releases page](https://github.com/yourusername/email-client/releases)
   - Download `email-client.deb`

2. Install using package manager
   ```bash
   sudo dpkg -i email-client.deb
   sudo apt-get install -f
   ```

### Other Linux Distributions
1. Download the AppImage
   - Download `email-client.AppImage`
   - Right-click → Properties → Permissions
   - Check "Allow executing file as program"
   ![Linux Permissions](images/linux-permissions.png)

2. Run the app
   - Double-click the AppImage file
   - Select "Run" when prompted

## Email Setup Guide

### Gmail Setup
1. Select Gmail from the provider list
   ![Provider Selection](images/provider-select.png)

2. Get an App Password
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification if not already enabled
   - Go to App Passwords
   - Select "Mail" and your device type
   - Copy the generated password
   ![Gmail App Password](images/gmail-app-password.png)

3. Enter your credentials
   - Your Gmail address
   - The App Password you just generated
   ![Email Setup](images/email-setup.png)

### Outlook Setup
1. Select Outlook from the provider list

2. Enable IMAP
   - Go to Outlook.com
   - Settings → View all Outlook settings
   - Mail → Sync email
   - Enable IMAP
   ![Outlook IMAP](images/outlook-imap.png)

3. Enter your credentials
   - Your Outlook email address
   - Your regular Outlook password

### Yahoo Setup
1. Select Yahoo from the provider list

2. Generate App Password
   - Go to Yahoo Account Security
   - Generate app password
   - Select "Other App" and name it "Email Client"
   ![Yahoo App Password](images/yahoo-app-password.png)

3. Enter your credentials
   - Your Yahoo email address
   - The generated App Password

## Troubleshooting

### Common Issues

#### App Won't Start
1. Check system requirements
   - Windows 10 or later
   - macOS 10.13 or later
   - Modern Linux distribution

2. Security Blocks
   - Windows: Right-click → Properties → Unblock
   - Mac: System Preferences → Security & Privacy → Open Anyway
   - Linux: Check file permissions

#### Connection Issues
1. Verify internet connection
2. Check email/password
3. For Gmail: Ensure using App Password
4. For Outlook: Check IMAP is enabled

### Getting Help
If you're still having issues:
1. Check our [FAQ](FAQ.md)
2. Join our [Discord community](https://discord.gg/your-server)
3. [Submit an issue](https://github.com/yourusername/email-client/issues)

### Updating the App
The app will automatically check for updates. When an update is available:
1. Click "Update Available" when prompted
2. Choose "Download Update"
3. Click "Restart" when ready

### Uninstalling
- Windows: Use "Add/Remove Programs"
- Mac: Drag to Trash from Applications
- Linux: Use package manager or delete AppImage 