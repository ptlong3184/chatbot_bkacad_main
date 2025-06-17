$(document).ready(function() {
      
      $('#owl-slideshow').owlCarousel({
    		autoplay: true, //Set AutoPlay to 3 seconds
            autoplaySpeed: 3000,
            //dragEndSpeed:3000,
            // smartSpeed:3000,
            loop: true,
            autoplayTimeout: 4000,
            autoplayHoverPause: true,
            pagination: true,
            items: 1,
            nav: false,
            animateOut: 'fadeOut'
    	}); //END: slideshow main

});