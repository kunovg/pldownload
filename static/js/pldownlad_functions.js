jQuery.validator.addMethod("not_arroba", function(value, element) {
  return this.optional(element) || /^[^@]*$/g.test(value);
}, "Enter a valid username");

function parse_ws_info(data){
    var error = []
    if(data.status == "STARTED"){
        $("#ws_resp").html('Process started');
    }
    else if(data.status == "OK"){
        $("#ws_resp").html('Processed ' + data.c + ' of ' + data.total);
    }
    else if(data.status == "ERROR"){
        error.push(data.songname)
    }
    else if(data.status == "FINISHED"){
        $("#ws_resp").html('Finished, ' + error.length +' errors');
        if (error.length > 0){
            $("#ws_resp").append("<p>Couldn't download the next songs:</p>")
            $("#ws_resp").append("<ul></ul>")
            error.foreach(function(item){
                $("#ws_resp ul").append('<li>'+item+'</li>')
            });
        }
    }    
}

function parse_ws_info_session(data, uuid){
    var error = []
    if(data.status == "STARTED"){
        $("#ws_resp"+uuid).html('Download started');
    }
    else if(data.status == "OK"){
        $("#ws_resp"+uuid).html('Downloaded ' + data.c + ' of ' + data.total);
    }
    else if(data.status == "ERROR"){
        error.push(data.songname)
    }
    else if(data.status == "FINISHED"){
        $("#ws_resp"+uuid).html('Finished download, ' + error.length +' errors');
        // if (error.length > 0){
        //     $("#ws_resp").append("<p>Couldn't doanload the next songs:</p>")
        //     $("#ws_resp").append("<ul></ul>")
        //     error.foreach(function(item){
        //         $("#ws_resp ul").append('<li>'+item+'</li>')
        //     });
        // }
    }    
}

$("[name='username']").change(function(){
    $.ajax({
            method: "POST",
            url: "/check_username",
            data: { username: $("[name='username']").val()},
            success: function(){
                $("#glyph_user").removeClass( "glyphicon-remove" ).addClass( "glyphicon-ok" ).css( "color", "green" );
            },
            error:function(){
                $("#glyph_user").removeClass( "glyphicon-ok" ).addClass( "glyphicon-remove" ).css( "color", "red" );
            }
        });
})
$("[name='email']").change(function(){
    $.ajax({
            method: "POST",
            url: "/check_email",
            data: { email: $("[name='email']").val() },
            success: function(){
                $("#glyph_email").removeClass( "glyphicon-remove" ).addClass( "glyphicon-ok" ).css( "color", "green" );
            },
            error:function(){
                $("#glyph_email").removeClass( "glyphicon-ok" ).addClass( "glyphicon-remove" ).css( "color", "red" );
            }
        });
})

$("#registerform").validate({
    rules: {
        username: {
            required: true,
            minlength: 1,
            maxlength: 30,
            not_arroba: true
        },
        email: {
            required: true,
            email: true,
        },
        password: {
            required: true,
            minlength: 8
        },
        password_:{
            required: true,
            equalTo: "#password"
        }
    },
    submitHandler: function(form) {
        $.ajax({
                method: "POST",
                url: "/add",
                data: $("#registerform").serialize(),
                success: function(){
                    window.location.reload(true);
                },
                error: function(){
                    $("#register_resp").removeClass( "alert-success" ).addClass( "alert-danger" ).html("<strong>Error!</strong> An error ocurred while registering your account").css( "display", "block" );
                }
            });
  }
 });

$("#loginform").validate({
    rules: {
        login_email: {
            required: true,
        },
        login_password: {
            required: true,
        }
    },
    submitHandler: function(form) {
        $("#login_gif").show()
        $.ajax({
            method: "POST",
            url: "/login",
            data: $("#loginform").serialize(),
            success: function(){
                window.location.reload(true); 
            },
            error: function(data){
                $("#login_gif").hide()
                $("#login_resp").addClass( "alert-danger" ).html("<strong>Error!</strong>User and password do not match").css( "display", "block" );
            }
        });
  }
 });


$("#reportform").validate({
    rules: {
        playlist: {
            maxlength: 50,
        },
        songname: {
            maxlength: 100,
        },        
        description: {
            maxlength: 250,
        }
    },
    submitHandler: function(form) {
        $("#report_gif").show()
        $.ajax({
            method: "POST",
            url: "/report",
            data: $("#reportform").serialize(),
            success: function(){
                window.location.reload(true); 
            },
            error: function(data){
                $("#report_gif").hide()
                $("#report_resp").addClass( "alert-danger" ).html("<strong>Error!</strong> ").css( "display", "block" );
            }
        });
  }
 });

$("#changepwform").validate({
    rules: {
        oldpw: {
            maxlength: 50,
        },
        newpw: {
            maxlength: 50,
        },        
        newpw_: {
            maxlength: 50,
            equalTo: "#newpw"
        }
    },
    submitHandler: function(form) {
        $("#changepw_gif").show()
        $.ajax({
            method: "POST",
            url: "/changepw",
            data: $("#changepwform").serialize(),
            success: function(){
                $("#changepw_gif").hide();
                $("#changepw_resp").removeClass( "alert-danger" ).addClass( "alert-success" ).html("<strong>Success!</strong>Password changed correctly").css( "display", "block" );
            },
            error: function(data){
                $("#changepw_gif").hide();
                $("#changepw_resp").removeClass( "alert-success" ).addClass( "alert-danger" ).html("<strong>Error!</strong> ").css( "display", "block" );
            }
        });
  }
 });

$("#addPL").click(function(){
    $("#addpl_resp").hide();
    $("#loading").show();
    if ( /youtube.com\/playlist\?list=.*|spotify.com\/user\/\d+|.+\/playlist\/.*|user:[^:]+:playlist:.*/.test($("#newpl").val()) ){
        $.ajax({
            method: "POST",
            url: "/insertpl",
            data: {'plurl': $("#newpl").val()},
            success: function(){
                window.location.reload(true); 
            },
            error: function(data){
                $("#loading").hide();
                $("#addpl_resp").addClass( "alert-danger" ).html("<strong>Error!</strong>An error ocurred while adding your playlist, please verify the URL is correct").css( "display", "block" );
            }
        });
    }
    else{
        $("#loading").hide();
        $("#addpl_resp").addClass( "alert-danger" ).html("<strong>Error!</strong>An error ocurred while adding your playlist, please verify the URL is correct").css( "display", "block" );
    }
});

$('#playlist_download').click(function(){
    $("#dlpl_resp").hide();
    $("#loading").show();
    if ( /youtube.com\/playlist\?list=.*|spotify.com\/user\/\d+|.+\/playlist\/.*|user:[^:]+:playlist:.*/.test($("#url_input").val()) ){
        $.ajax({
            method: "POST",
            url: "/freedownload",
            data: {'playlist_url': $("#url_input").val(), 'temp_id': temp_id},
            success: function(data){
                $("#loading").hide();
                $('#free_download').append("<a href='/getzip/"+ data + "' class='btn btn-pl' id='playlist_download'>Download ZIP</a>")

            },
            error: function(data){
                $("#loading").hide();
                $("#dlpl_resp").addClass( "alert-danger" ).html("<strong>Error!</strong>An error ocurred while downloading your playlist, verify the URL is correct").css( "display", "block" );
            }
        });
    }
    else{
        $("#loading").hide();
        $("#dlpl_resp").addClass( "alert-danger" ).html("<strong>Error!</strong>An error ocurred while downloading your playlist, verify the URL is correct").css( "display", "block" );
    }
});

$(".btn-rfsh").click(function(){
    $.ajax({
        method: "POST",
        url: "/update",
        data: {'uuid': $( this ).val()},
        success: function(){
            window.location.reload(true); 
        },
        error: function(data){
        }
    });
});

$(".btn-delete").click(function(){
    $.ajax({
        method: "POST",
        url: "/delete",
        data: {'uuid': $( this ).val()},
        success: function(){
            window.location.reload(true); 
        },
        error: function(data){
        }
    });
});
