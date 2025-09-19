// File: app/static/js/community.js (Versi Final dengan Logika Pengunci)

document.addEventListener('DOMContentLoaded', () => {

    // --- FUNGSI UNTUK MENAMPILKAN NOTIFIKASI POP-UP (TOAST) ---
    const toast = document.getElementById('toast-notification');
    const toastMessage = document.getElementById('toast-message');
    let toastTimeout;

    /**
     * Menampilkan notifikasi pop-up dari sudut kanan atas.
     * @param {string} message - Pesan yang akan ditampilkan.
     * @param {string} [type='success'] - Tipe notifikasi ('success' atau 'error').
     */
    function showToast(message, type = 'success') {
        if (!toast || !toastMessage) return;
        clearTimeout(toastTimeout);
        toastMessage.textContent = message;
        toast.className = 'toast';
        toast.classList.add(type);
        
        toast.classList.add('show');
        
        toastTimeout = setTimeout(() => {
            toast.classList.remove('show');
        }, 4000);
    }
    
    // --- LOGIKA UTAMA UNTUK HALAMAN KOMUNITAS ---
    const userGrid = document.querySelector('.user-grid');

    if (userGrid) {
        userGrid.addEventListener('click', async (e) => {
            const button = e.target.closest('button.action-btn');
            
            // --- LOGIKA PENGUNCI UTAMA ---
            // Jika yang diklik bukan tombol, atau tombol sedang dinonaktifkan, hentikan fungsi.
            if (!button || button.disabled) {
                return;
            }
            
            // Segera nonaktifkan tombol untuk mencegah klik ganda
            button.disabled = true;
            const originalButtonHTML = button.innerHTML;
            button.innerHTML = 'Memproses...';
            // --- AKHIR LOGIKA PENGUNCI ---

            const userCard = button.closest('.user-card');
            const userId = userCard.dataset.userId;
            const action = button.dataset.action;
            const requestId = button.dataset.requestId;

            let url = '';
            const options = {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
            };

            switch (action) {
                case 'send-request':
                    url = `/api/connect/request/${userId}`;
                    break;
                case 'cancel-request':
                    url = `/api/connect/cancel/${userId}`;
                    break;
                case 'accept-request':
                    url = `/api/connect/accept/${requestId}`;
                    break;
                case 'reject-request':
                    url = `/api/connect/reject/${requestId}`;
                    break;
                case 'remove-connection':
                    url = `/api/connect/remove/${userId}`;
                    break;
                default:
                    // Jika aksi tidak dikenali, aktifkan kembali tombolnya
                    button.disabled = false;
                    button.innerHTML = originalButtonHTML;
                    return;
            }
            
            try {
                const response = await fetch(url, options);
                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Terjadi kesalahan.');
                }
                
                showToast(data.message);

                // Update UI secara dinamis dengan tombol baru
                const actionsContainer = button.parentElement;
                actionsContainer.innerHTML = getUpdatedButtons(action, userId);

            } catch (error) {
                showToast(`Error: ${error.message}`, 'error');
                // Jika terjadi error, aktifkan kembali tombol agar pengguna bisa mencoba lagi.
                button.disabled = false;
                button.innerHTML = originalButtonHTML;
            }
        });
    }

    /**
     * Fungsi helper untuk membuat HTML tombol yang baru setelah aksi berhasil.
     * @param {string} lastAction - Aksi yang baru saja dilakukan.
     * @param {string} userId - ID pengguna yang terkait.
     * @returns {string} - String HTML untuk tombol baru.
     */
    function getUpdatedButtons(lastAction, userId) {
        switch (lastAction) {
            case 'send-request':
                return `<button class="button-secondary action-btn" data-action="cancel-request" data-user-id="${userId}">Batalkan Permintaan</button>`;
            case 'accept-request':
                return `<a href="/messages/${userId}" class="button-primary"><i class="fas fa-comment-dots"></i> Kirim Pesan</a>
                        <button class="button-secondary action-btn" data-action="remove-connection" data-user-id="${userId}">Hapus Koneksi</button>`;
            case 'cancel-request':
            case 'reject-request':
            case 'remove-connection':
                return `<button class="button-primary action-btn" data-action="send-request" data-user-id="${userId}">Tambah Koneksi</button>`;
            default:
                return '';
        }
    }
});