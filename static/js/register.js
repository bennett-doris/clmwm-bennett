function name_confirm(){
    $('#user_name').blur(
        $.get('/user/name_confirm',$(this).val,function (data){
            $('#is_confirm').html(data.message)
        })
    )
}



$(function () {
    name_confirm();

});