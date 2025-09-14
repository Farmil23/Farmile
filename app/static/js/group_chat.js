document.addEventListener('DOMContentLoaded', () => {
    // Ambil konfigurasi dari template HTML
    const config = window.GROUP_CHAT_CONFIG;
    if (!config) {
        console.error("Konfigurasi chat grup tidak ditemukan!");
        return;
    }

    // Referensi ke elemen-elemen penting di halaman
    const chatWindow = document.getElementById('chat-window');
    const messageInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const welcomeMessage = chatWindow.querySelector('.chat-welcome');

    // Variabel untuk menyimpan ID pesan terakhir yang ditampilkan
    let lastMessageId = 0;

    /**
     * Fungsi untuk menampilkan satu pesan di jendela chat.
     * @param {object} msg - Objek pesan dari server.
     */
    const appendMessage = (msg) => {
        // Hapus pesan selamat datang jika ada
        if (welcomeMessage && !welcomeMessage.hidden) {
            welcomeMessage.hidden = true;
        }

        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');

        // Tentukan apakah pesan ini dari pengguna saat ini atau orang lain
        if (msg.author.id === config.currentUserId) {
            messageDiv.classList.add('user'); // Pesan dari diri sendiri (kanan)
        } else {
            messageDiv.classList.add('ai'); // Kita pinjam style 'ai' untuk penerima (kiri)
        }
        
        // Buat HTML untuk gelembung pesan
        messageDiv.innerHTML = `
            <img src="${msg.author.profile_pic}" alt="${msg.author.name}" class="avatar" title="${msg.author.name}">
            <div class="bubble">
                <p>${msg.content.replace(/\n/g, '<br>')}</p>
            </div>
        `;
        chatWindow.appendChild(messageDiv);

        // Perbarui ID pesan terakhir
        if (msg.id > lastMessageId) {
            lastMessageId = msg.id;
        }
    };

    /**
     * Fungsi untuk menggulir jendela chat ke pesan paling bawah.
     */
    const scrollToBottom = () => {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };

    /**
     * Fungsi untuk memuat semua riwayat pesan saat halaman dibuka,
     * atau hanya memuat pesan baru jika sudah ada pesan.
     */
    const loadMessages = async () => {
        try {
            // URL API untuk mengambil pesan
            const url = `/api/groups/${config.groupId}/messages`;
            const response = await fetch(url);
            if (!response.ok) throw new Error("Gagal memuat pesan.");

            const messages = await response.json();
            
            // Jika ini pertama kali memuat, bersihkan jendela dan tampilkan semua
            if (lastMessageId === 0) {
                chatWindow.innerHTML = ''; // Bersihkan jendela dari pesan "memuat"
                messages.forEach(appendMessage);
            } else {
                // Jika tidak, hanya tampilkan pesan yang lebih baru
                messages.forEach(msg => {
                    if (msg.id > lastMessageId) {
                        appendMessage(msg);
                    }
                });
            }

            // Selalu gulir ke bawah setelah memuat pesan
            scrollToBottom();

        } catch (error) {
            console.error(error);
            // Anda bisa menambahkan pesan error di UI jika diperlukan
        }
    };

    /**
     * Fungsi untuk mengirim pesan baru ke server.
     */
    const sendMessage = async () => {
        const content = messageInput.value.trim();
        if (!content) return;

        sendBtn.disabled = true;
        sendBtn.textContent = '...';

        try {
            const formData = new FormData();
            formData.append('message_type', 'text');
            formData.append('content', content);

            const response = await fetch(`/api/groups/${config.groupId}/messages`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Gagal mengirim pesan.');
            }

            const newMessage = await response.json();
            appendMessage(newMessage); // Tampilkan pesan baru secara instan
            scrollToBottom();
            messageInput.value = ''; // Kosongkan input
            messageInput.style.height = 'auto'; // Reset tinggi textarea
        } catch (error) {
            alert(error.message); // Tampilkan error jika gagal
        } finally {
            sendBtn.disabled = false;
            sendBtn.textContent = 'Kirim';
        }
    };

    // --- Event Listeners ---
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', (e) => {
        // Kirim dengan Enter, buat baris baru dengan Shift+Enter
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Auto-resize textarea
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = `${messageInput.scrollHeight}px`;
    });


    // --- Inisialisasi ---
    // Muat pesan saat halaman pertama kali dibuka
    loadMessages();

    // Polling: Memeriksa pesan baru setiap 5 detik
    setInterval(loadMessages, 5000);
});