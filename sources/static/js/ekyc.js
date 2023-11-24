// sidebar
let menu_btn = document.querySelector("#menu-btn");
let sidebar = document.querySelector(".sidebar");
let search_btn = document.querySelector(".bx-search-alt-2");


menu_btn.onclick = function () {
  sidebar.classList.toggle("active");
}

search_btn.onclick = function () {
  sidebar.classList.toggle("active");
}

function loading_on() {
  document.querySelector('.overlay').style.display = "block";
}

function loading_off() {
  document.querySelector('.overlay').style.display = "none";
}

function startCamera() {
  document.querySelector('#videoElementContainer').style.display = "block";
  document.querySelector('.container').style.display = "none";
}

