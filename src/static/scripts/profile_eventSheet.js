/* EVENT MANAGER */
$(function() {
    var tableInstance = new Table("", 1, new Array(8), []);
    tableEventManager(tableInstance);

    // Start with beer
    tableInstance.loadTable("tab-content-1"); // Load table under beer tab
    $('input[name="tab-group"]:not(:checked)').each(function(index, item) { // Select every tab not currently selected
        document.getElementById(item.getAttribute("for")).style.display = 'none'; // Disable it
    });

    //On tab change
    $('input[name="tab-group"]').change(function () { // Selecting all tabs and looking for them to change
        tableInstance.uploadTable(); // Uploads table to currently logged-in user's database
        tableInstance.loadTable($(this).attr("for")); // Download currently logged-in user's selected table
    });

    // Update values on table
    $('.datatable').on('change', '.chart_field', function () {
        tableInstance.uploadTable(); // Uploads the table after changing a value
    });

    // Update values on table when clicking 'Done' TODO: Visualize upload
    $('#done').click(function (e) {
        e.preventDefault();  // Prevent default behavior for buttons
        tableInstance.uploadTable(); // Uploads the table after changing a value
    });
});