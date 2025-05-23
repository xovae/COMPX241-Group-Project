// ==UserScript==
// @name         Online Scam Detector
// @namespace    http://tampermonkey.net/
// @version      1.4
// @description  Warns and blocks all input on known scam sites until dismissed.
// @author       Online Scam group
// @match        *://*/*
// @grant        GM_addStyle

// @run-at       document-idle

// ==/UserScript==

(function () {
    'use strict';

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
    "asiapacificadvisors.com",
     "www.fx-gam.com",
    "www.selected-markets.com",
    "www.fxreview.com",
    "www.eternalwealthfx.com",
    "efsca.online",
    "www.aimcl.com",
    "www.cfdstocks.com",
    "www.abbeyhouseacquisitions.com",
    "www.abelmyers.com",
    "www.acctnyc.com",
    "www.acomex.nl",
    "www.theadamgroup.com",
    "www.adderleydavis.com",
    "admiralglobal.com",
    "www.afufx.com",
    "www.advantagesecurities.com",
    "www.advent-oriental.com",
    "www.adviser-inc.com",
    "www.aeginvltd.com",
    "www.agromicron.com",
    "www.ajwitherspoonandco.com",
    "http://brokerz.com",
    "www.afadvisoryinc.com",
    "http://alliancefrboard.us",
    "http://www.alliancefx.capital",
    "http://alliancegrouptokyo.com",
    "http://www.alliedcapmgt.com",
    "www.alliedsovereignzurich.com",
    "www.alphatakeovers.com",
    "www.ambercapitalpartners.com",


    ];

    const hostname = window.location.hostname.replace(/^www\./, '').toLowerCase();

    // Match exact domains or subdomains
    if (!fraudSites.some(domain =>
    hostname === domain || hostname.endsWith('.' + domain)

    )) return;

    // Block ALL user interaction with a full-screen overlay
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

    // Plays an alert sound
    function playAlertSound() {
    const sound = new Audio("https://drive.google.com/uc?export=download&id=1HuT1bgxI2wlV3V2JwLU3qvux_34ZmBqK");
    sound.volume = 1.0;

    // user interaction to enable sound
    const clickToEnable = () => {
        sound.play().catch(() => {});
        document.removeEventListener('click', clickToEnable);
    };

    document.addEventListener('click', clickToEnable);
   }


    // Shows an alert box warning about the scam site
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

        const box = document.createElement('div');
        box.id = 'fraudAlertBox';
        box.innerHTML = `
            <h2>Fraud Alert</h2>
            <p>This site (<strong>${hostname}</strong>) is flagged as fraudulent.</p>
            <p>Interaction is disabled. Do not share personal or payment information.</p>
            <button id="dismissFraudWarning">Dismiss</button>
            <button id="learnMoreBtn">Learn More</button>
        `;
        document.body.appendChild(box);

        // Removes the overlay and warning box
        document.getElementById('dismissFraudWarning').addEventListener('click', () => {
            document.getElementById('inputBlockerOverlay')?.remove();
            box.remove();
            document.body.style.overflow = '';
            playAlertSound(); // Retry sound in case of initial failure
        });

        // Opens external scam information site in new tab
        document.getElementById('learnMoreBtn').addEventListener('click', () => {
            window.open('https://www.consumerprotection.govt.nz/general-help/scamwatch', '_blank');
        });
    }

    // Execute protection
    blockUserInput();
    showFraudWarning();
    playAlertSound();

})();
