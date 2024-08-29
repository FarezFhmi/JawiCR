(function() {
    // Sidebar Show/Hide Functions
    window.showSidebar = function() {
        let sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.style.display = 'flex';
        }
    };
  
    window.hideSidebar = function() {
        let sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.style.display = 'none';
        }
    };
  
    // DOMContentLoaded Event Listener
    document.addEventListener('DOMContentLoaded', (event) => {
        const inputGallery = document.getElementById('fileInputGallery');
        const inputCamera = document.getElementById('fileInputCamera');
        const select = document.getElementById('select');
        const container = document.getElementById('container-photo');
        const dragArea = document.getElementById('dragArea');
        const uploadForm = document.getElementById('uploadForm');
        const messageError = document.getElementById('messageError');
        const modal = document.getElementById('fileChooserModal');
        const closeModal = document.querySelector('.close');
        const chooseCamera = document.getElementById('chooseCamera');
        const chooseGallery = document.getElementById('chooseGallery');
        const uploadButton = document.querySelector('button[type="submit"]');
        let file = null;
  
        /* CLICK LISTENER */
        if (select && inputGallery && inputCamera) {
            select.addEventListener('click', () => modal.style.display = 'block');
  
            chooseCamera.addEventListener('click', () => {
                inputCamera.click();
                modal.style.display = 'none';
            });
  
            chooseGallery.addEventListener('click', () => {
                inputGallery.click();
                modal.style.display = 'none';
            });
  
            closeModal.addEventListener('click', () => modal.style.display = 'none');
  
            window.onclick = function(event) {
                if (event.target == modal) {
                    modal.style.display = 'none';
                }
            }
  
            /* INPUT CHANGE EVENT */
            inputGallery.addEventListener('change', () => {
                let selectedFiles = inputGallery.files;
                if (selectedFiles.length === 0) return;
                file = selectedFiles[0];
                showImage();
            });
  
            inputCamera.addEventListener('change', () => {
                let selectedFiles = inputCamera.files;
                if (selectedFiles.length === 0) return;
                file = selectedFiles[0];
                showImage();
            });
  
            /** SHOW IMAGE */
            function showImage() {
                container.innerHTML = `
                    <div class="image-preview">
                        <span onclick="delImage()">&times;</span>
                        <img src="${URL.createObjectURL(file)}" />
                    </div>`;
            }
  
            /* DELETE IMAGE */
            window.delImage = function() {  // Make function available globally
                file = null;
                container.innerHTML = '';
                inputGallery.value = '';  // Clear the file input
                inputCamera.value = '';  // Clear the file input
            }
  
            /* DRAG & DROP */
            dragArea.addEventListener('dragover', e => {
                e.preventDefault();
                dragArea.classList.add('dragover');
            });
  
            dragArea.addEventListener('dragleave', e => {
                e.preventDefault();
                dragArea.classList.remove('dragover');
            });
  
            dragArea.addEventListener('drop', e => {
                e.preventDefault();
                dragArea.classList.remove('dragover');
                let droppedFiles = e.dataTransfer.files;
                if (droppedFiles.length > 0) {
                    file = droppedFiles[0];
                    showImage();
                }
            });
  
            // Submit form with selected file
            uploadForm.addEventListener('submit', e => {
                e.preventDefault();
                if (!file) {
                    messageError.style.display = 'block';
                    messageError.textContent = 'No file selected. Please choose a file to upload.';
                    return;
                }
                uploadButton.disabled = true;
                uploadButton.innerText = "Uploading...";
                const formData = new FormData();
                formData.append('imagefile', file);
                fetch(uploadForm.action, {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.text())
                .then(data => {
                    console.log('Success:', data);
                    document.open();
                    document.write(data);
                    document.close();
                })
                .catch(error => {
                    console.error('Error:', error);
                    uploadButton.disabled = false;
                    uploadButton.innerText = "Upload";
                });
            });
        }
    });
  
    // Input Field Focus/Blur Effects
    const inputs = document.querySelectorAll(".input-field");
    inputs.forEach((inp) => {
        inp.addEventListener("focus", () => {
            inp.classList.add("active");
        });
        inp.addEventListener("blur", () => {
            if (inp.value != "") return;
            inp.classList.remove("active");
        });
    });
  
    // Submenu Toggle Functions
    const subMenu = document.getElementById("subMenu");
    const subsidebar = document.querySelector('.sub-sidebar');
    window.toggleMenu = function() {
        if (subMenu) {
            subMenu.classList.toggle("open-menu");
        }
    };
  
    window.toggle = function() {
        if (subsidebar) {
            subsidebar.classList.toggle("open-options");
        }
    };
  
    // Carousel Functionality
    document.addEventListener("DOMContentLoaded", () => {
        const wrapper = document.querySelector(".wrapper");
        const carousel = document.querySelector(".carousel");
        const arrowBtns = document.querySelectorAll(".wrapper i");
        let currentIndex = 0;
        const cardCount = carousel.querySelectorAll("li.card").length;

        if (carousel && arrowBtns.length > 0) {
            const updateArrowVisibility = () => {
                if (cardCount <= 1) {
                    arrowBtns.forEach(btn => btn.classList.remove('show'));
                } else {
                    arrowBtns.forEach(btn => btn.classList.add('show'));
                }
            };
  
            updateArrowVisibility();
  
            arrowBtns.forEach(btn => {
                btn.addEventListener("click", () => {
                    const firstCardWidth = carousel.querySelector(".card").offsetWidth;
                    if (btn.id === "left") {
                        currentIndex = Math.max(currentIndex - 1, 0);
                    } else {
                        currentIndex = Math.min(currentIndex + 1, cardCount - 1);
                    }
                    carousel.scrollTo({
                        left: firstCardWidth * currentIndex,
                        behavior: "smooth"
                    });
                });
            });
  
            let isDragging = false;
            let startX, startScrollLeft;
  
            const dragStart = (e) => {
                isDragging = true;
                carousel.classList.add("dragging");
                startX = e.pageX;
                startScrollLeft = carousel.scrollLeft;
            };
  
            const dragging = (e) => {
                if (!isDragging) return;
                e.preventDefault();
                carousel.scrollLeft = startScrollLeft - (e.pageX - startX);
            };
  
            const dragStop = () => {
                if (!isDragging) return;
                isDragging = false;
                carousel.classList.remove("dragging");
                const firstCardWidth = carousel.querySelector(".card").offsetWidth;
                currentIndex = Math.round(carousel.scrollLeft / firstCardWidth);
                carousel.scrollTo({
                    left: firstCardWidth * currentIndex,
                    behavior: "smooth"
                });
            };
  
            carousel.addEventListener("mousedown", dragStart);
            carousel.addEventListener("mousemove", dragging);
            document.addEventListener("mouseup", dragStop);
        }
    });
})();

function hideAlert() {
    var alertElement = document.getElementById('messageError');
    if (alertElement) {
        alertElement.style.display = 'none';
    }
}