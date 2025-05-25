const params = new URLSearchParams(location.search);

if(params.has("name") && params.has("desc")) {
    const name = params.get("name");
    const desc = params.get("desc");

    const titleContainer = document.getElementById("webTitle");
    const descriptionContainer = document.getElementById("description");

    titleContainer.innerText = name;
    descriptionContainer.innerText = desc;
}