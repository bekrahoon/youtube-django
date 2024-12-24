document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.querySelector('input[type="file"]');
    const fileNameDisplay = document.createElement("span");

    if (fileInput) {
        fileInput.addEventListener("change", function () {
            const fileName = fileInput.files[0] ? fileInput.files[0].name : "";
            fileNameDisplay.textContent = fileName ? `Selected file: ${fileName}` : "";
            fileInput.parentNode.appendChild(fileNameDisplay);
        });
    }
});

