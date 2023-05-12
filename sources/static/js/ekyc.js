// sidebar
let menu_btn =  document.querySelector("#menu-btn");
let sidebar = document.querySelector(".sidebar");
let search_btn = document.querySelector(".bx-search-alt-2");


menu_btn.onclick = function(){
  sidebar.classList.toggle("active");
}

search_btn.onclick = function(){
  sidebar.classList.toggle("active");
}

button.onclick = () => {
  input.click();
};

p_button.onclick = () => {
    p_input.click();
};

function loading_on() {
  document.querySelector('.overlay').style.display = "block";
}

function loading_off() {
  document.querySelector('.overlay').style.display = "none";
}

function startCamera() {
    var videoElement = document.getElementById('videoElement');
    var cameraFrame = document.getElementById('videoElementContainer');

    // Check if video stream is already active
    if (videoElement.srcObject) {
        return;
    }

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            videoElement.srcObject = stream;
            videoElement.play();

            // Attach video to cameraFrame
            cameraFrame.appendChild(videoElement);
            document.querySelector('#videoElementContainer').style.display = "block";
            document.querySelector('.container').style.display = "none";
        })
        .catch(function (error) {
            console.error('Error accessing the camera.', error);
        });
}
