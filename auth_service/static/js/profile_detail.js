// Простая анимация для плавного появления элементов при загрузке страницы
window.addEventListener('load', function () {
    const profileDetail = document.querySelector('.profile-detail');
    profileDetail.style.opacity = 0;
    profileDetail.style.transition = 'opacity 0.5s ease-in-out';
    setTimeout(function () {
        profileDetail.style.opacity = 1;
    }, 100);
});

// WebSocket соединение
const socket = new WebSocket('ws://' + window.location.host + '/ws/subscribe/');

socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    const followersCount = document.getElementById('followers-count');

    if (data.action === 'subscribe') {
        document.getElementById('subscribe').style.display = 'none';
        document.getElementById('unsubscribe').style.display = 'inline-block';
    } else if (data.action === 'unsubscribe') {
        document.getElementById('subscribe').style.display = 'inline-block';
        document.getElementById('unsubscribe').style.display = 'none';
    }

    followersCount.textContent = data.followers_count;
};

function toggleSubscription(userId, action) {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            'action': action,
            'subscriber_id': userId,
            'subscribed_to_id': userId
        }));
    } else {
        console.error("WebSocket is not open.");
    }
}

