/*EVENT MANAGER*/
$(function() {
    $.ajax({ // Send request to get users and populate table
        contentType: 'json',
        data: JSON.stringify({}),
        type: 'POST',
        url: 'get-users',
        success: function (data) {
            users_table = document.getElementById('user_table_container');

            var json_data = JSON.parse(JSON.stringify(data));
            var user_list = json_data['user_list'];
            for (var i = 0; i < user_list.length; i++) {
                //Create row container
                row_container = document.createElement('tr');
                row_container.className = "user_table";

                //create username label
                username_element = document.createElement('td');
                username_element.innerHTML = user_list[i];
                username_element.className = "user_table";

                //create change password
                password_cell = document.createElement('td');
                password_cell.className = "user_table";
                password_form = document.createElement('form');
                password_field = document.createElement('textarea');
                password_field.className = 'password_field';
                password_submit = document.createElement('input');
                password_submit.type = "submit";
                password_submit.name = "submit";
                password_submit.value = "\u2713";
                password_form.appendChild(password_field);
                password_form.appendChild(password_submit);
                password_cell.appendChild(password_form);

                //create export button
                export_cell = document.createElement('td');
                export_cell.className = "user_table";
                export_button = document.createElement('button');
                export_button.className = "export_button"
                export_button.for = user_list[i];
                export_label = document.createElement('label');
                export_label.innerHTML = "\u2913";
                export_button.appendChild(export_label);
                export_cell.appendChild(export_button);

                //create view table button
                view_table_cell = document.createElement("td");
                view_table_cell.className = "user_table";
                view_table_button = document.createElement("button");
                view_table_button.className = "view_table";
                view_table_button.for = user_list[i];
                view_table_label = document.createElement('label');
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

    // TODO: Update user password button event

    // TODO: Table export button event
});