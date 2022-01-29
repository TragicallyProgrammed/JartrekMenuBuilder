/* EVENT MANAGER */
function tableEventManager(tableInstance) {
    $(function () {
        //Attributes
        let drink_div = document.getElementById("drink_div");
        let food_div = document.getElementById("food_div");
        let modifier_button = document.getElementById("modifier_button");
        let lastDrinkTab = $('input[id="tab-1"]');
        let lastFoodTab = $('input[id="tab2-1"]');

        /* On Fist Load */
        food_div.checked = false;
        drink_div.checked = true;


        // Start with beer
        tableInstance.loadTable("tab-content-1"); // Load table under beer tab
        $('input[name="tab-group"]:not(:checked)').each(function(index, item) { // Select every tab not currently selected
            document.getElementById(item.getAttribute("for")).style.display = 'none'; // Disable it
        });

        /* EVENTS */
        // Select 'Drinks'
        $('#drink').change(function () {
            drink_div.style.display = "block"; // Enables drink div
            food_div.style.display = "none"; // Disables food div
            modifier_button.style.display = "none";

            lastFoodTab = $('input[name="tab-group"]:checked'); // Saves selected tab under food div
            lastDrinkTab.prop("checked", true).change(); // enables previously selected tab under drink div
        });
        // Select 'Food'
        $('#food').change(function () {
            drink_div.style.display = "none"; // Disables drink div
            food_div.style.display = "block"; // Enables food div
            modifier_button.style.display = "block";

            lastDrinkTab = $('input[name="tab-group"]:checked'); // Saves previously selected tab under drink div
            lastFoodTab.prop("checked", true).change(); // enables previously selected tab under food div
        });
    });
}