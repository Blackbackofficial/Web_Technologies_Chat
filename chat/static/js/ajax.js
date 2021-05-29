$('.likes-button').click(function(){
    let ans = $(this).attr("data-ans");
    let answer = $(this).attr("answer");
    $.post('/add_like/', {answer_id: ans, answer: answer}, function(data) {
        if (data.rating !== "")
            $('#rating' + ans).text(data.rating);
        else {
            $('#rating' + ans).text(data.rating);
        }
    });
});


$('.correct-button').click(function(){
    let ans = $(this).attr("correct-ans");
    let answer = $(this).attr("answer");
    $.post('/is_correct/', {answer_id: ans, answer: answer});
});