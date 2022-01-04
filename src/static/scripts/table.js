/*TABLE CLASSES*/
class Table {
    /*CONSTRUCTOR*/
    constructor(tableName = "", colLen = 1, labels = new Array(8), items = []) {
        this.tableName = tableName;
        this.colLen = colLen;
        this.labels = labels;
        this.items = items;
        this.parentElementID = null;

        //Table Template Elements
        this.tableContainer = null;
        this.tableElement = null;
        this.headerRow = null;
        this.itemLabelColumn = null;
        this.itemLabel = null;
        this.priceLabelColumns = new Array(8);
        this.priceLabels = new Array(8);

        this.generateNewHTMLTable();

        //Table Structure
        this.structureHTMLTable();

        //Load label array
        this.labels[0] = "Regular";

        //Update graphics
        this.updateTableGraphics();
    }
    /*CONSTRUCTOR*/

    /*METHODS*/
    //Returns current name of table
    getPriceLabels() {
        return this.labels;
    }
    getItems() {
        var ret = [];
        for(var i = 0; i < this.items.length; i++) {
            var dict = {
                label: this.items[i].getLabel(),
                prices: this.items[i].getPrices()
            };
            ret.push(dict);
        }
        return ret;
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
        this.items[itemIndex].setPrice(priceIndex, value);
    }

    //Changes the label of a given item
    renameItemPrice(itemIndex, value) {
        this.items[itemIndex].setLabel(value);
    }

    //Adds a new row into the table
    addItem(item) {
        this.items.push(item);

        this.addHTMLTableRow(item);
        
        this.updateTableGraphics();
    }

    //Removes a row
    removeItem(username=null) {
        if (this.items.length > 1) {
            // Path syntax is such to be compatible with firefox
            var path = event.path || (event.composedPath && event.composedPath());
            var tableInstance = this;
            if(path){
                $.ajax({
                    contentType: 'json',
                    data: JSON.stringify({
                        'username': username,
                        'tableName': this.tableName,
                        'itemName': this.getItems()[path[2].rowIndex - 1].label
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

    //Uploads table to database
    uploadTable(username=null) {
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': username,
                'tableName': this.tableName,
                'priceLabelsLength': this.colLen,
                'priceLabels': this.labels,
                'items': this.getItems()
            }),
            type: 'POST',
            url: 'updatedb'
        });
    }

    //Downloads table from database
    downloadTable(username = null) {
        console.log("Downloading table with user: " + username)
        var table_instance = this;  // Get current instance of the class
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': username,
                'tableName': this.tableName,
                'priceLabelsLength': this.colLen,
                'priceLabels': this.getPriceLabels(),
            }),
            type: 'POST',
            url: 'getdb',
            success: function(data) {
                var price_labels = data["price_labels"];
                var items = data["items"];

                if(price_labels.length === 0) {
                    table_instance.colLen = 1;
                    table_instance.renamePriceLabel(0, "Regular");
                } else {
                    table_instance.colLen = price_labels.length;
                    for(var i = 0; i < price_labels.length; i++) {
                        table_instance.renamePriceLabel(i, price_labels[i]);
                    }
                }

                if(items.length === 0) {
                    table_instance.addItem(new Item("", table_instance.colLen, []))
                } else {
                    for(var i = 0; i < items.length; i++) {
                        table_instance.addItem(new Item(items[i]["label"], table_instance.colLen, items[i]["prices"]));
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
    loadTable(tabID, username = null) {
        console.log("loading table with user: " + username)
        //Place on document
        if (this.parentElementID != null) {
            this.clearTable();
        }
        this.parentElementID = tabID;
        document.getElementById(this.parentElementID).appendChild(this.tableContainer);

        var parentTabId = document.getElementById(this.parentElementID).getAttribute("for");
        var tab_labels = document.getElementsByClassName("tab-label");
        for (var i = 0; i < tab_labels.length; i++) {
            if (tab_labels[i].htmlFor === parentTabId) {
                this.tableName = tab_labels[i].children[0].innerHTML;
                break;
            }
        }
        //get table data from database
        this.downloadTable(username);
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
        this.generateNewHTMLTable();
        this.structureHTMLTable();
    }

    //Prints the table to the console
    printTable() {
        console.log(this.tableName);
        console.log("Num Columns: " + this.colLen);
        console.log("Num Rows: " + this.items.length);
        console.log("Columns: " + this.labels);
        for (var i = 0; i < this.items.length; i++) {
            this.items[i].printItem();
        }
    }
    /*METHODS*/

    /*HTML TABLE HELPERS*/
    //Adds a new row to the HTML Table
    addHTMLTableRow(item) {
        var row = this.tableElement.insertRow(-1);
        var cell0 = row.insertCell(-1);
        var del_button = document.createElement("img");
        del_button.src = "static/images/delete.png";
        del_button.className = "delete_row";
        del_button.alt = "Delete Row Icon";
        del_button.addEventListener("click", (event) => this.removeItem());
        cell0.appendChild(del_button);

        var cell1 = row.insertCell(-1);
        var item_cell = document.createElement("textarea");
        item_cell.className = "chart_field item_label";
        item_cell.placeholder = "Item";
        item_cell.maxLength = 32;
        item_cell.wrap = "hard";
        if(item.getLabel() !== "") {
            item_cell.value = item.getLabel();
        }
        cell1.appendChild(item_cell);

        for (var i = 2; i < (this.tableElement.rows[0].cells.length + 1); i++) {
            var celli = row.insertCell(-1);
            var datas = document.createElement("textarea");
            datas.className = "chart_field item_price";
            datas.placeholder = "-";
            datas.rows = 2;
            datas.cols = 14;
            datas.maxLength = 6;
            datas.addEventListener('keydown', function(event){
                if(!isFinite(event.key) && event.key !== "Backspace" && event.key !== ".") {
                    event.preventDefault()
                }
            });

            if(i-2 < item.getPricesLength()) {
                datas.value = item.getPrices()[i-2];
            }

            celli.appendChild(datas);
        }
    }
    
    //Removes a column from the HTML table
    removeColumn(index) {
        for(var i = index; i < this.colLen; i++) {
            if(i < this.colLen-1){
                this.priceLabels[i].value = this.priceLabels[i+1].value;
                this.labels[i] = this.priceLabels[i].value;
                for(var j = 1; j < this.items.length+1; j++) {
                    var cell = this.tableElement.rows[j].cells[i+2];
                    var next_column_cell = this.tableElement.rows[j].cells[i+3];
                    cell.firstChild.value = next_column_cell.firstChild.value;
                }
            } else {
                this.priceLabels[i].value = "";
                this.labels[i] = this.priceLabels[i].value;
                this.priceLabelColumns[i].setAttribute("enabled", false);
                for(var j = 1; j < this.items.length+1; j++) {
                    var cell = this.tableElement.rows[j].cells[i+2];
                    cell.firstChild.value = "";
                }
            }
        }
        this.colLen -= 1;
    }

    //Updates the shading on the table
    updateTableGraphics() {
        //Setting enabled attribute
        for(var i = 0; i < this.priceLabelColumns.length; i++) {
            if(this.priceLabelColumns[i].getAttribute("enabled") === "true"){
                this.priceLabelColumns[i].style.background = "none";
                this.priceLabels[i].style.background = "none";
                for(var j = 1; j < this.items.length+1; j++) {
                    var cell = this.tableElement.rows[j].cells[i+2];
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
                for(var j = 1; j < this.items.length+1; j++) {
                    var cell = this.tableElement.rows[j].cells[i+2];
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

        for(var i = 1; i < 8; i++) {
            this.priceLabelColumns[i] = document.createElement("th");
            this.priceLabelColumns[i].setAttribute("enabled", "false");

            this.priceLabels[i] = document.createElement("textarea");
            this.priceLabels[i].className = "chart_field price_label";
            this.priceLabels[i].setAttribute("placeholder", "Price Label");
            this.priceLabels[i].maxLength = "14";
            this.priceLabels[i].rows = 1;
            this.priceLabels[i].cols = 14;
        }
    }

    //Structures all elements in the HTML Table
    structureHTMLTable() {
        this.tableContainer.appendChild(this.tableElement);
        
        this.tableElement.appendChild(this.headerRow);

        this.headerRow.appendChild(this.itemLabelColumn);
        this.itemLabelColumn.appendChild(this.itemLabel);
        
        for(var i = 0; i < 8; i++) {
            this.headerRow.appendChild(this.priceLabelColumns[i]);
            this.priceLabelColumns[i].appendChild(this.priceLabels[i]);
        }
    }
    /*HTML TABLE HELPERS*/
}

/*ITEM CLASS*/
class Item {
    /*CONSTRUCTOR*/
    constructor(label = "", priceLen = 1, prices = new Array(8)) {
        this.label = label;
        this.priceLen = priceLen;
        this.prices = prices;

        if(prices.length !== 8) {
            for (var i = 0; i < this.priceLen; i++) {
                this.prices[i] = 0.0;
            }
        }
    }
    /*CONSTRUCTOR*/

    /*METHODS*/
    getLabel() {
        return this.label;
    }

    getPrices() {
        return this.prices;
    }

    getPricesLength() {
        return this.priceLen;
    }

    setLabel(label) {
        this.label = label;
    }

    setPrice(index, price) {
        this.prices[index] = price;
    }

    printItem() {
        console.log(this.label + ": [" + this.prices + "]");
    }
}
