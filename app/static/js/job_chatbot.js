document.addEventListener('DOMContentLoaded', () => {
    // Pastikan CONFIG ada sebelum melanjutkan
    if (typeof window.JOB_CHAT_CONFIG === 'undefined') {
        console.error('Job Chatbot configuration is missing!');
        return;
    }
    const CONFIG = window.JOB_CHAT_CONFIG;

    // Referensi ke elemen DOM
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-chat-btn');
    const chatWindow = document.getElementById('chat-window');

    // Fungsi untuk menambahkan satu pesan ke tampilan
    const appendMessage = (role, content, isLoading = false) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        if (isLoading) messageDiv.id = 'loading-indicator';

        const avatarSrc = role === 'user' ? CONFIG.userProfilePic : '/static/images/ai-avatar.png';
        messageDiv.innerHTML = `<img src="${avatarSrc}" alt="${role} avatar" class="avatar">`;
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'bubble';

        if (isLoading) {
            bubbleDiv.innerHTML = `<div class="typing-indicator"><span></span><span></span><span></span></div>`;
        } else {
            // Gunakan library 'marked' jika tersedia, jika tidak tampilkan teks biasa
            bubbleDiv.innerHTML = window.marked ? window.marked.parse(content) : content.replace(/\n/g, '<br>');
        }
        
        messageDiv.appendChild(bubbleDiv);
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };

    // Fungsi untuk menghapus indikator loading
    const removeLoadingIndicator = () => {
        document.getElementById('loading-indicator')?.remove();
    };
    
    // Fungsi untuk mengirim pesan ke backend
    const sendChatMessage = async (messageToSend) => {
        const message = messageToSend || chatInput.value.trim();
        if (!message) return;

        // Tampilkan pesan pengguna jika ini bukan pesan otomatis pertama
        if (!messageToSend) {
            appendMessage('user', message);
        }
        
        chatInput.value = '';
        chatInput.disabled = true;
        sendBtn.disabled = true;
        appendMessage('assistant', '', true); // Tampilkan loading

        try {
            const response = await fetch(CONFIG.chatApiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            
            removeLoadingIndicator();
            if (!response.ok) throw new Error('Network response was not ok.');
            
            const data = await response.json();
            appendMessage('assistant', data.response || 'Maaf, terjadi kesalahan.');

        } catch (error) {
            removeLoadingIndicator();
            appendMessage('assistant', 'Tidak dapat terhubung ke AI Coach saat ini.');
        } finally {
            chatInput.disabled = false;
            sendBtn.disabled = false;
            if (!messageToSend) chatInput.focus();
        }
    };

    // --- FUNGSI UTAMA SAAT HALAMAN DIBUKA ---
    const initializeChat = () => {
        // 1. Bersihkan jendela chat
        chatWindow.innerHTML = ''; 
        
        // 2. Tampilkan semua riwayat pesan yang sudah ada
        if (CONFIG.initialMessages && CONFIG.initialMessages.length > 0) {
            CONFIG.initialMessages.forEach(msg => {
                appendMessage(msg.role, msg.content);
            });
            chatWindow.scrollTop = chatWindow.scrollHeight;
        } else {
            // 3. Jika ini pertama kalinya chat dibuka, kirim sapaan awal
            sendChatMessage("Halo, bisa bantu aku persiapan untuk wawancara ini?");
        }
    };

    // Event Listeners
    sendBtn.addEventListener('click', () => sendChatMessage());
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    });

    // Jalankan fungsi utama
    initializeChat();
});