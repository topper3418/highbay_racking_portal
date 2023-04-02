// util.js
async function populateTableFromApi(tableId, apiUrl, query) {
    try {
        const response = await fetch(`${apiUrl}?query=${encodeURIComponent(query)}`);
        if (response.ok) {
            const jsonData = await response.json();
            populateTable(tableId, jsonData);
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
