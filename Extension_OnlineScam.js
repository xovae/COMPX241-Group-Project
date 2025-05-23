// ==UserScript==
// @name         Online Scam Detector
// @namespace    http://tampermonkey.net/
// @version      1.75
// @description  Warns and blocks input on scam sites after user click; warning shows on load
// @author       Online Scam group
// @match        *://*/*
// @grant        GM_addStyle
// @run-at       document-idle
// ==/UserScript==

(function () {
    'use strict';

    // List of known scam domains
    const fraudSites = [
        "pilosaleltd.com",
        "fx-gam.com",
        "selected-markets.com",
        "fxreview.com",
        "eternalwealthfx.com",
        "efsca.online",
        "aimcl.com",
        "cfdstocks.com",
        "abbeyhouseacquisitions.com",
        "abelmyers.com",
        "acctnyc.com",
        "acomex.nl",
        "theadamgroup.com",
        "adderleydavis.com",
        "admiralglobal.com",
        "afufx.com",
        "advantagesecurities.com",
        "advent-oriental.com",
        "adviser-inc.com",
        "aeginvltd.com",
        "agromicron.com",
        "ajwitherspoonandco.com",
        "brokerz.com",
        "afadvisoryinc.com",
        "alliancefrboard.us",
        "alliancefx.capital",
        "alliancegrouptokyo.com",
        "alliedcapmgt.com",
        "alliedsovereignzurich.com",
        "alphatakeovers.com",
        "ambercapitalpartners.com",
        "ambramsoninternational.com",
        "amcint-hk.com",
        "afoex.com",
        "americanhst.com",
        "amselcommodities.com",
        "annexinternational.com",
        "antonfalk.com",
        "apolloam.us",
        "apolloassetmanagementhk.com",
        "aqua-securities.com",
        "arambinaryoptions.com",
        "arcadia-hk.",
        "ariesventuresinc.com",
        "aristacv.com",
        "teramusu.com",
        "ivoryoption.com",
        "asean-commodities.com",
        "ashfordinvestments.com",
        "acglobalinc.com",
        "asiaworldcap.com",
        "asiapacificadvisors.com"
    ];

    // Get the current hostname and remove "www." if present
    const hostname = window.location.hostname.replace(/^www\./, '').toLowerCase();

    // Skip if the current site isn't in the list
    if (!fraudSites.some(domain => hostname === domain || hostname.endsWith('.' + domain))) return;

    // Track if the user has dismissed the warning
    let isDismissed = false;

    // Set up the audio element
    const player = document.createElement('audio');
    player.src = 'https://audio.jukehost.co.uk/IpeJpbsyPHDpCEoV8lzFU3mqznohtnqI';
    player.preload = 'auto';
    player.volume = 1.0;
    document.body.appendChild(player);

    // Show fraud warning immediately on page load
    function showFraudWarning() {
        // Add custom styles for the warning box
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
                margin-right: 10px;
                font-weight: bold;
            }

            #learnMoreBtn {
                background-color: #1976d2;
            }

            #learnMoreBtn:hover {
                background-color: #1254a1;
            }

            #fraudAlertBox button:hover {
                background-color: #d32f2f;
            }
        `);

        // Create and add the fraud alert box to the page
        const box = document.createElement('div');
        box.id = 'fraudAlertBox';
        box.innerHTML = `
            <h2>Fraud Alert</h2>
            <p>This site (<strong>${hostname}</strong>) is flagged as fraudulent.</p>
            <p>Do not share personal or payment information.</p>
            <button id="dismissFraudWarning">Dismiss</button>
            <button id="learnMoreBtn">Learn More</button>
        `;
        document.body.appendChild(box);

        // Dismiss the alert when "Dismiss" is clicked
        document.getElementById('dismissFraudWarning').addEventListener('click', () => {
            isDismissed = true; // Mark dismissal
            box.remove();

            // If input blocker is present, remove it and restore scrolling
            const existingBlocker = document.getElementById('inputBlockerOverlay');
            if (existingBlocker) {
                existingBlocker.remove();
                document.body.style.overflow = '';
            }
        });

        // Open the DIA scam info page when "Learn More" is clicked
        document.getElementById('learnMoreBtn').addEventListener('click', () => {
            window.open('https://www.dia.govt.nz/diawebsite.nsf/wpg_url/services-anti-spam-online-scams', '_blank');
        });
    }

    // Block user input with a fullscreen overlay
    function blockUserInput() {
        // Add styles for the blocking overlay
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

        // Create the blocking overlay
        const blocker = document.createElement('div');
        blocker.id = 'inputBlockerOverlay';
        blocker.setAttribute('tabindex', '-1');

        // List of events to block
        const events = [
            'click', 'mousedown', 'mouseup', 'mousemove',
            'keydown', 'keypress', 'keyup',
            'wheel', 'touchstart', 'touchend', 'touchmove',
            'pointerdown', 'pointerup', 'pointermove',
            'contextmenu'
        ];

        // Prevent all user interactions on the page
        for (const eventType of events) {
            blocker.addEventListener(eventType, e => {
                e.preventDefault();
                e.stopPropagation();
            }, true);
        }

        // Add the overlay to the page and disable scrolling
        document.body.appendChild(blocker);
        document.body.style.overflow = 'hidden';
    }

    // Activate sound and input blocker after user interaction
    function activateSecurity() {
        if (isDismissed) return; // Skip if dismissed before click

        // Play the warning sound
        player.play().catch(() => {});
        // Block all input
        blockUserInput();
        // Remove the listener after first interaction
        document.removeEventListener('click', activateSecurity);
    }

    // Start everything
    showFraudWarning(); // Show fraud warning immediately on page load
    document.addEventListener('click', activateSecurity, { once: true }); // Wait for first user click before activating audio and block
})();
