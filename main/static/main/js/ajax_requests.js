$(document).ready(function () {
  $("#success_tic").on("hidden.bs.modal", function () {
    $(".cart .label").prop("disabled", false);
  });
  $("#success_tic").on("shown.bs.modal", function () {
    $(".cart .label").prop("disabled", true);
  });

  $(".label").on("click", function () {
    $.ajax({
      url: "/show-preview/",
      success: function (res) {
        $("#cart_preview_container").empty();
        $("#cart_preview_container").append(res.cart_contents);
      },
    });
  });

  $("#loadMore").click(function () {
    var _currentProducts = $(".product_box").length;
    var _each_load = 3;
    var _total = $(this).attr("data-total");
    $.ajax({
      url: "/load-more-products/",
      data: {
        limit: _each_load,
        offset: _currentProducts,
      },
      dataType: "json",
      beforeSend: function () {
        $("#loadMore").attr("disabled", true);
        $(".load-more-icon").addClass("fa-spin");
      },
      success: function (res) {
        $("#product_container").append(res.more_products);
        $("#loadMore").attr("disabled", false);
        $(".load-more-icon").removeClass("fa-spin");

        var _totalShowing = $(".product_box").length;
        if (_totalShowing == _total) {
          $("#loadMore").remove();
        }
      },
    });
  });

  $(".newsletter-box").submit(function (event) {
    event.preventDefault();
    $.ajax({
      url: "/newsletter/",
      type: "POST",
      data: $(".newsletter-box").serialize(),
      success: function (response) {
        $(".modal-content h2").html("Successful subscription");
        $(".modal-content p").html(
          "You will receive email alerts anytime a new product is added to shop"
        );
        $("#success_tic").modal("show");
      },
    });
  });

  $(document).on("click", ".wishlist_btn", function () {
    var _btn = $(this);
    var prod_id = $(this).attr("data-id");
    $.ajax({
      url: "/add-to-wishlist/",
      method: "GET",
      data: {
        product_id: prod_id,
      },
      success: function (response) {
        _btn.attr("disabled", true);
        _btn.addClass("active");
        $(".modal-content h2").text("Added to Wishlist");
        $(".modal-content p").text(
          "This product has been successfully added to your wishlist"
        );
        $("#success_tic").modal("show");
      },
    });
  });

  $(document).on("click", ".add_to_cart_btn", function () {
    var _btn = $(this);
    var _product_id = $(this).attr("data-id");
    var _product_title = $(this).attr("data-title");
    var _product_price = $(this).attr("data-price");
    var _product_image = $(this).attr("data-image");
    $.ajax({
      url: "/add-to-cart/",
      data: {
        product_id: _product_id,
        product_title: _product_title,
        product_price: _product_price,
        product_image: _product_image,
      },
      dataType: "json",
      beforeSend: function () {
        _btn.attr("disabled", true);
      },
      success: function (res) {
        $(".badge-danger").text(res.total_items);
        _btn.attr("disabled", true);
        _btn.addClass("active");
        $("#cart_update").html(res.total_items);
        $(".modal-content h2").text("Added to Cart");
        $(".modal-content p").text(
          "This product has been successfully added to your cart"
        );
        $("#success_tic").modal("show");
      },
    });
  });

  $(document).on("click", ".delete-product", function () {
    var _product_id = $(this).attr("data-item");
    $.ajax({
      url: "/delete-from-cart/",
      data: {
        id: _product_id,
      },
      success: function (res) {
        $(".badge-danger").text(res.totalItems);
        $("#cartList").html(res.data);
        // $('.gr-total .h5').text(' $ ' + res.total_amount)
      },
    });
  });

  $(document).on("click", ".update-product", function () {
    var _product_id = $(this).attr("data-item");
    var _quantity = $(".qty-" + _product_id).val();
    $.ajax({
      url: "/update-cart/",
      data: {
        id: _product_id,
        qty: _quantity,
      },
      success: function (res) {
        $("#cartList").html(res.data);
        // $('.gr-total .h5').text(' $ ' + res.total_amount)
      },
    });
  });

  $(document).on("click", ".del_wish_item", function () {
    var _product_id = $(this).attr("data-id");
    $.ajax({
      url: "/delete-wishlist-item/",
      data: {
        id: _product_id,
      },
      success: function (res) {
        $("#wishlist_section").html(res.wishlist_products);
        $(".modal-content h2").text("Deleted from wishlist");
        $(".modal-content p").text(
          "This product has been successfully deleted from your wishlist"
        );
        $("#success_tic").modal("show");
      },
    });
  });

  $(document).on("click", "#show_details", function () {
    var _ref_code = $(this).attr("data-code");
    $.ajax({
      url: "/show-order-details/",
      data: {
        ref_code: _ref_code,
      },
      dataType: "json",
      success: function (res) {
        $("#order_details_box").html(res.order_details);
      },
    });
  });

  //   const filter = document.querySelector("#sidebar_filt_but");
  all_filter_buttons = $("#sidebar_filt_but").find("button");
  totalButtons = all_filter_buttons.length;

  for (let i = 0; i < totalButtons; i++) {
    const button = all_filter_buttons[i];
    button.addEventListener("click", function () {
      for (let j = 0; j < totalButtons; j++) {
        all_filter_buttons[j].classList.remove("active");
      }
      this.classList.add("active");
      var _category = this.innerHTML;
      $.ajax({
        url: "/specific-category/",
        data: {
          _category: _category,
        },
        dataType: "json",
        success: function (res) {
          console.log("scroll to top now...");
          $("#product_container").html(res.filtered_products);
          $("#cat_div h4").html("All " + res.category);
          $("#loadMore").remove();
          $("html, body").animate({ scrollTop: 0 }, "slow");
        },
      });
    });
  }

  $("#filter_form").submit(function (event) {
    event.preventDefault();

    var slider = document.getElementById("slider-range");
    var slider_value = slider.noUiSlider.get();
    var min_value = $("#min_value").val(slider_value[0]);
    var max_value = $("#max_value").val(slider_value[1]);

    $.ajax({
      url: "/specific-category-and-price/",
      type: "POST",
      data: $("#filter_form").serialize(),
      dataType: "json",
      success: function (res) {
        $("#cat_div h4").html("Filtered products category and price");
        $("#loadMore").remove();
        $("html, body").animate({ scrollTop: 0 }, "slow");
        if (res.filtered_products.length != 3) {
          $("#product_container").html(res.filtered_products);
        } else {
          $("#product_container .no-products").html(
            "No product within price and category range..."
          );
          $(".product_box").hide();
        }
      },
    });
  });
});
