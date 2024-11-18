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

document.addEventListener("DOMContentLoaded", function () {
    const deleteButton = document.querySelector('.btn-delete');

    if (deleteButton) {
        deleteButton.addEventListener('click', function (event) {
            const confirmation = confirm("Are you sure you want to delete this video? This action cannot be undone.");
            if (!confirmation) {
                event.preventDefault(); // Отменяем отправку формы, если пользователь не подтвердил
            }
        });
    }
});
