$(function(){
    $('.index-topic-item').mouseover(function(){
        $(this).css('background', '#EAF6FF');
    })
    .mouseout(function(){
        $(this).css('background', '#fff');
    });
    
    
    $('a#logOut').click(function(){
        $.ajax(
            {
                type: 'GET',
                url: '/account/logout/',
                async: false,
                success: function(data){
                    location.reload();
                },
                error: function(XmlHttprequest, textStatus, errorThrown){
                    location.reload();
                }
            }
        );
    });
    
    $('#loginForm button').click(function(){
        var username = $('#loginForm input[name=username]').val();
        var password = $('#loginForm input[name=password]').val();
        username = strip(username);
        password = strip(password);
        if(!username.length || !password.length){
            $('#loginErrorMsg').hide(200);
            $('#loginErrorMsg strong').text('需要用户名和密码才能登录');
            $('#loginErrorMsg').show(200);
            return false;
        }
        if(password.length < 4){
            $('#loginErrorMsg').hide(200);
            $('#loginErrorMsg strong').text('密码至少要4个字符');
            $('#loginErrorMsg').show(200);
            return false;
        }
        return true;
    });
    
    
    
    $('#registerForm button').click(function(){
        var username = $('#registerForm input[name=username]').attr('value');
        var email = $('#registerForm input[name=email]').attr('value');
        var password = $('#registerForm input[name=password]').attr('value');
        var password2 = $('#registerForm input[name=password2]').attr('value');
        
        username = strip(username);
        email = strip(email);
        password = strip(password);
        password2 = strip(password2);
        
        if(!username.length){
            show_error_msg('输个名字吧');
            return false;
        }
        if(!email.length){
            show_error_msg('输个邮箱吧');
            return false;
        }
        var _tmp_email = email.replace(/^.+@.+\..+$/, '');
        if(_tmp_email.length){
            show_error_msg('亲，邮箱格式不正确哦');
            return false;
        }
        if(!password.length){
            show_error_msg('输个密码吧');
            return false;
        }
        if(password.length<4){
            show_error_msg('密码太短了，至少要4个字符');
            return false;
        }
        if(password != password2){
            show_error_msg('亲，两次密码不一样哦');
            return false;
        }
        return true;
    });
    
    $('#loginErrorMsg a.close').click(function(){
        $('#loginErrorMsg').hide(200);
    });
    
    $('#registerErrorMsg a.close').click(function(){
        $('#registerErrorMsg').hide(200);
    });
    
    $('#newPasswordErrorMsg a.close').click(function(){
        $(this).parent().hide(200);
    })
    
    // bellow for relative time
    
    var $relative_time = $('span[_relative_time]');
    var _relative;
    var _realtime;
    var _difftime;
    var _nowtime = new Date();
    _nowtime = _nowtime.getTime().toString().slice(0, -3);
    _nowtime = parseInt(_nowtime);
    
    var _month = 30 * 24 * 60 * 60;
    var _day = 24 * 60 * 60;
    var _hour = 60 * 60;
    var _min = 60;
    
    var _pass_m, _pass_d, _pass_h, _pass_min;
    
    for(var i=0; i<$relative_time.length; i++){
        _relative = $($relative_time[i]);
        _realtime = parseInt(_relative.attr('_relative_time'));
        _difftime = _nowtime - _realtime;
        
        if(_difftime < 300){
            _relative.text('刚刚更新，热乎乎的哦');
            continue;
        }
        
        _pass_m = parseInt(_difftime / _month);
        _pass_d = parseInt(_difftime / _day);
        _pass_h = parseInt(_difftime / _hour);
        _pass_min = parseInt(_difftime / _min);
        
        if(_pass_m > 11){
            _relative.text('1年前');
            continue;
        }
        else if(_pass_m > 0){
            _relative.text(_pass_m + '个月前');
            continue;
        }
        else if(_pass_d > 0){
            _relative.text(_pass_d + '天前');
            continue;
        }
        else if(_pass_h > 0){
            _relative.text(_pass_h + '小时前');
            continue;
        }
        else if(_pass_min > 4){
            _relative.text(_pass_min + '分钟前');
            continue;
        }
        else{
            _relative.text('刚刚更新，热乎乎的哦');
            continue;
        }
    }
    
    
    // join/quit node
    
    $('#memberNodeBtn').click(function(){
        if($(this).attr('_action_value') == '0'){
            $('#memberNodeConfirm').show(200);
        }
        else{
            _start_post_for_node();
        }
        
    });
    
    $('#memberNodeConfirm a.close').click(function(){
        $('#memberNodeConfirm').hide(200);
    });
    $('#memberNodeConfirmCancel').click(function(){
        $('#memberNodeConfirm').hide(200);
    });
    $('#memberNodeConfirmYes').click(function(){
        $('#memberNodeConfirm').hide(200);
        _start_post_for_node();
    });
    
    $('#showLoginAlertNode a.close').click(function(){
        $(this).parent().hide(200);
    });
    
    
    // delete a notify
    $('span[_remove_notify]').click(function(){
        var notify_id = $(this).attr('_remove_notify');
         _start_post_for_notify(notify_id);
        $(this).parent().parent().parent().hide(200);
        return false;
    });
    
    $('a[_remove_notify]').click(function(){
        var notify_id = $(this).attr('_remove_notify');
         _start_post_for_notify(notify_id);
        $(this).parent().parent().hide(200);
        return true;
    });
});


function _start_post_for_notify(notify_id){
    $.ajax(
        {
            type: 'POST',
            url: '/member-notify/',
            data:{
                notify_id: notify_id,
                csrfmiddlewaretoken: get_csrf(),
            },
            async: true,
        }
    );
}


function show_error_msg(text){
    $('#registerErrorMsg').hide();
    $('#registerErrorMsg strong').text(text);
    $('#registerErrorMsg').show(200);
    return;
}

function strip(value){
    return value.replace(/(^\s+|\s+$)/, '');
}

function get_csrf(){
    return $('input[name=csrfmiddlewaretoken]').attr('value');
}


function _start_post_for_node(){
    $.ajax(
        {
            type: 'POST',
            url: '/member-node/',
            data:{
                node_name: $('#memberNodeBtn').attr('_node_name'),
                action: $('#memberNodeBtn').attr('_action_value'),
                csrfmiddlewaretoken: get_csrf(),
            },
            async: false,
            success: function(data){
                $this_btn = $('#memberNodeBtn');
                if(data=='0'){
                    $this_btn.removeClass('btn-success');
                    $this_btn.addClass('btn-warning');
                    $this_btn.attr('_action_value', '0');
                    $this_btn.text('退出');
                }
                else if(data=='1'){
                    $this_btn.removeClass('btn-warning');
                    $this_btn.addClass('btn-success');
                    $this_btn.attr('_action_value', '1');
                    $this_btn.text('加入');
                }
            }
        }
    );
}




function show_login_alert_node(){
    $('#showLoginAlertNode').show(200);
}


$(function(){
    $('#renewPasswordForm button').click(function(){
        if($(this).hasClass('disabled')){
            return false;
        }
        var email = $('#renewPasswordForm input[name=email]').val();
        email = strip(email);
        if(!email.length){
            $('#renewPasswordErrorMsg').hide(200);
            $('#renewPasswordErrorMsg strong').text('请输入邮箱');
            $('#renewPasswordErrorMsg').show(200);
            return false;
        }
        
        var _tmp_email = email.replace(/^.+@.+\..+$/, '');
        if(_tmp_email.length){
            $('#renewPasswordErrorMsg').hide(200);
            $('#renewPasswordErrorMsg strong').text('邮箱格式不正确');
            $('#renewPasswordErrorMsg').show(200);
            return false;
        }
        $(this).addClass('disabled');
        return true;
    });
    
    $('#renewPasswordErrorMsg a.close').click(function(){
        $(this).parent().hide(200);
    });
    
    
    $('#changePasswordForm button').click(function(){
        var check_email = $('#changePasswordForm input[name=check_email]').val();
        var email = $('#changePasswordForm input[name=email]').val();
        var password = $('#changePasswordForm input[name=password]').val();
        if(check_email=='1'){
            email = strip(email);
            if(!email.length){
                $('#changePasswordErrorMsg').hide(200);
                $('#changePasswordErrorMsg strong').text('请输入邮箱');
                $('#changePasswordErrorMsg').show(200);
                return false;
            }
            
            var _tmp_email = email.replace(/^.+@.+\..+$/, '');
            if(_tmp_email.length){
                $('#changePasswordErrorMsg').hide(200);
                $('#changePasswordErrorMsg strong').text('邮箱格式不正确');
                $('#changePasswordErrorMsg').show(200);
                return false;
            }
        }
        password = strip(password);
        if(!password.length){
                $('#changePasswordErrorMsg').hide(200);
                $('#changePasswordErrorMsg strong').text('请输入密码');
                $('#changePasswordErrorMsg').show(200);
                return false;
        }
        if(password.length < 4){
                $('#changePasswordErrorMsg').hide(200);
                $('#changePasswordErrorMsg strong').text('密码至少4个字符');
                $('#changePasswordErrorMsg').show(200);
                return false;
        }
        return true;
    });
    
    $('#changePasswordErrorMsg a.close').click(function(){
        $(this).parent().hide(200);
    })
});