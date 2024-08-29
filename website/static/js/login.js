const toggle_btn = document.querySelectorAll(".toggle");
const registerForm = document.querySelectorAll(".sign-up-mode");
const messageError = document.querySelectorAll('.alert.alert-warning');
const main = document.querySelector("main");
let eyeicon = document.getElementById('eyeicon')
let eyeicon1 = document.getElementById('eyeicon1')
let typepassword = document.getElementById('passworduser')
let typepassword1 = document.getElementById('passworduser1')
const sidebar = document.querySelector('.sidebar');
let subMenu = document.getElementById("subMenu");
const subsidebar = document.querySelector('.sub-sidebar');
const inputs = document.querySelectorAll(".input-field");

function showSidebar(){
  sidebar.style.display = 'flex';
}

function hideSidebar(){
  sidebar.style.display = 'none';
}

inputs.forEach((inp) => {
  inp.addEventListener("focus", () => {
    inp.classList.add("active");
  });
  inp.addEventListener("blur", () => {
    if (inp.value != "") return;
    inp.classList.remove("active");
  });
});
  
function toggleMenu(){
	subMenu.classList.toggle("open-menu");
}
  
function toggle(){
	subsidebar.classList.toggle("open-options");
}

toggle_btn.forEach((btn) => {
    btn.addEventListener("click", () => {
      main.classList.toggle("sign-up-mode");
      messageError.forEach((error) => {
          error.style.display = "none"; // Reset all error message divs
      });
    });
  });

/*Password Reveal*/
document.addEventListener("DOMContentLoaded", function() {

    // Login
    eyeicon.addEventListener('click', function() {
        // Toggle the type attribute of the password input field
        if (typepassword.type === 'password') {
            // If currently password type, change to text type to show the password
            typepassword.type = 'text';
            // Change the eye icon to open eye icon
            eyeicon.src = 'static/img/eye-open.png';
        } else {
            // If currently text type, change to password type to hide the password
            typepassword.type = 'password';
            // Change the eye icon to closed eye icon
            eyeicon.src = 'static/img/eye-close.png';
        }
    });

	//register
	eyeicon1.addEventListener('click', function() {
        // Toggle the type attribute of the password input field
        if (typepassword1.type === 'password') {
            // If currently password type, change to text type to show the password
            typepassword1.type = 'text';
            // Change the eye icon to open eye icon
            eyeicon1.src = 'static/img/eye-open.png';
        } else {
            // If currently text type, change to password type to hide the password
            typepassword1.type = 'password';
            // Change the eye icon to closed eye icon
            eyeicon1.src = 'static/img/eye-close.png';
        }
    });
});

function hideAlert() {
  var alertElement = document.getElementById('messageError');
  if (alertElement) {
      alertElement.style.display = 'none';
  }
}