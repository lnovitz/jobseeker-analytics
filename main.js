const { app, BrowserWindow, ipcMain } = require("electron");
const { autoUpdater } = require("electron-updater");
const path = require("path");
const Store = require("electron-store");
const sqlite3 = require("sqlite3").verbose();
const store = new Store();

let mainWindow;
let db;

// Initialize auto-updater
function initializeAutoUpdater() {
  autoUpdater.autoDownload = false;

  autoUpdater.on("error", (error) => {
    mainWindow.webContents.send("update-error", error.message);
  });

  autoUpdater.on("update-available", (info) => {
    mainWindow.webContents.send("update-available", info);
  });

  autoUpdater.on("update-downloaded", (info) => {
    mainWindow.webContents.send("update-downloaded", info);
  });

  // Check for updates every hour
  setInterval(() => {
    autoUpdater.checkForUpdates();
  }, 3600000);
}

// Initialize database
function initializeDatabase() {
  const dbPath = path.join(app.getPath("userData"), "emails.db");
  db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
      console.error("Error opening database:", err);
      return;
    }

    // Create emails table if it doesn't exist
    db.run(`CREATE TABLE IF NOT EXISTS emails (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      sender TEXT,
      subject TEXT,
      timestamp DATETIME,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  mainWindow.loadFile("index.html");

  // Check for updates on startup
  autoUpdater.checkForUpdates();
}

// Handle IPC messages for updates
ipcMain.on("install-update", () => {
  autoUpdater.downloadUpdate();
});

ipcMain.on("restart-app", () => {
  autoUpdater.quitAndInstall();
});

app.whenReady().then(() => {
  initializeDatabase();
  initializeAutoUpdater();
  createWindow();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    if (db) {
      db.close();
    }
    app.quit();
  }
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// Handle email configuration
ipcMain.on("save-email-config", (event, config) => {
  store.set("emailConfig", config);
  event.reply("config-saved", true);
});

// Function to log email to database
function logEmailToDatabase(email) {
  return new Promise((resolve, reject) => {
    const stmt = db.prepare(
      "INSERT INTO emails (sender, subject, timestamp) VALUES (?, ?, ?)"
    );
    stmt.run(
      email.from,
      email.subject,
      new Date(email.date).toISOString(),
      (err) => {
        if (err) {
          reject(err);
        } else {
          resolve();
        }
      }
    );
    stmt.finalize();
  });
}

// Handle email fetching
ipcMain.on("fetch-emails", async (event) => {
  const config = store.get("emailConfig");
  if (!config) {
    event.reply("emails-error", "No email configuration found");
    return;
  }

  const ImapClient = require("node-imap");
  const imap = new ImapClient({
    user: config.email,
    password: config.password,
    host: config.imapHost,
    port: config.imapPort,
    tls: config.useTLS,
  });

  const emails = [];

  imap.once("ready", () => {
    imap.openBox("INBOX", false, (err, box) => {
      if (err) {
        event.reply("emails-error", err.message);
        return;
      }

      // Calculate date for 1 week ago
      const lastWeek = new Date();
      lastWeek.setDate(lastWeek.getDate() - 7);

      const fetch = imap.search(["SINCE", lastWeek], (err, results) => {
        if (err) {
          event.reply("emails-error", err.message);
          return;
        }

        const f = imap.fetch(results, {
          bodies: "HEADER.FIELDS (FROM SUBJECT DATE)",
          struct: true,
        });

        f.on("message", (msg, seqno) => {
          msg.on("body", (stream, info) => {
            let buffer = "";
            stream.on("data", (chunk) => {
              buffer += chunk.toString("utf8");
            });
            stream.once("end", () => {
              const header = require("imap").parseHeader(buffer);
              const email = {
                from: header.from?.[0],
                subject: header.subject?.[0],
                date: header.date?.[0],
              };
              emails.push(email);

              // Log each email to database
              logEmailToDatabase(email).catch((err) => {
                console.error("Error logging email to database:", err);
              });
            });
          });
        });

        f.once("error", (err) => {
          event.reply("emails-error", err.message);
        });

        f.once("end", () => {
          imap.end();
          event.reply("emails-fetched", emails);
        });
      });
    });
  });

  imap.once("error", (err) => {
    event.reply("emails-error", err.message);
  });

  imap.connect();
});

// Handle request for stored emails
ipcMain.on("get-stored-emails", (event) => {
  db.all("SELECT * FROM emails ORDER BY timestamp DESC", (err, rows) => {
    if (err) {
      event.reply("stored-emails-error", err.message);
    } else {
      event.reply("stored-emails-fetched", rows);
    }
  });
});
