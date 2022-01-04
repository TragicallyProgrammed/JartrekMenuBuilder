/* EVENT MANAGER */
$(function() {
    var tableInstance = new Table();
    tableEventManager(tableInstance);

    user_manager(tableInstance);

    // Start with admin's beer table
    tableInstance.loadTable("tab-content-1", document.getElementById("current_user").innerHTML); // Load table under beer tab
    $('input[name="tab-group"]:not(:checked)').each(function(index, item) { // Select every tab not currently selected
        document.getElementById(item.getAttribute("for")).style.display = 'none'; // Disable it
    });

    //On tab change
    $('input[name="tab-group"]').change(function () { // Selecting all tabs and looking for them to change
        var current_user = document.getElementById("current_user").innerHTML;
        tableInstance.uploadTable(current_user); // Uploads table to currently logged-in user's database
        tableInstance.loadTable($(this).attr("for"), current_user); // Download currently logged-in user's selected table
    });

    // Update values on table
    $('.datatable').on('change', '.chart_field', function () {
        var current_user = document.getElementById("current_user").innerHTML;  // Get currently selected user
        tableInstance.uploadTable(current_user); // Uploads the table after changing a value
    });

    // Update values on table when clicking 'Done' TODO: Visualize upload
    $('#done').click(function (e) {
        e.preventDefault();  // Prevent default behavior for buttons
        var current_user = document.getElementById("current_user").innerHTML;  // Get currently selected user
        tableInstance.uploadTable(current_user); // Uploads the table after changing a value
    });
});