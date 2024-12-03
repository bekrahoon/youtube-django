// Простая анимация для плавного появления элементов при загрузке страницы
window.addEventListener('load', function () {
    const profileDetail = document.querySelector('.profile-detail');
    profileDetail.style.opacity = 0;
    profileDetail.style.transition = 'opacity 0.5s ease-in-out';
    setTimeout(function () {
        profileDetail.style.opacity = 1;
    }, 100);
});

function createWebSocket() {
    const userId = document.getElementById('user-id')?.value;
    const targetUserId = document.getElementById('target-user-id')?.value;

    if (!userId || !targetUserId) {
        console.error("Не все элементы DOM были найдены.");
        return null;
    }

    const url = `ws://http://127.0.0.1:8000//ws/subscribe/${userId}/${targetUserId}/`;
    console.log("WebSocket URL:", url);

    const chatSocket = new WebSocket(url);

    chatSocket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        console.log("Получено сообщение:", data);
        updateSubscriptionButton(data.action, data.subscribed_to_id);
        updateFollowersCount(data.followers_count);
    };

    chatSocket.onopen = function () {
        console.log("WebSocket соединение установлено.");
    };

    chatSocket.onerror = function (event) {
        console.error("Ошибка WebSocket:", event);
    };

    chatSocket.onclose = function (event) {
        console.log("WebSocket соединение закрыто:", event);
        if (event.wasClean) {
            console.log("Соединение было закрыто нормально.");
        } else {
            console.error("Ошибка при закрытии соединения:", event);
        }
    };

    return chatSocket;
}

function toggleSubscription() {
    const chatSocket = createWebSocket();

    if (chatSocket) {
        chatSocket.onopen = function () {
            const button = document.getElementById('subscribe');
            const action = button.innerText === "Подписаться" ? "subscribe" : "unsubscribe";
            const userId = document.getElementById('user-id').value;
            const targetUserId = document.getElementById('target-user-id').value;

            chatSocket.send(JSON.stringify({
                action: action,
                subscriber_id: userId,
                subscribed_to_id: targetUserId
            }));
            console.log("Сообщение отправлено:", { action, subscriber_id: userId, subscribed_to_id: targetUserId });
        };

        chatSocket.onerror = function (event) {
            console.error("Ошибка WebSocket:", event);
        };
    } else {
        console.error("WebSocket соединение не установлено.");
    }
}

function updateSubscriptionButton(action, subscribed_to_id) {
    const button = document.getElementById('subscribe');
    if (action === "subscribe") {
        button.innerText = "Отписаться";
        button.className = "btn btn-danger";
    } else if (action === "unsubscribe") {
        button.innerText = "Подписаться";
        button.className = "btn btn-success";
    }
}

function updateFollowersCount(count) {
    const followersCount = document.getElementById('followers-count');
    followersCount.innerText = count;
}




