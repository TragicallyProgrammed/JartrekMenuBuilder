$(function () {
    let userTable = new UserTable()
    userTable.downloadTable()

    // Search Bar
    $('#user_search_bar').on("keyup", function(event) {
        for(let i = 0; i < userTable.users.length; i++) {
            let username = userTable.users[i].username.toLowerCase()
            if(!username.includes(this.value.toLowerCase()))
                userTable.users[i].row.style.display = "none"
            else
                userTable.users[i].row.style.display = ""
        }
    })

    /* Table Events */
    $('#user_table_container')
    // Remove User
    .on('click', '.delete_user', function(){
        userTable.removeUser(Number(this.parentNode.parentNode.getAttribute("index")))
    })
    // Change password
    .on('change', '.password_field', function() {
        let index = Number(this.parentNode.parentNode.getAttribute("index"))
        userTable.users[index].password = this.value
    })
    .on('click', '.password_confirmation', function(event) {
        let index = Number(this.parentNode.parentNode.getAttribute("index"))
        userTable.changePassword(index, userTable.users[index].password)
    })
    // View Table
    .on('click', '.view_table', function(event) {
        userTable.viewTable(Number(this.parentNode.parentNode.getAttribute("index")))
    })

    /* Add Customer */
    $('#add_user_button').on('click', function() {
        let username = $('#new_username').val()
        let password = $('#new_password').val()
        let privilege_level = $('#privilege_level_dropdown').val()
        console.log(privilege_level)
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({
                'username': username,
                'password': password,
                'privilegeLevel': privilege_level
            }),
            type: 'POST',
            url: 'add-user',
            success: function() {
                location.reload()
            },
            error: function() {
                location.reload()
            }
        })
    })

    if(!(CurrentUser.privilegeLevel > 1)) {
        $('#add_user_container').remove()
    }
})

class UserTable {
    constructor() {
        this.users = []
    }

    downloadTable() {
        this.clearTable()

        let instance = this
        $.ajax({
            contentType: 'json',
            data: JSON.stringify({

            }),
            type: 'POST',
            url: 'get-users',
            success: function (data) {
                for(let i = 0; i < data["user_list"].length; i++) {
                    instance.addUser(new User(data["user_list"][i]["id"], data["user_list"][i]["username"], data["user_list"][i]["privilegeLevel"]))
                }
            }
        })
    }

    clearTable() {
        $($('#user_table_container').children[0]).empty()
    }

    addUser(user = new user()) {
        let row = $('#user_table_container')[0].insertRow(-1)
        row.setAttribute("index", this.users.length)
        user.row = row

        let cell0 = row.insertCell(-1)
        let delete_button = document.createElement("label")
        delete_button.className = "delete_user"
        delete_button.innerHTML = "&#10006"
        if(CurrentUser.privilegeLevel > 1)
            cell0.appendChild(delete_button)
        row.appendChild(cell0)

        let cell1 = row.insertCell(-1)
        let username = document.createElement("label")
        username.classname = "username_label"
        username.innerHTML = user.username
        cell1.appendChild(username)
        row.appendChild(cell1)

        let cell2 = row.insertCell(-1)
        let password_field = document.createElement("textarea")
        password_field.className = "password_field"
        password_field.rows = 1
        password_field.cols = 15
        password_field.maxLength = 16;
        password_field.placeholder = "Change Password"
        let cell3 = row.insertCell(-1)
        if(CurrentUser.privilegeLevel > 1 || !(user.privilegeLevel > 0)) {
            cell2.appendChild(password_field)

            let password_confirmation = document.createElement("button")
            password_confirmation.className = "password_confirmation"
            password_confirmation.innerHTML = "\u2713"
            cell3.appendChild(password_confirmation)
        }
        row.appendChild(cell2)
        row.appendChild(cell3)

        let cell4 = row.insertCell(-1)
        let download_table_tag = document.createElement("a")
        download_table_tag.href = "download-data/"+user.username
        let download_table = document.createElement("button")
        download_table.className = "export_button"
        download_table.innerHTML = "\u2913"
        download_table_tag.appendChild(download_table)
        cell4.appendChild(download_table_tag)
        row.appendChild(cell4)

        let cell5 = row.insertCell(-1)
        let view_table_button = document.createElement("button")
        view_table_button.className = "view_table"
        view_table_button.innerHTML = "\u27BE"
        cell5.appendChild(view_table_button)
        row.appendChild(cell5)

        this.users.push(user)
    }

    removeUser(index) {
        let instance = this
        $.ajax({
            contentType: 'JSON',
            data: JSON.stringify({
                'userID': instance.users[index].id
            }),
            type: 'POST',
            url: 'delete-user',
            success: function() {
                location.reload()
            }
        })
    }

    changePassword(index, password) {
        let instance = this
        $.ajax({
            contentType: 'JSON',
            data: JSON.stringify({
                'userID': instance.users[index].id,
                'password': password
            }),
            type: 'POST',
            url: 'change-password',
            success: function() {
                location.reload()
            }
        })
    }

    viewTable(index) {
        let selected_user = this.users[index]
        $('#current_user')[0].innerHTML = selected_user.username
        table.drink_tables = []
        table.food_tables = []
        table.modifier_categories = []
        table.clearTable()
        employeeTable.clearTable()
        paidsTable.clearTable()
        $('#mods_content').empty()
        $('#tab_button_container').empty()

        table.current_user = selected_user.username
        table.downloadTables()
        table.downloadModCategories()
        employeeTable.current_user = selected_user.username
        employeeTable.downloadTable()
        paidsTable.current_user = selected_user.username
        paidsTable.downloadTable()
    }
}
function User(id=-1, username="", privilegeLevel=0, row=null) {
    this.id = id
    this.username = username
    this.privilegeLevel = privilegeLevel
    this.row = row
}