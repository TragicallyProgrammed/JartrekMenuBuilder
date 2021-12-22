/*EVENT MANAGER*/
$(function () {
    //Attributes
    var drink_div = document.getElementById("drink_div");
    var food_div = document.getElementById("food_div");
    var lastDrinkTab = $('input[id="tab-1"]');
    var lastFoodTab = $('input[id="tab2-1"]');
    
    food_div.checked = false;
    drink_div.checked = true;

    //On First Load
    var tableInstance = new Table();
    
    //start with Beer selected
    tableInstance.loadTable("tab-content-1");
    $('input[name="tab-group"]:not(:checked)').each(function(index, item) {
            document.getElementById(item.getAttribute("for")).style.display = "none";
    });

    /*EVENTS*/
    //Keep price fields as numbers
    $('.item_price').on("textarea", function() {
        if(isNaN(parseFloat($(this).val(), 10))) {
            this.value  = this.value.slice(0, -1);
        }
    });
    
    //Show Drinks
    $('#drink').change(function () {
        drink_div.style.display = "block";
        food_div.style.display = "none";

        lastFoodTab = $('input[name="tab-group"]:checked');
        lastDrinkTab.prop("checked", true).change();
    });

    //Show Food
    $('#food').change(function () {
        drink_div.style.display = "none";
        food_div.style.display = "block";

        lastDrinkTab = $('input[name="tab-group"]:checked');
        lastFoodTab.prop("checked", true).change();
    });
    
    //On tab change
    $('input[name="tab-group"]').change(function () {
        tableInstance.uploadTable();
        //Loads table under what gets selected
        tableInstance.loadTable($(this).attr("for"));

        //Display current tab
        $('input[name="tab-group"]:not(:checked)').each(function(index, item) {
            document.getElementById(item.getAttribute("for")).style.display = "none";
        });
        var tab = document.getElementById(this.getAttribute('for'));
        tab.style.display = 'block';

        //Event to update values on table
        $('table').on("input", ".chart_field", function () {
            $(this).val($(this).val().replace(/[\r\n\v]+/g, '')); // Filters special characters
            var colIndex = $(this).parent().index();
            var rowIndex = $(this).parent().parent().index();

            if (rowIndex === 0) { //Change Column Label
                tableInstance.renamePriceLabel(colIndex - 1, $(this).val());
            } else { //Change cell in row
                if ((colIndex - 2) === -1) { //Change Item Label
                    tableInstance.renameItemPrice((rowIndex - 1), $(this).val());
                } else { //Change price in row
                    tableInstance.changeItemPrice(colIndex - 2, rowIndex - 1, $(this).val());
                }
            }
            //Updates graphics
            tableInstance.updateTableGraphics();
            console.log("After updating graphics: " + tableInstance.colLen);
            tableInstance.printTable();
        });
    });
    //Event to update values on table
    $('table').on("input", ".chart_field", function () {
        $(this).val($(this).val().replace(/[\r\n\v]+/g, '')); // Filters special characters
        var colIndex = $(this).parent().index();
        var rowIndex = $(this).parent().parent().index();

        if (rowIndex === 0) { //Change Column Label
            tableInstance.renamePriceLabel(colIndex - 1, $(this).val());
        } else { //Change cell in row
            if ((colIndex - 2) === -1) { //Change Item Label
                tableInstance.renameItemPrice((rowIndex - 1), $(this).val());
            } else { //Change price in row
                tableInstance.changeItemPrice(colIndex - 2, rowIndex - 1, $(this).val());
            }
        }
        //Updates graphics
        tableInstance.updateTableGraphics();
        tableInstance.printTable();
    });
    
    //Add Row
    $('#add_row').on("click", function() {
        tableInstance.addItem(new Item("", this.colLen, []));
    });
});
