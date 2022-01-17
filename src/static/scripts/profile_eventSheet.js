/* EVENT MANAGER */
$(function() {
    var tableInstance = new Table(current_user=document.getElementById("username").innerHTML.valueOf());
    tableEventManager(tableInstance);
});