jQuery(document).ready(function($){
$('.testimnials_slides').slick({
  slidesToShow: 1,
  slidesToScroll: 1,
  dots:true,
  arrows: false,
  autoplay:true
  });
});



window.addEventListener("load", function () {

  console.log("🔥 FINAL AUTOPLAY START");

  const slider = document.querySelector('.product__media-list');
  const slides = document.querySelectorAll('.product__media-item');

  if (!slider || slides.length === 0) {
    console.log("❌ Slider not found");
    return;
  }

  let index = 0;
  let isPaused = false;

  function goToSlide(i) {
    console.log("➡️ Slide:", i);

    const slide = slides[i];

    // 🔥 FORCE ACTIVE (important for Dawn)
    slider.scrollLeft = slide.offsetLeft;

    // Trigger event (Shopify sync)
    slide.dispatchEvent(new Event('click', { bubbles: true }));
  }

  setInterval(() => {
    if (!isPaused) {
      index = (index + 1) % slides.length; // infinite loop
      goToSlide(index);
    }
  }, 3000);

  slider.addEventListener("mouseenter", () => {
    console.log("⏸ Pause");
    isPaused = true;
  });

  slider.addEventListener("mouseleave", () => {
    console.log("▶ Resume");
    isPaused = false;
  });

});