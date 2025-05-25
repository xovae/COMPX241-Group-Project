var json;

// Collect the json file and decode into operation javascript
console.time("JSON Decode Time");
fetch('./investor-alert-list.json')
.then(response => response.json())
.then(data => {
    json = data;
    console.timeEnd("JSON Decode Time");

    runSearch();
})

// Run a search of the data, and connect it to button listener
function runSearch() {
    console.time("Search Time");
    checkData(json, "testSearch");
    console.timeEnd("Search Time");
}

document.getElementById("searchButton").addEventListener("click", runSearch);



// Search function for the data
function checkData(data, search) {
    for (var i = 0; i < data.length; i++) {
        if(data[i].websites == null) {
            continue;
        }

        var sites = data[i].websites;

        if (sites.length > 0) {
            for (var j = 0; j < sites.length; j++) {
                if (sites[i] === search) {
                    return;
                }
            } 
        }
    }
}

