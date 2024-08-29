const sidebar = document.querySelector('.sidebar');
let subMenu = document.getElementById("subMenu");
const subsidebar = document.querySelector('.sub-sidebar');
const messageError = document.querySelectorAll('.alert.alert-warning');
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
