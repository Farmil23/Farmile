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
        clearTimeout(toastTimeout); // Hapus timeout sebelumnya jika ada
        toastMessage.textContent = message;
        toast.className = 'toast'; // Reset class
        toast.classList.add(type); // Tambahkan tipe notifikasi (success/error)
        
        toast.classList.add('show');
        
        // Sembunyikan notifikasi setelah 4 detik
        toastTimeout = setTimeout(() => {
            toast.classList.remove('show');
        }, 4000);
    }

    // --- LOGIKA UNTUK MODAL BUAT GRUP ---
    const createModal = document.getElementById('create-group-modal');
    if (createModal) {
        const openModalBtn = document.getElementById('create-group-btn');
        const closeModalBtn = createModal.querySelector('.modal-close-btn');
        const createForm = document.getElementById('create-group-form');

        openModalBtn.addEventListener('click', () => createModal.classList.add('visible'));
        closeModalBtn.addEventListener('click', () => createModal.classList.remove('visible'));
        createModal.addEventListener('click', (e) => {
            if (e.target === createModal) createModal.classList.remove('visible');
        });

        createForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('group-name').value;
            const description = document.getElementById('group-description').value;
            const isPrivate = document.querySelector('input[name="group-privacy"]:checked').value === 'private';
            
            const submitButton = createForm.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            submitButton.textContent = 'Membuat...';

            try {
                const response = await fetch('/api/groups/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, description, is_private: isPrivate })
                });
                const data = await response.json();

                if (response.ok) {
                    showToast(data.message);
                    // Arahkan ke halaman grup baru setelah notifikasi tampil
                    setTimeout(() => {
                        window.location.href = data.group_url;
                    }, 1500);
                } else {
                    throw new Error(data.error);
                }
            } catch (error) {
                showToast(`Error: ${error.message}`, 'error');
                submitButton.disabled = false;
                submitButton.textContent = 'Buat Grup';
            }
        });
    }

    // --- LOGIKA UNTUK MODAL KELOLA GRUP ---
    const manageModal = document.getElementById('manage-group-modal');
    if (manageModal) {
        const manageForm = document.getElementById('manage-group-form');
        const manageIdInput = document.getElementById('manage-group-id');
        const manageNameInput = document.getElementById('manage-group-name');
        const manageDescInput = document.getElementById('manage-group-description');
        const deleteBtn = document.getElementById('delete-group-btn');

        // Event listener untuk semua tombol "Kelola"
        document.querySelectorAll('.manage-group-btn').forEach(button => {
            button.addEventListener('click', () => {
                const groupData = button.dataset;
                manageIdInput.value = groupData.groupId;
                manageNameInput.value = groupData.groupName;
                manageDescInput.value = groupData.groupDescription;
                
                if (groupData.groupPrivate === 'true') {
                    document.getElementById('manage-privacy-private').checked = true;
                } else {
                    document.getElementById('manage-privacy-public').checked = true;
                }
                
                manageModal.classList.add('visible');
            });
        });

        // Event listener untuk menutup modal
        manageModal.querySelector('.modal-close-btn').addEventListener('click', () => manageModal.classList.remove('visible'));
        manageModal.addEventListener('click', (e) => {
            if (e.target === manageModal) manageModal.classList.remove('visible');
        });

        // Event listener untuk submit form edit
        manageForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const groupId = manageIdInput.value;
            const name = manageNameInput.value;
            const description = manageDescInput.value;
            const is_private = document.querySelector('input[name="manage-group-privacy"]:checked').value === 'private';

            try {
                const response = await fetch(`/api/groups/${groupId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, description, is_private })
                });
                const data = await response.json();
                if (response.ok) {
                    showToast(data.message);
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    throw new Error(data.error || 'Gagal memperbarui grup.');
                }
            } catch (error) {
                showToast(`Error: ${error.message}`, 'error');
            }
        });

        // Event listener untuk tombol hapus
        deleteBtn.addEventListener('click', async () => {
            const groupId = manageIdInput.value;
            if (confirm(`Anda yakin ingin menghapus grup "${manageNameInput.value}"? Tindakan ini tidak bisa dibatalkan.`)) {
                try {
                    const response = await fetch(`/api/groups/${groupId}`, { method: 'DELETE' });
                    const data = await response.json();
                    if (response.ok) {
                        showToast(data.message);
                        setTimeout(() => window.location.reload(), 1500);
                    } else {
                        throw new Error(data.error || 'Gagal menghapus grup.');
                    }
                } catch(error) {
                    showToast(`Error: ${error.message}`, 'error');
                }
            }
        });
    }

    // --- LOGIKA UNTUK TOMBOL GABUNG GRUP ---
    document.querySelectorAll('.join-group-btn').forEach(button => {
        button.addEventListener('click', async () => {
            const groupId = button.dataset.groupId;
            button.disabled = true;
            button.textContent = 'Memproses...';

            try {
                const response = await fetch(`/api/groups/${groupId}/join`, { method: 'POST' });
                const data = await response.json();
                if (response.ok) {
                    showToast(data.message);
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    throw new Error(data.error);
                }
            } catch (error) {
                showToast(`Error: ${error.message}`, 'error');
                button.disabled = false;
                button.textContent = 'Gabung';
            }
        });
    });

    // --- LOGIKA UNTUK TOMBOL KELUAR GRUP ---
    document.querySelectorAll('.leave-group-btn').forEach(button => {
        button.addEventListener('click', async () => {
            const groupId = button.dataset.groupId;
            const groupName = button.dataset.groupName;

            if (confirm(`Anda yakin ingin keluar dari grup "${groupName}"?`)) {
                button.disabled = true;
                button.textContent = 'Memproses...';

                try {
                    const response = await fetch(`/api/groups/${groupId}/leave`, { method: 'POST' });
                    const data = await response.json();
                    if (response.ok) {
                        showToast(data.message);
                        setTimeout(() => window.location.reload(), 1500);
                    } else {
                        throw new Error(data.error);
                    }
                } catch (error) {
                    showToast(`Error: ${error.message}`, 'error');
                    button.disabled = false;
                    button.textContent = 'Keluar';
                }
            }
        });
    });
});