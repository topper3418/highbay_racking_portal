async function populateTable() {
    const table = document.querySelector('#requests-table');
    const tableData = await fetch('/get_tickets').then(response => response.json());
    
    // Clear existing table rows
    while (table.rows.length > 1) {
      table.deleteRow(-1);
    }
  
    // Add new rows
    for (const row of tableData) {
      const newRow = table.insertRow(-1);
      const rowData = [row.type, row.submitter, row.submitted, row.due_date, row.due_date_reason];
      for (const data of rowData) {
        const newCell = newRow.insertCell(-1);
        const newText = document.createTextNode(data);
        newCell.appendChild(newText);
      }
    }
  }
  
  // Call populateTable on page load
  populateTable();
  