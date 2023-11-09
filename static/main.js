function alertDialog() {
    alert("제출이 완료되었습니다.");
}

document.addEventListener('DOMContentLoaded', function() {
    const stars = document.querySelectorAll(".four-rating span");
    stars.forEach((star, index) => {
        star.addEventListener("click", function() {
            stars.forEach((star, subIndex) => {
                if(subIndex <= index) {
                    star.textContent = "★";
                } else {
                    star.textContent = "☆";
                }
            });
        });
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const ratingContainer = document.querySelector('.four-rating');
    const ratingValue = 2; // 별점값을 이곳에 설정하십시오.
    
    for (let i = 0; i < 5; i++) {
        const star = document.createElement('div');
        if (i < ratingValue) {
            star.style.backgroundColor = "gold";
        }
        ratingContainer.appendChild(star);
    }
});

function toggleImage() {
    var img = document.getElementById('thumb-image');
    if (img.src.match(/thumb-up/)) {
        img.src = 'static/images/thumb-up-filled.png'; // '도움이 되었어요'를 클릭했을 때 변경될 이미지 경로
    } else {
        img.src = 'static/images/thumb-up.png'; // 다시 원래의 이미지 경로
    }
}