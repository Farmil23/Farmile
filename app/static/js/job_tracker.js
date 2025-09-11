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
        }).then(res => res.json()),
        updateApp: (id, data) => fetch(`/api/applications/${id}`, {
            method: 'PUT', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(res => res.json()),
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
        document.querySelectorAll('.kanban-cards').forEach(col => col.innerHTML = '');
        apps.forEach(app => {
            const column = document.querySelector(`.kanban-column[data-status='${app.status}'] .kanban-cards`);
            if (column) {
                const card = document.createElement('div');
                card.className = 'kanban-card';
                card.draggable = true;
                card.dataset.id = app.id;
                card.innerHTML = `
                    <button class="delete-card-btn" title="Hapus">&times;</button>
                    <div class="card-content">
                        <h4>${app.position}</h4>
                        <p>${app.company_name}</p>
                    </div>
                    <div class="card-footer">
                        <a href="/job-tracker/coach/${app.id}" class="ai-coach-btn">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                            Ngobrol Sama AI
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
                        loadApplications();
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
                    column.querySelector('.kanban-cards').appendChild(draggedCard);
                    const appId = draggedCard.dataset.id;
                    const newStatus = column.dataset.status;
                    await api.updateApp(appId, { status: newStatus });
                }
            });
        });
    }

    const openModalForAdd = () => {
        appForm.reset();
        document.getElementById('application-id').value = '';
        appModalTitle.textContent = 'Lacak Lamaran Baru';
        appModal.classList.add('visible');
    };

    const openModalForEdit = (id) => {
        const app = applications.find(a => a.id == id);
        if (!app) return;
        appForm.reset();
        document.getElementById('application-id').value = app.id;
        document.getElementById('company-name').value = app.company_name;
        document.getElementById('position').value = app.position;
        document.getElementById('job-link').value = app.job_link || '';
        document.getElementById('notes').value = app.notes || '';
        appModalTitle.textContent = `Detail: ${app.position}`;
        appModal.classList.add('visible');
    };

    document.getElementById('add-application-btn').addEventListener('click', openModalForAdd);
    appModal.addEventListener('click', e => {
        if (e.target === appModal || e.target.closest('.modal-close-btn')) {
            appModal.classList.remove('visible');
        }
    });

    appForm.addEventListener('submit', async e => {
        e.preventDefault();
        const id = document.getElementById('application-id').value;
        const data = {
            company_name: document.getElementById('company-name').value,
            position: document.getElementById('position').value,
            job_link: document.getElementById('job-link').value,
            notes: document.getElementById('notes').value
        };
        try {
            if (id) {
                await api.updateApp(id, data);
            } else {
                await api.addApp(data);
            }
            appForm.reset();
            appModal.classList.remove('visible');
            loadApplications();
        } catch (error) {
            console.error("Gagal menyimpan:", error);
            alert("Gagal menyimpan lamaran. Silakan coba lagi.");
        }
    });

    // Initial Load
    renderBoard();
    loadApplications();
});