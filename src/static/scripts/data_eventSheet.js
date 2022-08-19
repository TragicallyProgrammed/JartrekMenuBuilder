/* EVENT MANAGER */
let table = new MenuTable(current_user=CurrentUser.username)
let employeeTable = new EmployeeTable(CurrentUser.username)
let paidsTable = new PaidsTable(CurrentUser.username)
$(function() {
    $('#content_container')
     // Text Filters
    .on('keypress', '.tab_label', (event) => filterTextField(event))
    .on('keypress', '.item_label', (event) => filterTextField(event))
    .on('keypress', '.item_price', (event) => filterPriceField(event))
    .on('keypress', '.modifier_label', (event) => filterTextField(event))
    .on('keypress', '.modifier_price', (event) => filterPriceField(event))
    .on('keypress', '.employee_name', (event) => filterTextField(event))
    .on('keypress', '.PIN_label', (event) => filterPINField(event))
    .on('keypress', '.employee_title', (event) => filterTextField(event))
    .on('keypress', '.paid_description', (event) => filterTextField(event))
    .on('keypress', '.paid_price', (event) => filterPriceField(event))
    /* Menu Table Events */
     // Delete Item
     .on('click', '.delete_item', function(){
         let row_index = Number(this.parentNode.parentNode.parentNode.getAttribute("row_index"))
         table.removeItem(row_index)
     })
     // Item label
    .on('change', '.item_label', function() {
        let row_index = Number(this.parentNode.parentNode.getAttribute("row_index"))
        let item = table.items[row_index]
        if(item.id === -1) {
            let cell = $($($(item.row).children()[0]).children()[0])
            console.log(cell.children())
            $(cell.children('.add_item_button')[0]).css("display", "none")
            $(cell.children('.view_mods_button')[0]).css("display", "")
            if(CurrentUser.privilegeLevel > 0)
                $(cell.children('.delete_item')[0]).css("display", "")
        }
        table.updateItemLabel(row_index, this.value)
    })
    // Item Price
    .on('change', '.item_price', function() {
        let colIndex = Number(this.getAttribute("column_index"))
        let rowIndex = Number(this.getAttribute("row_index"))
        this.value = (this.value !== "") ? Number(this.value).toFixed(2) : null
        table.updateItemPrice(rowIndex, colIndex, this.value)
    })
    // Select Item
    .on('click', '.view_mods_button', function() {
        $('#modifier_panel').css("display", "flex")
        let row_index = Number(this.parentNode.parentNode.parentNode.getAttribute("row_index"))
        table.selectRow(row_index)
    })


    // Search Bar
    $('#data_table_search_bar').on("keyup", function() {
        let rows = $('#menu_table').children("tr")
        for(let i = 1; i < rows.length; i++) {
            let cells = $(rows[i]).children("td")
            let cell_text = $(cells[1]).children()[0].value
            let val = new RegExp(this.value, 'i')
            if(cell_text.match(val) !== null) {
                rows[i].style.display = ""
            }
            else {
                rows[i].style.display = "none"
            }
        }
    })

    /* Modifier Panel */
    // Draggable
    $('#minmax_button').on('click', function(){
        let modifier_panel = $('#modifier_panel')
        if(modifier_panel.css("display") === "flex") {
            modifier_panel.css("display", "none")
        } else {
            modifier_panel.css("display", "flex")
        }
    })
    $('#modifier_panel').draggable()
    $('#modifier_header').on('mouseenter', function() {
        $('#modifier_panel').draggable("option", "disabled", false)
    })
    .on('mouseleave', function() {
        $('#modifier_panel').draggable("option", "disabled", true)
    })
    // Close Modifier Panel
    $('#close_mod_panel').on('click', function() {
            $('#modifier_panel').css("display", "none")
    })
    // Dropdown button
    $('#mods_content').on('click', '.category_dropdown_button', function() {
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
    })
    // Change Category Label
    .on('change', '.category_label', function() {
        let index = Number(this.parentNode.parentNode.getAttribute("index"))
        table.modifier_categories[index].label = this.value

        $.ajax({
            contentType: 'JSON',
            data: JSON.stringify({
                "username": table.current_user,
                "categoryID": table.modifier_categories[index].id,
                "label": table.modifier_categories[index].label
            }),
            type: 'POST',
            url: 'update-category-label',
            success: function(data) {
                if(table.modifier_categories[index]["id"] === -1) {
                    let empty_cat = new Category()
                    table.modifier_categories.push(empty_cat)
                    empty_cat.addContainer($('#mods_content'))

                    let header = $(table.modifier_categories[index].htmlContainer.children[0])
                    header.children('.add_category')[0].style.display = "none"
                    if(CurrentUser.privilegeLevel > 1)
                        header.children('.delete_category')[0].style.display = ""
                    let mods_container = table.modifier_categories[index].htmlContainer.children[1]
                    for(let i = 0; i < mods_container.children.length; i++) {
                        let mod_container = mods_container.children[i]
                        $(mod_container.children[1]).removeAttr("readonly").css("background", "white").css("color", "black")
                        $(mod_container.children[2]).removeAttr("readonly").css("background", "white").css("color", "black")
                        $(mod_container.children[4]).css("background", "buttonface").css("color", "black")
                    }
                }

                if(Number(table.modifier_categories[index].id) !== Number(data["id"])) {
                    table.modifier_categories[index].id = data["id"]

                    // Update all children modifiers
                    for (let i = 0; i < table.modifier_categories[index].mods.length; i++) {
                        table.modifier_categories[index].mods[i].category_id = table.modifier_categories[index].id
                        if(table.modifier_categories[index].mods[i].id === 0) {
                            table.modifier_categories[index].mods[i].updateModifier()
                        }
                    }
                }
                if(table.current_item !== null)
                    table.selectRow(table.current_item["row"].getAttribute("row_index"))
            }
        })
    })
    // Delete Category
    .on('click', '.delete_category', function() {
        if(confirm("!!Warning!!\nDeleting a modifier category deletes all modifiers belonging to it...\nContinue?")) {
            let container = this.parentNode.parentNode
            let index = container.getAttribute("index")

            if(table.modifier_categories[index].id !== -1) {
                $.ajax({
                    contentType: 'JSON',
                    data: JSON.stringify({
                        "categoryID": table.modifier_categories[index].id
                    }),
                    type: 'POST',
                    url: 'delete-category',
                    success: function() {
                        $(container).remove()

                        table.modifier_categories.splice(index, 1)
                        for(let i = 0; i < table.modifier_categories.length; i++) {
                            $('#mods_content').children()[i].setAttribute("index", i)
                        }
                        if(table.current_item !== null)
                            table.selectRow(table.current_item.row.getAttribute("row_index"))
                    }
                })
            }
        }
    })
    // Change Modifier Label
    .on('change', '.modifier_label', function() {
        if(this.value === "")
            $(this.parentNode.children[0]).prop("checked", false).attr("disabled", true)
        else
            $(this.parentNode.children[0]).attr("disabled", false)

        let modifiers_container = this.parentNode.parentNode
        let category_index = this.parentNode.parentNode.parentNode.getAttribute("index")
        let modifier_index = this.parentNode.getAttribute("index")
        let modifier = table.modifier_categories[category_index].mods[modifier_index]
        modifier.label = this.value
        modifier.updateModifier(category_index, modifiers_container)
    })
    // Change Modifier Price
    .on('change', '.modifier_price', function() {
        let modifiers_container = this.parentNode.parentNode
        let category_index = this.parentNode.parentNode.parentNode.getAttribute("index")
        let modifier_index = this.parentNode.getAttribute("index")
        let modifier = table.modifier_categories[category_index].mods[modifier_index]
        this.value = (this.value === "") ? this.value = null : Number(this.value).toFixed(2)
        modifier.price = this.value

        modifier.updateModifier(category_index, modifiers_container)
    })
    // Delete Modifier
    .on('click', '.delete_modifier', function() {
        let modifier_container = this.parentNode
        let category_index = this.parentNode.parentNode.parentNode.getAttribute("index")
        let modifier_index = this.parentNode.getAttribute("index")

        if(table.modifier_categories[category_index].mods[modifier_index].id !== 0 && table.modifier_categories[category_index].id !== -1) {
            $.ajax({
                contentType: 'JSON',
                data: JSON.stringify({
                    "modifierID": table.modifier_categories[category_index].mods[modifier_index].id
                }),
                type: 'POST',
                url: 'delete-modifier',
                success: function() {
                    modifier_container.remove()
                    if(table.current_item !== null)
                        table.selectRow(table.current_item.row.getAttribute("row_index"))
                }
            })
        }
    })
    // Set Modifier Button
    $('#set_modifier_button').on('click', function() {
        if(table.current_item !== null) {
            $('input[class=modifier_checkbox]:checked').each(function() {
                let category_index = this.parentNode.parentNode.parentNode.getAttribute("index")
                let modifier_index = this.parentNode.getAttribute("index")

                if(table.modifier_categories[category_index].mods[modifier_index].id !== -1 && table.modifier_categories[category_index].mods[modifier_index].id !== 0) {
                    $.ajax({
                        async: false,
                        contentType: 'JSON',
                        data: JSON.stringify({
                            'itemID': table.current_item.id,
                            'modifierID': table.modifier_categories[category_index].mods[modifier_index].id
                        }),
                        type: 'POST',
                        url: 'set-item-modifier',
                    })
                }
            })
            table.selectRow(table.current_item.row.getAttribute("row_index"))
        }
    })

    /* Item Modifier Events */
    // Dropdown Button
    $('#item_mods_content').on('click', '.category_dropdown_button', function(){
        let item_modifier_container = this.parentNode.parentNode.children[1]
        if(item_modifier_container.style.display === "") {
            item_modifier_container.style.display = "none"
            this.parentNode.style.borderBottom = "none"
            this.style.transform = "rotateZ(90deg)"
        } else {
            item_modifier_container.style.display = ""
            this.parentNode.style.borderBottom = "ridge"
            this.style.transform = "rotateZ(0)"
        }
    })
    // Delete Modifier Item Relationship
    .on('click', '.remove_item_modifier', function(){
        let category_index = this.parentNode.parentNode.parentNode.getAttribute("index")
        let modifier_index = this.parentNode.getAttribute("index")
        let index = table.current_item.row.getAttribute("row_index")

        $.ajax({
            contentType: 'JSON',
            data: JSON.stringify({
                'itemID': table.items[index].id,
                'modifierID': table.items[index].categories[category_index].mods[modifier_index].id
            }),
            type: 'POST',
            url: 'remove-item-modifier',
            success: function() {
                table.selectRow(index)
            }
        })
    })
    // Select Modifier
    .on('click', '.select_modifier', function() {
        let category_index = this.parentNode.parentNode.parentNode.getAttribute("index")
        let modifier_index = this.parentNode.getAttribute("index")
        let item_index = table.current_item.row.getAttribute("row_index")

        let category_id = table.items[item_index].categories[category_index].id
        let modifier_id = table.items[item_index].categories[category_index].mods[modifier_index].id

        for(let i = 0; i < table.modifier_categories.length; i++) {
            if(table.modifier_categories[i].id === category_id) {
                for(let j = 0; j < table.modifier_categories[i].mods.length; j++) {
                    if(table.modifier_categories[i].mods[j].id === modifier_id) {
                        let category_container = $('.category_container[index="'+i+'"]')
                        if(category_container.children()[1].style.display === "none") {
                            $(category_container.children()[0].children[0]).trigger('click')
                        }
                        $(category_container.children()[1].children[j].children[1]).trigger('focus')
                    }
                }
            }
        }
    })

    /* Table Tabs */
    // Change Menu Button
    $('input[name="menu_button"]')
    .on('change', function() {

        // Clear Table Tabs
        let tab_button_container = document.getElementById("tab_button_container")
        while(tab_button_container.firstChild) {
            tab_button_container.firstChild.remove()
        }

        let selected_category_id = $('input[name="menu_button"]:checked').attr("id")
        if(selected_category_id === "drink") {
            $('#tab_buttons_div').css("display", "")
            $('#tab_content_div').css("display", "")
            $('#confirmation_container').css("display", "")
            $('#paids_content').css("display", "none")
            for (let i = 0; i < table.drink_tables.length; i++) {
                table.drink_tables[i].addTable()
            }
            $($('#tab_button_container').children()[0].children[0]).prop("checked", true).trigger("change")
        } else if(selected_category_id === "food") {
            $('#tab_buttons_div').css("display", "")
            $('#tab_content_div').css("display", "")
            $('#confirmation_container').css("display", "")
            $('#paids_content').css("display", "none")
            for (let i = 0; i < table.food_tables.length; i++) {
                table.food_tables[i].addTable()
            }
            $($('#tab_button_container').children()[0].children[0]).prop("checked", true).trigger("change")
        } else if(selected_category_id === "paids") {
            $('#tab_buttons_div').css("display", "none")
            $('#tab_content_div').css("display", "none")
            $('#confirmation_container').css("display", "none")
            $('#paids_content').css("display", "")
        }
        $('#modifier_panel').css("display", "none")
    })
    // Scroll Tabs
    $('#tab_button_container').on('mousewheel', function(event){ // Horizontal Scroll
        this.scrollLeft += event.originalEvent.deltaY
    })
    // Change tabs
    .on('change', 'input[name="tab_group"]', function(){
        let id = -1;
        let index_str = $('input[name="tab_group"]:checked').attr("id")
        let index = index_str.substring(index_str.length - 1)
        let selected_category_id = $('input[name="menu_button"]:checked').attr("id")
        if(selected_category_id === "drink") {
            id = table.drink_tables[index].id
        } else if(selected_category_id === "food") {
            id = table.food_tables[index].id
        }

        if(id !== -1) {
            $(this).parent().css("background", "white") // Set selected background to white
            $($(this).parent().children()[2]).css("background", "none").css("border", "1px solid black")
            $('input[name="tab_group"]:not(:checked)').each(function () {
                $(this).parent().css("background", "linear-gradient(#659BF7, #BBC4D9)") // Set unselected background to gradient
                $($(this).parent().children()[2]).css("background", "none").css("border", "none")

                let index_str = $(this).attr("id")
                let index = index_str.substring(index_str.length - 1)
                let unselected_id = -1
                if(selected_category_id === "drink") {
                    unselected_id = table.drink_tables[index].id
                } else if(selected_category_id === "food") {
                    unselected_id = table.food_tables[index].id
                }
                if(unselected_id === -1) {
                    $($(this).parent().children()[2]).css("background", "white").css("border", "1px solid black")
                }
            })

            $('#tab_content_div').append(table.generateNewHTMLTable()) // Create new table

            // Download current table
            if (selected_category_id === "drink") {
                table.downloadTable(table.drink_tables[index].id)
            } else if (selected_category_id === "food") {
                table.downloadTable(table.food_tables[index].id)
            }
        }
    })
    // Click to change to that tab
    .on('click', '.tab_button', function() {
        let checked_tab = $('input[name="tab_group"]:checked')
        if (this.children[0].id !== checked_tab.prop("id")) {
            checked_tab.prop("checked", false)
            $(this.children[0]).prop("checked", true).trigger("change")
        }
    })
    // Change table label
    .on("change", '.tab_label', function() {
        let tab = $(this).parent()
        let index = Number(this.getAttribute("for").substring("tab_".length))
        let current_table = null

        let selected_category_id = $('input[name="menu_button"]:checked').attr("id")
        if(selected_category_id === "drink") { // Update table under drink list
            current_table = table.drink_tables[index]
        } else if(selected_category_id === "food") { // Update table under food list
            current_table = table.food_tables[index]
        }
        current_table.table_name = this.value

        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': table.current_user,
                'table': current_table,
                'completed': table.completed
            }),
            type: 'POST',
            url: 'update-table',
            success: function (data) {
                let new_table_container = null
                table.tableID = data["id"]
                if(current_table["id"] === -1 && current_table["table_name"].value !== ""){
                    let new_table = new Table()
                    if(selected_category_id === "drink") {
                        new_table.table_type = "drink"
                        table.drink_tables.push(new_table)
                    } else if(selected_category_id === "food") {
                        new_table.table_type = "food"
                        table.food_tables.push(new_table)
                    }
                    new_table_container = new_table.addTable()

                    tab.children(".delete_table")[0].style.display = ""

                    tab.children(".add_tab")[0].style.display = "none"
                }

                if(selected_category_id === "drink") {
                    table.drink_tables[index].id = data["id"]
                } else if(selected_category_id === "food") {
                    table.food_tables[index].id = data["id"]
                }

                if(new_table_container !== null) {
                    $($(new_table_container).children()[0]).trigger("click")
                }
            }
        })
    })
    // Delete tables
    .on('click', '.delete_table', function(event) {
        event.preventDefault()
        if(confirm("!!WARNING!!\nDeleting a table also deletes all items belonging to it... Continue deleting the table?")) {
            let table_tabs = $(this).parent().parent().children()
            let index = Number(this.getAttribute("for").substring("tab-".length))

            let table_id = null
            let valid_delete = false

            let selected_category_id = $('input[name="menu_button"]:checked').attr("id")
            if (selected_category_id === "drink") {
                if (table.drink_tables[index]["id"] !== -1) {
                    table_id = table.drink_tables[index]["id"]
                    table.drink_tables.splice(index, 1)
                    valid_delete = true
                }
            } else if (selected_category_id === "food") {
                if (table.food_tables[index]["id"] !== -1) {
                    table_id = table.food_tables[index]["id"]
                    table.food_tables.splice(index, 1)
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
                    success: function () {
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

    // Confirmation Box
    $('#confirmation_box').on('change',function(event) {
        let checked_tab = $('input[name="tab_group"]:checked')
        let index = checked_tab.attr("id").substring("tab-".length)
        let current_table = null

        let selected_category_id = $('input[name="menu_button"]:checked').attr("id")
        if(selected_category_id === "drink") {
            current_table = table.drink_tables[index]
        } else if(selected_category_id === "food") {
            current_table = table.food_tables[index]
        }
        table.completed = $('#confirmation_box').is(':checked')

        if(current_table["id"] !== -1) {
            $.ajax({
                contentType: 'json',
                data: JSON.stringify({
                    'username': table.current_user,
                    'table': current_table,
                    'completed': table.completed
                }),
                type: 'POST',
                url: 'update-table'
            })
        }
    })


    /* Employee Table */
    $('#employee_table')
    // Title Autocomplete
    .on('keydown.autocomplete', '.employee_title', function() {
        $(this).autocomplete({
            source: ["Bartender", "Cook", "Manager"],
            minLength: 0
        })
    }) .on('focus', '.employee_title', function() { $(this).trigger('keydown.autocomplete'); })
    // Update employee name
    .on('change', '.employee_name', function() {
        employeeTable.updateEmployeeName(Number(this.parentNode.parentNode.getAttribute("index")), this.value)
    })
    // Update employee PIN
    .on('change', '.PIN_label', function() {
        employeeTable.updateEmployeePIN(Number(this.parentNode.parentNode.getAttribute("index")), this.value)
    })
    // Update employee title
    .on('change', '.employee_title', function() {
        employeeTable.updateEmployeeTitle(Number(this.parentNode.parentNode.getAttribute("index")), this.value)
    })
    // Delete Employee
    .on('click', '.delete_employee', function() {
        employeeTable.removeEmployee(this.parentNode.parentNode.getAttribute("index"))
    })


    /* Paids Table */
    // Update paids type
    $('#paids_table').on('change', '.paid_dropdown', function() {
        if(this.value === "true") {
            paidsTable.updateType(this.parentNode.parentNode.getAttribute("index"), true)
        }
        else if(this.value === "false") {
            paidsTable.updateType(this.parentNode.parentNode.getAttribute("index"), false)
        }
    })
    // Update paids description
    .on('change', '.paid_description', function() {
        paidsTable.updateDescription(this.parentNode.parentNode.getAttribute("index"), this.value)
    })
    // Update paids price
    .on('change', '.paid_price', function() {
        this.value = (this.value !== "") ? Number(this.value).toFixed(2) : null
        paidsTable.updatePrice(this.parentNode.parentNode.getAttribute("index"), this.value)
    })
    // Delete Paid
    .on('click', '.delete_paid', function() {
        paidsTable.removePaids(this.parentNode.parentNode.getAttribute("index"))
    })


    /* on First Load */
    // Get tables for logged in user
    table.downloadTables()
    // Get mods for logged in user
    table.downloadModCategories()

    // Get Employees
    employeeTable.downloadTable()

    // Get Paids
    paidsTable.downloadTable()
})

/* EVENT HELPERS */
function filterTextField(event) {
    if(event.which === 13) {
        // Focus Next Item
        return false
    }
    else if(event.key === '/') return false
    return true
}
function filterPriceField(event) {
    let regex = /\d+\.?\d{0,2}|\.\d{0,2}/
    if(event.key === '.' && event.target.value.includes('.')) return false

    if(!!event.key.match(regex)) return true
    return false
}
function filterPINField(event) {
    return !!event.key.match(/\d/);

}