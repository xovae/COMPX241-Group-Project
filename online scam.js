// ==UserScript==
// @name         Online Scam
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Displays a fraud alert when visiting known scam sites
// @author       You
// @match        *://*/*
// @grant        GM_addStyle
// ==/UserScript==

(function() {
    'use strict';

    // List of known fraudulent domains (add more as needed)
    const fraudSites = [
        "pilosaleltd.com",
        "scammyexample1.com",
        "fraudpaymentsite.net",
        "fakeshoponline.co",
        "dangerousdeals.xyz"
    ];

    // Get the current site's hostname
    const hostname = window.location.hostname.replace(/^www\./, '').toLowerCase();

    // Check if this site is in the fraud list
    if (fraudSites.includes(hostname)) {
        showFraudWarning();
    }

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
                z-index: 10000;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                font-family: Arial, sans-serif;
                width: 300px;
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

        // Create the warning panel
        const alertBox = document.createElement('div');
        alertBox.id = 'fraudAlertBox';
        alertBox.innerHTML = `
            <h2>:warning: Fraud Alert</h2>
            <p>This website (<strong>${hostname}</strong>) is listed as potentially fraudulent.</p>
            <p>Proceed with caution. Do not enter personal or payment information.</p>
            <button onclick="this.parentElement.style.display='none';">Dismiss</button>
        `;
        document.body.appendChild(alertBox);
    }
})();
