/*TABLE CLASSES*/
class Table {
    /*CONSTRUCTOR*/
    constructor(current_user=null, tableName = "", colLen = 1, labels = new Array(8), items = [], completed=false, modifiers=[]) {
        this.current_user = current_user;
        this.tableName = tableName;
        this.colLen = colLen;
        this.labels = labels;
        this.items = items;
        this.modifiers = modifiers;
        this.parentElementID = null;

        //Table Template Elements
        this.html_tabs = document.getElementsByClassName("tab_group");
        this.tableContainer = null;
        this.tableElement = null;
        this.headerRow = null;
        this.itemLabelColumn = null;
        this.itemLabel = null;
        this.priceLabelColumns = new Array(8);
        this.priceLabels = new Array(8);
        this.completed = completed;
        this.selected_item = null;

        this.generateNewHTMLTable();

        // Generate Table Structure
        this.structureHTMLTable();

        //Load default label array
        this.labels[0] = "Regular";

        //Load events
        this.staticTableEvents();
    }
    /*CONSTRUCTOR*/

    /*METHODS*/
    staticTableEvents() {
        let tableInstance = this;
        //Change tabs
        $('input[name="tab-group"]').change(function () { // Selecting all tabs and looking for them to change
            //Display current tab
            $('input[name="tab-group"]:not(:checked)').each(function (index, tab) { // Selects all tabs not selected
                document.getElementById(tab.getAttribute("for")).style.display = "none"; // Disables that tab
            });
            let tab = document.getElementById(this.getAttribute('for')); // Gets the div for currently selected tab
            tab.style.display = 'block'; // Enables that div

            tableInstance.updateTable();
            tableInstance.loadTable($(this).attr("for"));
        });

        // Search Bar
        $('#data_table_search_bar').on("keyup", function(event) {
            let rows = $('#tableID').children("tr");
            for(let i = 1; i < rows.length; i++) {
                let cells = $(rows[i]).children("td");
                let cell_text = $(cells[1]).children()[0].value
                if(!cell_text.includes(this.value)) {
                    rows[i].style.display = "none";
                }
                else {
                    rows[i].style.display = "";
                }
            }
        });

        //Add row
        $('#add_row').on("click", function () { // Selects add row button
            tableInstance.addItem({label: "", prices: []}); // Calls addItem from table to append new row
        });

        //Confirmation box event
        $('#confirmation_box').change(function(e) {
            e.preventDefault();
            if($(this).is(":checked")){
                $(this).parent().css("background-color", "lime");
                tableInstance.setCompleted(true);
            }
            else {
                $(this).parent().css("background-color", "red");
                tableInstance.setCompleted(false);
            }
            tableInstance.updateTable();
        });

        //Modifier Button
        $('#minmax_button').on('click', function(event) {
            if($(this).attr("state") === "max") {
                $('#modifier_panel').css("display", "none");
                $(this).attr("state", "min");
            }
            else if($(this).attr("state") === "min") {
                $('#modifier_panel').css("display", "flex");
                $(this).attr("state", "max");
            }
        });

        // Modifier Panel
        $('#modifier_panel').draggable();
        $('#modifier_header').on('mouseenter', function(event) {
            $('#modifier_panel').draggable("option", "disabled", false);
        });
        $('#modifier_header').on('mouseleave', function(event) {
            $('#modifier_panel').draggable("option", "disabled", true);
        });

        //Add Modifier Category
        $('#add_modifier_type').on('click', function(event) {
            tableInstance.addModifierCategory();
        });
    }
    //Returns current name of table
    getPriceLabels() {
        return this.labels;
    }
    getItems() {
        return this.items;
    }

    changeCurrentUser(username) {
        this.current_user = username;
    }

    setCompleted(value) {
        this.completed = value;
    }

    //Changes the label of an existing price column
    renamePriceLabel(index, label) {
        if(label === "") {
            if (index >= 0 && index < this.colLen) {
                this.labels[index] = label;
                this.removeColumn(index);
            }
        } else {
            if (index > 0 && index < this.colLen) {
                this.labels[index] = label;
                this.priceLabelColumns[index].setAttribute("enabled", "true");
                this.priceLabels[index].value = label;
            } else if(index >= this.colLen) {
                this.colLen += 1;
                this.labels[index] = label;
                this.priceLabelColumns[index].setAttribute("enabled", "true");
                this.priceLabels[index].value = label;
            }
        }
        this.updateTableGraphics()
    }

    //Changes the price of a given cell
    changeItemPrice(priceIndex, itemIndex, value) {
        this.items[itemIndex]["prices"][priceIndex] = value;
    }

    //Changes the label of a given item
    renameItemPrice(itemIndex, value) {
        this.items[itemIndex]["label"] = value;
    }

    //Adds a new row into the table
    addItem(item) {
        this.items.push(item);

        this.addHTMLTableRow(item);
        
        this.updateTableGraphics();
    }

    //Removes a row
    removeItem() {
        if (this.items.length > 1) {
            // Path syntax is such to be compatible with firefox
            let path = event.path || (event.composedPath && event.composedPath());
            let tableInstance = this;
            if(path){
                $.ajax({
                    contentType: 'json',
                    data: JSON.stringify({
                        'username': this.current_user,
                        'tableName': this.tableName,
                        'itemName': this.getItems()[path[2].rowIndex - 1]["label"]
                    }),
                    type: 'POST',
                    url: 'remove_item',
                    statusCode: {
                        200: function() {
                            console.log("status 200");
                            //Remove from local array
                            tableInstance.items.splice(path[2].rowIndex - 1, 1);
                            //Remove HTML Table Row
                            path[2].parentNode.removeChild(path[2]);
                        },
                        500: function() {
                            console.log("status 500");
                        }
                    }
                });
            }
        }
    }

    //Selects a row
    selectRow(new_row) {
        if (this.selected_item != null) {
            this.selected_item.style.backgroundColor = "white";
        }
        this.selected_item = new_row;
        this.selected_item.style.backgroundColor = "#00E3FF";

        document.getElementById("item_name").innerHTML = this.items[Number(this.selected_item.getAttribute("row_index"))].label;
        this.getItemModifiers();
    }

    //Updates database with current table
    updateTable() {
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': this.current_user,
                'tableName': this.tableName
            }),
            type: 'POST',
            url: 'update-table'
        });
    }

    //Updates database with current column labels
    updateColumns() {
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': this.current_user,
                'tableName': this.tableName,
                'priceLabelsLength': this.colLen,
                'priceLabels': this.getPriceLabels()
            }),
            type: 'POST',
            url: 'update-columns'
        });
    }

    //Updates item label in database
    updateItemLabel(prev_label, current_label) {
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': this.current_user,
                'tableName': this.tableName,
                'prevItemName': prev_label,
                'currentItemName': current_label
            }),
            type: 'POST',
            url: 'update-item-label'
        });
    }

    //Update item prices in database
    updateItemPrices(item_name, item_prices) {
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': this.current_user,
                'tableName': this.tableName,
                'itemName': item_name,
                'itemPrices': item_prices
            }),
            type: 'POST',
            url: 'update-item-prices'
        });
    }

    //Downloads table from database
    downloadTable() {
        console.log("Downloading table with user: " + this.current_user)
        let table_instance = this;  // Get current instance of the class
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': this.current_user,
                'tableName': this.tableName,
                'priceLabelsLength': this.colLen,
                'priceLabels': this.getPriceLabels()
            }),
            type: 'POST',
            url: 'getdb',
            success: function(data) {
                let price_labels = data["price_labels"];
                let items = data["items"];

                table_instance.setCompleted(data["completed"]);

                if(price_labels.length === 0) {
                    table_instance.colLen = 1;
                    table_instance.renamePriceLabel(0, "Regular");
                } else {
                    table_instance.colLen = price_labels.length;
                    for(let i = 0; i < price_labels.length; i++) {
                        table_instance.renamePriceLabel(i, price_labels[i]);
                    }
                }

                if(items.length === 0) {
                    table_instance.addItem({label: "", prices: []});
                } else {
                    for(let i = 0; i < items.length; i++) {
                        table_instance.addItem({label: items[i]["label"], prices: items[i]["prices"]});
                    }
                }
            },
            error: function(data) {
                alert("ERROR OCCURRED WHILE LOADING TABLE!!!!");
                console.log(data);
            }
        });
    }

    //Clears the table, places it under the specified HTML element, and loads data from server-side database
    loadTable(tabID) {
        console.log("loading table with user: " + this.current_user)
        //Place on document
        if (this.parentElementID != null) {
            this.clearTable();
        }
        this.parentElementID = tabID;
        document.getElementById(this.parentElementID).appendChild(this.tableContainer);

        let parentTabId = document.getElementById(this.parentElementID).getAttribute("for");
        let tab_labels = document.getElementsByClassName("tab-label");
        for (let i = 0; i < tab_labels.length; i++) {
            if (tab_labels[i].htmlFor === parentTabId) {
                this.tableName = tab_labels[i].children[0].innerHTML;
                break;
            }
        }

        //get table data from database
        this.downloadTable(this.current_user);
        this.updateTableGraphics();
    }

    //Clears the current data in the table, and removes all columns and rows from the HTML table
    clearTable() {
        //Clearing table data
        this.tableName = "";
        this.labels = new Array(8);
        this.labels[0] = "Regular";
        this.items = [];

        //Clearing HTML table
        while (document.getElementById(this.parentElementID).firstChild) {
            document.getElementById(this.parentElementID).removeChild(document.getElementById(this.parentElementID).firstChild);
        }
        this.clearModifierPanel();
        this.generateNewHTMLTable();
        this.structureHTMLTable();
    }

    //Clear the modifier panel
    clearModifierPanel() {
        $('#item_name').value = "";
        this.modifiers = [];

        let container = document.getElementById("modifier_panel_container");
        while(container.firstChild) {
            container.removeChild(container.firstChild);
        }
    }

    //Prints the table to the console
    printTable() {
        console.log("---------TABLE---------");
        console.log("Username: " + this.current_user);
        console.log(this.tableName);
        console.log("Num Columns: " + this.colLen);
        console.log("Num Rows: " + this.items.length);
        console.log("Columns: " + this.labels);
        for (let i = 0; i < this.items.length; i++) {
            console.log(this.items[i]["label"] + ": " + this.items[i]["prices"]);
        }
        for (let i = 0; i < this.modifiers.length; i++) {
            let category = this.modifiers[i]["category"];
            let modifiers = this.modifiers[i]["modifier_list"];

            console.log("Modifier Category: " + category)
            for (let j = 0; j < modifiers.length; j++) {
                console.log(modifiers[j]["label"] + ": " + modifiers[j]["price"]);
            }
        }
        console.log("---------TABLE---------");
    }
    /*METHODS*/

    /*HTML TABLE HELPERS*/
    //Adds a new row to the HTML Table
    addHTMLTableRow(item) {
        let tableInstance = this;

        let row = this.tableElement.insertRow(-1);
        row.setAttribute("row_index", String(this.tableElement.rows.length-2));
        this.selectRow(row);

        let cell0 = row.insertCell(-1);
        let del_button = document.createElement("img");
        del_button.src = "static/images/delete.png";
        del_button.className = "delete_row";
        del_button.alt = "Delete Row Icon";
        del_button.addEventListener("click", (event) => this.removeItem());
        cell0.appendChild(del_button);

        let cell1 = row.insertCell(-1);
        cell1.addEventListener("click", function (event) {
            tableInstance.selectRow(row);
        });
        let item_cell = document.createElement("textarea");
        item_cell.className = "chart_field item_label";
        item_cell.placeholder = "Item";
        item_cell.maxLength = 32;
        item_cell.wrap = "hard";
        item_cell.setAttribute("row_index", String(this.tableElement.rows.length-2));
        item_cell.addEventListener('change', function(event){
            event.preventDefault();

            let prev_label = tableInstance.getItems()[this.getAttribute("row_index")]['label']

            tableInstance.renameItemPrice(this.getAttribute("row_index"), this.value);

            tableInstance.updateTableGraphics();

            tableInstance.updateItemLabel(prev_label, this.value);

            tableInstance.printTable();
        });
        if(item["label"] !== "") {
            item_cell.value = item["label"];
        }
        cell1.appendChild(item_cell);

        for (let i = 2; i < (this.tableElement.rows[0].cells.length + 1); i++) {
            let celli = row.insertCell(-1);
            let datas = document.createElement("textarea");
            datas.className = "chart_field item_price";
            datas.placeholder = "$-";
            datas.rows = 2;
            datas.cols = 14;
            datas.maxLength = 6;
            datas.setAttribute("column_index", String((i-1)));
            datas.setAttribute("row_index", String(this.tableElement.rows.length-2));
            datas.addEventListener('change', function(event){
                tableInstance.changeItemPrice(this.getAttribute("column_index")-1, this.getAttribute("row_index"), this.value);

                tableInstance.updateTableGraphics();

                tableInstance.updateItemPrices(tableInstance.getItems()[this.getAttribute("row_index")]["label"], tableInstance.getItems()[this.getAttribute("row_index")]["prices"]);

                tableInstance.printTable();
            });
            datas.addEventListener('keydown', function(event) {
                console.log(event.keyCode);
                if((!(47 < event.keyCode && event.keyCode < 58)) && (!(95 < event.keyCode && event.keyCode < 106)) && (!(event.keyCode === 110 || event.keyCode === 190 || event.keyCode === 8))) {
                    console.log("not allowed value");
                    event.preventDefault();
                }
            });

            if(i-2 < item["prices"].length) {
                datas.value = item["prices"][i-2];
            }

            celli.addEventListener("click", function (event) {
                tableInstance.selectRow(row);
            });

            celli.appendChild(datas);
        }
    }
    
    //Removes a column from the HTML table
    removeColumn(index) {
        for(let i = index; i < this.colLen; i++) {
            if(i < this.colLen-1){
                console.log("i: ", i);
                console.log(this.priceLabels[Number(i)+Number(1)].value);
                this.priceLabels[i].value = this.priceLabels[Number(i)+Number(1)].value;
                this.labels[i] = this.priceLabels[i].value;
                for(let j = 1; j < this.items.length+1; j++) {
                    let cell = this.tableElement.rows[j].cells[Number(i)+Number(2)];
                    let next_column_cell = this.tableElement.rows[j].cells[Number(i)+Number(3)];
                    cell.firstChild.value = next_column_cell.firstChild.value;
                }
            } else {
                this.priceLabels[i].value = "";
                this.labels[i] = this.priceLabels[i].value;
                this.priceLabelColumns[i].setAttribute("enabled", false);
                for(let j = 1; j < this.items.length+1; j++) {
                    let cell = this.tableElement.rows[j].cells[Number(i) + Number(2)];
                    cell.firstChild.value = "";
                }
            }
        }
        this.colLen -= 1;
    }

    //Updates the shading on the table
    updateTableGraphics() {
        //Update completion box
        if(this.completed === true) {
            $('#confirmation_box').prop("checked", true).change();
        }
        else {
            $('#confirmation_box').prop("checked", false).change();
        }
        //Setting enabled attribute
        for(let i = 0; i < this.priceLabelColumns.length; i++) {
            if(this.priceLabelColumns[i].getAttribute("enabled") === "true"){
                this.priceLabelColumns[i].style.background = "none";
                this.priceLabels[i].style.background = "none";
                for(let j = 1; j < this.items.length+1; j++) {
                    let cell = this.tableElement.rows[j].cells[i+2];
                    cell.style.background = "none";
                    cell.firstChild.style.background = "none";
                    cell.firstChild.getAttribute("readonly") === "readonly" && cell.firstChild.removeAttribute("readonly");
                }
            } else {
                if(this.priceLabelColumns[i-1].getAttribute("enabled") === "true"){
                    this.priceLabelColumns[i].style.background = "none";
                    this.priceLabels[i].style.background = "none";
                    this.priceLabels[i].getAttribute("readonly") === "readonly" && this.priceLabels[i].removeAttribute("readonly");
                } else {
                    this.priceLabelColumns[i].style.background = "grey";
                    this.priceLabels[i].style.background = "grey";
                    this.priceLabels[i].setAttribute("readonly", "readonly");
                }
                for(let j = 1; j < this.items.length+1; j++) {
                    let cell = this.tableElement.rows[j].cells[i+2];
                    cell.style.background = "grey";
                    cell.firstChild.style.background = "grey";
                    cell.firstChild.setAttribute("readonly", "readonly");
                }
            }
        }
    }

    //Generates the base HTML Table
    generateNewHTMLTable() {
        this.tableContainer = document.createElement("div");
        this.tableContainer.id = "table_container"

        this.tableElement = document.createElement("table");
        this.tableElement.setAttribute("name", "table_panel");
        this.tableElement.id = "tableID";
        this.tableElement.className = "datatable";

        this.headerRow = document.createElement("tr");
        this.headerRow.id = "header_row";

        this.itemLabelColumn = document.createElement("th");
        this.itemLabelColumn.setAttribute("colspan", "2");

        this.itemLabel = document.createElement("label");
        this.itemLabel.innerHTML = "Item";

        this.priceLabelColumns[0] = document.createElement("th");
        this.priceLabelColumns[0].setAttribute("enabled", "true");

        this.priceLabels[0] = document.createElement("label");
        this.priceLabels[0].innerHTML = "Regular";

        let tableInstance = this;
        for(let i = 1; i < 8; i++) {
            this.priceLabelColumns[i] = document.createElement("th");
            this.priceLabelColumns[i].setAttribute("enabled", "false");

            this.priceLabels[i] = document.createElement("textarea");
            this.priceLabels[i].className = "chart_field price_label";
            this.priceLabels[i].setAttribute("placeholder", "Price Label");
            this.priceLabels[i].maxLength = "14";
            this.priceLabels[i].rows = 1;
            this.priceLabels[i].cols = 14;
            this.priceLabels[i].setAttribute("column_index", String(i));
            this.priceLabels[i].addEventListener('change', function(event){
                event.preventDefault();

                tableInstance.renamePriceLabel(this.getAttribute("column_index"), this.value);

                tableInstance.updateTableGraphics();

                tableInstance.updateColumns();

                tableInstance.printTable();
            });
        }
    }

    //Structures all elements in the HTML Table
    structureHTMLTable() {
        this.tableContainer.appendChild(this.tableElement);
        
        this.tableElement.appendChild(this.headerRow);

        this.headerRow.appendChild(this.itemLabelColumn);
        this.itemLabelColumn.appendChild(this.itemLabel);
        
        for(let i = 0; i < 8; i++) {
            this.headerRow.appendChild(this.priceLabelColumns[i]);
            this.priceLabelColumns[i].appendChild(this.priceLabels[i]);
        }
    }
    /*HTML TABLE HELPERS*/

    /*MODIFIER HELPERS*/
    //Add a category under modifiers panel
    addModifierCategory(label="", modifiers_list=[]) {
        let tableInstance = this;

        let modifier_panel_container = document.getElementById("modifier_panel_container");

        let modifier_dropdown = document.createElement("div");
        modifier_dropdown.className = "dropdown_container";

        let dropdown_header = document.createElement("div");
        dropdown_header.className = "dropdown_header";
        dropdown_header.style.marginBottom = "0px";
        let dropdown_button = document.createElement("button")
        dropdown_button.className = "dropdown_button";
        dropdown_button.innerHTML = "\u21D3";
        dropdown_button.setAttribute("for", "dropdown_"+String(this.modifiers.length));
        dropdown_button.addEventListener("click", function(event) {
            event.preventDefault();
            if(dropdown_content.style.display === "flex") {
                this.innerHTML = "\u21D2";
                dropdown_content.style.display = "none";
                dropdown_header.style.borderBottomRightRadius = "5px";
                dropdown_header.style.borderBottomLeftRadius = "5px";
            }
            else if(dropdown_content.style.display === "none") {
                this.innerHTML = "\u21D3";
                dropdown_content.style.display = "flex";
                dropdown_header.style.borderBottomRightRadius = "0";
                dropdown_header.style.borderBottomLeftRadius = "0";
            }
        });

        let category_label = document.createElement("textarea");
        category_label.className = "category_label";
        category_label.setAttribute("for", "dropdown_"+String(this.modifiers.length));
        category_label.placeholder = "Category";
        category_label.addEventListener("change", function(event) {
            let prev_label = tableInstance.modifiers[this.getAttribute("for").charAt(this.getAttribute("for").length-1)].category;
            tableInstance.modifiers[this.getAttribute("for").charAt(this.getAttribute("for").length-1)].category = this.value;

            tableInstance.updateModifierCategory(prev_label, this.value);
        });
        category_label.value = label;

        let delete_button = document.createElement("img");
        delete_button.className = "modifier_delete";
        delete_button.src = "static/images/delete.png";
        delete_button.style.width = "40px";
        delete_button.style.background = "none";
        delete_button.addEventListener("click", function(event) {
            if(confirm("!!WARNING!!\nDeleting a Modifier Category will PERMANENTLY DELETE ALL MODIFIERS FOUND UNDER IT! Only Continue if you are sure.")) {
                console.log("Confirmed Yes!")
                tableInstance.removeCategory(category_label.value);

                while(dropdown_content.firstChild) {
                    dropdown_content.firstChild.remove();
                }
                dropdown_content.remove();
                while(modifier_dropdown.firstChild) {
                    modifier_dropdown.firstChild.remove();
                }
                modifier_dropdown.remove();
            }
            else {
                console.log("Confirmed No!")
            }
        });

        dropdown_header.appendChild(dropdown_button);
        dropdown_header.append(category_label);
        dropdown_header.appendChild(delete_button);

        let dropdown_content = document.createElement("div");
        dropdown_content.className = "dropdown_content";
        dropdown_content.id = "dropdown_"+String(this.modifiers.length);
        dropdown_content.style.display = "flex";
        dropdown_content.style.marginTop = "0px";

        let add_modifier_button = document.createElement("button");
        add_modifier_button.className = "add_modifier";
        add_modifier_button.innerHTML = "&#x2b;";
        add_modifier_button.setAttribute("for", "dropdown_"+String(this.modifiers.length));
        add_modifier_button.addEventListener("click", function(event) {
            tableInstance.addModifier(this.getAttribute("for"));
        });

        modifier_panel_container.appendChild(modifier_dropdown);
        modifier_dropdown.appendChild(dropdown_header);
        modifier_dropdown.appendChild(dropdown_content);
        dropdown_content.appendChild(add_modifier_button);

        this.modifiers.push({category: "", modifier_list: []});
        if(modifiers_list.length > 0) {
            for(let i = 0; i < modifiers_list.length; i++) {
                this.addModifier(dropdown_content.id, modifiers_list[i]["label"], modifiers_list[i]["price"])
            }
        }
    }

    //Add a modifier to a category
    addModifier(modifier_category_id, mod_label="", mod_price=0.0) {
        let tableInstance = this;
        let dropdown_container = document.getElementById(modifier_category_id);

        let modifier_container = document.createElement("div");
        modifier_container.className = "modifier_container"
        modifier_container.setAttribute("for", modifier_category_id);
        modifier_container.setAttribute("index", String(this.modifiers[modifier_category_id.charAt(modifier_category_id.length-1)].modifier_list.length));

        let delete_button = document.createElement("img");
        delete_button.className = "modifier_delete";
        delete_button.src = "static/images/delete.png";
        delete_button.style.width = "30px";
        delete_button.style.background = "none";
        delete_button.addEventListener("click", function(event) {
            let index = modifier_container.getAttribute("for").charAt(modifier_container.getAttribute("for").length-1);
            tableInstance.removeModifier(tableInstance.modifiers[index].category, tableInstance.modifiers[index].modifier_list[modifier_container.getAttribute("index")].label);

            while (modifier_container.firstChild) {
                modifier_container.firstChild.remove();
            }
            modifier_container.remove();

            if (dropdown_container.children.length > 1) {
                for (let i = 0; i < dropdown_container.children.length; i++) {
                    dropdown_container.children[i].setAttribute("index", String(Number(dropdown_container.children[i].getAttribute("index")) - Number(1)));
                }
            }
        });

        let modifier_label_container = document.createElement("div");
        modifier_label_container.className = "modifier_label_container";
        modifier_label_container.style.margin = "0";

        let modifier_label = document.createElement("textarea");
        modifier_label.className = "modifier_label";
        modifier_label.placeholder = "modifier";
        modifier_label.style.margin = "0";
        modifier_label.addEventListener("change", function(event) {
            let index = modifier_container.getAttribute("for").charAt(modifier_container.getAttribute("for").length-1);
            let prev_label = tableInstance.modifiers[index].modifier_list[modifier_container.getAttribute("index")].label;
            tableInstance.modifiers[index].modifier_list[modifier_container.getAttribute("index")].label = this.value;

            tableInstance.updateItemModifier(tableInstance.modifiers[index].category, modifier_label.value, this.value, prev_label);
        });
        modifier_label.value = mod_label;
        modifier_label_container.appendChild(modifier_label);

        let modifiers_dropdown = document.createElement("button");
        modifiers_dropdown.className = "modifiers_dropdown";
        modifiers_dropdown.innerHTML = "\u21D3";
        modifiers_dropdown.style.margin = "0";
        modifier_label_container.appendChild(modifiers_dropdown);

        let modifier_price = document.createElement("textarea");
        modifier_price.className = "modifier_price";
        modifier_price.placeholder = "$-";
        modifier_price.addEventListener("change", function(event) {
            let index = modifier_container.getAttribute("for").charAt(modifier_container.getAttribute("for").length-1);
            tableInstance.modifiers[index].modifier_list[this.parentElement.getAttribute("index")].price = Number(this.value);

            tableInstance.updateItemModifier(tableInstance.modifiers[index].category, modifier_label.value, this.value);
        });
        modifier_price.value = mod_price;

        let colon = document.createElement("label");
        colon.innerHTML = ":";

        dropdown_container.insertBefore(modifier_container, dropdown_container.lastChild);
        modifier_container.appendChild(delete_button);
        modifier_container.appendChild(modifier_label_container);
        modifier_container.appendChild(colon);
        modifier_container.appendChild(modifier_price);

        this.modifiers[modifier_category_id.charAt(modifier_category_id.length-1)].modifier_list.push({label: mod_label, price: mod_price});
    }

    //Updates modifier category
    updateModifierCategory(prev_category, current_category) {
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': this.current_user,
                'prevModifierCategory': prev_category,
                'currentModifierCategory': current_category
            }),
            url: 'update-category',
            method: 'POST'
        });
    }

    //Updates item's modifiers to database
    updateItemModifier(category, current_label, price, prev_label=null) {
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': this.current_user,
                'tableName': this.tableName,
                'itemName': this.items[Number(this.selected_item.getAttribute("row_index"))].label,
                'modifierCategory': category,
                'prevModifierName': prev_label,
                'currentModifierName': current_label,
                'modifierPrice': price
            }),
            url: 'update-modifier',
            method: 'POST'
        });
    }

    //Get item's modifier's from the database
    getItemModifiers() {
        let tableInstance = this;
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': this.current_user,
                'tableName': this.tableName,
                'itemName': this.items[Number(this.selected_item.getAttribute("row_index"))].label
            }),
            success: function(data) {
                tableInstance.clearModifierPanel();

                let categories = data["categories"];
                let modifiers = data["modifiers"];
                for (let i = 0; i < categories.length; i++) {
                    let mods = []
                    for (let j = 0; j < modifiers.length; j++) {
                        mods.push(modifiers[j]);
                    }
                    tableInstance.addModifierCategory(categories[i], mods);
                }
            },
            url: 'get-modifiers',
            type: 'POST'
        });
    }

    //Remove modifier category
    removeCategory(category) {
        $.ajax({
            contentType: 'JSON',
            data: JSON.stringify({
                'username': this.current_user,
                'modifierCategory': category
            }),
            url: 'remove-category',
            type: 'POST'
        });
    }

    //Remove a given modifier
    removeModifier(category, modifier) {
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': this.current_user,
                'tableName': this.tableName,
                'itemName': this.items[Number(this.selected_item.getAttribute("row_index"))].label,
                'modifierCategory': category,
                'modifierLabel': modifier
            }),
            url: 'remove-modifier',
            type: 'POST'
        });
    }
    /*MODIFIER HELPERS*/
}
