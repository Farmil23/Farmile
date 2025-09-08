// File: static/js/notifications.js

document.addEventListener('DOMContentLoaded', function() {
    const bellIcon = document.getElementById('notification-bell');
    if (!bellIcon) {
        return; 
    }

    const indicator = document.getElementById('notification-indicator');
    const panel = document.getElementById('notification-panel');
    const notificationList = document.getElementById('notification-list');

    const API_URL = '/api/notifications';
    const MARK_READ_URL = '/api/notifications/mark-as-read';

    let isPanelOpen = false;

    async function fetchNotifications() {
        try {
            const response = await fetch(API_URL);
            if (!response.ok) return;

            const data = await response.json();
            // --- DEBUG: Tampilkan data mentah dari API ---
            console.log("[NOTIFIKASI] Data diterima dari API:", data);
            updateNotificationUI(data.notifications, data.unread_count);
        } catch (error) {
            console.error("Gagal mengambil notifikasi:", error);
        }
    }

    function updateNotificationUI(notifications, unreadCount) {
        // --- DEBUG: Lihat apa yang diputuskan oleh fungsi ini ---
        console.log(`[NOTIFIKASI] Update UI dengan unreadCount: ${unreadCount}`);

        if (unreadCount > 0) {
            console.log("[NOTIFIKASI] KEPUTUSAN: Menampilkan indikator merah.");
            indicator.classList.add('visible');
            indicator.textContent = unreadCount > 9 ? '9+' : unreadCount;
        } else {
            console.log("[NOTIFIKASI] KEPUTUSAN: Menyembunyikan indikator merah.");
            indicator.classList.remove('visible');
        }

        notificationList.innerHTML = '';
        if (notifications.length === 0) {
            notificationList.innerHTML = '<li class="notification-item-empty">Tidak ada notifikasi baru.</li>';
        } else {
            notifications.forEach(notif => {
                const item = document.createElement('li');
                item.className = 'notification-item';
                if (!notif.is_read) {
                    item.classList.add('unread');
                }

                const link = document.createElement('a');
                link.className = 'dropdown-item';
                link.href = notif.link || '#';
                
                const message = document.createElement('div');
                message.className = 'message';
                message.textContent = notif.message;

                const timestamp = document.createElement('div');
                timestamp.className = 'timestamp';
                timestamp.textContent = new Date(notif.timestamp).toLocaleString('id-ID', {
                    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'
                });

                link.appendChild(message);
                link.appendChild(timestamp);
                item.appendChild(link);
                notificationList.appendChild(item);
            });
        }
    }

    async function markAsRead() {
        // --- DEBUG: Lihat kapan fungsi ini dipanggil ---
        console.log("[NOTIFIKASI] Memanggil fungsi markAsRead() untuk dikirim ke server.");
        try {
            await fetch(MARK_READ_URL, { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
             });
            indicator.classList.remove('visible');
        } catch (error) {
            console.error("Gagal menandai notifikasi sebagai dibaca:", error);
        }
    }

    bellIcon.addEventListener('click', function(event) {
        event.stopPropagation();
        isPanelOpen = !isPanelOpen;
        panel.classList.toggle('visible', isPanelOpen);
        
        // --- DEBUG: Lihat apakah kondisi untuk markAsRead terpenuhi ---
        console.log(`[NOTIFIKASI] Ikon lonceng diklik. Panel terbuka: ${isPanelOpen}. Indikator terlihat: ${indicator.classList.contains('visible')}`);

        if (isPanelOpen && indicator.classList.contains('visible')) {
            setTimeout(markAsRead, 2000);
        }
    });

    window.addEventListener('click', function() {
        if (isPanelOpen) {
            isPanelOpen = false;
            panel.classList.remove('visible');
        }
    });

    fetchNotifications();
    setInterval(fetchNotifications, 60000); 
});