// Imports
const { app, BrowserWindow, ipcMain } = require('electron');
const fs = require('fs');
const path = require('path');

// Constants
const processEventQuit = ['uncaughtException', 'unhandledRejection', 'warning']
const appEventQuit = ['child-process-gone', 'render-process-gone']
const webContentsEventQuitList = ['destroyed', 'did-fail-load', 'did-fail-provisional-load', 'render-process-gone', 'unresponsive']

// Derived Constants
const isDev = process.env.APP_DEV ? (process.env.APP_DEV.trim() == "true") : false;

// Initialize Variables
let mmd = []
let pipeChunks = []
let pipeInput = ""
let pipeFinished = false;

// Functions
function quit() {
    app.quit()
}

function errorFn(cause, error) {
    console.error(`[${cause}]`);
    console.error(error);
    quit();
}

// Event Listeners

// Process Event Listeners
process.stdin
    .on('data', chunk => {
        pipeChunks.push(chunk);
    })
    .once('end', () => {
        pipeInput = JSON.parse(Buffer.concat(pipeChunks).toString());
        pipeFinished = true;
    })

for (const event of processEventQuit) {
    process.once(event, (error) => {
        errorFn(`Process: ${event}`, error);
    });
}

// IPC Event listeners
ipcMain.once('error', (event, error) => {
    errorFn('Renderer: error', error)
})

ipcMain.once('done', () => {
    console.log(JSON.stringify(mmd))
    if (!isDev) {
        quit();
    }
})

// App Event Listeners
for (const event of appEventQuit) {
    app.once(event, (error) => {
        errorFn(`App: ${event}`, error);
    });
}

app.on('ready', async () => {
    // Wait until the contents of pipe are read
    await new Promise((resolve) => {
        const intervalId = setInterval(() => {
            if (pipeFinished) {
                clearInterval(intervalId);
                resolve();
            }
        }, 100);
    });

    const width = pipeInput.config.width

    let winConfig = {
        show: false,
        width: width,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            offscreen: true,
        },
    }

    if (isDev) {
        winConfig.show = true;
        winConfig.webPreferences.offscreen = false;
    }

    const win = new BrowserWindow(winConfig);

    // Window Event Listeners
    for (const event of webContentsEventQuitList) {
        win.webContents.once(event, quit);
    }

    if (isDev) {
        win.webContents.openDevTools();
    }

    win.loadFile(path.join(__dirname, 'index.html'));

    const w_width = win.getContentSize()[0];

    if (pipeInput.config.max_width == -1) {
        pipeInput.config.max_width = w_width
    }

    ipcMain.once('ready', async () => {
        win.webContents.send('mermaid', pipeInput);
    })

    ipcMain.on('screenshot', () => {
        win.webContents.capturePage().then(image => {
            win.webContents.send('continue');
            mmd.push(image.toPNG().toString('base64'));
        })
    })
})