$(document).ready(function () {

    $("nav#menu").mmenu();
    var API = $('nav#menu').data("mmenu");

    $('#call_menu').click(function () {
        API.open();
    });

});
