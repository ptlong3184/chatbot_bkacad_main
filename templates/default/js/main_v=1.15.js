//<![CDATA[
$(window).on('load', function () { // makes sure the whole site is loaded
    $('.loader').fadeOut(); // will first fade out the loading animation
    $('.preloader').delay(350).fadeOut('slow'); // will fade out the white DIV that covers the website.
    $('body').delay(350).css({
        'overflow': 'visible'
    });
})
//]]>
var is_rewrite = 1;
var root = '/';
(function () {
    if (navigator.userAgent.match(/IEMobile\/10\.0/)) {
        var msViewportStyle = document.createElement("style");
        msViewportStyle.appendChild(
            document.createTextNode(
                "@-ms-viewport{width:auto!important}"
            )
        );
        document.getElementsByTagName("head")[0].appendChild(msViewportStyle);
    }
})();

function changeCaptcha() {
    var date = new Date();
    var captcha_time = date.getTime();
    $("#imgCaptcha").attr({
        src: '/libraries/jquery/ajax_captcha/create_image.php?' + captcha_time
    });
}

function changeCaptcha2() {
    var date = new Date();
    var captcha_time = date.getTime();
    $("#imgCaptcha2").attr({
        src: '/libraries/jquery/ajax_captcha/create_image.php?' + captcha_time
    });
}

function openNav() {
    document.getElementById("myNav").style.height = "100%";
}

function closeNav() {
    document.getElementById("myNav").style.height = "0%";
}

$(document).ready(function () {

    $("#close-cart").click(function () {
        $(".wrapper-popup").hide();
        $(".wrapper-popup-2").hide();
        $(".full").hide();
    });
    $(".show-info-member").click(function () {
        $(".title-login-club ul").toggle("slow");
    });

    $(".full").click(function () {
        $(".wrapper-popup").hide();
        $(".wrapper-popup-2").hide();
        $("#wrapper-video").hide();
        $(".full").hide();
        $("#basic-setup-example").hide();
    });


    $('#mm-blocker').on('click', function () {
        var menu = $('#menu');
        menu.addClass('hide').hide();
    });
    // menu- responsive
    $('#search-mobile').on('click', function () {
        var menu = $(this);
        if (menu.hasClass('open')) {
            menu.removeClass('open');
            $('#search_form').removeClass('open').slideUp(200);
        } else {
            menu.addClass('open');
            $('#search_form').addClass('open').slideDown(200);
        }
    });

    $(window).scroll(function () {
        if (window.innerWidth < 767) {
            $(".group-modal").css("display", "none").fadeIn("10000");
        }
        if ($(this).scrollTop() > 300) {
            $('.scrollToTop').fadeIn().addClass('active');
            //$('.group-modal').fadeIn().addClass('active');
        } else {
            $('.scrollToTop').fadeOut().removeClass('active');
            //$('.group-modal').fadeOut().removeClass('active');
        }
    });

    //Click event to scroll to top
    $('.scrollToTop').click(function () {
        $('html, body').animate({
            scrollTop: 0
        }, 800);
        return false;
    });

    $('#nav_tab a').click(function () {
        var id = $(this).data('id');
        $('#groupModal .tab-pane').hide();
        $('#tab-pane-' + id).show();
    });

    $('.c-box_search .c-call_search').click(function () {
        $(".c-box_search .search-box").toggle(400);
        return false;
    })

});

function OpenPrint() {
    u = location.href;
    window.open(u + "?print=1");
    return false;
}


function registration() {
    $.ajax({
        type: 'GET',
        dataType: 'html',
        url: '/index.php?module=users&view=users&raw=1&task=registration',
        success: function (data) {
            $("#wrapper-popup-2").html(data);
            close();
        }
    });
    $(".wrapper-popup-2").show();
    $(".full").show();

}

function login() {
    $.ajax({
        type: 'GET',
        dataType: 'html',
        url: '/index.php?module=users&view=users&raw=1&task=login',
        success: function (data) {
            $("#wrapper-popup-2").html(data);
            close();
        }
    });
    $(".wrapper-popup-2").show();
    $(".full").show();

}

function forget() {
    $.ajax({
        type: 'GET',
        dataType: 'html',
        url: '/index.php?module=users&view=users&raw=1&task=forget',
        success: function (data) {
            $("#wrapper-popup-2").html(data);
            close();
        }
    });
    $(".wrapper-popup-2").show();
    $(".full").show();

}

function close() {
    $("#close-cart").click(function () {
        $(".wrapper-popup").hide();
        $(".wrapper-popup-2").hide();
        $(".full").hide();
    });
}

function ajax_pop_cart() {
    $("#close-cart").click(function () {
        $(".wrapper-popup-2").hide();
        $(".wrapper-popup").hide();
        $(".full").hide();
    });
}


function order($id_pro) {
    // $('html,body').animate({scrollTop: '0px'}, 500);
    var $id = $id_pro;

    var $quan = $("#quantity").val();
    if ($quan == undefined)
        $quan = 1;
    else
        $quan = $quan;

    $.ajax({
        type: 'GET',
        dataType: 'html',
        url: '/index.php?module=products&view=product&raw=1&task=buy',
        data: "quantity=" + $quan + "&id=" + $id,
        success: function (data) {
            $("#wrapper-popup").html(data);
            ajax_pop_cart();
        }
    });
    $(".wrapper-popup").show();
    $(".full").show();
}


function del_cart($id) {

    $a = $('#' + $id).attr("data-tr");
    $("." + $a).hide();
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: '/index.php?module=products&view=cart&task=edel',
        data: "id=" + $id,
        success: function () {

        }
    });

// $(".continue-buy").click(function () {
//     document.order_form.submit();
// });
}

