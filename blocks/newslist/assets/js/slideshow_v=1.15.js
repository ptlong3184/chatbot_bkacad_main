$(document).ready(function () {

    $('.owl_news').owlCarousel({
        autoplay: false, //Set AutoPlay to 3 seconds
        autoplaySpeed: 1000,

        //dragEndSpeed:3000,
        smartSpeed: 1000,
        loop: true,
        autoplayTimeout: 5000,
        autoplayHoverPause: true,
        pagination: true,
        margin: 25,
        items: 3,
        nav: false,
        dot: true,
        animateOut: 'fadeOut',
        responsive: {
            0: {
                items: 1.35,
                margin: 15,
                // stagePadding: 50,
            },
            500:{
                items: 2,
                margin: 15,
            },
            920:{
                margin:25
            }
        }
    })
    ; //END: slideshow main

    $(".owl-prev").prepend("<i class='fa fa-angle-left'/>  ");
    $(".owl-next").prepend("<i class='fa fa-angle-right'/>  ");
});