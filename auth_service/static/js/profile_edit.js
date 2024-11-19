// Скрипт для подтверждения отправки формы
document.getElementById("profile-edit-form").addEventListener("submit", function (event) {
    if (!confirm("Вы уверены, что хотите сохранить изменения?")) {
        event.preventDefault();  // Отменяем отправку формы, если пользователь не подтвердил
    }
});