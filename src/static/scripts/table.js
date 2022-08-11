/*
Menu Table Class
    -ATTRIBUTES-
        current_user: String
            Stores the table's username
        tableID: Number
            ID of the table in the database
        items: Array
            Stores item data
        current_item: Item
            Currently selected item for modifier panel
        colLen: Number
            Number of active columns
        completed: Boolean
            Tracks if the table is complete or not
        tableElement: HTMLElement
            HTML Element for the table
        priceLabelColumns: Array
            Stores the first row of columns for the table
        priceLabels: Array
            Stores the labels for each column

    -FUNCTIONS-
        downloadTable(tableID)
            Downloads price labels and items from database
        addItem(item)
            Adds a new HTML row on the current table with the given item
        removeColumn(index)
            Removes label from priceLabels and clears the column
        generateNewHTMLTable()
            Returns a blank HTML Table
        updateTableGraphics()
            Greys out all inactive cells and colors table complete checkbox
        clearTable()
            Clears out the tableElement of table data
        selectRow(item_index)
            Selects a row at a given index
        updatePriceLabel(index, label)
            Updates the price label of a column
        updateItemLabel(item_index, label)
            Updates label for an item
        updateItemPrice(item_index, price_index, price)
            Updates price for an item
        removeItem(item_index)
            Deletes an item
*/
class MenuTable {
    constructor(current_user="", tableID=-1) {
        this.current_user = current_user
        this.tableID = tableID
        this.items = []
        this.current_item = null;
        this.colLen = 1
        this.completed = false

        //HTML Table Elements
        this.tableElement = document.createElement("table")
        this.priceLabelColumns = Array(8)
        this.priceLabels = Array(8)

        this.drink_tables = []
        this.food_tables = []
        this.modifier_categories = []
    }

    downloadTables() {
        let instance = this
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': instance.current_user
            }),
            type: 'POST',
            url: 'get-tables',
            success: function (data) {
                instance.downloadColumns()

                // fill tables
                let tables = data["tables"]
                for(let i = 0; i < tables.length; i++) {
                    if(tables[i]["tableType"] === "drink")
                        instance.drink_tables.push(new Table(data["tables"][i]["id"], data["tables"][i]["tableName"], data["tables"][i]["tableType"]))
                    else if(tables[i]["tableType"] === "food")
                        instance.food_tables.push(new Table(data["tables"][i]["id"], data["tables"][i]["tableName"], data["tables"][i]["tableType"]))
                }
                instance.drink_tables.push(new Table(-1, "", "drink"))
                instance.food_tables.push(new Table(-1, "", "food"))


                let selected_category_id = $('input[name="menu_button"]:checked').attr("id")
                if(selected_category_id === "drink") {
                    for(let i = 0; i < instance.drink_tables.length; i++) {
                        instance.drink_tables[i].addTable()
                    }
                    $($('#tab_button_container').children()[0].children[0]).prop("checked", true).trigger("change")
                } else if(selected_category_id === "food") {
                    for(let i = 0; i < instance.food_tables.length; i++) {
                        instance.food_tables[i].addTable()
                    }
                    $($('#tab_button_container').children()[0].children[0]).prop("checked", true).trigger("change")
                }
            }
        })
    }

    downloadModCategories() {
        let instance = this
        $.ajax({
            contentType: 'JSON',
            data: JSON.stringify({
                'username': instance.current_user
            }),
            type: 'POST',
            url: 'get-categories',
            success: function(data) {
                for(let i = 0; i < data["categories"].length; i++) {
                    let category = new Category(data["categories"][i]["id"], data["categories"][i]["label"], [])
                    for(let j = 0; j < data["categories"][i]["mods"].length; j++) {
                        category.mods.push(new Modifier(category.id, data["categories"][i]["mods"][j]["id"], data["categories"][i]["mods"][j]["label"], data["categories"][i]["mods"][j]["price"]))
                    }
                    category.mods.push(new Modifier(category.id))
                    instance.modifier_categories.push(category)
                }
                instance.modifier_categories.push(new Category())

                let mods_content = $('#mods_content')

                for(let i = 0; i < instance.modifier_categories.length; i++) {
                    instance.modifier_categories[i].addContainer(mods_content)
                }
            }
        })
    }

    downloadTable(tableID) {
        let instance = this
        $.ajax({
            async: 'false',
            contentType: 'json',
            data: JSON.stringify({
                'username': instance.current_user,
                'tableID': tableID
            }),
            type: 'POST',
            url: 'get-table',
            success: function(data) {
                instance.tableID = tableID

                let items = data["items"]

                instance.completed = data["completed"]

                for(let i = 0; i < items.length; i++) {
                    let item = new Item(items[i]["id"], items[i]["label"], items[i]["prices"], null, items[i]["categories"])
                    instance.addItem(item)
                }
                instance.addItem()

                instance.downloadColumns()
            }
        })
    }

    downloadColumns() {
        let instance = this
        $.ajax({
            contentType: 'JSON',
            data: JSON.stringify({
                "username": instance.current_user
            }),
            type: 'POST',
            url: 'get-columns',
            success: function(data) {
                let labels = data["priceLabels"]
                for(let i = 1; i < labels.length; i++) {
                    instance.priceLabels[i].value = labels[i]
                    instance.priceLabelColumns[i].setAttribute("enabled", "true")
                }
                instance.colLen = labels.length
                instance.updateTableGraphics()
            }
        })
    }

    addItem(item = new Item()) {
        let row = this.tableElement.insertRow(-1)
        row.setAttribute("row_index", String(this.items.length))

        let cell0 = row.insertCell(-1)
        cell0.className = "cell0"
        let container = document.createElement("div")
        container.className = "cell0_container"
        cell0.appendChild(container)
        let add_item = document.createElement("button")
        add_item.className = "add_item_button"
        add_item.innerHTML = "Add"
        container.appendChild(add_item)
        let del_button = document.createElement("button")
        del_button.className = "delete_item"
        del_button.innerHTML = "&#10006"
        container.appendChild(del_button)
        let view_mods = document.createElement("button")
        view_mods.className = "view_mods_button"
        view_mods.innerHTML = "Mods"
        container.appendChild(view_mods)

        let cell1 = row.insertCell(-1)
        let item_label = document.createElement("textarea")
        item_label.className = "chart_field item_label"
        item_label.placeholder = "Item"
        item_label.cols = 20
        item_label.rows = 1
        item_label.maxLength = 19
        item_label.value = item.label
        cell1.appendChild(item_label)

        for(let i = 2; i < this.priceLabelColumns.length+2; i++) {
            let celli = row.insertCell(-1)
            let data = document.createElement("textarea")
            data.className = "chart_field item_price"
            data.placeholder = "$0.00"
            data.cols = 14
            data.rows = 1
            data.maxLength = 6
            data.setAttribute("column_index", String(Number(i)-1))
            data.setAttribute("row_index", String(this.items.length))

            if(i-2 < item.prices.length) {
                data.value = item.prices[i-2]
            }

            celli.appendChild(data)
        }
        item.row = row
        this.items.push(item)

        if(item.id === -1) {
            del_button.style.display = "none"
            view_mods.style.display = "none"
        } else {
            add_item.style.display = "none"
        }

        this.updateTableGraphics()
    }

    removeColumn(index) {
        for(let i = index; i < this.colLen; i++) {
            if(i < this.colLen-1) {
                this.priceLabels[i].value = this.priceLabels[Number(i)+1].value
                for(let j = 0; j < this.items.length; j++) {
                    this.items[j].row.children[Number(i)+2].firstChild.value = this.items[j].row.children[Number(i)+3].firstChild.value
                }
            } else {
                this.priceLabels[i].value = ""
                this.priceLabelColumns[i].setAttribute("enabled", false)
                for(let j = 0; j < this.items.length; j++) {
                    this.items[j].row.children[Number(i)+2].firstChild.value = ""
                }
            }
        }
        this.colLen -= 1
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
        headerRow.appendChild(this.priceLabelColumns[0])
        this.priceLabelColumns[0].appendChild(this.priceLabels[0])

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
            this.priceLabels[i].addEventListener("change", () => this.updatePriceLabel(this.priceLabels[i].getAttribute("column_index"), this.priceLabels[i].value))

            headerRow.appendChild(this.priceLabelColumns[i])
            this.priceLabelColumns[i].appendChild(this.priceLabels[i])
        }

        this.updateTableGraphics()

        return this.tableElement
    }

    updateTableGraphics() {
        //Update completion box
        let confirmation_box = $('#confirmation_box')
        confirmation_box.prop("checked", this.completed)

        //Setting enabled attribute
        for(let i = 0; i < this.priceLabelColumns.length; i++) {
            if(this.priceLabelColumns[i].getAttribute("enabled") === "true"){
                this.priceLabelColumns[i].style.background = "none"
                this.priceLabels[i].style.background = "none"
                this.priceLabels[i].removeAttribute("readonly")
                for(let j = 0; j < this.items.length; j++) {
                    if (this.items[j].id === -1) {
                        this.items[j].row.children[i+2].style.background = "grey"
                        this.items[j].row.children[i+2].firstChild.style.background = "grey"
                        this.items[j].row.children[i+2].firstChild.setAttribute("readonly", "readonly")
                    } else {
                        this.items[j].row.children[i + 2].style.background = "none"
                        this.items[j].row.children[i + 2].firstChild.style.background = "none"
                        this.items[j].row.children[i + 2].firstChild.getAttribute("readonly") === "readonly" && this.items[j].row.children[i + 2].firstChild.removeAttribute("readonly")
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
                    this.items[j].row.children[i+2].style.background = "grey"
                    this.items[j].row.children[i+2].firstChild.style.background = "grey"
                    this.items[j].row.children[i+2].firstChild.setAttribute("readonly", "readonly")
                }
            }
        }
    }

    clearTable() {
        // Clearing Table Data
        this.items = []

        // Clear HTML Table
        while(this.tableElement.firstChild) {
            this.tableElement.removeChild(this.tableElement.firstChild)
        }
    }

    selectRow(item_index) {
        if(this.current_item !== null) {
            this.current_item.row.firstChild.style.background = "none"
        }
        // Clear item modifiers content
        let item_mods_contents = $('#item_mods_content')
        item_mods_contents.empty()
        $('#current_item').html(this.items[item_index].label)

        if(this.items[item_index].id !== -1 && this.items[item_index].id !== 0) { // If the item selected does not have an invalid id
            this.current_item = this.items[item_index]
            this.current_item.row.firstChild.style.background = "#83AAD1"
            let instance = this

            $.ajax({
                contentType: 'JSON',
                data: JSON.stringify({
                    "username": instance.current_user,
                    "itemID": instance.items[item_index].id
                }),
                type: 'POST',
                url: 'download-item',
                success: function (data) {
                    if(data !== "") {
                        instance.items[item_index] = new Item(data["item"]["id"], data["item"]["label"], data["item"]["prices"], instance.items[item_index].row, data["item"]["categories"])

                        let categories = instance.items[item_index].categories
                        for (let i = 0; i < categories.length; i++) {
                            // Create category HTML
                            let item_category_container = document.createElement("div")
                            item_category_container.className = "item_category_container"
                            item_category_container.setAttribute("index", item_mods_contents.children().length)
                            item_mods_contents.append(item_category_container)

                            let item_category_header = document.createElement("div")
                            item_category_header.className = "item_category_header"
                            item_category_container.appendChild(item_category_header)

                            let item_category_dropdown_button = document.createElement("input")
                            item_category_dropdown_button.className = "category_dropdown_button"
                            item_category_dropdown_button.type = "button"
                            item_category_dropdown_button.value = "\u25B6"
                            item_category_header.appendChild(item_category_dropdown_button)

                            let item_category_label = document.createElement("label")
                            item_category_label.className = "item_category_label"
                            item_category_label.innerHTML = categories[i]["label"]
                            item_category_header.appendChild(item_category_label)

                            let item_category_mods_container = document.createElement("div")
                            item_category_mods_container.className = "item_category_mods_container"
                            item_category_container.appendChild(item_category_mods_container)

                            for (let j = 0; j < categories[i].mods.length; j++) {
                                let modifier_container = document.createElement("div")
                                modifier_container.className = "item_modifier_container"
                                modifier_container.setAttribute("index", item_category_mods_container.children.length)
                                item_category_mods_container.appendChild(modifier_container)

                                let remove_modifier = document.createElement("label")
                                remove_modifier.className = "remove_item_modifier"
                                remove_modifier.innerHTML = "&#10006"
                                modifier_container.appendChild(remove_modifier)

                                let modifier_label = document.createElement("label")
                                modifier_label.className = "item_modifier_label"
                                modifier_label.innerHTML = categories[i].mods[j].label
                                modifier_container.appendChild(modifier_label)

                                let modifier_price = document.createElement("label")
                                modifier_price.className = "item_modifier_price"
                                if (categories[i].mods[j].price == null)
                                    modifier_price.innerHTML = "$-"
                                else
                                    modifier_price.innerHTML = "$" + categories[i].mods[j].price
                                modifier_container.appendChild(modifier_price)

                                let select_modifier = document.createElement("input")
                                select_modifier.type = "button"
                                select_modifier.className = "select_modifier"
                                select_modifier.value = "\u00BB"
                                modifier_container.appendChild(select_modifier)
                            }
                        }
                    }
                }
            })
        } else {
            this.current_item = null;
        }
    }

    updatePriceLabel(index, label="") {
        let instance = this
        let delete_column = false

        if(index >= this.colLen)
            this.colLen += 1

        this.priceLabelColumns[index].setAttribute("enabled", "true")
        if(index >= 1 && index < this.colLen) {
            if (label === "") {
                //this.priceLabels[index].value = label
                if (confirm("!!WARNING!!\nDo you wish to delete this column? Doing so will remove the price under this column for all items")) {
                    this.removeColumn(index)
                    delete_column = true
                }
            }
        }

        let labels = ["Regular"]
        for(let i = 1; i < this.colLen; i++) {
            labels.push(this.priceLabels[i].value)
        }

        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': instance.current_user,
                'priceLabels': labels,
                'deleteColumn': delete_column,
                'index': Number(index)
            }),
            type: 'POST',
            url: 'update-columns'
        })
        this.updateTableGraphics()
    }

    updateItemLabel(item_index, label="") {
        let instance = this

        this.items[item_index].label = label

        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'tableID': instance.tableID,
                'itemID': instance.items[item_index].id,
                'label': label
            }),
            type: 'POST',
            url: 'update-item-label',
            success: function(data) {
                if(instance.items[item_index].id === -1 || instance.items[item_index].id === 0) {
                    instance.items[item_index].id = data["id"]
                    instance.addItem()
                }
            }
        })
    }

    updateItemPrice(item_index, price_index, price) {
        this.items[item_index].prices[price_index-1] = price

        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'itemID': this.items[item_index].id,
                'prices': this.items[item_index].prices
            }),
            type: 'POST',
            url: 'update-item-prices'
        })
    }

    removeItem(item_index) {
        let tableInstance = this
        let item_id = this.items[item_index].id
        if(item_id !== -1) {
            $.ajax({
                contentType: 'json',
                data: JSON.stringify({
                    'itemID': item_id
                }),
                type: 'POST',
                url: 'remove-item',
                success: function () {
                    tableInstance.current_item = null
                    let row = tableInstance.items[item_index].row
                    $(row).remove()
                    tableInstance.items.splice(item_index, 1)
                    for(let i = item_index; i < tableInstance.items.length; i++) {
                        tableInstance.items[i].row.setAttribute("row_index", i)
                    }
                }
            })
        }
    }
}

class EmployeeTable {
    constructor(current_user) {
        this.current_user = current_user
        this.employees = []
    }

    downloadTable() {
        let instance = this
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': this.current_user
            }),
            type: 'POST',
            url: 'get-employees',
            success: function (data) {
                for(let i = 0; i < data["employees"].length; i++) {
                    let emp = new Employee(data["employees"][i]["id"], data["employees"][i]["name"], data["employees"][i]["pin"], data["employees"][i]["title"])
                    instance.addEmployee(emp)
                }
                instance.addEmployee()
                instance.updateTableGraphics()
            }
        })
    }

    addEmployee(employee = new Employee()) {
        let row = $('#employee_table')[0].insertRow(-1)
        row.setAttribute("index", this.employees.length)
        employee.row = row

        let cell0 = row.insertCell(-1)
        let del_button = document.createElement("label")
        del_button.className = "delete_employee"
        del_button.innerHTML = "&#10006"
        cell0.appendChild(del_button)

        let cell1 = row.insertCell(-1)
        let name_label = document.createElement("textarea")
        name_label.className = "employee_name"
        name_label.placeholder = "Name"
        name_label.rows = 1
        name_label.cols = 19
        name_label.maxLength = 20
        name_label.value = employee.name
        cell1.appendChild(name_label)

        let cell2 = row.insertCell(-1)
        let pin_label = document.createElement("textarea")
        pin_label.className = "PIN_label"
        pin_label.placeholder = "0000"
        pin_label.rows = 1
        pin_label.cols = 5
        pin_label.maxLength = 6
        pin_label.value = employee.pin
        cell2.appendChild(pin_label)

        let cell3 = row.insertCell(-1)
        let title_label = document.createElement("textarea")
        title_label.className = "employee_title"
        title_label.placeholder = "Title"
        title_label.rows = 1
        title_label.cols = 19
        title_label.maxLength = 20
        title_label.value = employee.title
        cell3.appendChild(title_label)

        this.employees.push(employee)
        this.updateTableGraphics()
    }

    removeEmployee(index) {
        let instance = this
        if(this.employees[index].id !== -1) {
            $.ajax({
                contentType: 'json',
                data: JSON.stringify({
                    'id': instance.employees[index].id
                }),
                type: 'POST',
                url: 'remove-employee',
                success: function () {
                    let row = instance.employees[index].row
                    $(row).remove()
                    instance.employees.splice(index, 1)

                    for(let i = index; i < instance.employees.length; i++) {
                        instance.employees[i].row.setAttribute("index", i)
                    }
                }
            })
        }
    }

    updateEmployeeName(index, name="") {
        if(this.employees[index].id === -1) {
            this.addEmployee()
        }
        if(name === "") {
            this.removeEmployee(index)
        } else {
            let instance = this
            instance.employees[index].name = name
            $.ajax({
                contentType: 'json',
                data: JSON.stringify({
                    'username': this.current_user,
                    'id': instance.employees[index].id,
                    'name': instance.employees[index].name
                }),
                type: 'POST',
                url: 'update-employee-name',
                success: function (data) {
                    instance.employees[index].id = data["id"]
                    instance.updateTableGraphics()
                }
            })
        }
    }

    updateEmployeePIN(index, pin=null) {
        let instance = this
        if(this.employees[index].id !== -1) {
            instance.employees[index].pin = pin
            $.ajax({
                contentType: 'json',
                data: JSON.stringify({
                    'id': instance.employees[index].id,
                    'pin': instance.employees[index].pin
                }),
                type: 'POST',
                url: 'update-employee-pin',
                success: function (data) {
                    instance.employees[index].id = data["id"]
                }
            })
        }
    }

    updateEmployeeTitle(index, title="") {
        let instance = this
        if(this.employees[index].id !== -1) {
            instance.employees[index].title = title
            $.ajax({
                contentType: 'json',
                data: JSON.stringify({
                    'id': instance.employees[index].id,
                    'title': instance.employees[index].title
                }),
                type: 'POST',
                url: 'update-employee-title',
                success: function (data) {
                    instance.employees[index].id = data["id"]
                }
            })
        }
    }

    updateTableGraphics() {
        for(let i = 0; i < this.employees.length; i++) {
            if(this.employees[i].name === "") {
                this.employees[i].row.children[2].style.background = "grey"
                this.employees[i].row.children[2].children[0].readOnly = true
                this.employees[i].row.children[2].children[0].style.background = "grey"
                this.employees[i].row.children[3].style.background = "grey"
                this.employees[i].row.children[3].children[0].readOnly = true
                this.employees[i].row.children[3].children[0].style.background = "grey"
            } else {
                this.employees[i].row.children[2].style.background = "none"
                this.employees[i].row.children[2].children[0].readOnly = false
                this.employees[i].row.children[2].children[0].style.background = "none"
                this.employees[i].row.children[3].style.background = "none"
                this.employees[i].row.children[3].children[0].readOnly = false
                this.employees[i].row.children[3].children[0].style.background = "none"
            }
        }
    }

    clearTable() {
        for(let i = 0; i < this.employees.length; i++) {
            $(this.employees[i].row).empty()
        }
        this.employees = []
    }
}

class PaidsTable {
    constructor(current_user="") {
        this.current_user = current_user
        this.paids = []
    }

    downloadTable() {
        let instance = this
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': this.current_user
            }),
            type: 'POST',
            url: 'get-paids',
            success: function (data) {
                for(let i = 0; i < data["paids"].length; i++) {
                    let paid = new Paids(data["paids"][i]["id"], data["paids"][i]["paidIn"], data["paids"][i]["description"], data["paids"][i]["price"])
                    instance.addPaids(paid)
                }
                instance.addPaids()
            }
        })
    }

    addPaids(paid=new Paids()) {
        let row = $('#paids_table')[0].insertRow(-1)
        row.setAttribute("index", this.paids.length)
        paid.row = row

        let cell0 = row.insertCell(-1)
        let del_button = document.createElement("label")
        del_button.className = "delete_paid"
        del_button.innerHTML = "&#10006"
        cell0.appendChild(del_button)

        let cell1 = row.insertCell(-1)
        let dropdown = document.createElement("select")
        dropdown.className = "paid_dropdown"
        let _none = document.createElement("option")
        _none.value = "none"
        dropdown.appendChild(_none)
        let _out = document.createElement("option")
        _out.innerHTML = "Paid Out"
        _out.value = "false"
        dropdown.appendChild(_out)
        let _in = document.createElement("option")
        _in.innerHTML = "Paid In"
        _in.value = "true"
        dropdown.appendChild(_in)
        cell1.appendChild(dropdown)
        if(paid.paidIn === true) {
            dropdown.value = "true"
            _in.selected = true
            _none.setAttribute("disabled", true)
        } else if(paid.paidIn === false) {
            dropdown.value = "false"
            _out.selected = true
            _none.setAttribute("disabled", false)
        } else {
            dropdown.value = "none"
            _none.selected = true
        }

        let cell2 = row.insertCell(-1)
        let description = document.createElement("textarea")
        description.className = "paid_description"
        description.placeholder = "Description"
        description.rows = 1
        description.cols = 19
        description.maxLength = 20
        description.value = paid.description
        cell2.appendChild(description)

        let cell3 = row.insertCell(-1)
        let price = document.createElement("textarea")
        price.className = "paid_price"
        price.placeholder = "$-"
        price.rows = 1
        price.cols = 5
        price.maxLength = 6
        price.value = paid.price
        cell3.appendChild(price)

        this.paids.push(paid)
        this.updateTableGraphics()
    }

    removePaids(index) {
        if(this.paids[index].id !== -1) {
            let instance = this
            $.ajax({
                contentType: 'json',
                data: JSON.stringify({
                    'id': instance.paids[index].id
                }),
                type: 'POST',
                url: 'remove-paid',
                success: function () {
                    let row = instance.paids[index].row
                    $(row).remove()
                    instance.paids.splice(index, 1)

                    for(let i = index; i < instance.paids.length; i++) {
                        instance.paids[i].row.setAttribute("index", i)
                    }
                    instance.updateTableGraphics()
                }
            })
        }
    }

    updateType(index, paidIn) {
        let dropdown = this.paids[index].row.children[1].children[0]
        let none = dropdown.children[0]

        if(this.paids[index].paidIn === null) {
            none.setAttribute("disabled", true)
            this.addPaids()
        }

        this.paids[index].paidIn = paidIn

        let instance = this
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': this.current_user,
                'id': this.paids[index].id,
                'isPaidIn': this.paids[index].paidIn
            }),
            type: 'POST',
            url: 'update-paid-type',
            success: function (data) {
                instance.paids[index].id = data["id"]
                instance.updateTableGraphics()
            }
        })
    }

    updateDescription(index, description="") {
        this.paids[index].description = description

        let instance = this
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'id': this.paids[index].id,
                'description': this.paids[index].description
            }),
            type: 'POST',
            url: 'update-paid-description',
            success: function (data) {
                instance.paids[index].id = data["id"]
            }
        })
    }

    updatePrice(index, price) {
        this.paids[index].price = price

        let instance = this
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'id': this.paids[index].id,
                'price': this.paids[index].price
            }),
            type: 'POST',
            url: 'update-paid-price',
            success: function (data) {
                instance.paids[index].id = data["id"]
            }
        })
    }

    updateTableGraphics() {
        for(let i = 0; i < this.paids.length; i++) {
            if(this.paids[i].row.children[1].children[0].value === "none") {
                this.paids[i].row.children[2].style.background = "grey"
                this.paids[i].row.children[2].children[0].readOnly = true
                this.paids[i].row.children[2].children[0].style.background = "grey"
                this.paids[i].row.children[3].style.background = "grey"
                this.paids[i].row.children[3].children[0].readOnly = true
                this.paids[i].row.children[3].children[0].style.background = "grey"
            } else {
                this.paids[i].row.children[2].style.background = "none"
                this.paids[i].row.children[2].children[0].readOnly = false
                this.paids[i].row.children[2].children[0].style.background = "none"
                this.paids[i].row.children[3].style.background = "none"
                this.paids[i].row.children[3].children[0].readOnly = false
                this.paids[i].row.children[3].children[0].style.background = "none"
            }
        }
    }

    clearTable() {
        for(let i = 0; i < this.paids.length; i++) {
            $(this.paids[i].row).empty()
        }
        this.paids = []
    }
}

function Table(id=-1, table_name="", table_type=""){
    this.id = id
    this.table_name = table_name
    this.table_type = table_type
    this.addTable = function() {
        let tab_button_container = document.getElementById("tab_button_container")

        let tab_button = document.createElement("div")
        tab_button.className = "tab_button"

        let radio_button = document.createElement("input")
        radio_button.type = "radio"
        radio_button.name = "tab_group"
        radio_button.id = "tab-"+String(tab_button_container.children.length)

        let tab_delete = document.createElement("button")
        tab_delete.className = "delete_table"
        tab_delete.innerHTML = "&#10006"
        tab_delete.setAttribute("for", "tab-"+tab_button_container.children.length)

        let tab_label = document.createElement("textarea")
        tab_label.setAttribute("for", "tab_"+String(tab_button_container.children.length))
        tab_label.className = "tab_label"
        tab_label.maxLength = 18
        tab_label.rows = 1
        tab_label.cols = 17
        tab_label.value = this.table_name

        let add_button = document.createElement("button")
        add_button.className = "add_tab"
        add_button.innerHTML = "Add Menu"

        if (this.id !== -1) {
            add_button.style.display = "none"
        }
        else {
            tab_delete.style.display = "none"
        }

        tab_button_container.append(tab_button)
        tab_button.appendChild(radio_button)
        tab_button.appendChild(tab_delete)
        tab_button.appendChild(tab_label)
        tab_button.appendChild(add_button)

        return tab_button_container
    }
}
function Item(id = -1, label = "", prices = [], row=null, categories=[]) {
    this.id = id
    this.label = label
    this.prices = prices
    this.row = row
    this.categories = categories
}
function Category(id = -1, label="", mods=[new Modifier()]) {
    this.id = id
    this.label = label
    this.mods = mods
    this.htmlContainer = null
    this.getHTML = function() {
        let category_container = document.createElement("div")
        category_container.className = "category_container"


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
        category_label.value = this.label
        category_header.appendChild(category_label)

        let delete_category = document.createElement("button")
        delete_category.className = "delete_category"
        delete_category.innerHTML = "\u2716"
        category_header.appendChild(delete_category)

        let add_category = document.createElement("button")
        add_category.className = "add_category"
        add_category.innerHTML = "Add"
        category_header.appendChild(add_category)

        category_container.appendChild(category_header)


        let category_mods_container = document.createElement("div")
        category_mods_container.className = "category_mods_container"

        category_container.appendChild(category_mods_container)

        for(let i = 0; i < this.mods.length; i++) {
            this.mods[i].category_id = this.id
            this.mods[i].addModifier($(category_mods_container))
            if(this.id === -1) {
                $(this.mods[i].htmlContainer.children[1]).attr("readonly", "readonly")
                    .css("background", "darkgrey").css("color", "grey")
                $(this.mods[i].htmlContainer.children[2]).attr("readonly", "readonly")
                    .css("background", "darkgrey").css("color", "grey")
                $(this.mods[i].htmlContainer.children[4]).css("background", "darkgrey").css("color", "grey")
            }
        }

        if(this.id !== -1) {
            $(add_category).css("display", "none")
        } else {
            $(delete_category).css("display", "none")
        }

        this.htmlContainer = category_container

        return category_container
    }
    this.addContainer = function(parent) {
        let category_container = this.getHTML()
        category_container.setAttribute("index", parent.children().length)
        parent.append(category_container)
    }
}
function Modifier(category_id=-1, id=-1, label="", price=null) {
    this.category_id = category_id
    this.id = id
    this.label = label
    this.price = price
    this.htmlContainer = null
    this.getHTML = function() {
        let modifier_container = document.createElement("div")
        modifier_container.className = "modifier_container"

        let modifier_checkbox = document.createElement("input")
        modifier_checkbox.type = "checkbox"
        modifier_checkbox.className = "modifier_checkbox"
        if(this.label === "")
            modifier_checkbox.setAttribute("disabled", 'true')
        modifier_container.appendChild(modifier_checkbox)

        let modifier_label = document.createElement("textarea")
        modifier_label.className = "modifier_label"
        modifier_label.maxLength = 20
        modifier_label.cols = 19
        modifier_label.rows = 1
        modifier_label.placeholder = "Modifier"
        modifier_label.value = this.label
        modifier_container.appendChild(modifier_label)

        let modifier_price = document.createElement("textarea")
        modifier_price.className = "modifier_price"
        modifier_price.maxLength = 6
        modifier_price.cols = 6
        modifier_price.rows = 1
        modifier_price.placeholder = "$0.00"
        modifier_price.value = this.price
        modifier_container.appendChild(modifier_price)

        let delete_modifier = document.createElement("button")
        delete_modifier.className = "delete_modifier"
        delete_modifier.innerHTML = "\u2716"
        modifier_container.appendChild(delete_modifier)

        let add_modifier = document.createElement("button")
        add_modifier.className = "add_modifier"
        add_modifier.innerHTML = "Add"
        modifier_container.appendChild(add_modifier)

        if (this.id !== -1) {
            add_modifier.style.display = "none"
        }
        else {
            delete_modifier.style.display = "none"
            modifier_price.style.display = "none"
        }

        this.htmlContainer = modifier_container

        return modifier_container
    }
    this.addModifier = function(parent) {
        let modifier_container = this.getHTML()
        modifier_container.setAttribute("index", parent.children().length)
        parent.append(modifier_container)
    }
    this.updateModifier = function(category_index, modifiers_container) {
        let instance = this
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                "categoryID": instance.category_id,
                "modifierID": instance.id,
                "label": instance.label,
                "price": instance.price
            }),
            type: 'POST',
            url: 'update-modifier',
            success: function(data) {
                if(instance.id === -1 && instance.label !== "") {
                    let mod = new Modifier(instance.category_id, -1, "", null)
                    table.modifier_categories[category_index].mods.push(mod)
                    mod.addModifier($(modifiers_container))

                    $(instance.htmlContainer.children[2]).css("display", "")
                    $(instance.htmlContainer.children[3]).css("display", "")
                    $(instance.htmlContainer.children[4]).css("display", "none")
                }
                instance.id = data["id"]
                if(table.current_item !== null)
                    table.selectRow(table.current_item["row"].getAttribute("row_index"))
            }
        })
    }
}
function Employee(id=-1, name="", pin=null, title="", row=null) {
    this.id = id
    this.name = name
    this.pin = pin
    this.title = title
    this.row = row
}
function Paids(id=-1, paidIn=null, description="", price=null, row=null) {
    this.id = id
    this.paidIn = paidIn
    this.description = description
    this.price = price
    this.row = row
}