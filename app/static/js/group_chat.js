// File: app/static/js/direct_message.js (Versi Final dengan Kunci Unik)

document.addEventListener('DOMContentLoaded', () => {
    const config = window.DM_CONFIG;
    if (!config) return;

    const chatWindow = document.getElementById('chat-window');
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const apiUrl = `/api/messages/${config.conversationId}`;
    
    let isSending = false; // Kunci untuk mencegah klik berturut-turut

    // Fungsi appendMessage dan scrollToBottom tetap sama...
    const appendMessage = (msg) => {
        if (document.querySelector(`.message[data-id='${msg.id}']`)) return;
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${msg.sender.id === config.currentUserId ? 'user' : 'ai'}`;
        messageDiv.dataset.id = msg.id;
        messageDiv.innerHTML = `
            <img src="${msg.sender.profile_pic}" alt="${msg.sender.name}" class="avatar">
            <div class="bubble"><p>${msg.content.replace(/\n/g, '<br>')}</p></div>`;
        chatWindow.appendChild(messageDiv);
    };
    const scrollToBottom = () => { chatWindow.scrollTop = chatWindow.scrollHeight; };

    const loadMessages = async () => {
        // Logika polling sederhana untuk pesan dari orang lain
        try {
            const response = await fetch(apiUrl);
            const messages = await response.json();
            messages.forEach(appendMessage);
        } catch (error) { console.error("Gagal memuat pesan:", error); }
    };

    const sendMessage = async () => {
        const content = messageInput.value.trim();
        if (!content || isSending) return;
        
        isSending = true; // <-- KUNCI DI SINI
        sendBtn.disabled = true;

        // --- TIKET UNIK ---
        // Buat sebuah ID unik untuk permintaan ini di sisi klien
        const requestId = `msg_${Date.now()}_${Math.random()}`;
        // --- AKHIR TIKET UNIK ---

        // Tampilkan pesan di UI secara optimis (tapi tanpa ID dari server)
        const tempMessageDiv = document.createElement('div');
        tempMessageDiv.className = 'message user pending'; // Beri class 'pending'
        tempMessageDiv.innerHTML = `
            <img src="${config.currentUserProfilePic}" alt="You" class="avatar">
            <div class="bubble"><p>${content.replace(/\n/g, '<br>')}</p></div>`;
        chatWindow.appendChild(tempMessageDiv);
        scrollToBottom();
        messageInput.value = '';

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    content: content,
                    request_id: requestId // Kirim tiket unik ke server
                }),
            });

            if (!response.ok) throw new Error('Gagal mengirim pesan.');
            
            const newMessages = await response.json();
            
            // Hapus pesan sementara dan ganti dengan pesan asli dari server
            tempMessageDiv.remove();
            newMessages.forEach(appendMessage); // Tampilkan semua pesan baru dari server

        } catch (error) {
            tempMessageDiv.remove(); // Hapus pesan sementara jika gagal
            alert(error.message);
        } finally {
            isSending = false; // <-- BUKA KUNCI DI SINI
            sendBtn.disabled = false;
        }
    };

    // --- Inisialisasi ---
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });

    // Muat semua pesan awal, lalu mulai polling
    fetch(apiUrl).then(res => res.json()).then(messages => {
        chatWindow.innerHTML = '';
        messages.forEach(appendMessage);
        scrollToBottom();
        setInterval(loadMessages, 5000);
    });
});