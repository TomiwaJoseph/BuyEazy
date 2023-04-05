$(document).ready(function () {
  $(function () {
    $("input").blur();
  });

  $(".search").click(function (e) {
    e.preventDefault();
    $(".navbar form").fadeToggle();
    document.getElementById("search_text").focus();
  });

  $(".carousel-item").eq(0).addClass("active");

  $("li.active").removeClass("active");
  $('a[href="' + location.pathname + '"]')
    .closest("li")
    .addClass("active");

  //Toggle
  setTimeout(function () {
    $("body").find(".cart").fadeIn("slow");
  }, 1000);

  $(".cart").on("click", ".label", function () {
    $("body").addClass("modal-open");
    $(this).parents(".cart").attr("data-toggle", "active");
  });

  $(".cart").on("click", "button.close, .overlay", function () {
    $("body").removeClass("modal-open");
    $("body").find(".cart").attr("data-toggle", "inactive");
  });
  //Toggle

  $("#dash_btn").addClass("active");
  $("#dashboard_section").show();
  $("#wishlist_section").hide();
  $("#orders_section").hide();
  $("#password_change_section").hide();
  $("#your_addresses_section").hide();

  all_sidebar_buttons = $("#dashboard_sidebar").find("button");
  sidebarButtonCount = all_sidebar_buttons.length;

  for (let i = 0; i < sidebarButtonCount; i++) {
    const side_buttons = all_sidebar_buttons[i];
    side_buttons.addEventListener("click", function () {
      for (let j = 0; j < sidebarButtonCount; j++) {
        all_sidebar_buttons[j].classList.remove("active");
      }
      this.classList.add("active");
      if (this.innerHTML == "Wishlist") {
        $("#dashboard_section").hide();
        $("#wishlist_section").show();
        $("#orders_section").hide();
        $("#password_change_section").hide();
        $("#your_addresses_section").hide();
      } else if (this.innerHTML == "Orders") {
        $("#dashboard_section").hide();
        $("#orders_section").show();
        $("#wishlist_section").hide();
        $("#password_change_section").hide();
        $("#your_addresses_section").hide();
      } else if (this.innerHTML == "Dashboard") {
        $("#dashboard_section").show();
        $("#orders_section").hide();
        $("#wishlist_section").hide();
        $("#password_change_section").hide();
        $("#your_addresses_section").hide();
      } else if (this.innerHTML == "Profile edit") {
        $("#dashboard_section").hide();
        $("#password_change_section").show();
        $("#orders_section").hide();
        $("#wishlist_section").hide();
        $("#your_addresses_section").hide();
      } else {
        $("#dashboard_section").hide();
        $("#your_addresses_section").show();
        $("#password_change_section").hide();
        $("#orders_section").hide();
        $("#wishlist_section").hide();
      }
    });
  }
});
