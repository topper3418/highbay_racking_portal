// util.js
async function populateTableFromApi(tableId, apiUrl, query) {
    try {
        const response = await fetch(`${apiUrl}?query=${encodeURIComponent(query)}`);
        if (response.ok) {
            const jsonData = await response.json();
            populateTable(tableId, jsonData);
            return jsonData;
        } else {
            console.error("Error fetching data from API:", response.statusText);
        }
    } catch (error) {
        console.error("Error fetching data from API:", error);
    }
}

function populateTable(tableId, data) {
    const table = document.getElementById(tableId);
    const thead = table.querySelector("thead");
    const tbody = table.querySelector("tbody");

    // Clear existing header and rows
    thead.innerHTML = "";
    tbody.innerHTML = "";

    if (data.length > 0) {
        // Generate table header based on keys of the first object in data
        const headerRow = document.createElement("tr");
        for (const key in data[0]) {
            const th = document.createElement("th");
            th.textContent = key;
            headerRow.appendChild(th);
        }
        thead.appendChild(headerRow);

        // Generate table rows based on data
        data.forEach(row => {
            const tr = document.createElement("tr");
            for (const key in row) {
                const td = document.createElement("td");
                td.textContent = row[key];
                tr.appendChild(td);
            }
            tbody.appendChild(tr);
        });
    }
}

async function populateDropdownsFromApi(container) {
    // get all the dropdowns that have a data-link attribute
    const dropdowns = container.querySelectorAll('select[data-link]');
    // wrap main functionality in a loop
    for (const dropdown of dropdowns) {
        try {
            const api_url = dropdown.dataset.link;
            const response = await fetch(api_url)
            if (response.ok) {
                const jsonData = await response.json();
                jsonData.forEach(value => {
                    const option = document.createElement('option');
                    option.value = value;
                    option.text = value;
                    dropdown.appendChild(option);
                });
            } else {
                console.error("Error fetching data from API:", response.statusText);
            }
        } catch (error) {
            console.error("Error fetching data from API:", error);
        }
    }
}

// function to fetch a popup run functions on it after
function fetchPopup(event, callbacks) {
    // get the link from the button's data-link attribute
    const button = event.target;
    const link = button.dataset.link;
    // fetch the popup content from the link and get the html
    fetch(link) // returns a promise
        .then(response => response.text()) // returns a promise
        .then(html => {
            // create a div element to hold the html
            const container = document.createElement("div");
            container.classList.add("popup-content");
            // add the html to the div
            container.innerHTML = html;
            // create a wrapper div to hold the content and black out most of the screen
            const wrapper = document.createElement('div');
            wrapper.classList.add('popup-wrapper');
            wrapper.appendChild(container);
            // add the wrapper to the body
            document.body.appendChild(wrapper);
            // add an event listener to the wrapper to remove it from the DOM when clicked
            wrapper.addEventListener('click', function (event) {
                // check if the click target is the wrapper element
                if (event.target === wrapper) {
                    // remove the wrapper element from the DOM
                    wrapper.remove();
                }
            });
            // run the callbacks
            if (callbacks && callbacks.length > 0) {
                callbacks.forEach(callback => callback(container));
            }
        });
}
