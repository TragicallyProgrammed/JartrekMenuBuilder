/* EVENT MANAGER */
function MenuTable(initial_user)
{
    let table = new Table(current_user=initial_user)

    /* On Fist Load */
    // Get all tables
    let drink_tables = []
    let food_tables = []
    $.ajax({
        contentType: 'json',
        data: JSON.stringify({
            'username': table.current_user
        }),
        type: 'POST',
        url: 'get-tables',
        success: function(data) {
            let tables = data["tables"]
            for(let i = 0; i < tables.length; i++) {
                if(tables[i]["tableType"] === "drink")
                    drink_tables.push(tables[i])
                else if(tables[i]["tableType"] === "food")
                    food_tables.push(tables[i])
            }
            drink_tables.push({"id": -1, "tableName": "", "tableType": "drink"})
            food_tables.push({"id": -1, "tableName": "", "tableType": "food"})

            let selected_category_id = $('input[name="menu_button"]:checked').attr("id")
            if(selected_category_id === "drink") {
                for(let i = 0; i < drink_tables.length; i++) {
                    addTable(drink_tables[i]["tableName"])
                }
            } else if(selected_category_id === "food") {
                for(let i = 0; i < food_tables.length; i++) {
                    addTable(food_tables[i]["tableName"])
                }
            }
            let value = $($('#tab_button_container').children()[0].children[0]).prop("checked", true).trigger("change")
        }
    })

    // Get all modifiers
    let modifier_categories = []
    $.ajax({
        contentType: 'JSON',
        data: JSON.stringify({
            'username': current_user
        }),
        type: 'POST',
        url: 'get-categories',
        success: function(data) {
            modifier_categories = data["categories"]
            modifier_categories.push({"id": -1, "label": "", "mods": []})
            for(let i = 0; i < modifier_categories.length; i++) {
                modifier_categories[i]["mods"].push({"id": -1, "categoryID": -1, "label": "", "price": ""})
                addModifierCategory(modifier_categories[i])
            }
        }
    })

    /* EVENTS */
    // Select Drinks/Food
    $('input[name="menu_button"]').on("change", function () {
        let modifier_button = $('#modifier_button')
        if(this.id === "food")
            modifier_button.css("display", "")
        else
            modifier_button.css("display", "none")

        clearTables()
        let selected_category_id = $('input[name="menu_button"]:checked').attr("id")
        if(selected_category_id === "drink") {
            for (let i = 0; i < drink_tables.length; i++) {
                addTable(drink_tables[i]["tableName"])
            }
        } else if(selected_category_id === "food") {
            for (let i = 0; i < food_tables.length; i++) {
                addTable(food_tables[i]["tableName"])
            }
        }
        $($('#tab_button_container').children()[0].children[0]).prop("checked", true).trigger("change")
    })

    // Table Tabs
    $('#tab_button_container').on("mousewheel", function(event, delta){ // Horizontal Scroll
        this.scrollLeft += event.originalEvent.deltaY
    }
    ).on("change", 'input[name="tab_group"]',  function () { // Changing tabs
        $(this).parent().css("background", "white").css("z-index", 2)
        $('input[name="tab_group"]:not(:checked)').each(function() {
            $(this).parent().css("background", "lightgray").css("z-index", 1)
        })
        let id = $('input[name="tab_group"]:checked').attr("id")
        $('#tab_content_div').append(table.generateNewHTMLTable())

        let selected_category_id = $('input[name="menu_button"]:checked').attr("id")
        if(selected_category_id === "drink") {
            table.downloadTable(drink_tables[id.substring(id.length - 1)]["id"])
        } else if(selected_category_id === "food") {
            table.downloadTable(food_tables[id.substring(id.length - 1)]["id"])
        }
    }
    ).on("click", '.tab_button', function() { // Click to change to that tab
        let checked_tab = $('input[name="tab_group"]:checked')
        if (this.children[0].id !== checked_tab.prop("id")) {
            checked_tab.prop("checked", false)
            $(this.children[0]).prop("checked", true).trigger("change")
        }
    }
    ).on("change", '.tab_label', function(event){  // Change table label
        let index = Number(this.getAttribute("for").substring(0, "tab-".length))
        let current_table = null

        let selected_category_id = $('input[name="menu_button"]:checked').attr("id")
        if(selected_category_id === "drink") {
            current_table = drink_tables[index]
        } else if(selected_category_id === "food") {
            current_table = food_tables[index]
        }
        current_table["tableName"] = this.value

        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': table.current_user,
                'table': current_table,
                'completed': $('#confirmation_box').is(':checked')
            }),
            type: 'POST',
            url: 'update-table',
            success: function(data) {
                table.tableID = data["id"]
                if(current_table["id"] === -1 && this.value !== ""){
                    if(selected_category_id === "drink") {
                        drink_tables.push({"id": -1, "tableName": "", "tableType": "drink"})
                    } else if(selected_category_id === "food") {
                        food_tables.push({"id": -1, "tableName": "", "tableType": "food"})
                    }
                    addTable()
                }

                if(selected_category_id === "drink") {
                    drink_tables[index]["id"] = data["id"]
                } else if(selected_category_id === "food") {
                    food_tables[index]["id"] = data["id"]
                }

                for(let i = 0; i < table.items.length; i++) {
                    if(table.items[i]["id"] === 0 && table.items[i]["label"] !== "") {
                        table.updateItemLabel(null, i, table.items[i]["label"])
                        for(let j = 0; j < table.items[i]["prices"].length; j++) {
                            table.updateItemPrice(null, i, j, table.items[i]["prices"][j])
                        }
                    }
                }
            }
        })
    }
    ).on('click', '.delete_table', function(event) { // Delete tables
        event.preventDefault()
        if(confirm("Deleting a table also deletes all items belonging to it... Continue deleting the table?")) {
            let table_tabs = $(this).parent().parent().children()
            let index = Number(this.getAttribute("for").substring("tab-".length))

            let table_id = null
            let valid_delete = false

            let selected_category_id = $('input[name="menu_button"]:checked').attr("id")
            if (selected_category_id === "drink") {
                if (drink_tables[index]["id"] !== -1) {
                    table_id = drink_tables[index]["id"]
                    drink_tables.splice(index, 1)
                    valid_delete = true
                }
            } else if (selected_category_id === "food") {
                if (food_tables[index]["id"] !== -1) {
                    table_id = food_tables[index]["id"]
                    food_tables.splice(index, 1)
                    valid_delete = true
                }
            }

            if (valid_delete) {
                $.ajax({
                    contentType: 'JSON',
                    data: JSON.stringify({
                        'tableID': table_id
                    }),
                    type: 'POST',
                    url: 'delete-table',
                    success: function (data) {
                        for (let i = index + 1; i < table_tabs.length; i++) {
                            table_tabs[i].children[0].setAttribute("id", table_tabs[i - 1].children[0].getAttribute("id"))
                            table_tabs[i].children[1].setAttribute("for", table_tabs[i - 1].children[1].getAttribute("for"))
                            table_tabs[i].children[2].setAttribute("for", table_tabs[i - 1].children[2].getAttribute("for"))
                        }
                        while (table_tabs[index].firstChild) {
                            table_tabs[index].firstChild.remove()
                        }
                        table_tabs[index].remove()
                        if(index <= 0) {
                            $(table_tabs[1]).trigger("click")
                        } else {
                            $(table_tabs[0]).trigger("click")
                        }
                    }
                })
            }
        }
    })


    // Search Bar
    $('#data_table_search_bar').on("keyup", function(event) {
        let rows = $('#menu_table').children("tr")
        for(let i = 1; i < rows.length; i++) {
            let cells = $(rows[i]).children("td")
            let cell_text = $(cells[1]).children()[0].value
            if(!cell_text.includes(this.value)) {
                rows[i].style.display = "none"
            }
            else {
                rows[i].style.display = ""
            }
        }
    })

    // Modifier Panel
    $('#minmax_button').on('click', function(event){
        let modifier_panel = $('#modifier_panel')
        if(modifier_panel.css("display") === "flex") {
            modifier_panel.css("display", "none")
        } else {
            modifier_panel.css("display", "flex")
        }
    })
    $('#modifier_panel').draggable()
    $('#modifier_header').on('mouseenter', function(event) {
        $('#modifier_panel').draggable("option", "disabled", false)
    }
    ).on('mouseleave', function(event) {
        $('#modifier_panel').draggable("option", "disabled", true)
    })
    // Modifier Events
    $('#mods_panel').on('click', '.category_dropdown_button', function(event) {  // Dropdown button
        let modifier_container = this.parentNode.parentNode.children[1]
        if(modifier_container.style.display === "") {
            modifier_container.style.display = "none"
            this.parentNode.style.borderBottom = "none"
            this.style.transform = "rotateZ(90deg)"
        } else {
            modifier_container.style.display = ""
            this.parentNode.style.borderBottom = "ridge"
            this.style.transform = "rotateZ(0)"
        }
    }
    ).on('change', '.category_label', function(event){
        let index = Number(this.parentNode.parentNode.getAttribute("index"))
        modifier_categories[index]["label"] = this.value

        $.ajax({
            contentType: 'JSON',
            data: JSON.stringify({
                "username": current_user,
                "categoryID": modifier_categories[index]["id"],
                "label": modifier_categories[index]["label"]
            }),
            type: 'POST',
            url: 'update-category-label',
            success: function(data) {
                if(modifier_categories[index]["id"] === -1) {
                    modifier_categories.push({"id": -1, "label": "", "mods": []})
                    addModifierCategory()
                }
                modifier_categories[index]["id"] = data["id"]
            }
        })
    }
    ).on('change', '.modifier_label', function(event) {
        let modifiers_container = this.parentNode.parentNode
        let category_index = this.parentNode.parentNode.parentNode.getAttribute("index")
        let modifier_index = this.parentNode.getAttribute("index")
        let modifier = modifier_categories[category_index]["mods"][modifier_index]
        modifier["label"] = this.value

        $.ajax({
            contentType: 'JSON',
            data: JSON.stringify({
                "categoryID": modifier_categories[category_index]["id"],
                "modifierID": modifier["id"],
                "label": modifier["label"]
            }),
            type: 'POST',
            url: 'update-modifier-label',
            success: function(data) {
                if(modifier["id"] === -1) {
                    modifier_categories[category_index]["mods"].push({"id": -1, "categoryID": -1, "label": "", "price": ""})
                    addModifier($(modifiers_container))
                }
                modifier["id"] = data["id"]
            }
        })
    }
    ).on('change', '.modifier_price', function(event){
        let modifiers_container = this.parentNode.parentNode
        let category_index = this.parentNode.parentNode.parentNode.getAttribute("index")
        let modifier_index = this.parentNode.getAttribute("index")
        let modifier = modifier_categories[category_index]["mods"][modifier_index]
        modifier["price"] = Number(this.value)

        $.ajax({
            contentType: 'JSON',
            data: JSON.stringify({
                "categoryID": modifier_categories[category_index]["id"],
                "modifierID": modifier["id"],
                "price": modifier["price"]
            }),
            type: 'POST',
            url: 'update-modifier-price',
            success: function(data) {
                if(modifier["id"] === -1) {
                    modifier_categories[category_index]["mods"].push({"id": -1, "categoryID": -1, "label": "", "price": ""})
                    addModifier($(modifiers_container))
                }
                modifier["id"] = data["id"]
            }
        })
    })

    // Confirmation Box
    $('#confirmation_box').on("change",function(event) {
        if($(this).is(':checked') === true) {
            $(this).parent().css("background", "green")
        } else if($(this).is(':checked') === false) {
            $(this).parent().css("background", "red")
        }

        let checked_tab = $('input[name="tab_group"]:checked')
        let index = checked_tab.attr("id").substring("tab-".length)
        let current_table = null

        let selected_category_id = $('input[name="menu_button"]:checked').attr("id")
        if(selected_category_id === "drink") {
            current_table = drink_tables[index]
        } else if(selected_category_id === "food") {
            current_table = food_tables[index]
        }

        if(current_table["id"] !== -1) {
            $.ajax({
                contentType: 'json',
                data: JSON.stringify({
                    'username': table.current_user,
                    'table': current_table,
                    'completed': $('#confirmation_box').is(':checked')
                }),
                type: 'POST',
                url: 'update-table'
            })
        }
    })

    return table
}

function filterTextField(event) {
    if(event.key==="Enter" || event.key==="$" || event.key==="@" || event.key==="!" || event.key===";") {
        event.preventDefault()
    }
}
function filterPriceField(event) {
    if(((event.key!=="Backspace") && (event.key!==".") && !(event.key>=0) && !(event.key<=9)) || (event.key===" ")){
        event.preventDefault()
    }
}
/* EVENT HELPERS */
function addTable(label="") {
    let tab_button_container = document.getElementById("tab_button_container")

    let tab_button = document.createElement("div")
    tab_button.className = "tab_button"

    let radio_button = document.createElement("input")
    radio_button.type = "radio"
    radio_button.name = "tab_group"
    radio_button.id = "tab-"+String(tab_button_container.children.length)

    let tab_label = document.createElement("textarea")
    tab_label.setAttribute("for", "tab_"+String(tab_button_container.children.length))
    tab_label.className = "tab_label"
    tab_label.maxLength = 13
    tab_label.rows = 1
    tab_label.cols = 12
    tab_label.placeholder = "table name..."
    tab_label.innerHTML = label
    tab_label.addEventListener("keydown", (event)=>filterTextField(event))

    let tab_delete = document.createElement("label")
    tab_delete.className = "delete_table"
    tab_delete.innerHTML = "&#10006"
    tab_delete.setAttribute("for", "tab-"+tab_button_container.children.length)

    tab_button_container.append(tab_button)
    tab_button.appendChild(radio_button)
    tab_button.appendChild(tab_label)
    tab_button.appendChild(tab_delete)
}
function clearTables() {
    let tab_button_container = document.getElementById("tab_button_container")
    while(tab_button_container.firstChild) {
        tab_button_container.firstChild.remove()
    }
}

function addModifierCategory(category = {"id": "-1", "label": "", "mods": []}) {
    let mods_content = $('#mods_content')

    let category_container = document.createElement("div")
    category_container.className = "category_container"
    category_container.setAttribute("index", String(mods_content.children().length))

    mods_content.append(category_container)


    let category_header = document.createElement("div")
    category_header.className = "category_header"

    let dropdown_button = document.createElement("input")
    dropdown_button.className = "category_dropdown_button"
    dropdown_button.type = "button"
    dropdown_button.value = "\u25B6"
    category_header.appendChild(dropdown_button)

    let category_label = document.createElement("textarea")
    category_label.className = "category_label"
    category_label.maxLength = 20
    category_label.cols = 20
    category_label.rows = 1
    category_label.placeholder = "Category"
    category_label.value = category["label"]
    category_label.addEventListener("keydown", (event)=>filterTextField(event))
    category_header.appendChild(category_label)

    let delete_category = document.createElement("label")
    delete_category.className = "delete_category"
    delete_category.innerHTML = "\u2716"
    category_header.appendChild(delete_category)


    category_container.appendChild(category_header)


    let category_mods_container = document.createElement("div")
    category_mods_container.className = "category_mods_container"

    category_container.appendChild(category_mods_container)

    for(let i = 0; i < category["mods"].length; i++) {
        addModifier($(category_mods_container), category["mods"][i])
    }
}
function addModifier(parent=null, modifier={"id": -1, "categoryID": -1, "label": "", "price": ""}) {
    let modifier_container = document.createElement("div")
    modifier_container.className = "modifier_container"
    modifier_container.setAttribute("index", parent.children().length)
    parent.append(modifier_container)

    let modifier_checkbox = document.createElement("input")
    modifier_checkbox.type = "checkbox"
    modifier_checkbox.className = "modifier_checkbox"
    modifier_container.appendChild(modifier_checkbox)

    let modifier_label = document.createElement("textarea")
    modifier_label.className = "modifier_label"
    modifier_label.maxLength = 14
    modifier_label.cols = 14
    modifier_label.rows = 1
    modifier_label.placeholder = "Modifier"
    modifier_label.value = modifier["label"]
    modifier_label.addEventListener('keydown', (event)=>filterTextField(event))
    modifier_container.appendChild(modifier_label)

    let modifier_price = document.createElement("textarea")
    modifier_price.className = "modifier_price"
    modifier_price.maxLength = 6
    modifier_price.cols = 6
    modifier_price.rows = 1
    modifier_price.placeholder = "$-"
    modifier_price.value = modifier["price"]
    modifier_price.addEventListener('keydown', (event)=>filterPriceField(event))
    modifier_container.appendChild(modifier_price)

    let delete_modifier = document.createElement("label")
    delete_modifier.className = "delete_modifier"
    delete_modifier.innerHTML = "\u2716"
    modifier_container.appendChild(delete_modifier)
}

/*
TABLE CLASS
    -ATTRIBUTES-
        tableName: String
            Stores the name of the table
        items: Array
            An array of dictionaries containing two elements: label and prices
                                    label is a string, prices is an array of 8 numbers
        colLen: Number
            Stores the length of filled in columns
        completed: Boolean
            Stores whether the table is completed or not
        priceLabelColumns: Array
            An array of 8 'td' elements representing the top row of the table
        priceLabels: Array
            An array of 1 'label' element and 7 'textarea' elements containing the values of the top row of the table

    -FUNCTIONS-
    downloadTable(tableID)
        Takes the database ID of a table and pulls the items from the server and adds them
        to the table
    addItem(item)
        Takes in a dictionary that contains item data and creates a new html row on
        the table containing one row for a label and 8 rows for pricing.
    renamePriceLabel(index, label="")
        Takes an index between 1 and colLen with an optional label
        Sets the value of the priceLabel at the given index to the label
        If the label is blank, the column is removed from the table
        If index is larger than colLen, colLen is increased by 1
    removeColumn(index)
        Takes an index between 0 and colLen, removes all values in column at the index,
        and moves any remaining columns to the right over
    clearTable()
        Clears the table and reloads it with a blank table
        Returns the tableElement
    generateNewHTMLTable()
        Returns a 'div' element containing a blank table
    updateTableGraphics()
        Updates color for table complete checkbox
        Checks the status of all cells in the table and blanks out cells with a blank top row cell,
        and blanks out all top row cells proceeding the first blank cell in the top row

 */
class Table {
    constructor(current_user="", tableID=-1, table_name="") {
        this.current_user = current_user
        this.tableID = tableID
        this.table_name = table_name
        this.items = []
        this.current_row = null;
        this.colLen = 1
        this.completed = false

        //HTML Table Elements
        this.tableElement = document.createElement("table")
        this.priceLabelColumns = Array(8)
        this.priceLabels = Array(8)
    }
    /*CLASS FUNCTIONS*/
    downloadTable(tableID) {
        let tableInstance = this;
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': this.current_user,
                'tableID': tableID
            }),
            type: 'POST',
            url: 'get-table',
            success: function(data) {
                tableInstance.tableID = tableID

                let price_labels = data["price_labels"]
                let items = data["items"]

                tableInstance.completed = data["completed"]

                for(let i = 0; i < price_labels.length; i++) {
                    tableInstance.renamePriceLabel(null, i, price_labels[i])
                }

                for (let i = 0; i < items.length; i++) {
                    let item = {
                        "id": items[i]["id"],
                        "label": items[i]["label"],
                        "prices": items[i]["prices"],
                        "row": null,
                        "categories": items[i]["categories"]
                    }
                    tableInstance.addItem(item)
                }
                tableInstance.addItem()
            }
        })
    }

    addItem(item={"id": -1, "label": "", "prices": [], "row": null, "categories": []}) {
        let row = this.tableElement.insertRow(-1)
        row.setAttribute("row_index", String(this.items.length))

        let cell0 = row.insertCell(-1)
        let del_button = document.createElement("label")
        del_button.className = "delete_item"
        del_button.innerHTML = "&#10006"
        del_button.addEventListener("click", (event)=>this.removeItem(event, Number(row.getAttribute("row_index"))))
        cell0.appendChild(del_button)

        let cell1 = row.insertCell(-1)
        let item_label = document.createElement("textarea")
        item_label.className = "chart_field item_label"
        item_label.placeholder = "Item"
        item_label.cols = 14
        item_label.rows = 1
        item_label.maxLength = 14
        item_label.setAttribute("row_index", String(this.tableElement.rows.length-2))
        item_label.addEventListener("change", (event)=>this.updateItemLabel(event, Number(row.getAttribute("row_index")), item_label.value))
        item_label.addEventListener("keydown", (event)=>filterTextField(event))
        item_label.value = item["label"]
        cell1.appendChild(item_label)

        for(let i = 2; i < this.priceLabelColumns.length+2; i++) {
            let celli = row.insertCell(-1)
            let data = document.createElement("textarea")
            data.className = "chart_field item_price"
            data.placeholder = "$-"
            data.cols = 14
            data.rows = 1
            data.maxLength = 6
            data.setAttribute("column_index", String(Number(i)-1))
            data.setAttribute("row_index", String(this.items.length))
            data.addEventListener("change", (event)=>this.updateItemPrice(event, Number(row.getAttribute("row_index")), Number(i)-2, Number(data.value)))
            data.addEventListener("keydown", (event)=>filterPriceField(event))

            if(i-2 < item["prices"].length) {
                data.value = item["prices"][i-2]
            }

            celli.appendChild(data)
        }
        item["row"] = row
        this.items.push(item)
        this.updateTableGraphics()
    }

    removeColumn(index) {
    for(let i = index; i < this.colLen; i++) {
        if(i < this.colLen-1) {
            this.priceLabels[i].value = this.priceLabels[Number(i)+1].value
            for(let j = 0; j < this.items.length; j++) {
                this.items[j]["row"].children[Number(i)+2].firstChild.value = this.items[j]["row"].children[Number(i)+3].firstChild.value
            }
        } else {
            this.priceLabels[i].value = ""
            this.priceLabelColumns[i].setAttribute("enabled", false)
            for(let j = 0; j < this.items.length; j++) {
                this.items[j]["row"].children[Number(i)+2].firstChild.value = ""
            }
        }
    }
        this.colLen -= 1
    }

    clearTable() {
        // Clearing Table Data
        this.priceLabelColumns = new Array(8)
        this.priceLabels = new Array(8)
        this.items = []

        // Clear HTML Table
        while(this.tableElement.firstChild) {
            this.tableElement.removeChild(this.tableElement.firstChild)
        }
    }

    generateNewHTMLTable() {
        this.clearTable()

        this.tableElement.id = "menu_table"

        let headerRow = document.createElement("tr")
        headerRow.id = "header_row"
        this.tableElement.appendChild(headerRow)

        let itemLabelColumn = document.createElement("th")
        itemLabelColumn.setAttribute("colspan", "2")
        headerRow.appendChild(itemLabelColumn)

        let itemLabel = document.createElement("label")
        itemLabel.innerHTML = "Items"
        itemLabelColumn.appendChild(itemLabel)

        this.priceLabelColumns[0] = document.createElement("th")
        this.priceLabelColumns[0].setAttribute("enabled", "true")

        this.priceLabels[0] = document.createElement("label")
        this.priceLabels[0].innerHTML = "Regular"
        this.priceLabels[0].className = "chart_field"

        for(let i = 1; i < 8; i++) {
            this.priceLabelColumns[i] = document.createElement("th")
            this.priceLabelColumns[i].setAttribute("enabled", "false")

            this.priceLabels[i] = document.createElement("textarea")
            this.priceLabels[i].className = "chart_field price_label"
            this.priceLabels[i].setAttribute("placeholder", "Price Label")
            this.priceLabels[i].maxLength = "14"
            this.priceLabels[i].rows = 1
            this.priceLabels[i].cols = 14
            this.priceLabels[i].setAttribute("column_index", String(i))
            this.priceLabels[i].addEventListener("change", (event)=>this.renamePriceLabel(event, this.priceLabels[i].getAttribute("column_index"), this.priceLabels[i].value))
            this.priceLabels[i].addEventListener("keydown", (event)=>filterTextField(event))
        }

        for(let i = 0; i < this.priceLabelColumns.length; i++) {
            headerRow.appendChild(this.priceLabelColumns[i])
            this.priceLabelColumns[i].appendChild(this.priceLabels[i])
        }

        this.updateTableGraphics()

        return this.tableElement
    }

    //Updates the shading on the table
    updateTableGraphics() {
        //Update completion box
        if(this.completed === true) {
            $('#confirmation_box').prop("checked", true).change()
        }
        else if(this.completed === false) {
            $('#confirmation_box').prop("checked", false).change()
        }
        //Setting enabled attribute
        for(let i = 0; i < this.priceLabelColumns.length; i++) {
            if(this.priceLabelColumns[i].getAttribute("enabled") === "true"){
                this.priceLabelColumns[i].style.background = "none"
                this.priceLabels[i].style.background = "none"
                for(let j = 0; j < this.items.length; j++) {
                    if (this.items[j]["id"] === -1) {
                        this.items[j]["row"].children[i+2].style.background = "grey"
                        this.items[j]["row"].children[i+2].firstChild.style.background = "grey"
                        this.items[j]["row"].children[i+2].firstChild.setAttribute("readonly", "readonly")
                    } else {
                        this.items[j]["row"].children[i + 2].style.background = "none"
                        this.items[j]["row"].children[i + 2].firstChild.style.background = "none"
                        this.items[j]["row"].children[i + 2].firstChild.getAttribute("readonly") === "readonly" && this.items[j]["row"].children[i + 2].firstChild.removeAttribute("readonly")
                    }
                }
            } else {
                if (this.priceLabelColumns[i - 1].getAttribute("enabled") === "true") {
                    this.priceLabelColumns[i].style.background = "none"
                    this.priceLabels[i].style.background = "none"
                    this.priceLabels[i].getAttribute("readonly") === "readonly" && this.priceLabels[i].removeAttribute("readonly")
                } else {
                    this.priceLabelColumns[i].style.background = "grey"
                    this.priceLabels[i].style.background = "grey"
                    this.priceLabels[i].setAttribute("readonly", "readonly")
                }
                for(let j = 0; j < this.items.length; j++) {
                    this.items[j]["row"].children[i+2].style.background = "grey"
                    this.items[j]["row"].children[i+2].firstChild.style.background = "grey"
                    this.items[j]["row"].children[i+2].firstChild.setAttribute("readonly", "readonly")
                }
            }
        }
    }

    // EVENTS
    selectRow(event, item_index) {
        if(event !== null)
            event.preventDefault()

        if(this.current_row !== null) {
            this.current_row.style.background = "none"
        }
        this.current_row.style.background = "lightblue"

        let item_mods_contents = $('#item_mods_content')
        while(item_mods_contents.firstChild) {
            item_mods_contents.firstChild.remove()
        }

        for(let i = 0; i < this.items.length; i++) {

        }
    }

    renamePriceLabel(event, index, label="") {
        if (event !== null)
            event.preventDefault()

        this.priceLabelColumns[index].setAttribute("enabled", "true")
        if(index >= 1 && index < this.colLen) {
            this.priceLabels[index].value = label
            if (label === "") {
                this.removeColumn(index)
            }
        }
        else if(index >= this.colLen) {
            this.priceLabels[this.colLen].value = label
            this.colLen += 1
        }

        let labels = ["Regular"]
        for(let i = 1; i < this.priceLabels.length; i++) {
            labels.push(this.priceLabels[i].value)
        }

        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': this.current_user,
                'priceLabelsLength': this.colLen,
                'priceLabels': labels
            }),
            type: 'post',
            url: 'update-columns'
        })

        this.updateTableGraphics()
    }

    removeItem(event, item_index) {
        let tableInstance = this
        if (event !== null)
            event.preventDefault()
        let item_id = this.items[item_index]["id"]
        if(item_id !== -1) {
            $.ajax({
                contentType: 'json',
                data: JSON.stringify({
                    'itemID': item_id
                }),
                type: 'POST',
                url: 'remove-item',
                success: function () {
                    let row = tableInstance.items[item_index]["row"]
                    while (row.firstChild) {
                        row.removeChild(row.firstChild)
                    }
                    row.remove()
                    tableInstance.items.splice(item_index, 1)
                }
            })
        }
    }

    updateItemLabel(event=null, item_index, label) {
        console.log(this.items[item_index])
        let tableInstance = this
        if (event !== null)
            event.preventDefault()

        let prev_label = this.items[item_index]["label"]
        this.items[item_index]["label"] = label

        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'tableID': this.tableID,
                'itemID': this.items[item_index]["id"],
                'label': label
            }),
            type: 'POST',
            url: 'update-item-label',
            success: function(data) {
                if(tableInstance.items[item_index]["id"] === -1 || tableInstance.items[item_index]["id"] === 0) {
                    tableInstance.items[item_index]["id"] = data["id"]
                    if(prev_label === "")
                        tableInstance.addItem()
                }
            }
        })
    }

    updateItemPrice(event, item_index, price_index, price) {
        if (event !== null)
            event.preventDefault()

        this.items[item_index]["prices"][price_index] = price

        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'itemID': this.items[item_index]["id"],
                'prices': this.items[item_index]["prices"]
            }),
            type: 'POST',
            url: 'update-item-prices'
        })
    }
}