var handleLogin = function () {
    var form = $('#login_form');
    var error = $('.alert-danger', form);
    form.validate({
        errorElement: 'span', //default input error message container
        errorClass: 'help-block', // default input error message class
        focusInvalid: false, // do not focus the last invalid input
        rules: {
            username: {
                required: true
            },
            password: {
                required: true
            }
        },
        messages: {
            username: {
                required: "请输入用户名."
            },
            password: {
                required: "请输入密码."
            }
        },

        invalidHandler: function (event, validator) { //display error alert on form submit
            error.show();
            App.scrollTo(error, -200);
        },

        highlight: function (element) { // hightlight error inputs
            $(element)
                .closest('.form-group').addClass('has-error'); // set error class to the control group
        },

        success: function (label, element) {
            label.closest('.form-group').removeClass('has-error');
        },

        errorPlacement: function (error, element) {
        },

        submitHandler: function (form) {
            var username = $("input[name='username']").val();
            var password = $("input[name='password']").val();
            $.ajax({
                type: 'get',
                url: '/validate',
                data: {username: username, password: password},
                dataType: 'JSON',
                success: function (data) {
                    if (data["status"] == 1) {
                        $('.alert-danger span').html("用户名错误");
                        $('.alert-danger', $('.login-form')).show();
                    }
                    else if (data["status"] == 2) {
                        $('.alert-danger span').html("密码错误");
                        $('.alert-danger', $('.login-form')).show();
                    }
                    else if (data["status"] === 3) {
                        $('.alert-danger span').html("账号登陆IP限制");
                        $('.alert-danger', $('.login-form')).show();
                    }
                    else {
                        window.location.href = "/";
                    }
                },
                error: function (XMLHttpRequest) {
                error_func(XMLHttpRequest);
            }
            })
        }
    });

    $('.login-form input').keypress(function (e) {
        if (e.which == 13) {
            if ($('.login-form').validate().form()) {
                $('.login-form').submit(); //form validation success, call ajax form submit
            }
            return false;
        }
    });
};
handleLogin();
