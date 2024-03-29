
/*
*   Global navbar scroll listener
*/
window.addEventListener('scroll', function() {
    let items = document.querySelectorAll('.navbar.second');
    let scrollPosition = window.scrollY;

    items.forEach(function(item) {
        if (scrollPosition > 90) {
            item.classList.remove("py-4");
            item.classList.add("py-2");
        }
        else if (scrollPosition < 50) {
            item.classList.add("py-4");
            item.classList.remove("py-2");
        }
    });
});