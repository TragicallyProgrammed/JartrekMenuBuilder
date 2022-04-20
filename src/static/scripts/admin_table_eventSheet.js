$(function () {
    let table = MenuTable(document.getElementById("username").innerHTML.valueOf());

    $('#user_search_bar').on("keyup", function(event) {
        console.log("Key pressed!")
        let rows = $($('#user_table_container')).children("tr");
        for(let i = 0; i < rows.length; i++) {
            cells = $(rows[i]).children("td");
            console.log($(cells[1]).text());
            console.log(this.value);
            if (!$(cells[1]).text().includes(this.value)) {
                rows[i].style.display = "none";
            }
            else {
                rows[i].style.display = "";
            }
        }
    });

    $.ajax({ // Send request to get users and populate table
        contentType: 'json',
        data: JSON.stringify({}),
        type: 'POST',
        url: 'get-users',
        success: function (data) {
            let users_table = document.getElementById('user_table_container');

            let json_data = JSON.parse(JSON.stringify(data));
            let user_list = json_data['user_list'];
            for (let i = 0; i < user_list.length; i++) {
                let username = user_list[i];
                //Create row container
                let row_container = document.createElement('tr');
                row_container.className = "user_table";

                //create delete button
                let delete_cell = document.createElement('td');
                delete_cell.className = "user_table";
                let delete_button = document.createElement('button');
                delete_button.innerHTML = "\u274C";
                delete_button.className = "delete_user";
                delete_button.setAttribute("for", username);
                delete_button.addEventListener("click", function(event){
                    if(confirm("!!WARNING!!\nDeleting a user permanently deletes the user and all their data. Are you sure you would like to continue?")) {
                        $.ajax({
                            contentType: 'json',
                            data: JSON.stringify({
                                'username': this.getAttribute("for")
                            }),
                            type: 'POST',
                            url: 'remove_user',
                            statusCode: {
                                200: function () {
                                    location.reload(true);
                                }
                            }
                        });
                    }
                });
                delete_cell.appendChild(delete_button);

                //create username label
                let username_element = document.createElement('td');
                username_element.className = "user_table";
                let username_label = document.createElement('label');
                username_label.className = "username";
                username_label.innerHTML = username;
                username_element.appendChild(username_label);

                //create change password
                let password_cell = document.createElement('td');
                password_cell.className = "user_table";
                let password_form = document.createElement('form');
                password_form.method = "POST";
                password_form.className = "change_password"
                let password_field = document.createElement('input');
                password_field.type = "text";
                password_field.name = "password";
                password_field.setAttribute("for", username)
                password_field.className = 'password_field';
                password_field.placeholder = "Enter new password"
                let for_user = document.createElement("input");
                for_user.type = "hidden";
                for_user.name = "username"
                for_user.value = username;
                let password_submit = document.createElement('button');
                password_submit.type = "submit";
                password_submit.name = "submit";
                password_submit.value = "change_pass"
                password_submit.innerHTML = "\u2713";
                password_form.appendChild(password_field);
                password_form.appendChild(for_user);
                password_form.appendChild(password_submit);
                password_cell.appendChild(password_form);

                //create export button
                let export_cell = document.createElement('td');
                export_cell.className = "user_table";
                let export_button_container = document.createElement('a');
                export_button_container.href = "download-data/"+username;
                let export_button = document.createElement('button');
                export_button.className = "export_button";
                export_button.setAttribute("for", username);
                let export_label = document.createElement('label');
                export_label.innerHTML = "\u2913";
                export_button.appendChild(export_label);
                export_button_container.appendChild(export_button)
                export_cell.appendChild(export_button_container);

                //create view table button
                let view_table_cell = document.createElement("td");
                view_table_cell.className = "user_table";
                let view_table_button = document.createElement("button");
                view_table_button.className = "view_table";
                view_table_button.setAttribute('for', username);
                view_table_button.addEventListener("click", function (e) {
                    e.preventDefault();
                    let label = document.getElementById("current_user");  // Get label
                    label.innerHTML = this.getAttribute("for");  // Update label
                    table.current_user = this.getAttribute("for") // Update table's current user
                    //tableInstance.loadTable($('input[name="tab-group"]:checked').attr("for"));  // Loading table for currently selected user
                });
                let view_table_label = document.createElement('label');
                view_table_label.innerHTML = "\u27BE";
                view_table_button.appendChild(view_table_label);
                view_table_cell.appendChild(view_table_button);

                users_table.appendChild(row_container);
                row_container.appendChild(delete_cell);
                row_container.appendChild(username_element);
                row_container.appendChild(password_cell);
                row_container.appendChild(export_cell)
                row_container.appendChild(view_table_cell);
            }
        }
    });
});