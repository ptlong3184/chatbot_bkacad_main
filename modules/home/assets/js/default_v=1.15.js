$(document).ready(function () {

    $("#myPopup").modal("show");


    $('.owl_partner').owlCarousel({
        autoplay: true, //Set AutoPlay to 3 seconds
        autoplaySpeed: 1000,
        smartSpeed: 1000,
        loop: true,
        autoplayTimeout: 3500,
        autoplayHoverPause: true,
        pagination: true,
        margin: 10,
        items: 6,
        nav: true,
        dot: false,
        animateOut: 'fadeOut',
        responsive: {
            0: {
                items: 2,
            },
            500: {
                items: 3,
            },
            920: {
                items: 4,
            },
            1200: {
                items: 6,
            }
        }
    })
    ; //END: slideshow main

    // $(".owl-prev").prepend("<i class='fa fa-angle-left'/>  ");
    // $(".owl-next").prepend("<i class='fa fa-angle-right'/>  ");

});

// function checkFormsubmit____() {
//     $('label.label_error').prev().remove();
//     $('label.label_error').remove();
//     email_new = $('#email_new').val();
//
//     alert('is here');
//     // return false;
//     if (!notEmpty("home_name", "Bạn chưa nhập họ và tên")) {
//         return false;
//     }
//     if (!lengthMin("home_name", 6, '"Họ tên của bạn" phải 6 kí tự trở lên, vui lòng sửa lại!')) {
//         return false;
//     }
//
//     if (!notEmpty("home_phone", "Bạn chưa nhập số điện thoại."))
//         return false;
//
//     if (!isPhone("home_phone", "Số điện thoại không đúng."))
//         return false;
//
//     if (!lengthMin("home_phone", 8, 'Số điện thoại không đúng.')) {
//         return false;
//     }
//     if (!lengthMax("home_phone", 11, 'Số điện thoại không đúng.')) {
//         return false;
//     }
//
//     if (notEmpty("contact_email", "Bạn chưa nhập Email")) {
//
//         if (!emailValidator("contact_email", "Emal không đúng định dạng")) {
//             return false;
//         }
//     } else {
//
//     }
//     if ($('#home_email').val() != '') {
//         if (!emailValidator("home_email", "Emal không đúng định dạng")) {
//             return false;
//         }
//     }
//
//
//     if (!notEmpty("home_product", "Bạn chưa chọn sản phẩm đã mua")) {
//         return false;
//     }
//
//
//
//     if (!notEmpty("home_city", "Bạn chưa chọn Tỉnh/Thành phố")) {
//         return false;
//     }
//
//     if (!notEmpty("home_district", "Bạn chưa chọn Quận/Huyện")) {
//         return false;
//     }
//
//     // if (!notEmpty("contact_address", "Bạn chưa nhập địa chỉ")) {
//     //     return false;
//     // }
//
//
//     // if (!notEmpty("txtCaptcha", "Nhập mã xác minh"))
//     //     return false;
//
//
//     // $.ajax({
//     //     url: "/index.php?module=users&task=ajax_check_captcha&raw=1",
//     //     data: {txtCaptcha: $('#txtCaptcha').val()},
//     //     dataType: "text",
//     //     async: false,
//     //     success: function (data) {
//     //         console.log(data);
//     //         $('label.username_check').prev().remove();
//     //         $('label.username_check').remove();
//     //         if (data == '0') {
//     //             invalid('txtCaptcha', 'Captcha là không chính xác.');
//     //             //alert('Captcha is incorrect');
//     //             //console.log('--------');
//     //             return false;
//     //         } else {
//     //             valid('txtCaptcha');
//     //             console.log('+++');
//     //             document.contact.submit();
//     //             return true;
//     //         }
//     //     }
//     // });
// }