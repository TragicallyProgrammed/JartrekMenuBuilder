/* EVENT MANAGER */
function tableEventManager(tableInstance) {
    $(function () {
        //Attributes
        var drink_div = document.getElementById("drink_div");
        var food_div = document.getElementById("food_div");
        var lastDrinkTab = $('input[id="tab-1"]');
        var lastFoodTab = $('input[id="tab2-1"]');

        /* On Fist Load */
        food_div.checked = false;
        drink_div.checked = true;

        /* EVENTS */
        // Select 'Drinks'
        $('#drink').change(function () {
            drink_div.style.display = "block"; // Enables drink div
            food_div.style.display = "none"; // Disables food div

            lastFoodTab = $('input[name="tab-group"]:checked'); // Saves selected tab under food div
            lastDrinkTab.prop("checked", true).change(); // enables previously selected tab under drink div
        });
        // Select 'Food'
        $('#food').change(function () {
            drink_div.style.display = "none"; // Disables drink div
            food_div.style.display = "block"; // Enables food div

            lastDrinkTab = $('input[name="tab-group"]:checked'); // Saves previously selected tab under drink div
            lastFoodTab.prop("checked", true).change(); // enables previously selected tab under food div
        });

        //On tab change
        $('input[name="tab-group"]').change(function () { // Selecting all tabs and looking for them to change
            //Display current tab
            $('input[name="tab-group"]:not(:checked)').each(function (index, tab) { // Selects all tabs not selected
                document.getElementById(tab.getAttribute("for")).style.display = "none"; // Disables that tab
            });
            var tab = document.getElementById(this.getAttribute('for')); // Gets the div for currently selected tab
            tab.style.display = 'block'; // Enables that div
        });

        //Add Row
        $('#add_row').on("click", function () { // Selects add row button
            tableInstance.addItem(new Item("", this.colLen, [])); // Calls addItem from table to append new row
        });
    });
}