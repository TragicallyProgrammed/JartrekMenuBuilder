/*GLOBAL EVENTS*/
$(function () {
    //flashbox timout
    $('.flash_box').delay(5000).fadeOut("slow", function() {
        $(this).remove();
    });
});