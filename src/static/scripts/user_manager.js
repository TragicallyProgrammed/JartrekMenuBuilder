function user_manager(tableInstance) {
    $(function () {
        $.ajax({ // Send request to get users and populate table
            contentType: 'json',
            data: JSON.stringify({}),
            type: 'POST',
            url: 'get-users',
            success: function (data) {
                var users_table = document.getElementById('user_table_container');

                var json_data = JSON.parse(JSON.stringify(data));
                var user_list = json_data['user_list'];
                for (var i = 0; i < user_list.length; i++) {
                    var username = user_list[i];
                    //Create row container
                    var row_container = document.createElement('tr');
                    row_container.className = "user_table";

                    //create username label
                    var username_element = document.createElement('td');
                    username_element.className = "user_table";
                    var username_label = document.createElement('label');
                    username_label.className = "username";
                    username_label.innerHTML = username;
                    username_element.appendChild(username_label);

                    //create change password
                    var password_cell = document.createElement('td');
                    password_cell.className = "user_table";
                    var password_form = document.createElement('form');
                    password_form.method = "POST";
                    password_form.className = "change_password"
                    var password_field = document.createElement('input');
                    password_field.type = "text";
                    password_field.name = "password";
                    password_field.setAttribute("for", username)
                    password_field.className = 'password_field';
                    password_field.placeholder = "Enter new password"
                    var for_user = document.createElement("input");
                    for_user.type = "hidden";
                    for_user.name = "username"
                    for_user.value = username;
                    var password_submit = document.createElement('button');
                    password_submit.type = "submit";
                    password_submit.name = "submit";
                    password_submit.value = "change_pass"
                    password_submit.innerHTML = "\u2713";
                    password_form.appendChild(password_field);
                    password_form.appendChild(for_user);
                    password_form.appendChild(password_submit);
                    password_cell.appendChild(password_form);

                    //create export button
                    var export_cell = document.createElement('td');
                    export_cell.className = "user_table";
                    var export_button_container = document.createElement('a');
                    export_button_container.href = "download-data/"+username;
                    var export_button = document.createElement('button');
                    export_button.className = "export_button";
                    export_button.setAttribute("for", username);
                    var export_label = document.createElement('label');
                    export_label.innerHTML = "\u2913";
                    export_button.appendChild(export_label);
                    export_button_container.appendChild(export_button)
                    export_cell.appendChild(export_button_container);

                    //create view table button
                    var view_table_cell = document.createElement("td");
                    view_table_cell.className = "user_table";
                    var view_table_button = document.createElement("button");
                    view_table_button.className = "view_table";
                    view_table_button.setAttribute('for', username);
                    view_table_button.addEventListener("click", function (e) {
                        e.preventDefault();
                        tableInstance.uploadTable(this.getAttribute("for")); // Upload previously selected user's table
                        var label = document.getElementById("current_user");  // Get label
                        label.innerHTML = this.getAttribute("for");  // Update label
                        tableInstance.loadTable("tab-content-1", this.getAttribute("for"));  // Loading table for currently selected user
                    });
                    var view_table_label = document.createElement('label');
                    view_table_label.innerHTML = "\u27BE";
                    view_table_button.appendChild(view_table_label);
                    view_table_cell.appendChild(view_table_button);

                    users_table.appendChild(row_container);
                    row_container.appendChild(username_element);
                    row_container.appendChild(password_cell);
                    row_container.appendChild(export_cell)
                    row_container.appendChild(view_table_cell);
                }
            }
        });
    });
}