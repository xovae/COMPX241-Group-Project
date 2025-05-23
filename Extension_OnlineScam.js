// ==UserScript==
// @name         Online Scam Detector
// @namespace    http://tampermonkey.net/
// @version      1.4
// @description  Warns and blocks all input on known scam sites until dismissed.
// @author       Online Scam Group
// @match        *://*/*
// @grant        GM_addStyle
// ==/UserScript==

(function () {
    'use strict';

    // List of known scam domains
    const fraudSites = [
        "pilosaleltd.com",
        "scammyexample1.com",
        "fraudpaymentsite.net",
        "fakeshoponline.co",
        "dangerousdeals.xyz"
    ];

    const hostname = window.location.hostname.replace(/^www\./, '').toLowerCase();

    // Check if current hostname is in the scam list
    if (!fraudSites.includes(hostname)) return;

    // Block ALL user interaction
    function blockUserInput() {
        GM_addStyle(`
            #inputBlockerOverlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background-color: rgba(0,0,0,0.4);
                z-index: 9999;
                cursor: not-allowed;
                pointer-events: all;
            }
        `);

        const blocker = document.createElement('div');
        blocker.id = 'inputBlockerOverlay';
        blocker.setAttribute('tabindex', '-1');

        const events = [
            'click', 'mousedown', 'mouseup', 'mousemove',
            'keydown', 'keypress', 'keyup',
            'wheel', 'touchstart', 'touchend', 'touchmove',
            'pointerdown', 'pointerup', 'pointermove',
            'contextmenu'
        ];

        for (const eventType of events) {
            blocker.addEventListener(eventType, e => {
                e.preventDefault();
                e.stopPropagation();
            }, true);
        }

        document.body.appendChild(blocker);
        document.body.style.overflow = 'hidden';
    }

    // Try to play alert sound
    function playAlertSound() {
        const sound = new Audio("https://www.soundjay.com/button/beep-07.wav");
        sound.volume = 1.0;
        sound.play().catch(() => {
            document.addEventListener('click', () => {
                sound.play().catch(() => {});
            }, { once: true });
        });
    }

    // Show fraud alert
    function showFraudWarning() {
        GM_addStyle(`
            #fraudAlertBox {
                position: fixed;
                top: 20px;
                right: 20px;
                background-color: #ffebee;
                color: #b71c1c;
                border: 2px solid #f44336;
                padding: 20px;
                z-index: 10001;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                font-family: Arial, sans-serif;
                width: 320px;
            }

            #fraudAlertBox h2 {
                margin: 0 0 10px;
                font-size: 18px;
            }

            #fraudAlertBox button {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                cursor: pointer;
                margin-top: 10px;
                font-weight: bold;
            }

            #fraudAlertBox button:hover {
                background-color: #d32f2f;
            }
        `);

        const box = document.createElement('div');
        box.id = 'fraudAlertBox';
        box.innerHTML = `
            <h2>⚠️ Fraud Alert</h2>
            <p>This site (<strong>${hostname}</strong>) is flagged as fraudulent.</p>
            <p>Interaction is disabled. Do not share personal or payment information.</p>
            <button id="dismissFraudWarning">Dismiss</button>
        `;
        document.body.appendChild(box);

        // Remove overlay and alert on dismiss
        document.getElementById('dismissFraudWarning').addEventListener('click', () => {
            document.getElementById('inputBlockerOverlay')?.remove();
            box.remove();
            document.body.style.overflow = '';
            playAlertSound(); // Retry sound
        });
    }

    // Execute protections
    blockUserInput();
    showFraudWarning();
    playAlertSound();

})();
