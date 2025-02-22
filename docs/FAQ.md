# Frequently Asked Questions (FAQ)

## Installation

### Q: Is this app safe to install?
**A:** Yes, the app is open-source and the code is publicly available for review. The installers are digitally signed and automatically check for updates to ensure security.

### Q: What are the system requirements?
**A:**
- Windows: Windows 10 or later
- Mac: macOS 10.13 or later
- Linux: Any modern distribution with GLIBC 2.28 or later
- At least 100MB of free disk space
- Active internet connection

### Q: Why do I get a security warning when installing?
**A:** This is normal for new applications. The warning appears because the app isn't yet widely distributed. You can safely proceed with installation.

## Email Setup

### Q: Why do I need an App Password for Gmail?
**A:** Google requires App Passwords for applications that don't use their OAuth system. This is a security measure to protect your account while still allowing access to your email.

### Q: Where do I find my IMAP settings?
**A:** Common IMAP settings:
- Gmail: imap.gmail.com:993
- Outlook: outlook.office365.com:993
- Yahoo: imap.mail.yahoo.com:993
For other providers, check their help documentation or contact support.

### Q: Is my email password stored securely?
**A:** Yes, your password is stored locally on your computer using secure encryption. It's never transmitted anywhere except to your email provider's servers.

## Using the App

### Q: How often does the app check for new emails?
**A:** The app fetches emails from the last week when you click the "Fetch Recent Emails" button. It doesn't automatically sync in the background.

### Q: Where is my email data stored?
**A:** Email data is stored locally on your computer in a SQLite database in your application data directory:
- Windows: `%APPDATA%/email-client/`
- Mac: `~/Library/Application Support/email-client/`
- Linux: `~/.config/email-client/`

### Q: Can I delete stored emails?
**A:** Yes, you can delete stored emails from the "View Stored Emails" tab. This only removes them from the local database, not from your email account.

## Troubleshooting

### Q: The app won't connect to my email
**Common solutions:**
1. Check your internet connection
2. Verify your password is correct
3. For Gmail: Make sure you're using an App Password
4. For Outlook: Ensure IMAP access is enabled
5. Check your firewall isn't blocking the connection

### Q: I'm getting an "Invalid Password" error
**Try these steps:**
1. Double-check your password for typos
2. For Gmail/Yahoo: Generate a new App Password
3. For Outlook: Try resetting your password
4. Make sure CAPS LOCK isn't on

### Q: The app is stuck loading
**Solutions:**
1. Close and restart the app
2. Check your internet connection
3. Try fetching emails again
4. If problem persists, check the troubleshooting guide

## Updates

### Q: How do I update the app?
**A:** The app automatically checks for updates. When available:
1. You'll see an "Update Available" notification
2. Click to download the update
3. The app will restart to install

### Q: How often are updates released?
**A:** We release updates:
- Monthly for feature updates
- Immediately for security fixes
- As needed for bug fixes

## Privacy and Security

### Q: Can the app read my emails?
**A:** The app only downloads email headers (subject, sender, date) from the last week. It doesn't download or store email content.

### Q: Is my data shared with anyone?
**A:** No. All data is stored locally on your computer. The app doesn't send any data to external servers except to communicate with your email provider.

## Getting Help

### Q: Where can I report bugs?
**A:** You can:
1. Submit an issue on our GitHub page
2. Join our Discord community
3. Email our support team

### Q: How do I request new features?
**A:** We welcome feature requests! You can:
1. Submit a feature request on GitHub
2. Discuss ideas in our Discord community
3. Email our development team

### Q: How do I completely uninstall the app?
**To remove everything:**
1. Uninstall the app normally
2. Delete the application data folder
3. Remove any desktop/start menu shortcuts 