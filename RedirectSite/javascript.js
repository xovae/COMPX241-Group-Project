const params = new URLSearchParams(location.search);

setGetReq("webTitle", "name", params);
setGetReq("description", "desc", params);


function setGetReq(id, reqName, params) {
    const info = params.get(reqName);

    if(info == null) { return; }

    const docItem = document.getElementById(id);
    docItem.innerHTML = info;
}