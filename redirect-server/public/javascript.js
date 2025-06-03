const params = new URLSearchParams(location.search);

const searchURL = params.get("url");

// Send request to server
fetch('https://mmm.so-we-must-think.space/scams')
.then(res => res.json()) 
.then(data => {
for (var i = 0; i < data.length; i++) {
        if(data[i].Websites == null) {
            continue;
        }

        var sites = data[i].Websites;

        if (sites.length > 0) {
            for (var j = 0; j < sites.length; j++) {
                if (sites[j] == searchURL) {
                    const name = data[i].Name;
                    const desc = data[i].Description;

                    // These are all for handling IOSCO targets
                    const type = data[i].Type;
                    const NCA = data[i].NCA;
                    const URL = data[i].URL;

                    setData(name, desc, type, NCA, URL);
                    return;
                }
            } 
        }
    }
});

// Sets internal data for the item
function setData(name, desc, type, NCA, URL) {
    var titleElement = document.getElementById("webTitle");
    var descriptionElement = document.getElementById("description");
    var informationDiv = document.getElementById("informationDiv");

    if (name) {
        titleElement.innerText = name;
    }

    if (desc) {
        descriptionElement.innerText = desc;
    }

    // Add for info div
    const paragraph = document.createElement("p");

    if (type == "IOSCO") {
        paragraph.innerHTML = "The " + NCA + " has released this alert, more info can be found on their website <a href='" + URL + "'>here</a>";

        informationDiv.appendChild(paragraph);
    } else if (type == "NZ"){
        paragraph.innerHTML = "The Financial Markets Authority has released this alert, more info can be found on their website <a href='https://www.fma.govt.nz/library/warnings-and-alerts/'>here</a>"

        informationDiv.appendChild(paragraph);
    } else if (type == "AUS") {
        paragraph.innerHTML = "The Australian Securities and Investments Commision has released this alert, more info can be found on their website <a href='https://moneysmart.gov.au/check-and-report-scams/investor-alert-list'>here</a>"

        informationDiv.appendChild(paragraph);
    }
}