// File: app/static/js/job_tracker.js
document.addEventListener('DOMContentLoaded', () => {
    // --- Referensi Elemen ---
    const kanbanBoard = document.getElementById('kanban-board');
    const appModal = document.getElementById('application-modal');
    const appForm = document.getElementById('application-form');
    const appModalTitle = document.getElementById('modal-title');
    
    const confirmModal = document.getElementById('confirm-delete-modal');
    const confirmModalTitle = document.getElementById('confirm-modal-title');
    const confirmModalMessage = document.getElementById('confirm-modal-message');
    const confirmBtn = document.getElementById('modal-confirm-btn');
    const cancelBtn = document.getElementById('modal-cancel-btn');

    let applications = [];

    const columns = [
        { id: 'wishlist', title: 'Wishlist' },
        { id: 'applied', title: 'Applied' },
        { id: 'interview', title: 'Interview' },
        { id: 'offer', title: 'Offer' },
        { id: 'rejected', title: 'Rejected' }
    ];

    const api = {
        getApps: () => fetch('/api/applications').then(res => res.json()),
        addApp: (data) => fetch('/api/applications', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(res => res.ok ? res.json() : Promise.reject(res.json())),
        updateApp: (id, data) => fetch(`/api/applications/${id}`, {
            method: 'PUT', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(res => res.ok ? res.json() : Promise.reject(res.json())),
        deleteApp: (id) => fetch(`/api/applications/${id}`, { method: 'DELETE' })
    };
    
    const showConfirmModal = (title, message) => {
        return new Promise((resolve) => {
            confirmModalTitle.textContent = title;
            confirmModalMessage.textContent = message;
            confirmModal.classList.add('visible');
            const onConfirm = () => {
                confirmModal.classList.remove('visible');
                resolve(true);
            };
            const onCancel = () => {
                confirmModal.classList.remove('visible');
                resolve(false);
            };
            confirmBtn.onclick = onConfirm;
            cancelBtn.onclick = onCancel;
            confirmModal.onclick = (e) => {
                if (e.target === confirmModal) onCancel();
            };
        });
    };

    const renderBoard = () => {
        kanbanBoard.innerHTML = '';
        columns.forEach(col => {
            const columnEl = document.createElement('div');
            columnEl.className = 'kanban-column';
            columnEl.dataset.status = col.id;
            columnEl.innerHTML = `<h3>${col.title}</h3><div class="kanban-cards"></div>`;
            kanbanBoard.appendChild(columnEl);
        });
    };
    
    const renderCards = (apps) => {
        applications = apps;
        const emptyState = document.getElementById('empty-state');
        const board = document.getElementById('kanban-board');

        if (apps.length === 0) {
            board.style.display = 'none';
            emptyState.style.display = 'block';
        } else {
            board.style.display = 'grid';
            emptyState.style.display = 'none';
        }

        document.querySelectorAll('.kanban-cards').forEach(col => col.innerHTML = '');
        apps.forEach(app => {
            const column = document.querySelector(`.kanban-column[data-status='${app.status}'] .kanban-cards`);
            if (column) {
                const card = document.createElement('div');
                card.className = 'kanban-card';
                card.draggable = true;
                card.dataset.id = app.id;

                const appDate = new Date(app.application_date).toLocaleDateString('id-ID', { day: 'numeric', month: 'short' });
                const workModelBadge = app.work_model ? `<span class="work-model-badge">${app.work_model}</span>` : '';
                const resumeBadge = app.resume_filename ? `<span class="resume-badge">CV</span>` : '';

                card.innerHTML = `
                    <button class="delete-card-btn" title="Hapus">&times;</button>
                    <div class="card-content">
                        <div class="card-header">
                            <h4>${app.position}</h4>
                            <span class="date">${appDate}</span>
                        </div>
                        <p>${app.company_name}</p>
                        <div class="card-badges">
                            ${workModelBadge}
                            ${resumeBadge}
                        </div>
                    </div>
                    <div class="card-footer">
                        <a href="/job-tracker/coach/${app.id}" class="ai-coach-btn">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                            AI Coach
                        </a>
                    </div>`;
                column.appendChild(card);
            }
        });
        addEventListeners();
    };

    const loadApplications = async () => {
        try {
            const apps = await api.getApps();
            renderCards(apps);
        } catch (error) {
            console.error("Gagal memuat aplikasi:", error);
        }
    };

    function addEventListeners() {
        document.querySelectorAll('.kanban-card').forEach(card => {
            const cardContent = card.querySelector('.card-content');
            if (cardContent) {
                cardContent.addEventListener('click', () => {
                    openModalForEdit(card.dataset.id);
                });
            }
            const deleteBtn = card.querySelector('.delete-card-btn');
            if(deleteBtn) {
                deleteBtn.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    const id = card.dataset.id;
                    const app = applications.find(a => a.id == id);
                    const confirmed = await showConfirmModal('Konfirmasi Hapus', `Anda yakin ingin menghapus lamaran "${app.position}"?`);
                    if (confirmed) {
                        await api.deleteApp(id);
                        // Hapus dari array lokal dan render ulang
                        applications = applications.filter(a => a.id != id);
                        renderCards(applications);
                    }
                });
            }
        });
        
        const cards = document.querySelectorAll('.kanban-card');
        const columns = document.querySelectorAll('.kanban-column');
        let draggedCard = null;

        cards.forEach(card => {
            card.addEventListener('dragstart', () => {
                draggedCard = card;
                setTimeout(() => card.classList.add('dragging'), 0);
            });
            card.addEventListener('dragend', () => {
                if(draggedCard) draggedCard.classList.remove('dragging');
                draggedCard = null;
            });
        });

        columns.forEach(column => {
            column.addEventListener('dragover', e => { e.preventDefault(); column.classList.add('drag-over'); });
            column.addEventListener('dragleave', () => { column.classList.remove('drag-over'); });
            column.addEventListener('drop', async (e) => {
                e.preventDefault();
                column.classList.remove('drag-over');
                if (draggedCard) {
                    const appId = draggedCard.dataset.id;
                    const newStatus = column.dataset.status;
                    
                    // Update status di array lokal
                    const appIndex = applications.findIndex(a => a.id == appId);
                    if (appIndex > -1) {
                        applications[appIndex].status = newStatus;
                    }
                    
                    // Render ulang dari data lokal (sangat cepat)
                    renderCards(applications);
                    
                    // Kirim pembaruan ke server di latar belakang
                    await api.updateApp(appId, { status: newStatus });
                }
            });
        });
    }

    const openModalForAdd = () => {
        appForm.reset();
        document.getElementById('application-id').value = '';
        appModalTitle.textContent = 'Lacak Lamaran Baru';
        document.getElementById('application-date').valueAsDate = new Date();
        appModal.classList.add('visible');
    };

    const openModalForEdit = (id) => {
        const app = applications.find(a => a.id == id);
        if (!app) return;
        appForm.reset();
        document.getElementById('application-id').value = app.id;
        document.getElementById('company-name').value = app.company_name;
        document.getElementById('position').value = app.position;
        document.getElementById('application-date').value = app.application_date.split('T')[0];
        document.getElementById('work-model').value = app.work_model || 'onsite';
        document.getElementById('job-link').value = app.job_link || '';
        document.getElementById('notes').value = app.notes || '';
        
        const resumeSelect = document.getElementById('resume-select');
        const resumeIdFromServer = app.resume_id;
        resumeSelect.value = resumeIdFromServer || "";

        appModalTitle.textContent = `Detail: ${app.position}`;
        appModal.classList.add('visible');
    };

    document.getElementById('add-application-btn').addEventListener('click', openModalForAdd);
    appModal.addEventListener('click', e => {
        if (e.target === appModal || e.target.closest('.modal-close-btn')) {
            appModal.classList.remove('visible');
        }
    });

    // --- LOGIKA SUBMIT FORM YANG SUDAH DIPERBAIKI ---
    appForm.addEventListener('submit', async e => {
        e.preventDefault();
        const id = document.getElementById('application-id').value;
        const resumeSelect = document.getElementById('resume-select');
        const data = {
            company_name: document.getElementById('company-name').value,
            position: document.getElementById('position').value,
            application_date: document.getElementById('application-date').value,
            work_model: document.getElementById('work-model').value,
            job_link: document.getElementById('job-link').value,
            notes: document.getElementById('notes').value,
            resume_id: resumeSelect.value || null
        };

        try {
            if (id) {
                // --- LOGIKA UPDATE BARU ---
                const currentApp = applications.find(a => a.id == id);
                data.status = currentApp.status; // Pastikan status tidak berubah saat edit
                const updatedApp = await api.updateApp(id, data);
                
                const index = applications.findIndex(a => a.id == id);
                if (index !== -1) {
                    applications[index] = updatedApp;
                }
            } else {
                // --- LOGIKA ADD BARU ---
                data.status = 'wishlist'; // Selalu mulai dari Wishlist
                const newApp = await api.addApp(data);
                applications.unshift(newApp); // Tambahkan ke awal array
            }
            
            // Render ulang dari data lokal yang sudah diupdate
            renderCards(applications);
            
            // Tutup modal setelah selesai
            appForm.reset();
            appModal.classList.remove('visible');

        } catch (error) {
            console.error("Gagal menyimpan:", await error);
            alert("Gagal menyimpan lamaran. Periksa kembali isian Anda.");
        }
    });

    // Initial Load
    renderBoard();
    loadApplications();
});