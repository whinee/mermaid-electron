const { ipcRenderer, webFrame } = require('electron');
import mermaid from '../node_modules/mermaid/dist/mermaid.esm.mjs'

window.mermaid = mermaid

let canContinue = false;

ipcRenderer.on('continue', () => {
    canContinue = true;
});

async function mermaidEvent(event, arg) {
    const mmd_ls = arg.mmd;
    const config = arg.config;
    const defaultMmdConfig = arg.mmd_config;

    console.log(arg)

    if (config.zoom != 1) {
        webFrame.setZoomFactor(config.zoom)
    }

    for (const mmd of mmd_ls) {
        const mermaidElement = document.createElement('pre');
        mermaidElement.setAttribute('id', 'mermaid');
        mermaidElement.textContent = mmd.code;
        document.body.appendChild(mermaidElement);

        if (mmd.config) {
            mermaid.initialize({ ...defaultMmdConfig, ...mmd.config });
        } else {
            mermaid.initialize(defaultMmdConfig);
        }

        await mermaid.run({
            querySelector: '#mermaid',
        }).catch((error) => {
            console.error(error)
            ipcRenderer.send('error', error)
        });

        await new Promise((resolve) => {
            const intervalId = setInterval(() => {
                const element = document.querySelector('#mermaid[data-processed]');
                if (element) {
                    element.setAttribute('style', `max-width:${config.max_width}px;`);
                    clearInterval(intervalId);
                    resolve();
                }
            }, 100);
        });

        await new Promise((resolve) => {
            const intervalId = setInterval(() => {
                if (document.querySelector('#mermaid[style]')) {
                    clearInterval(intervalId);
                    resolve();
                }
            }, 100);
        });

        ipcRenderer.send('screenshot');

        await new Promise((resolve) => {
            const intervalId = setInterval(() => {
                if (canContinue) {
                    canContinue = false;
                    clearInterval(intervalId);
                    resolve();
                }
            }, 100);
        });

        mermaidElement.remove()
    }

    ipcRenderer.send('done')

}

ipcRenderer.on('mermaid', async (event, arg) => {
    try {
        await mermaidEvent(event, arg)
    } catch (e) {
        ipcRenderer.send('error', e)
    }
})

ipcRenderer.send('ready')
