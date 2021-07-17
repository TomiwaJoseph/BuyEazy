$(document).ready(function () {

    $('#all_cat').addClass('active');

    $(".carousel-item").eq(0).addClass('active');
    // $('div.carousel-inner > div:first-child').addClass('active')

    const filter = document.querySelector('#sidebar_filt_but');
    all_filter_buttons = filter.querySelectorAll('button');
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


    //Cart
    //Toggle
    setTimeout(function () {
        $('body').find('.cart').fadeIn('slow');
    }, 1000);
    
    $('#show_cart').click(function(e){
        e.preventDefault();
        know_state = $('.cart').attr("data-toggle")
        console.log(know_state)
        if (know_state == 'inactive'){
            $('body').addClass('modal-open');
            $('body').find('.cart').attr('data-toggle', 'active');
        }
        else {
            console.log('working active')
            $('body').removeClass('modal-open');
            $('body').find('.cart').attr('data-toggle', 'inactive');    
        };
    });


    $('.cart').on('click', '.label', function () {
        $('body').addClass('modal-open');
        $(this).parents('.cart').attr('data-toggle', 'active');
        //$('body').find('.cart').fadeIn('slow');
    });

    $('.cart').on('click', 'button.close, .overlay', function () {
        $('body').removeClass('modal-open');
        $('body').find('.cart').attr('data-toggle', 'inactive');
        // $(this).parents('.cart').attr('data-toggle', 'inactive');
        //$('body').find('.cart').fadeOut('slow');
    });
    //Toggle

    //Remove
    $('.cart').on('click', 'a[href="#remove"]', function () {
        $(this).parents('.media').fadeOut('300');
    });
    //Remove

    //Count
    $('.cart').on('click', '.input-group button[data-action="plus"]', function () {
        $(this).parents('.input-group').find('input').val(parseInt($(this).parents('.input-group').find('input').val()) + 1);
    });
    $('.cart').on('click', '.input-group button[data-action="minus"]', function () {
        if (parseInt($(this).parents('.input-group').find('input').val()) > 1) {
            $(this).parents('.input-group').find('input').val(parseInt($(this).parents('.input-group').find('input').val()) - 1);
        }
    });
    //Count
    //Cart

});