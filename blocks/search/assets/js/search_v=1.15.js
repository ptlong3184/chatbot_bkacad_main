// function submit_form_search() {
//     //itemid = 9;
//     url = '';
//     var keyword = document.getElementById('keyword').value;
//     keyword = encodeURIComponent(encodeURIComponent(keyword));
//     var link_search = document.getElementById('link_search').value;
//
//     var $type = $('#type_search').val();
//
//     if (keyword && keyword != '') {
//         url += '&keyword=' + keyword + '&type=' + $type;
//         var check = 1;
//     } else {
//         var check = 0;
//     }
//     if (check == 0) {
//         alert('Bạn phải nhập tham số tìm kiếm');
//         return false;
//     }
//
//     var ccode = $('#ccode').val();
//     var cid = $('#cid').val();
//     if (cid && ccode) {
//         var link = link_search + ccode + '-cp' + cid + '.html' + url;
//     } else {
//         // var link_search = document.getElementById('link_search2').value;
//         var link = link_search + '/' + url + '.html';
//     }
// // alert(url);
// //     return false;
//
//     window.location.href = link;
//     return false;
// }

function submit_form_search() {
    itemid = 20;
    url = '';
    var keyword = document.getElementById('keyword').value;
    keyword = encodeURIComponent(encodeURIComponent(keyword));
    var link_search = document.getElementById('link_search').value;
    var type = $('#type_search').val();

    if (keyword != 'Tìm kiếm xe' && keyword != '') {
        url += '&keyword=' + keyword ;
        var check = 1;
    } else {
        var check = 0;
    }
    if (check == 0) {
        alert('Bạn chưa nhập từ khóa tìm kiếm!');
        return false;
    }


    var link = link_search + '/'  + keyword+'.html';

    window.location.href = link;
    return false;
}

$(document).ready(function () {
    // $('.item_cate').click(function () {
    //     var ccode = $(this).data('ccode');
    //     var cid = $(this).data('id');
    //     var name_cate = $(this).data('name');
    //     $('#find_name').html(name_cate);
    //     $('#ccode').val(ccode);
    //     $('#cid').val(cid);
    // })

    // $('#bt-search').click(function () {
    //
    //     if (submit_form_search())
    //         document.form_search.submit();
    // })
    // $('#bt_search_main').click(function () {
    //     // if (checkFormsubmit())
    //
    //     document.search_main.submit();
    // })
});


function checkFormsubmit() {


    return true;

}
