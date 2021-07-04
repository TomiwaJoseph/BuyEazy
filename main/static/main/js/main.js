$(document).ready(function () {

    $('#all_cat').addClass('active')

    const filter = document.querySelector('#sidebar_filt_but');
    all_filter_buttons = filter.querySelectorAll('button');
    totalButtons = all_filter_buttons.length;

    for (let i = 0; i < totalButtons; i++){
        const button = all_filter_buttons[i]
        button.addEventListener('click', function(){
            for (let j = 0; j < totalButtons; j++){
                all_filter_buttons[j].classList.remove('active');
            }
            this.classList.add('active');
        })
    }

    // $('li.active').removeClass('active');
    // $('a[href="' + location.pathname + '"]').closest('li').addClass('active');

    // $('.add_pho').click(function () {
    //     $('#add_try').show()
    //     $('#show_inp').removeClass('active')
    //     $('#tried').removeClass('active')
    //     $('#paint_comments').removeClass('active')
    //     $('#comments').hide()
    //     $('#tries').hide()
    //     $('#add_comment').hide()
    // })


    // $('.carousel-item').eq(0).addClass('active')
    // $('div.carousel-inner > div:first-child').addClass('active')

});
