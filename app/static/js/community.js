document.addEventListener('DOMContentLoaded', () => {
    const userGrid = document.querySelector('.user-grid');

    if (userGrid) {
        userGrid.addEventListener('click', async (e) => {
            // Pastikan yang diklik adalah tombol dengan class 'action-btn'
            const button = e.target.closest('button.action-btn');
            if (!button) return;

            // Ambil data dari elemen HTML
            const userCard = button.closest('.user-card');
            const userId = userCard.dataset.userId;
            const action = button.dataset.action;
            const requestId = button.dataset.requestId;

            let url = '';
            const options = {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
            };

            // Tentukan URL API berdasarkan aksi tombol
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
                    return; // Jika aksi tidak dikenali, hentikan
            }
            
            // Nonaktifkan tombol untuk mencegah klik ganda
            button.disabled = true;
            button.textContent = 'Memproses...';

            try {
                const response = await fetch(url, options);
                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Terjadi kesalahan pada server.');
                }
                
                // Jika berhasil, muat ulang halaman untuk menampilkan status tombol yang baru
                // Ini adalah pendekatan paling sederhana dan efektif untuk saat ini.
                alert(data.message); // Tampilkan pesan sukses dari server
                window.location.reload();

            } catch (error) {
                alert(`Error: ${error.message}`);
                // Muat ulang juga jika terjadi error agar state tombol kembali normal
                window.location.reload();
            }
        });
    }
});