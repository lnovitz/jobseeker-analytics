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

A simple and user-friendly email client built with Electron.

## Prerequisites

- Node.js 20.11.1 or later (LTS version recommended)
- npm (comes with Node.js)
- Git

## Installation

1. If you use nvm (Node Version Manager), simply run:
   ```bash
   nvm install
   nvm use
   ```
   This will automatically use the correct Node.js version specified in `.nvmrc`.

   If you don't use nvm, please ensure you have Node.js 20.11.1 or later installed.

2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/email-client.git
   cd email-client
   ```

3. Install dependencies:
   ```bash
   npm install
   ```
   This will automatically install all dependencies and rebuild native modules for Electron.

4. Start the application:
   ```bash
   npm start
   ```

## Building the Application

To build the application for your platform:

```bash
# For all platforms
npm run build

# For specific platforms
npm run build:mac    # macOS
npm run build:win    # Windows
npm run build:linux  # Linux
```

The built applications will be available in the `dist` directory.

## Features

- Simple and intuitive email interface
- Support for IMAP email accounts
- Local email storage using SQLite
- Automatic updates
- Cross-platform support (macOS, Windows, Linux)

## Development

- `npm start` - Start the application in development mode
- `npm run build` - Build the application for distribution
- `npm run publish` - Build and publish the application

## Troubleshooting

If you encounter any issues with native modules, try:

1. Delete the `node_modules` folder
2. Run `npm install` again
3. If issues persist, manually rebuild native modules:
   ```bash
   ./node_modules/.bin/electron-rebuild
   ```

## License

ISC
