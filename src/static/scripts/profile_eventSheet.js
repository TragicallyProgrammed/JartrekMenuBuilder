/* EVENT MANAGER */
$(function() {
    var tableInstance = new Table(current_user=document.getElementById("current_user").innerHTML.valueOf());
    tableEventManager(tableInstance);
});