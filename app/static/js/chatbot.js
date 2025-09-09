// File: static/js/chatbot.js

document.addEventListener('DOMContentLoaded', () => {
    // Mengambil data dari objek global yang didefinisikan di HTML
    const CONFIG = window.CHAT_CONFIG;

    // --- Definisi Semua Elemen ---
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-chat-btn');
    const chatWindow = document.getElementById('chat-window');
    const titleDisplay = document.getElementById('session-title');
    const titleInput = document.getElementById('session-title-input');
    const editBtn = document.getElementById('edit-title-btn');
    const sidebar = document.getElementById('history-sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle-btn');
    const closeBtn = document.getElementById('close-sidebar-btn');
    const overlay = document.getElementById('sidebar-overlay');
    
    const sendIconSVG = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>`;
    const spinnerIconSVG = `<svg class="spinner" width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><style>.spinner{transform-origin:center;animation:spinner_StKS .75s linear infinite}@keyframes spinner_StKS{100%{transform:rotate(360deg)}}</style><circle cx="12" cy="12" r="10" fill="none" stroke-width="2" stroke="currentColor" opacity="0.3"/><path d="M12,2 A10,10 0 0,1 22,12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>`;

    /**
     * Menambahkan pesan baru ke jendela chat, dengan dukungan Markdown.
     */
    const addMessage = (text, sender, isMarkdown = false) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        const avatarSrc = sender === 'user' ? CONFIG.userProfilePic : CONFIG.aiAvatarPic;
        const avatar = `<img src="${avatarSrc}" class="avatar">`;
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'bubble';

        if (isMarkdown && window.marked) {
            bubbleDiv.innerHTML = marked.parse(text);
            bubbleDiv.querySelectorAll('pre code').forEach((block) => {
                if (window.hljs) hljs.highlightElement(block);
            });
        } else {
            bubbleDiv.textContent = text;
        }
        
        messageDiv.innerHTML = avatar;
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

        addMessage(message, 'user', false);
        chatInput.value = '';

        sendBtn.disabled = true;
        sendBtn.innerHTML = spinnerIconSVG;

        try {
            const response = await fetch(CONFIG.chatApiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            const data = await response.json();
            addMessage(data.response || data.error, 'ai', !data.error);
        } catch (error) {
            addMessage('Tidak dapat terhubung ke server.', 'ai', false);
        } finally {
            sendBtn.disabled = false;
            sendBtn.innerHTML = sendIconSVG;
        }
    };
    
    /**
     * Menyimpan judul sesi yang baru diedit ke backend.
     */
    const saveNewTitle = async () => {
        if (!titleInput) return;
        const newTitle = titleInput.value.trim();
        if (newTitle && newTitle !== titleDisplay.textContent) {
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
                }
            } catch (error) { console.error('Gagal menyimpan judul'); }
        }
        titleInput.classList.add('hidden');
        titleDisplay.classList.remove('hidden');
    };
    
    /**
     * Menampilkan atau menyembunyikan sidebar riwayat.
     */
    const toggleSidebar = () => {
        if (sidebar && overlay) {
            sidebar.classList.toggle('visible');
            overlay.classList.toggle('visible');
        }
    };
    
    // --- Render Pesan Awal dari Riwayat ---
    chatWindow.innerHTML = '';
    CONFIG.initialMessages.forEach(msg => {
        addMessage(msg.content, msg.role === 'user' ? 'user' : 'ai', msg.role !== 'user');
    });

    // --- Event Listeners ---
    if (sendBtn) sendBtn.addEventListener('click', sendChatMessage);
    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }

    if (editBtn) {
        editBtn.addEventListener('click', () => {
            titleDisplay.classList.add('hidden');
            titleInput.classList.remove('hidden');
            titleInput.focus();
            titleInput.select();
        });
    }

    if (titleInput) {
        titleInput.addEventListener('blur', saveNewTitle);
        titleInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') { e.preventDefault(); saveNewTitle(); } 
            else if (e.key === 'Escape') {
                titleInput.value = titleDisplay.textContent;
                titleInput.classList.add('hidden');
                titleDisplay.classList.remove('hidden');
            }
        });
    }

    if (toggleBtn) toggleBtn.addEventListener('click', toggleSidebar);
    if (closeBtn) closeBtn.addEventListener('click', toggleSidebar);
    if (overlay) overlay.addEventListener('click', toggleSidebar);

    // --- Logika untuk Menu Aksi ---
    document.querySelectorAll('.session-actions-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            const sessionId = e.currentTarget.dataset.sessionId;
            const dropdown = document.getElementById(`dropdown-${sessionId}`);

            document.querySelectorAll('.actions-dropdown.visible').forEach(d => {
                if (d !== dropdown) d.classList.remove('visible');
            });

            dropdown.classList.toggle('visible');
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

    window.addEventListener('click', () => {
        document.querySelectorAll('.actions-dropdown.visible').forEach(d => {
            d.classList.remove('visible');
        });
    });

    document.querySelectorAll('.actions-dropdown').forEach(dropdown => {
        dropdown.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    });
});