const stars_ = document.getElementsByClassName('rate-star');
const rating = document.getElementById('rating');

function removeColor() {
    for (let star of stars_) {
        star.classList.remove('orange');
    }
}

function addColor(stars) {
    let star, rest;
    [star, ...rest] = stars;
    if (star) {
        star.addEventListener('click', function(event) {
            removeColor();
            for (let s of stars) {
                s.classList.toggle('orange');
            }
            rating.value = stars.length;
        });
    }
    if (rest.length) {
        addColor(rest);
    }
}

addColor(stars_);