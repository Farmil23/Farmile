document.addEventListener('DOMContentLoaded', () => {
    // Mengambil data konfigurasi dari objek global yang didefinisikan di HTML
    const CONFIG = window.CHAT_CONFIG;
    if (!CONFIG) {
        console.error('Chatbot configuration object is missing!');
        return;
    }

    // --- Definisi Semua Elemen ---
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-chat-btn');
    const chatWindow = document.getElementById('chat-window');
    const titleDisplay = document.getElementById('session-title');
    const titleInput = document.getElementById('session-title-input');
    const editBtn = document.getElementById('edit-title-btn');
    const historySidebar = document.getElementById('history-sidebar');
    const historyToggleBtn = document.getElementById('sidebar-toggle-btn');
    const historyCloseBtn = document.getElementById('close-sidebar-btn');
    const overlay = document.getElementById('sidebar-overlay');
    
    const sendIconSVG = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>`;
    const spinnerIconSVG = `<svg class="spinner" width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><style>.spinner{transform-origin:center;animation:spinner_StKS .75s linear infinite}@keyframes spinner_StKS{100%{transform:rotate(360deg)}}</style><circle cx="12" cy="12" r="10" fill="none" stroke-width="2" stroke="currentColor" opacity="0.3"/><path d="M12,2 A10,10 0 0,1 22,12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>`;

    /**
     * Menambahkan pesan baru ke jendela chat.
     * @param {string} role - 'user' atau 'assistant'
     * @param {string} content - Teks pesan
     * @param {boolean} isLoading - Apakah pesan ini adalah indikator loading
     */
    const appendMessage = (role, content, isLoading = false) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role === 'user' ? 'user' : 'ai'}`;

        const avatarSrc = role === 'user' ? CONFIG.userProfilePic : CONFIG.aiAvatarPic;
        messageDiv.innerHTML = `<img src="${avatarSrc}" alt="${role} avatar" class="avatar">`;

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'bubble';

        if (isLoading) {
            bubbleDiv.innerHTML = `<div class="typing-indicator"><span></span><span></span><span></span></div>`;
        } else {
            // --- PERUBAHAN UTAMA DI SINI ---
            // 1. Ubah konten Markdown menjadi HTML menggunakan marked.js
            bubbleDiv.innerHTML = window.marked ? marked.parse(content) : content;
            
            // 2. Terapkan syntax highlighting pada semua blok kode di dalam bubble baru ini
            if (window.hljs) {
                bubbleDiv.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });
            }
        }
        
        messageDiv.appendChild(bubbleDiv);
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };

    /**
     * Mengirim pesan ke backend dan menampilkan respons AI.
     */
    const sendChatMessage = async () => {
        const message = chatInput.value.trim();
        if (!message) return;

        appendMessage('user', message);
        chatInput.value = '';
        chatInput.style.height = 'auto'; // Reset tinggi textarea

        sendBtn.disabled = true;
        sendBtn.innerHTML = spinnerIconSVG;
        appendMessage('assistant', '', true); // Tampilkan indikator loading

        try {
            const response = await fetch(CONFIG.chatApiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            if (!response.ok) throw new Error('Network response was not ok.');
            
            const data = await response.json();
            
            // Hapus indikator loading sebelum menampilkan pesan dari AI
            const loadingIndicator = chatWindow.querySelector('.message.ai:last-child');
            if(loadingIndicator && loadingIndicator.querySelector('.typing-indicator')) {
                loadingIndicator.remove();
            }

            appendMessage('assistant', data.response || 'Maaf, terjadi kesalahan.');
        } catch (error) {
            console.error('Fetch error:', error);
            const loadingIndicator = chatWindow.querySelector('.message.ai:last-child');
            if(loadingIndicator && loadingIndicator.querySelector('.typing-indicator')) {
                loadingIndicator.remove();
            }
            appendMessage('assistant', 'Tidak dapat terhubung ke server. Silakan coba lagi.');
        } finally {
            sendBtn.disabled = false;
            sendBtn.innerHTML = sendIconSVG;
        }
    };
    
    /**
     * Menyimpan judul sesi yang baru diedit ke backend.
     */
    const saveNewTitle = async () => {
        if (!titleInput || !titleDisplay) return;

        const newTitle = titleInput.value.trim();
        const oldTitle = titleDisplay.textContent.trim();

        titleInput.classList.add('hidden');
        titleDisplay.classList.remove('hidden');

        if (newTitle && newTitle !== oldTitle) {
            try {
                const response = await fetch(CONFIG.renameSessionUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title: newTitle })
                });
                const data = await response.json();
                if (data.status === 'success') {
                    titleDisplay.textContent = data.new_title;
                    const activeSessionLink = document.querySelector(`.session-item.active .session-title-link`);
                    if (activeSessionLink) activeSessionLink.textContent = data.new_title;
                } else {
                    titleDisplay.textContent = oldTitle; // Kembalikan jika gagal
                }
            } catch (error) { 
                console.error('Failed to save title:', error);
                titleDisplay.textContent = oldTitle; // Kembalikan jika error
            }
        }
    };
    
    /**
     * Mengelola visibilitas sidebar riwayat chat.
     */
    const toggleHistorySidebar = () => {
        if (historySidebar && overlay) {
            historySidebar.classList.toggle('visible');
            overlay.classList.toggle('active'); // Gunakan 'active' untuk konsistensi
        }
    };
    
    // --- Render Pesan Awal & Pengaturan Awal ---
    chatWindow.innerHTML = '';
    if (CONFIG.initialMessages && Array.isArray(CONFIG.initialMessages)) {
        CONFIG.initialMessages.forEach(msg => {
            appendMessage(msg.role, msg.content);
        });
    }

    // --- Event Listeners ---
    if (sendBtn) sendBtn.addEventListener('click', sendChatMessage);
    
    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
        // Auto-resize textarea
        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = `${chatInput.scrollHeight}px`;
        });
    }

    if (editBtn) {
        editBtn.addEventListener('click', () => {
            if (titleDisplay && titleInput) {
                titleDisplay.classList.add('hidden');
                titleInput.classList.remove('hidden');
                titleInput.focus();
                titleInput.select();
            }
        });
    }

    if (titleInput) {
        titleInput.addEventListener('blur', saveNewTitle);
        titleInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') { 
                e.preventDefault(); 
                saveNewTitle(); 
            } else if (e.key === 'Escape') {
                titleInput.value = titleDisplay.textContent;
                titleInput.classList.add('hidden');
                titleDisplay.classList.remove('hidden');
            }
        });
    }

    // Event listeners untuk sidebar riwayat chat
    if (historyToggleBtn) historyToggleBtn.addEventListener('click', toggleHistorySidebar);
    if (historyCloseBtn) historyCloseBtn.addEventListener('click', toggleHistorySidebar);
    
    // Overlay sekarang bisa menutup kedua jenis sidebar
    if (overlay) {
        overlay.addEventListener('click', () => {
            // Menutup sidebar utama jika ada
            const mainSidebar = document.getElementById('dashboardSidebar');
            if (mainSidebar && mainSidebar.classList.contains('active')) {
                mainSidebar.classList.remove('active');
            }
            // Menutup sidebar riwayat chat
            if (historySidebar && historySidebar.classList.contains('visible')) {
                historySidebar.classList.remove('visible');
            }
            overlay.classList.remove('active');
        });
    }

    // --- Logika untuk Menu Aksi di Riwayat Chat ---
    document.body.addEventListener('click', (e) => {
        // Sembunyikan semua dropdown jika klik di luar
        if (!e.target.closest('.session-actions-btn')) {
            document.querySelectorAll('.actions-dropdown.visible').forEach(d => {
                d.classList.remove('visible');
            });
        }
    });

    document.querySelectorAll('.session-actions-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            const sessionId = e.currentTarget.dataset.sessionId;
            const dropdown = document.getElementById(`dropdown-${sessionId}`);

            const isVisible = dropdown.classList.contains('visible');

            // Sembunyikan semua dropdown lain
            document.querySelectorAll('.actions-dropdown.visible').forEach(d => d.classList.remove('visible'));
            
            // Toggle dropdown yang diklik
            if (!isVisible) {
                dropdown.classList.add('visible');
            }
        });
    });

    document.querySelectorAll('.rename-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            const activeSessionLink = document.querySelector('.session-item.active');
            const clickedSessionItem = e.currentTarget.closest('.session-item');

            if (activeSessionLink === clickedSessionItem && editBtn) {
                editBtn.click();
            } else {
                alert("Anda hanya bisa mengubah nama sesi yang sedang aktif.");
            }
        });
    });
});