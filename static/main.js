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



function menu1(){
  document.getElementById('nine_container1').className = 'active';
  document.getElementById('nine_container2').classList.remove('active');
  
  var list =  document.querySelector('.nine_list');
  var sold = document.querySelector('.nine_container2');
  var selling = document.querySelector('.nine_container1');

  selling.style.display = 'flex';
  sold.style.display = 'none';
  
  list.appendChild(sold);
}

function menu2(){
      document.getElementById('nine_container1').classList.remove('active');
      document.getElementById('nine_container2').className = 'active';
      
      var list =  document.querySelector('.nine_list');
      var sold = document.querySelector('.nine_container1');
      var selling = document.querySelector('.nine_container2');
    
      selling.style.display = 'none';
      sold.style.display = 'flex';

      list.appendChild(selling);

}


function like(likeDiv){
    if(likeDiv.textContent == '♡'){
      likeDiv.textContent = '❤';
    }else{
     likeDiv.textContent = '♡';
      }
  }

function toggleDiv(){
    var dropdownContent = document.getElementById("sortContents");
    if (dropdownContent.style.display === "block") {
      dropdownContent.style.display = "none";
    } else {
      dropdownContent.style.display = "block";
    }
    
}

var isIdChecked = false;
var isPasswordChecked = false;

function checkId() {
    var userId = document.getElementById('eight_userid').value;
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/check_id', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
        if (this.readyState == XMLHttpRequest.DONE && this.status == 200) {
            alert(this.responseText);
        }
    }
    xhr.send(JSON.stringify({id: userId}));
    isIdChecked = true;
}

function checkPassword() {
    var password = document.getElementById('eight_userpwd').value;
    var confirmPassword = document.getElementById('eight_userpwd_check').value;

    if (password === confirmPassword) {
        alert("비밀번호가 일치합니다.");
    } else {
        alert("비밀번호가 일치하지 않습니다.");
    }
    isPasswordChecked = true;
}

function submitForm() {
    var form = document.querySelector('form');
    var hiddenFieldId = document.createElement('input');
    hiddenFieldId.type = 'hidden';
    hiddenFieldId.name = 'isIdChecked';
    hiddenFieldId.value = isIdChecked;
    form.appendChild(hiddenFieldId);

    var hiddenFieldPw = document.createElement('input');
    hiddenFieldPw.type = 'hidden';
    hiddenFieldPw.name = 'isPasswordChecked';
    hiddenFieldPw.value = isPasswordChecked;
    form.appendChild(hiddenFieldPw);

    form.submit();
}