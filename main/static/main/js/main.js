$(document).ready(function () {

    $('.search').click(function (e) {
        e.preventDefault();
        $('.navbar form').fadeToggle();
        document.getElementById("search_text").focus();
    });

    $('#all_cat').addClass('active');

    $(".carousel-item").eq(0).addClass('active');
    // $('div.carousel-inner > div:first-child').addClass('active')

    const filter = document.querySelector('#sidebar_filt_but');
    // all_filter_buttons = filter.querySelectorAll('button');
    all_filter_buttons = $('#sidebar_filt_but').find('button')
    totalButtons = all_filter_buttons.length;

    for (let i = 0; i < totalButtons; i++) {
        const button = all_filter_buttons[i]
        button.addEventListener('click', function () {
            for (let j = 0; j < totalButtons; j++) {
                all_filter_buttons[j].classList.remove('active');
            }
            this.classList.add('active');
        })
    };

    // $('li.active').removeClass('active');
    // $('a[href="' + location.pathname + '"]').closest('li').addClass('active');


    //Toggle
    setTimeout(function () {
        $('body').find('.cart').fadeIn('slow');
    }, 1000);
    
    $('#show_cart').click(function(e){
        e.preventDefault();
        know_state = $('.cart').attr("data-toggle")
        if (know_state == 'inactive'){
            $('body').addClass('modal-open');
            $('body').find('.cart').attr('data-toggle', 'active');
        }
        else {
            $('body').removeClass('modal-open');
            $('body').find('.cart').attr('data-toggle', 'inactive');    
        };
    });

    $('.cart').on('click', '.label', function () {
        $('body').addClass('modal-open');
        $(this).parents('.cart').attr('data-toggle', 'active');
    });

    $('.cart').on('click', 'button.close, .overlay', function () {
        $('body').removeClass('modal-open');
        $('body').find('.cart').attr('data-toggle', 'inactive');
    });
    //Toggle

});