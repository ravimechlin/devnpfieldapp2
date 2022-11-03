$(document).ready(function()
{
    $("#href_change_pass").click(function()
    {
        try
        {
            $.each(BootstrapDialog.dialogs, function(i, dialog)
            {
                dialog.close();
            });
        }
        catch(e6)
        {

        }
        var div = $("<div></div>");
        $("<p></p>").addClass("change_pass_label").text("Current Password").appendTo(div);
        $("<input />").attr("type", "password").attr("id", "temp_curr").attr("placeholder", "*****").appendTo(div);
        $("<p></p>").addClass("change_pass_label").text("New Password").appendTo(div);
        $("<input />").attr("type", "password").attr("id", "temp_pass").attr("placeholder", "*****").appendTo(div);
        $("<p></p>").addClass("change_pass_label").text("Confirm Password").appendTo(div);
        $("<input />").attr("type", "password").attr("id", "temp_confirm").attr("placeholder", "*****").appendTo(div);

        $("<button />").attr("type", "button").text("Change Password").attr("id", "temp_btn_change_pass").appendTo(div);

        $("<button />").attr("type", "button").text("Cancel").attr("id", "temp_btn_change_pass_cancel").appendTo(div);

        var html = $("<div></div>");
        html.append(div);
        BootstrapDialog.alert({"title": "Change Password", "message": html.html()});
        setTimeout(function()
        {
            $(".bootstrap-dialog-footer-buttons").find("button").css("display", "none");
            $("#temp_btn_change_pass").click(function()
            {
                // check password
                var pass = $("#temp_pass").val();
                var confirm = $("#temp_confirm").val();
                if(pass !== confirm)
                {
                    window.alert("Your passwords must match");
                    return;
                }
                var found_upper = false;
                var found_lower = false;
                var found_number = false;
                for(var i = 0; i < 10; i++)
                {
                    var str = i + '';
                    if(pass.indexOf(str) > -1)
                    {
                        found_number = true;
                        i = 9;
                    }
                }
                for(var i = 65; i < (65 + 26); i++)
                {
                    var str = String.fromCharCode(i);
                    if(pass.indexOf(str) > -1)
                    {
                        found_upper = true;
                        i = 65 + 25;
                    }
                }
                for(var i = 97; i < (97 + 26); i++)
                {
                    var str = String.fromCharCode(i);
                    if(pass.indexOf(str) > -1)
                    {
                        found_lower = true;
                        i = 97 + 25;
                    }
                }
                if(!found_upper || !found_lower || !found_number)
                {
                    window.alert("Your new password must contain at least one uppercase letter, one lowercase letter, and one digit.")
                    return;
                }

                $("#temp_btn_change_pass").text("Checking current password");

                $.post("/data", {"fn": "validate_password_against_user_in_session", "password": $("#temp_curr").val()}).done(function(resp)
                {
                    if(!resp.success)
                    {
                        $("#temp_btn_change_pass").text("Change Password");
                        window.alert("Either the value you provided for your current password is incorrect, or your session has been lost.");
                    }
                    else
                    {
                        $("#temp_btn_change_pass").text("Changing Password...");
                        $.post("/data", {"fn": "set_password_for_user_in_session", "password": $("#temp_pass").val()}).done(function(resp)
                        {
                            $(".bootstrap-dialog-message").html("<p style='text-align: center;'>Your password has succesfully been changed.</p>");
                            setTimeout(function()
                            {
                                $.each(BootstrapDialog.dialogs, function(i, dialog)
                                {
                                    dialog.close();
                                });
                            }, 2000);
                        });
                    }
                });
            });

            $("#temp_btn_change_pass_cancel").click(function()
            {
                $.each(BootstrapDialog.dialogs, function(i, dialog)
                {
                    dialog.close();
                });
            });

        }, 250);
    });
});