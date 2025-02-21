# Welcome!

Whether this is your first open-source project or you are a veteran contributor, we are happy to see you. This document is the single source of truth for how to contribute to the code base. You'll be able to pick up issues, write code to fix them, and get your work reviewed and merged. Feel free to browse the [open issues](https://github.com/lnovitz/jobseeker-analytics/issues). All feedback are welcome.

Thank you for taking the time to contribute! 🎉

## Code of Conduct

<details>
<summary> Please make sure to read and observe the <a href="">Code of Conduct</a></summary>

We aim to make participation in this project and in the community a harassment-free experience for everyone.

### Examples of behavior that contributes to positive environment

- Use welcoming and inclusive language
- Be respectful of other viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards others

### Examples of unacceptable behavior

- Use of sexualized language or imagery
- Trolling, insulting, derogatory comments and political attacks
- Public or private harassment
- Publishing other's private information or illegal information/documents
- Other conduct which could be reasonably considered inappropriate

This Code of Conduct applies to both within project spaces and in public spaces when an individual is representing the project or its community. By participating, you are expected to uphold this code. Please report unacceptable behavior.

</details>

## How Can I Contribute?

This project uses **Google OAuth** for authentication. To run the app locally, you’ll need to configure your own Google API credentials.  

### Clone the repo
1. On Windows: We recommend that you use WSL2. [Installation instructions here](https://learn.microsoft.com/en-us/windows/wsl/). 
2. On Windows: start WSL 
3. In Github, fork the repository
4. Clone this fork  using ```git clone https://github.com/lnovitz/jobseeker-analytics.git```
5. ```cd jobseeker-analytics``` into the repo you just cloned

### Get a Google AI API key
1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Click **Create and API Key**
3. Copy your API key and save it for later

---

### Create a Google OAuth App 
1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project (or use an existing one).  
2. Navigate to **APIs & Services** → **Credentials**.  
3. If this is your first time creating credentials with this project, you will have to configure the OAuth consent screen.
4. On the OAuth Consent Screen page, scroll to "Test Users" and add your gmail address.
3. Click **Create Credentials** → **OAuth 2.0 Client IDs**.  
4. Set the application type to **Web Application**.  
5. Under "Authorized redirect URIs," add:  
   - https://jobseeker-analytics.onrender.com/login
   - http://localhost:8000/login
6. Copy the **Client ID** and **Client Secret** for later.  
7. Download and save your credentials locally to the `backend` folder for this repo in a file named ```credentials.json```

---

### Set Up Environment Variables
1. Copy `backend\.env.example` to `backend\.env`:
   ```sh
   cp backend/.env.example backend/.env
   ```
2. Edit the `.env` file with your credentials:  
   ```ini
   GOOGLE_CLIENT_ID=your-client-id-here
   COOKIE_SECRET=your-random-secret-here
   GOOGLE_API_KEY=your-api-key-here
   DB_HOST=your-db-host-here
   DB_NAME=your-db-name-here
   DB_USER=your-db-user-here
   DB_PASSWORD=your-db-password-here
   APP_URL=http://localhost:3000
   ```
   **🔒 Never share your `.env` file or commit it to Git!**  

---


### Run the App

Once your `.env` file is set up, start the app by following the instructions below:
1. Create and activate virtual environment:
   ```sh
   # MAC/LINUX
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   ```sh
   # WINDOWS (CMD)
   python -m venv .venv
   .venv\Scripts\activate
   ```
   
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   cd frontend && npm install
   ```
4. Run backend and frontend apps:
   In one terminal window, run:
   ```bash
   cd backend && uvicorn main:app --reload
   ```
   In another terminal window, run:
   ```bash
   cd frontend && npm run dev
   ```
6. Check it out @:
   http://127.0.0.1:8000
   
Then, visit `http://localhost:8000/login` to test the authentication flow.  

You can view logs from the app by finding your container in Docker Desktop/Docker Engine and clicking on it. The app will automatically refresh when you make changes. 
---

### Troubleshooting Tips
- **Not redirected after login?**  
  Double-check your `REDIRECT_URI` in both `.env` and Google Cloud settings.  
- **Invalid API key errors?**  
  Some Google APIs require API key restrictions—try generating a new unrestricted key for local testing.  
- **Cannot Build Docker Image?**
   Try option 2, with venv and FastAPI server instead. 

---

### Submit Changes  
1. **Fork** this repository.  
2. **Clone** your fork:  
   ```sh
   git clone https://github.com/your-username/repo-name.git
   cd repo-name
   ```
3. **Create a new branch** for your changes:
- use branch convention <feature|bugfix|hotfix|docs>/<issueNumber>-<issueDescription>
   ```sh
   git checkout -b docs/65-add-contribution-guidelines
   ```
4. **Make your changes** and commit them:  
   ```sh
   git add .
   git commit -m "Add submission guidelines and env setup"
   ```
   Note: if you end up using a new Python library (e.g. I just added `ruff`) with `pip install`, be sure to do the following from the `backend` folder:
   `pip freeze > requirements.txt`

   You will need to add the `requirements.txt` file change as a commit, to ensure the environment has all its dependencies and production and local development environments run smoothly.
   ```sh
   git add requirements.txt
   git commit -m "add python library ruff"
   ```

5. **Format your changes** and commit them:

- If you're using Python, run:
   ```sh
   ruff format path/to/your/code
   git add .
   git commit -m "format with ruff"
   ```
(Please ensure your code passes all linting checks before submitting a pull request.)

6. **Push to your fork**:  
   ```sh
   git push origin docs/65-add-contribution-guidelines
   ```
7. **Open a Pull Request** on GitHub.  

Please ensure your changes align with the project's goals and do your best to follow the below coding style guides.
- Python: https://google.github.io/styleguide/pyguide.html
- TypeScript: https://google.github.io/styleguide/tsguide.html
- HTML/CSS: https://google.github.io/styleguide/htmlcssguide.html

---


### Report a Bug

This section guides you through submitting a bug report for Job Analytics. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior and provide a proper solution.

Before creating a bug report, please check this [list](https://github.com/lnovitz/jobseeker-analytics/issues) as you might find out you don't need to create a new one. When you are creating a bug report, please include as many details as possible, including screenshots or clips.

#### How Do I Submit a (Good) Bug Report?

Bugs are tracked as [GitHub issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues). Create an issue by providing the following information:

- Use a clear and descriptive title.
- Describe the exact steps which reproduce the problem. Include details on what you did and how you did it.
- Describe the behavior you observed after following the steps.
- Include screenshots and/or animated GIFs when possible.
- If the problem wasn't triggered by a specific action, describe what you were doing before the problem occurred.
