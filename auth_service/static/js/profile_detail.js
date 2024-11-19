// Простая анимация для плавного появления элементов при загрузке страницы
window.addEventListener('load', function () {
    const profileDetail = document.querySelector('.profile-detail');
    profileDetail.style.opacity = 0;
    profileDetail.style.transition = 'opacity 0.5s ease-in-out';
    setTimeout(function () {
        profileDetail.style.opacity = 1;
    }, 100);
});