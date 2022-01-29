/* EVENT MANAGER */
$(function() {
    var tableInstance = new Table(current_user=document.getElementById("username").innerHTML.valueOf());
    tableEventManager(tableInstance);

    $('.content').on("keypress", function(event) {
        console.log(event.key);
        if (event.key === " ") {
            console.log("Getting modifiers...");
            tableInstance.getItemModifiers();
        }
    });
});