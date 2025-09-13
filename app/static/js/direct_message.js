document.addEventListener('DOMContentLoaded', () => {
    const config = window.DM_CONFIG;
    if (!config) return;

    const chatWindow = document.getElementById('chat-window');
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const apiUrl = `/api/messages/${config.conversationId}`;

    // Fungsi untuk menampilkan satu pesan di jendela chat
    const appendMessage = (msg) => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');

        // Tentukan apakah pesan ini dari pengguna saat ini atau orang lain
        if (msg.sender.id === config.currentUserId) {
            messageDiv.classList.add('user');
        } else {
            messageDiv.classList.add('ai'); // Kita pinjam style 'ai' untuk penerima
        }
        
        messageDiv.innerHTML = `
            <img src="${msg.sender.profile_pic}" alt="${msg.sender.name}" class="avatar">
            <div class="bubble">
                <p>${msg.content.replace(/\n/g, '<br>')}</p>
            </div>
        `;
        chatWindow.appendChild(messageDiv);
    };

    // Fungsi untuk menggulir ke pesan terakhir
    const scrollToBottom = () => {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };

    // Fungsi untuk memuat semua riwayat pesan
    const loadMessages = async () => {
        try {
            // Di dalam app/static/js/direct_message.js, fungsi loadMessages
            const response = await fetch(`/api/messages/${config.conversationId}`);
            const messages = await response.json();
            chatWindow.innerHTML = ''; // Bersihkan jendela
            messages.forEach(appendMessage);
            scrollToBottom();
        } catch (error) {
            console.error("Gagal memuat pesan:", error);
        }
    };

    // Fungsi untuk mengirim pesan baru
    const sendMessage = async () => {
        const content = messageInput.value.trim();
        if (!content) return;

        sendBtn.disabled = true;
        sendBtn.textContent = '...';

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: content }),
            });

            if (!response.ok) {
                throw new Error('Gagal mengirim pesan.');
            }

            const newMessage = await response.json();
            appendMessage(newMessage);
            scrollToBottom();
            messageInput.value = ''; // Kosongkan input
        } catch (error) {
            alert(error.message);
        } finally {
            sendBtn.disabled = false;
            sendBtn.textContent = 'Kirim';
        }
    };

    // Event Listeners
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Muat pesan saat halaman pertama kali dibuka
    loadMessages();

    // Polling: Memeriksa pesan baru setiap 5 detik
    setInterval(loadMessages, 5000);
});