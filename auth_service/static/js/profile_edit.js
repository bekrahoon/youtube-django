// Скрипт для подтверждения отправки формы
document.getElementById("profile-edit-form").addEventListener("submit", function (event) {
    if (!confirm("Вы уверены, что хотите сохранить изменения?")) {
        event.preventDefault();  // Отменяем отправку формы, если пользователь не подтвердил
    }
});

// Получаем токен из сессии
const token = sessionStorage.getItem('access_token');



const form = document.querySelector('#profile-edit-form');
form.addEventListener('submit', (e) => {
    e.preventDefault();

    const token = sessionStorage.getItem('access_token');
    const formData = new FormData(form);

    fetch('/profile/edit/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = `/profile/${data.pk}/`;
            } else {
                console.error('Error:', data.error);
            }
        })
        .catch(error => console.error('Error:', error));
});
