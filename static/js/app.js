$(function() {
    $('#fab-trigger').click(function(e) {
        if ($(this).hasClass('fab-active')) {
            $(this).removeClass('fab-active');
            $('.fab-info').removeClass("fab-info-active")
            globalThis.fabActive = false
        } else {
            $(this).addClass('fab-active');
            $('.fab-info').addClass("fab-info-active")
            globalThis.fabActive = true
        }
        $(this).closest('div.floating-action-menu').toggleClass('active');
        e.stopPropagation()
    })
    $("#fab-trigger").click()
})
