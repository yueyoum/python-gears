$(function(){
    $('#newTopic button').click(function(){
        var node = $('#newTopic select').val();
        var title = $('#newTopic input[name=title]').val();
        var content = $('#newTopic textarea').val();
        
        if(node=='选择日志所属的节点'){
            set_newtopic_error_msg('请选择节点');
            return false;
        }
        
        title = title.replace(/(^\s+|\s+$)/, '');
        if(!title.length){
            set_newtopic_error_msg('没有标题');
            return false;
        }
        if(title.length>100){
            set_newtopic_error_msg('标题不能超过100个字符');
            return false;
        }
        
        var _tmp_content = content.replace(/\s+/g, '');
        _tmp_content = _tmp_content.replace(/<.+?>/g, '');
        _tmp_content = _tmp_content.replace(/&nbsp;/g, '');
        if(_tmp_content.length<2){
            set_newtopic_error_msg('内容不能少于两个字符');
            return false;
        }
        return true;
    });
    
    
    $('#newTopicErrorMsg a').click(function(){
        $(this).parent().hide(200);
    });
    
    
    
    // like/unlike
    $('#showLoginAlert a.close').click(function(){
        $(this).parent().hide(200);
    });
    
    $('#topicLikeBtn').click(function(){
        if($(this).attr('_action_value') == '0'){
            $('#topicUnlikeConfirm').show(200);
        }
        else{
            _start_post_for_topic();
        }
    });
    
    $('#topicUnlikeConfirm a.close').click(function(){
        $('#topicUnlikeConfirm').hide(200);
    });
    $('#topicUnlikeConfirmCancel').click(function(){
        $('#topicUnlikeConfirm').hide(200);
    });
    $('#topicUnlikeConfirmYes').click(function(){
        $('#topicUnlikeConfirm').hide(200);
        _start_post_for_topic();
    });
    
    
    
    $('#replyBtn').click(function(){
        var content = $('#replyDiv textarea').val();
        var _tmp_content = content.replace(/\s+/g, '');
        _tmp_content = _tmp_content.replace(/<.+?>/g, '');
        _tmp_content = _tmp_content.replace(/&nbsp;/g, '');
        if(_tmp_content.length < 2){
            $('#replyErrorMsg').hide();
            $('#replyErrorMsg').show(200);
            return false;
        }
        return true;
    });
    
    $('#replyErrorMsg a').click(function(){
        $(this).parent().hide(200);
    });
    
    
    var $colorbox_imgs = $('a[rel=colorbox]');
    if($colorbox_imgs.length){
        $('a[rel=colorbox]').colorbox();
    }
    
    prettyPrint();
    
    var customXhePlugin = {
        Code:{c:'editor-insert-code', t:'插入代码', h:1, e:function(){
            var _this = this;
            _this.saveBookmark();
            var htmlCode = '<div><textarea id="xheCodeValue" wrap="soft" spellcheck="false" style="width:300px;height:100px;" /></div>\
                           <div style="text-align:right;"><input type="button" id="xheSave" value="确定" /></div>';
            var jCode = $(htmlCode);
            var jValue = $('#xheCodeValue', jCode);
            var jSave = $('#xheSave', jCode);
            
            jSave.click(function(){
                _this.loadBookmark();
                _this.pasteHTML('<pre class="prettyprint prettyprint-custom">' + _this.domEncode(jValue.val()) + '</pre>');
                _this.appendHTML('<br/>');
                _this.hidePanel();
                return false;
            });
            _this.showDialog(jCode);
        }},
        
        LinkImg:{c:'editor-link-image', t:'链接图片', h:1, e:function(){
            var _this = this;
            _this.saveBookmark();
            var htmlCode = '<div><input id="xheLinkImg" type="text" style="width:300px; height:20px;"/></div>\
                           <div style="text-align:right;"><input type="button" id="xheSave" value="确定" /></div>';
            
            var jCode = $(htmlCode);
            var jValue = $('#xheLinkImg', jCode);
            var jSave = $('#xheSave', jCode);
            
            jSave.click(function(){
                _this.loadBookmark();
                _this.pasteHTML('<p><a href="' + _this.domEncode(jValue.val()) + '" target="_blank" rel="colorbox"><img src="' + _this.domEncode(jValue.val()) + '" width="300"/></a></p>');
                _this.appendHTML('<br/>');
                _this.hidePanel();
                return false;
            });
            _this.showDialog(jCode);
        }},
        
    };
    
    var topic_editor = $('#topicEditor');
    var _editor;
    if(topic_editor.length){
        _editor = topic_editor;
        topic_editor.xheditor(
            {
                tools: 'Blocktag,FontSize,Bold,Italic,Underline,Strikethrough,FontColor,BackColor,|,List,Outdent,Indent,Link,Unlink,Removeformat,|,LinkImg,Flash,Table,Code,|,Preview,About',
                plugins: customXhePlugin,
                loadCSS: '/static/lib/prettify/prettify.css',
                shortcuts: {
                            'alt+enter': function(){this.pasteHTML('<br/><br/>');},
                            'ctrl+enter': function(){this.appendHTML('<br/>');},
                            'alt+c': function(){quick_insert_code()},
                            },
                width: 600,
                height:600,
            }
        );
    }
    
    
    var $_replyDiv = $('#replyDiv');
    if($_replyDiv.length){
        var reply_y = $('#replyDiv').offset().top;
        $('#iWannaReplyBtn').click(function(){
            $('body, html').animate({scrollTop: reply_y}, 600);
        });
    }
        
    var reply_editor = $('#replyEditor');
    if(reply_editor.length){
        _editor = reply_editor;
        reply_editor.xheditor(
            {
                tools: 'Bold,Italic,Underline,FontColor,BackColor,|,List,Outdent,Indent,Link,Unlink,Removeformat,|,LinkImg,Flash,Code,About',
                plugins: customXhePlugin,
                loadCSS: '/static/lib/prettify/prettify.css',
                shortcuts: {
                            'alt+enter': function(){this.pasteHTML('<br/><br/>');},
                            'ctrl+enter': function(){this.appendHTML('<br/>');},
                            'alt+c': function(){quick_insert_code()},
                           },
                width: 550,
                height:300,
            }
        );
        
        
        $('span[_reply_user]').click(function(){
            var _this_user = $(this).attr('_reply_user');
            reply_editor.xheditor().pasteHTML('<p>回复 <a href="/member/' + $(this).attr('_reply_user') + '" _reply_to="' + $(this).attr('_reply_user') + '">' + $(this).attr('_reply_user') + '</a> ，' + $(this).text() + '楼:</p><br/>');
            $('body, html').animate({scrollTop: reply_y}, 600);
            return false;
        });
        
    };
    
    function quick_insert_code(){
        _editor.xheditor().pasteHTML('<pre class="prettyprint prettyprint-custom"></pre>');
    }
});



function _start_post_for_topic(){
    $.ajax(
        {
            type: 'POST',
            url: '/member-topic/',
            data:{
                topic_id: $('#topicLikeBtn').attr('_topic_id'),
                action: $('#topicLikeBtn').attr('_action_value'),
                csrfmiddlewaretoken: get_csrf(),
            },
            async: false,
            success: function(data){
                $this_btn = $('#topicLikeBtn');
                if(data=='0'){
                    $this_btn.removeClass('btn-success');
                    $this_btn.addClass('btn-warning');
                    $this_btn.attr('_action_value', '0');
                    $this_btn.text('不再喜欢');
                }
                else if(data=='1'){
                    $this_btn.removeClass('btn-warning');
                    $this_btn.addClass('btn-success');
                    $this_btn.attr('_action_value', '1');
                    $this_btn.text('喜欢');
                }
            }
        }
    );
}


function show_login_alert(){
    $('#showLoginAlert').show(200);
}


function set_newtopic_error_msg(msg){
    $('#newTopicErrorMsg').hide();
    $('#newTopicErrorMsg strong').text(msg);
    $('#newTopicErrorMsg').show(200);
}


$(function(){
})