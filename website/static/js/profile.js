let eyeicon2 = document.getElementById('eyeicon2');
let eyeicon3 = document.getElementById('eyeicon3');
let eyeicon4 = document.getElementById('eyeicon4');
let typepassword2 = document.getElementById('password_old');
let typepassword3 = document.getElementById('password_new');
let typepassword4 = document.getElementById('password_confirm');
const sidebar = document.querySelector('.sidebar');
let subMenu = document.getElementById("subMenu");
const subsidebar = document.querySelector('.sub-sidebar');
const messageError = document.querySelectorAll('.alert.alert-warning');
const inputs = document.querySelectorAll(".input-field");

// Ensure Setting link always opens Profile Update
const settingLinks = document.querySelectorAll('#settingLink');

function showSidebar() {
    sidebar.style.display = 'flex';
}

function hideSidebar() {
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

function toggleMenu() {
    subMenu.classList.toggle("open-menu");
}

function toggle() {
    subsidebar.classList.toggle("open-options");
}

document.addEventListener("DOMContentLoaded", function() {
    // Password reveal functionality
    function togglePasswordVisibility(eyeIcon, passwordField) {
        eyeIcon.addEventListener('click', function() {
            if (passwordField.type === 'password') {
                passwordField.type = 'text';
                eyeIcon.src = 'static/img/eye-open.png';
            } else {
                passwordField.type = 'password';
                eyeIcon.src = 'static/img/eye-close.png';
            }
        });
    }

    // Initialize password visibility toggle
    togglePasswordVisibility(eyeicon2, typepassword2);
    togglePasswordVisibility(eyeicon3, typepassword3);
    togglePasswordVisibility(eyeicon4, typepassword4);
});

function hideAlert() {
    var alertElement = document.getElementById('messageError');
    if (alertElement) {
        alertElement.style.display = 'none';
    }
}
