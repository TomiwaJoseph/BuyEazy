
$(document).ready(function(){
    
    $('.newsletter-box').submit(function(event){
        event.preventDefault();
        $.ajax({
            url: 'newsletter/',
            type: 'POST',
            data: $('.newsletter-box').serialize(),
            success: function(response){
                $('#success_tic').modal('show');
            }
        });
    });

    $(".wishlist_btn").click(function(){
        var prod_id;
        prod_id = $(this).attr("data-id")
        $.ajax({
            url: 'add_to_wishlist/',
            method: 'GET',
            data: {
                product_id: prod_id,
            },
            success: function(response){
                $('.modal-content h2').html('Added to Wishlist')
                $('.modal-content p').html('This product has been successfully added to your wishlist')
                $('#success_tic').modal('show');
            }
        });
    });

    $(".add_to_cart_btn").click(function(){
        var prod_id;
        prod_id = $(this).attr("data-id")
        $.ajax({
            url: 'add_to_cart/',
            method: 'GET',
            data: {
                product_id: prod_id,
            },
            success: function(response){
                console.log('Successful!');
                cart_items_count = $('.badge-danger').html()
                $('.badge-danger').html(parseInt(cart_items_count)+1)

            }
        });
    })




})