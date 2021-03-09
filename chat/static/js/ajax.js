$('.likes-button').click(function(){
    let ans = $(this).attr("data-ans");
    $.get('/add_like/', {answer_id: ans}, function(data){
        $('#like_count').html(data);
    });
});

$('.dismiss-button').click(function(){
    let ans = $(this).attr("data-ans");
    $.get('/dismiss_like/', {answer_id: ans}, function(data){
        $('#dismiss_count').html(data);
    });
});