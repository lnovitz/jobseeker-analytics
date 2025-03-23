# Welcome!

Whether this is your first time downloading code or the gazillionth time cloning a repo, we are happy to see you. 

Here you will learn how to install the app directly on your personal computer. 

Once the app is installed, you'll be able to gain full access to all the features. 

If you are a current or aspiring developer, you can pick up [open issues](https://github.com/lnovitz/jobseeker-analytics/issues), write code to fix them, and get your work reviewed and merged. Comment on an issue if you'd like to try resolving it.

If you're not an aspiring developer, that's totally ok. 

Keep reading to install the app. 

You may run into issues - email help@jobba.help for help :)

## How can I install the app directly on my computer?

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
2. Edit the `.env` file with your own credentials.
   **🔒 Never share your `.env` file or commit it to Git!**  
3. Copy `frontend\.env.sample` to `frontend\.env`:
   ```sh
   cp frontend/.env.sample frontend/.env
   ```
---


### Run the App: Two options  

#### Option 1: Docker Compose (Preferred Option)

1. If this is your first time using Docker, install as below:
   - Install Docker. On Windows/Mac install [Docker Desktop](https://docs.docker.com/get-started/get-docker/). On Linux install [Docker Engine](https://docs.docker.com/engine/install/). 
   - Start Docker Desktop or Docker Engine
      - On Windows: make sure to select "Use the WSL 2 based engine" under Settings/general.
      - On Linux: you may need to take additional post-installation steps, see (here)[https://docs.docker.com/engine/install/linux-postinstall/]. 
2. Start the app using Docker compose-up. The first time you run this locally it may take a few minutes to set up.
```
docker-compose up --build
```
3. Then, visit [http://localhost:3000](http://localhost:3000) to begin testing the app locally.
4. Troubleshooting:
   - Attempted import error
      - `cd frontend`
      - `npm ci`

You can view logs from the app by finding your container in Docker Desktop/Docker Engine and clicking on it. The app will automatically refresh when you make changes. 

#### Option 2: Virtual Environment

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
3. Start the PostgreSQL database:
   - Ensure Docker is installed and running.
   - Use Docker to start the PostgreSQL database:
     ```bash
     docker run --name jobseeker-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=jobseeker_analytics -p 5433:5432 -d postgres:13
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
5. Check it out @:
   http://127.0.0.1:8000
   
Then, visit `http://localhost:8000/login` to test the authentication flow.  

---


### Inspect the Database with DBeaver

To inspect your PostgreSQL database running in Docker, follow these steps:

1. **Install DBeaver**:
   - Go to the [DBeaver download page](https://dbeaver.io/download/).
   - Download and install the appropriate version for your operating system (Windows, macOS, or Linux).

2. **Start Docker Services (choose one of the commands below to start it if you haven't already)**:
   - Ensure your Docker services are running using the following command:
     ```bash
     docker-compose -f docker-compose-dev.yaml up --build
     ```
   - Or use the following command to simulate a production build (useful if you do not need to test frontend changes and only want to test backend functionality changes - you won't need to wait for the frontend to compile every time you navigate to a different page):
     ```bash
     docker-compose up --build
     ```

3. **Create a New Database Connection in DBeaver (if this is your first time opening DBeaver for this project)**:
   - Open DBeaver.
   - - Note: you may need to Download SQLLite driver files - Driver settings window will prompt you.
   - Click on the `Database` menu and select `New Database Connection`.
   - Select `PostgreSQL` and click `Next`.

4. **Enter Connection Details**:
   - **Host**: `localhost`
   - **Port**: `5433` (as specified in your `docker-compose.yaml` file)
   - **Database**: `jobseeker_analytics`
   - **Username**: `postgres`
   - **Password**: `postgres`
   - Click on the `Test Connection` button to ensure the connection is successful.
   - Note: you may need to Download PostgreSQL driver files - Driver settings window will prompt you.

5. **Save the Connection**:
   - If the connection test is successful, click `Finish` to save the connection.
   - If the connection test fails, double-check the connection details and ensure that your Docker services are running.

6. **Inspect the Database**:
   - In the `Database Navigator` pane on the left side of DBeaver, expand the `PostgreSQL` node.
   - Expand the `jobseeker_analytics` node to see the available schemas and tables.
   - Right-click on a table (e.g., `test_table`) and select `View Data` to see the data in the table.

7. **Open the Playground Page**:
   - Open your browser and navigate to `http://localhost:3000/playground`.

8. **Insert a Record**:
   - Use the form on the playground page to insert a new record by entering a name and clicking "Insert Data".
   - Observe the changes in DBeaver. You should see the new record appear in the `test_table`.

9. **Delete All Records**:
   - Click the "Delete All Data" button on the playground page to delete all records.
   - Observe the changes in DBeaver. You should see the records being removed from the `test_table`.



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

## Code of Conduct

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

