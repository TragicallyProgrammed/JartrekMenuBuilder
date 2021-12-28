/* EVENT MANAGER */
$(function() {
    var tableInstance = new Table("", 1, new Array(8), []);
    tableEventManager(tableInstance);

    // Start with admin's beer table
    tableInstance.loadTable("tab-content-1", "test"); // Load table under beer tab
    $('input[name="tab-group"]:not(:checked)').each(function(index, item) { // Select every tab not currently selected
        document.getElementById(item.getAttribute("for")).style.display = 'none'; // Disable it
    });

    // TODO: Tab switching for currently selected user

    // TODO: Update values on table for currently selected user
    // TODO: And update for 'done' button

    // TODO: Customer select button event: Set current user to selected user, save changes on table of previous user, download and display table of current user
});