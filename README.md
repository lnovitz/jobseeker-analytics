# **jobba.help - The Open-Source Job Search Tracker**

## **Overview**

jobba.help is an open-source job search tracker designed to empower jobseekers. 

By integrating with the Gmail API, jobba.help automates tracking and generates insights to improve transparency in hiring.

## **The Vision**

With enough support, jobba.help will overhaul the job search. The more jobseekers contribute, the better insights and tools we generate. 

Imagine the perfect job search:

- **Relevant roles**  - you don't have to visit 10 job boards to find a job
- **Analytics** - you know which industries and company sizes your profile attracts
- **Task organization** - see pending interviews and follow-ups at a glance without digging through hundreds of emails
- **Ghosting exposed** - public leaderboards will discourage bad hiring practices
- **Interview scheduling** is effortless, eliminating back-and-forth emails
- **Asking for help is easy** - Share job search updates with your support system and keep your search visible to the people who can vouch for you

## **Want to Beta Test?**

We'd love to have you on board! Here's how you can join:

1. **Send an Email:** [Click here to email us](mailto:help@jobba.help?subject=jobba.help%20beta%20signup&body=my%20google%20gmail%20address%20is)
   - Mention how you heard about the app (community, friend's name, etc.).
   - We'll respond as soon as possible to grant you access (subject to Google's beta testing user limits).
2. **Join our Discord:** [https://discord.gg/5tTT6WVQyw](https://discord.gg/5tTT6WVQyw)

## **Latest Feature: Automated Job Tracker**

Our automated job tracker allows you to:

- **Login with Google:** Automatically generate a spreadsheet filled with the date you applied, company name, and status of the application.
- **No manual updates required:** The spreadsheet updates automagically, saving you time and effort.

🎥 **Sneak Peek**: https://www.youtube.com/watch?v=-cOKR4JtceY

[![Watch the video](http://img.youtube.com/vi/-cOKR4JtceY/maxresdefault.jpg)](https://www.youtube.com/watch?v=-cOKR4JtceY)

## 🛠 **Features in Development**

- ✅ Built-in networking tools to engage friends & family in your search.
- ✅ Customized job search filter
- ✅ Pending interview & task management to keep you organized.
- ✅ Job application analytics for smarter decision-making.
- ✅ Ghosting reports to hold companies accountable.

## 🤝 **Contributing**

jobba.help is open-source and community-driven. We welcome contributions from developers, designers, and jobseekers alike! 

You do not have to have experience with our tech stack to contribute.

View contributing guidelines [here.](https://github.com/lnovitz/jobseeker-analytics/blob/main/CONTRIBUTING.md)

 🏗 **Tech Stack**

- **Frontend:** Next, TypeScript
- **Backend:** FastAPI, Python
- **Database:** PostgreSQL
- **Integrations:** Gmail API

## 🔒 **Privacy & Security**

We take data privacy seriously. jobba.help is currently in beta (100 user testing limit), and we have a code scanning tool in place to actively address security issues. Since jobba.help integrates with Gmail, the application will undergo a strict verification process before it is published to the public. 

## 📢 **A note from the maintainer**

Help us build the first open-source job search platform. Join our Discord at [https://discord.gg/5tTT6WVQyw](https://discord.gg/5tTT6WVQyw)

Why open-source, you might ask?

Companies often prioritize their own interests over those of jobseekers, focusing on profit rather than genuine support.

My goal is different.

I envision a community-driven tool, built by the people, for the people, ensuring it remains accessible and beneficial to all jobseekers.

Because it's open-source, future developers can always fork this project and continue the work. 

This is especially important if I, the maintainer, ever win the lottery, retire my computer, and open a cat café. 👀 

-Lianna

## **Support & Feedback**

If you experience any errors or want to share feedback, join our Discord at [https://discord.gg/5tTT6WVQyw](https://discord.gg/5tTT6WVQyw).

You can also always email us at [help@jobba.help](mailto:help@jobba.help).

# Email Client

A simple desktop email client that helps you view and store your recent emails.

## ⚡ Quick Start

**New to Email Client?** Get started in minutes with our [Quick Start Guide](docs/QUICK-START.md)!

1. Download for your system:
   - [Windows Installer](https://github.com/yourusername/email-client/releases/latest/download/Email-Client-Setup.exe)
   - [Mac App](https://github.com/yourusername/email-client/releases/latest/download/Email-Client.dmg)
   - [Linux AppImage](https://github.com/yourusername/email-client/releases/latest/download/email-client.AppImage)

2. Install and run
3. Select your email provider
4. Enter your credentials
5. Start viewing your emails!

Need more help? Check out our:
- 📚 [Full Installation Guide](docs/INSTALLATION.md)
- ❓ [FAQ](docs/FAQ.md)
- 💬 [Discord Community](https://discord.gg/your-server)

## Download and Install

### Windows Users
1. Download the latest `Email-Client-Setup.exe` from the [Releases page](https://github.com/yourusername/email-client/releases)
2. Double-click the downloaded file
3. Follow the installation wizard
4. Once installed, find "Email Client" in your Start menu

### Mac Users
1. Download the latest `Email-Client.dmg` from the [Releases page](https://github.com/yourusername/email-client/releases)
2. Double-click the downloaded file
3. Drag the Email Client app to your Applications folder
4. Find "Email Client" in your Applications folder or Launchpad

### Linux Users
1. Download the latest `email-client.AppImage` from the [Releases page](https://github.com/yourusername/email-client/releases)
2. Right-click the downloaded file and select "Properties"
3. In the Permissions tab, check "Allow executing file as program"
4. Double-click the file to run

## Setting Up Your Email

### For Gmail Users
1. Select "Gmail" from the provider dropdown
2. Enter your Gmail address
3. For the password, you'll need to use an App Password:
   - Go to your [Google Account Security Settings](https://myaccount.google.com/security)
   - Enable 2-Step Verification if you haven't already
   - Go to App Passwords
   - Select "Mail" and your device type
   - Click Generate
   - Use the 16-character password that appears

### For Outlook Users
1. Select "Outlook/Hotmail" from the provider dropdown
2. Enter your full email address
3. Use your regular Outlook password
4. If connection fails:
   - Go to Outlook.com
   - Settings → View all Outlook settings
   - Mail → Sync email
   - Make sure IMAP is enabled

### For Yahoo Users
1. Select "Yahoo Mail" from the provider dropdown
2. Enter your Yahoo email address
3. For the password:
   - Go to Yahoo Account Security
   - Generate app password
   - Use that password instead of your regular Yahoo password

### For Other Email Providers
1. Select "Other Provider" from the dropdown
2. Enter your email address
3. Enter your password
4. You'll need to enter your provider's IMAP settings:
   - IMAP Host (e.g., mail.provider.com)
   - IMAP Port (usually 993)
   - TLS should typically be enabled

## Features
- Connect to your email account
- View emails from the last week
- Automatically store email information locally
- View history of previously fetched emails

## Troubleshooting

### Connection Issues
- Make sure you have an internet connection
- Verify your email and password are correct
- For Gmail: Make sure you're using an App Password
- For Outlook: Ensure IMAP access is enabled
- Check if your antivirus or firewall is blocking the connection

### App Won't Start
- Try uninstalling and reinstalling the app
- Make sure your computer meets the minimum requirements
- Check if your antivirus is blocking the app

### Still Having Problems?
Contact us with:
- Your operating system (Windows/Mac/Linux)
- Your email provider
- The error message you're seeing
- Steps to reproduce the problem

## For Developers
If you're a developer interested in building the app from source, see [CONTRIBUTING.md](CONTRIBUTING.md) for instructions.
