const { app, BrowserWindow, ipcMain, Menu } = require("electron");
const { autoUpdater } = require("electron-updater");
const path = require("path");
const Store = require("electron-store");
const sqlite3 = require("sqlite3").verbose();
const store = new Store();

let mainWindow;
let db;

// Create application menu
function createMenu() {
  const isMac = process.platform === "darwin";
  const template = [
    ...(isMac
      ? [
          {
            label: app.name,
            submenu: [
              { role: "about" },
              { type: "separator" },
              { role: "services" },
              { type: "separator" },
              { role: "hide" },
              { role: "hideOthers" },
              { role: "unhide" },
              { type: "separator" },
              {
                label: "Force Quit",
                accelerator: "CmdOrCtrl+Q",
                click: () => {
                  if (db) {
                    db.close();
                  }
                  app.quit();
                },
              },
            ],
          },
        ]
      : []),
    {
      label: "File",
      submenu: [
        isMac
          ? { role: "close" }
          : {
              label: "Force Quit",
              accelerator: "Alt+F4",
              click: () => {
                if (db) {
                  db.close();
                }
                app.quit();
              },
            },
      ],
    },
    {
      label: "View",
      submenu: [
        { role: "reload" },
        { role: "forceReload" },
        { role: "toggleDevTools" },
        { type: "separator" },
        { role: "resetZoom" },
        { role: "zoomIn" },
        { role: "zoomOut" },
        { type: "separator" },
        { role: "togglefullscreen" },
      ],
    },
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

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
  createMenu();
});

// Add force quit handler for Windows/Linux
app.on("before-quit", () => {
  if (db) {
    db.close();
  }
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

      // Calculate date for 1 week ago and format it properly
      const lastWeek = new Date();
      lastWeek.setDate(lastWeek.getDate() - 7);

      // Format date as DD-Mon-YYYY
      // Example: "1-Jan-2024"
      const formattedDate = lastWeek
        .toLocaleString("en-US", {
          day: "numeric",
          month: "short",
          year: "numeric",
        })
        .replace(/,/g, "");

      imap.search([["SINCE", formattedDate]], (err, results) => {
        if (err) {
          event.reply("emails-error", err.message);
          return;
        }

        if (!results || results.length === 0) {
          event.reply("emails-fetched", []);
          imap.end();
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
              const header = require("node-imap").parseHeader(buffer);
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
