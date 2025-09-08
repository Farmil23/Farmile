document.addEventListener('DOMContentLoaded', function() {
    // --- 3.1. API ENDPOINTS & REFERENSI ELEMEN DOM ---
    const EVENTS_API_URL = window.APP_CONFIG.api.events;
    const TASKS_API_URL = window.APP_CONFIG.api.tasks;
    let selectedDateForNewEvent = new Date();

    const calendarEl = document.getElementById('calendar');
    const sidebarDateEl = document.getElementById('sidebar-date-today');
    const sidebarEventsList = document.querySelector('#sidebar-events .item-list');
    const sidebarTasksContainer = document.getElementById('task-categories-container');
    
    const eventModal = document.getElementById('eventModal');
    const eventForm = document.getElementById('eventForm');
    const eventModalTitle = document.getElementById('eventModalTitle');
    const eventIdInput = document.getElementById('eventId');
    const eventDeleteBtn = document.getElementById('eventDeleteBtn');
    const eventColorInput = document.getElementById('eventColor');

    const taskModal = document.getElementById('taskModal');
    const taskForm = document.getElementById('taskForm');
    const taskModalTitle = document.getElementById('taskModalTitle');
    const taskIdInput = document.getElementById('taskId');
    const taskDeleteBtn = document.getElementById('taskDeleteBtn');

    const dailyAgendaModal = document.getElementById('dailyAgendaModal');
    const confirmDeleteModal = document.getElementById('confirmDeleteModal');
    const aiOrganizerBtn = document.getElementById('ai-organizer-btn');
    
    // --- 3.1a. LOGIKA UNTUK NOTIFIKASI DESKTOP ---
    const notificationManager = {
        notifiedItemIds: new Set(), 
        permissionGranted: false,
    };

    function requestNotificationPermission() {
        if (!('Notification' in window)) {
            console.warn("Browser ini tidak mendukung notifikasi desktop.");
            return;
        }
        if (Notification.permission === 'granted') {
            notificationManager.permissionGranted = true;
            return;
        }
        if (Notification.permission !== 'denied') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    notificationManager.permissionGranted = true;
                    new Notification("Notifikasi Diaktifkan!", {
                        body: "Anda akan menerima pengingat untuk jadwal Anda.",
                        icon: window.APP_CONFIG.static.logo
                    });
                }
            });
        }
    }

    // Fungsi notifikasi yang sudah ditingkatkan
    // GANTI FUNGSI LAMA DENGAN VERSI BARU INI UNTUK DEBUGGING
function checkAndNotify() {
    if (!notificationManager.permissionGranted) return;
    const now = new Date();

    console.log(`--- Pengecekan Notifikasi Dijalankan pada: ${now.toLocaleTimeString()} ---`);

    calendar.getEvents().forEach(event => {
        const itemType = event.extendedProps.item_type;

        // Mengambil waktu pengingat dari data
        let reminderMinutes;
        if (itemType === 'task') {
            reminderMinutes = event.extendedProps.original_task.reminder_minutes;
        } else {
            reminderMinutes = event.extendedProps.reminder_minutes;
        }

        // --- BLOK DEBUGGING BARU ---
        const eventStart = new Date(event.start);
        const timeUntilEventMs = eventStart.getTime() - now.getTime();

        console.log(`[DEBUG NOTIFIKASI UNTUK: "${event.title}"]
- Tipe Item: ${itemType}
- Waktu Mentah dari Kalender: ${event.start}
- Waktu Acara (setelah di-parse browser): ${eventStart.toLocaleString()}
- Waktu Sekarang: ${now.toLocaleString()}
- Pengingat diatur untuk: ${reminderMinutes} menit sebelumnya
- Sisa Waktu: ${Math.round(timeUntilEventMs / 60000)} menit lagi
- Apakah notifikasi akan terpicu? ${timeUntilEventMs > 0 && timeUntilEventMs <= (reminderMinutes * 60000)}`);
        // --- AKHIR BLOK DEBUGGING ---

        if (!reminderMinutes || reminderMinutes < 0) {
            return;
        }

        const eventId = event.id;
        if (notificationManager.notifiedItemIds.has(eventId)) return;

        const reminderThreshold = reminderMinutes * 60 * 1000;

        if (timeUntilEventMs > 0 && timeUntilEventMs <= reminderThreshold) {
            console.log("KONDISI IF TERPENUHI! Notifikasi seharusnya muncul."); // Log jika berhasil

            const minutesUntil = Math.round(timeUntilEventMs / 60000);
            let title = event.title.replace('Deadline: ', '');
            let bodyText = itemType === 'task' 
                ? `Deadline tugas akan tiba dalam ${minutesUntil} menit.`
                : `Acara akan dimulai dalam ${minutesUntil} menit.`;

            const notification = new Notification(title, {
                body: bodyText,
                icon: window.APP_CONFIG.static.logo,
                tag: event.id
            });

            notification.onclick = () => {
                window.focus();
                if (itemType === 'task') {
                    openTaskModal(event.extendedProps.original_task);
                } else {
                    openEventModal(event);
                }
                notification.close();
            };

            notificationManager.notifiedItemIds.add(eventId);
        }
    });
    console.log(`--- Pengecekan Selesai ---`);
}

    // --- 3.2. INISIALISASI LIBRARY ---
    const flatpickrConfig = { locale: "id", onOpen: () => document.body.classList.add('no-scroll'), onClose: () => document.body.classList.remove('no-scroll') };
    const startDatePicker = flatpickr("#eventStartDate", { ...flatpickrConfig, dateFormat: "Y-m-d" });
    const endDatePicker = flatpickr("#eventEndDate", { ...flatpickrConfig, dateFormat: "Y-m-d" });
    const startTimePicker = flatpickr("#eventStartTime", { ...flatpickrConfig, enableTime: true, noCalendar: true, dateFormat: "H:i", time_24hr: true });
    const endTimePicker = flatpickr("#eventEndTime", { ...flatpickrConfig, enableTime: true, noCalendar: true, dateFormat: "H:i", time_24hr: true });
    const taskDueDatePicker = flatpickr("#taskDueDate", { ...flatpickrConfig, enableTime: true, dateFormat: "Y-m-d H:i" });

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: { left: 'prev,next today', center: 'title', right: 'dayGridMonth,timeGridWeek,list7Days,list30Days' },
        views: {
            list7Days: { type: 'list', duration: { days: 7 }, buttonText: '7 Hari' },
            list30Days: { type: 'list', duration: { days: 30 }, buttonText: '30 Hari' }
        },
        events: EVENTS_API_URL, 
        editable: true,
        selectable: true,
        dateClick: (info) => handleDateClick(info),
        eventClick: (info) => {
            const props = info.event.extendedProps;
            if (props.item_type === 'task') {
                openTaskModal(props.original_task);
            } else {
                openEventModal(info.event);
            }
        },
        eventDrop: (info) => handleEventDrop(info.event),
        eventTimeFormat: { hour: '2-digit', minute: '2-digit', hour12: false },
    });
    calendar.render();

    // --- EVENT LISTENERS ---
    document.querySelector('.fc-today-button').addEventListener('click', () => { calendar.today(); loadTodaysAgenda(); });
    document.getElementById('add-task-btn').addEventListener('click', () => openTaskModal(null));
    document.getElementById('addNewEventFromDailyBtn').addEventListener('click', () => { dailyAgendaModal.classList.remove('visible'); openEventModal(null, selectedDateForNewEvent); });
    document.getElementById('addNewTaskFromDailyBtn').addEventListener('click', () => {
        dailyAgendaModal.classList.remove('visible');
        openTaskModal(null);
        taskDueDatePicker.setDate(selectedDateForNewEvent, true);
    });
    
    document.querySelectorAll('.modal-overlay').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal || e.target.closest('.modal-close-btn')) {
                modal.classList.remove('visible');
            }
        });
    });

    eventForm.addEventListener('submit', handleEventFormSubmit);
    taskForm.addEventListener('submit', handleTaskFormSubmit);
    eventDeleteBtn.addEventListener('click', () => { const eventId = eventIdInput.value.replace('event-',''); const event = { id: eventId, title: document.getElementById('eventTitle').value }; handleDeleteEvent(event); });
    taskDeleteBtn.addEventListener('click', () => { const taskId = taskIdInput.value.replace('task-',''); const task = { id: taskId, title: document.getElementById('taskTitle').value }; handleDeleteTask(task); });
    
    document.querySelectorAll('.color-option').forEach(option => {
        option.addEventListener('click', function() {
            document.querySelectorAll('.color-option').forEach(o => o.classList.remove('selected'));
            this.classList.add('selected');
            eventColorInput.value = this.dataset.color;
        });
    });

    aiOrganizerBtn.addEventListener('click', handleAIOrganizerClick);

    // --- FUNGSI LOGIKA UTAMA ---
    async function handleDateClick(clickInfo) {
        selectedDateForNewEvent = clickInfo.date;
        const dateStr = clickInfo.dateStr;
        const dailyAgendaTitle = document.getElementById('dailyAgendaTitle');
        const dailyAgendaContent = document.getElementById('dailyAgendaContent');
        
        dailyAgendaTitle.textContent = `Agenda untuk ${clickInfo.date.toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'long' })}`;
        dailyAgendaContent.innerHTML = "<p class='empty-item'>Memuat agenda...</p>";
        dailyAgendaModal.classList.add('visible');

        try {
            const response = await fetch(`${EVENTS_API_URL}?start=${dateStr}&end=${dateStr}T23:59:59`);
            const items = await response.json();

            const events = items.filter(item => item.extendedProps.item_type === 'event');
            const tasks = items.filter(item => item.extendedProps.item_type === 'task');
            
            dailyAgendaContent.innerHTML = '';
            
            const eventHeader = document.createElement('h4');
            eventHeader.textContent = 'Acara';
            dailyAgendaContent.appendChild(eventHeader);

            if (events.length === 0) {
                const p = document.createElement('p');
                p.className = 'empty-item';
                p.textContent = 'Tidak ada acara terjadwal.';
                dailyAgendaContent.appendChild(p);
            } else {
                const list = document.createElement('ul');
                list.className = 'daily-agenda-list';
                events.forEach(event => {
                    const li = document.createElement('li');
                    li.className = 'agenda-item';
                    const startTime = new Date(event.start).toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
                    let descriptionHtml = event.extendedProps.description ? `<p class="agenda-item-detail">${event.extendedProps.description}</p>` : '';
                    li.innerHTML = `
                        <div class="agenda-item-title">
                            <span class="item-color-dot" style="background-color: ${event.backgroundColor || '#3B82F6'}"></span>
                            ${startTime} - ${event.title}
                        </div>
                        ${descriptionHtml}
                    `;
                    li.addEventListener('click', () => {
                        dailyAgendaModal.classList.remove('visible');
                        openEventModal(event);
                    });
                    list.appendChild(li);
                });
                dailyAgendaContent.appendChild(list);
            }

            const taskHeader = document.createElement('h4');
            taskHeader.textContent = 'Tugas';
            taskHeader.style.marginTop = '1rem';
            dailyAgendaContent.appendChild(taskHeader);

            if (tasks.length === 0) {
                const p = document.createElement('p');
                p.className = 'empty-item';
                p.textContent = 'Tidak ada tugas untuk hari ini.';
                dailyAgendaContent.appendChild(p);
            } else {
                const list = document.createElement('ul');
                list.className = 'daily-agenda-list';
                tasks.forEach(taskItem => {
                    const task = taskItem.extendedProps.original_task;
                    const li = document.createElement('li');
                    li.className = 'agenda-item';
                    let deadlineHtml = task.due_date ? `<p class="agenda-item-detail"><strong>Deadline:</strong> ${new Date(task.due_date).toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })}</p>` : '';
                    let descriptionHtml = task.description ? `<p class="agenda-item-detail">${task.description}</p>` : '';
                    li.innerHTML = `
                        <div class="agenda-item-title">✔️ ${task.title} (Prioritas: ${task.priority})</div>
                        ${descriptionHtml}
                        ${deadlineHtml}
                    `;
                    li.addEventListener('click', () => {
                        dailyAgendaModal.classList.remove('visible');
                        openTaskModal(task);
                    });
                    list.appendChild(li);
                });
                dailyAgendaContent.appendChild(list);
            }

        } catch (error) {
            console.error("Gagal memuat agenda harian:", error);
            dailyAgendaContent.innerHTML = "<p class='empty-item error'>Gagal memuat agenda.</p>";
        }
    }

    async function loadTodaysAgenda() {
        const today = new Date();
        const dateStr = today.toISOString().split('T')[0];
        
        sidebarDateEl.textContent = today.toLocaleDateString('id-ID', { day: 'numeric', month: 'long' });
        sidebarEventsList.innerHTML = '<li class="empty-item">Memuat...</li>';
        sidebarTasksContainer.innerHTML = '<p class="empty-item">Memuat...</p>';

        try {
            const [eventsResponse, tasksResponse] = await Promise.all([
                fetch(`${EVENTS_API_URL}?start=${dateStr}&end=${dateStr}T23:59:59`),
                fetch(`${TASKS_API_URL}?filter=today_and_overdue`)
            ]);
            const allCalendarItems = await eventsResponse.json();
            const tasks = await tasksResponse.json();
            
            const events = allCalendarItems.filter(item => item.extendedProps.item_type === 'event');
            
            renderEvents(sidebarEventsList, events);
            renderCategorizedTasks(sidebarTasksContainer, tasks);
        } catch (error) {
            console.error("Gagal memuat data agenda:", error);
            sidebarEventsList.innerHTML = '<li class="empty-item error">Gagal memuat acara.</li>';
            sidebarTasksContainer.innerHTML = '<p class="empty-item error">Gagal memuat tugas.</p>';
        }
    }

    function renderEvents(listElement, events) {
        listElement.innerHTML = '';
        if (events.length === 0) {
            listElement.innerHTML = `<li class="empty-item">Tidak ada acara untuk hari ini.</li>`;
            return;
        }
        events.forEach(event => {
            const li = document.createElement('li');
            li.className = 'agenda-item';
            
            const timeString = new Date(event.start).toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
            
            let descriptionHtml = '';
            if (event.extendedProps.description) {
                descriptionHtml = `<p class="agenda-item-detail">${event.extendedProps.description}</p>`;
            }

            li.innerHTML = `
                <div class="agenda-item-title">
                    <span class="item-color-dot" style="background-color: ${event.backgroundColor || '#3B82F6'}"></span>
                    ${event.title}
                </div>
                <p class="agenda-item-detail">${timeString}</p>
                ${descriptionHtml}
            `;
            
            li.addEventListener('click', () => {
                const eventDataForModal = {
                    id: event.id,
                    title: event.title,
                    start: event.start,
                    end: event.end,
                    backgroundColor: event.backgroundColor,
                    extendedProps: event.extendedProps
                };
                openEventModal(eventDataForModal);
            });
            listElement.appendChild(li);
        });
    }

    function renderCategorizedTasks(container, tasks) {
        container.innerHTML = '';
        const categories = {
            urgent: { title: 'Mendesak', icon: '🔥', tasks: [] },
            high: { title: 'Penting', icon: '📌', tasks: [] },
            medium: { title: 'Biasa', icon: '🗓️', tasks: [] },
            low: { title: 'Santai', icon: '☕', tasks: [] },
        };
        tasks.forEach(task => { (categories[task.priority] || categories.medium).tasks.push(task); });
        let hasTasks = false;
        for (const key in categories) {
            const category = categories[key];
            if (category.tasks.length > 0) {
                hasTasks = true;
                const categoryDiv = document.createElement('div');
                categoryDiv.className = 'task-category';
                
                let tasksHtml = `<div class="task-category-header"><span class="icon">${category.icon}</span> ${category.title}</div><ul class="item-list">`;
                
                category.tasks.forEach(task => {
                    const dueDateString = task.due_date ? `Jatuh tempo: ${new Date(task.due_date).toLocaleDateString('id-ID', {day: 'numeric', month: 'numeric', year: 'numeric'})}` : 'Tanpa batas waktu';
                    
                    let descriptionHtml = '';
                    if (task.description) {
                        descriptionHtml = `<p class="agenda-item-detail">${task.description}</p>`;
                    }

                    tasksHtml += `
                        <li class="agenda-item" data-task-id="${task.id}">
                            <div class="agenda-item-title">${task.title}</div>
                            ${descriptionHtml}
                            <p class="agenda-item-detail">${dueDateString}</p>
                        </li>`;
                });
                tasksHtml += `</ul>`;
                categoryDiv.innerHTML = tasksHtml;
                container.appendChild(categoryDiv);
                categoryDiv.querySelectorAll('.agenda-item').forEach(item => {
                    item.addEventListener('click', () => {
                        const taskId = item.dataset.taskId;
                        const taskData = tasks.find(t => t.id == taskId);
                        if(taskData) openTaskModal(taskData);
                    });
                });
            }
        }
        if (!hasTasks) { container.innerHTML = `<p class="empty-item">Tidak ada tugas yang relevan hari ini.</p>`; }
    }


    function openEventModal(event, initialDate = null) {
        eventForm.reset();
        document.querySelectorAll('.color-option').forEach(o => o.classList.remove('selected'));
        if (event) { // Mode Edit
            eventModalTitle.textContent = "Edit Acara";
            eventIdInput.value = event.id;
            document.getElementById('eventTitle').value = event.title;
            document.getElementById('eventDescription').value = event.extendedProps.description || '';
            document.getElementById('eventLink').value = event.extendedProps.link || '';
            document.getElementById('eventReminder').value = event.extendedProps.reminder_minutes || '10';

            const start = new Date(event.start);
            const end = event.end ? new Date(event.end) : null;
            startDatePicker.setDate(start, true);
            startTimePicker.setDate(start, true);
            if (end) { endDatePicker.setDate(end, true); endTimePicker.setDate(end, true); } else { endDatePicker.clear(); endTimePicker.clear(); }
            const eventColor = event.backgroundColor || event.color || '#3B82F6';
            eventColorInput.value = eventColor;
            const selectedColorEl = document.querySelector(`.color-option[data-color='${eventColor}']`);
            if (selectedColorEl) selectedColorEl.classList.add('selected');
            eventDeleteBtn.style.display = 'inline-block';
        } else { // Mode Baru
            eventModalTitle.textContent = "Acara Baru";
            eventIdInput.value = '';
            document.getElementById('eventReminder').value = '10';
            const initialDateToSet = initialDate || new Date(); 
            startDatePicker.setDate(initialDateToSet, true);
            startTimePicker.clear();
            endDatePicker.clear();
            endTimePicker.clear();
            eventColorInput.value = '#3B82F6';
            document.querySelector(".color-option[data-color='#3B82F6']").classList.add('selected');
            eventDeleteBtn.style.display = 'none';
        }
        eventModal.classList.add('visible');
    }

    async function handleEventFormSubmit(e) {
        e.preventDefault();
        const eventIdRaw = eventIdInput.value;
        const eventId = eventIdRaw.startsWith('event-') ? eventIdRaw.replace('event-', '') : eventIdRaw;
        
        const eventData = { 
            title: document.getElementById('eventTitle').value, 
            description: document.getElementById('eventDescription').value, 
            start: combineDateTime(startDatePicker.input.value, startTimePicker.input.value), 
            end: combineDateTime(endDatePicker.input.value, endTimePicker.input.value), 
            link: document.getElementById('eventLink').value, 
            color: eventColorInput.value,
            reminder_minutes: document.getElementById('eventReminder').value
        };

        const url = eventId ? `${EVENTS_API_URL}/${eventId}` : EVENTS_API_URL;
        const method = eventId ? 'PUT' : 'POST';
        try {
            const response = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(eventData) });
            if (!response.ok) throw new Error((await response.json()).message || 'Gagal menyimpan acara');
            eventModal.classList.remove('visible');
            calendar.refetchEvents();
            loadTodaysAgenda();
        } catch (error) { alert(error.message); }
    }
    
    async function handleDeleteEvent(event) {
        const confirmed = await showConfirmModal("Hapus Acara", `Anda yakin ingin menghapus "${event.title}"?`);
        if (event.id && confirmed) {
            try {
                const response = await fetch(`${EVENTS_API_URL}/${event.id}`, { method: 'DELETE' });
                if (!response.ok) throw new Error('Gagal menghapus acara');
                eventModal.classList.remove('visible');
                calendar.refetchEvents();
                loadTodaysAgenda();
            } catch (error) { alert(error.message); }
        }
    }
    
    async function handleEventDrop(info) {
        if (info.event.extendedProps.item_type === 'task') {
            info.revert();
            alert('Tugas tidak dapat dipindahkan. Harap ubah tanggalnya melalui menu edit.');
            return;
        }
        const eventData = { start: info.event.start.toISOString(), end: info.event.end ? info.event.end.toISOString() : null };
        try {
            const response = await fetch(`${EVENTS_API_URL}/${info.event.id.replace('event-', '')}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(eventData) });
            if (!response.ok) throw new Error('Gagal update waktu acara');
            loadTodaysAgenda();
        } catch (error) { alert(error.message); info.revert(); }
    }

    function openTaskModal(task, initialDate = null) {
        taskForm.reset();
        if(task) { // Mode Edit
            taskModalTitle.textContent = "Detail Tugas";
            taskIdInput.value = task.id;
            document.getElementById('taskTitle').value = task.title;
            document.getElementById('taskDescription').value = task.description || '';
            taskDueDatePicker.setDate(task.due_date || '', true);
            document.getElementById('taskPriority').value = task.priority || 'medium';
            document.getElementById('taskReminder').value = task.reminder_minutes || '30';
            taskDeleteBtn.style.display = 'inline-block';
        } else { // Mode Baru
            taskModalTitle.textContent = "Tugas Baru";
            taskIdInput.value = '';
            taskDueDatePicker.setDate(initialDate || '', true);
            document.getElementById('taskPriority').value = 'medium';
            document.getElementById('taskReminder').value = '30';
            taskDeleteBtn.style.display = 'none';
        }
        taskModal.classList.add('visible');
    }

    async function handleTaskFormSubmit(e) {
        e.preventDefault();
        const taskId = taskIdInput.value;
        
        const taskData = { 
            title: document.getElementById('taskTitle').value, 
            description: document.getElementById('taskDescription').value, 
            due_date: document.getElementById('taskDueDate').value || null, 
            priority: document.getElementById('taskPriority').value,
            reminder_minutes: document.getElementById('taskReminder').value
        };
        
        const url = taskId ? `${TASKS_API_URL}/${taskId}` : TASKS_API_URL;
        const method = taskId ? 'PUT' : 'POST';
        try {
            const response = await fetch(url, { method, headers: {'Content-Type': 'application/json'}, body: JSON.stringify(taskData)});
            if (!response.ok) throw new Error((await response.json()).message || 'Gagal menyimpan tugas');
            taskModal.classList.remove('visible');
            calendar.refetchEvents();
            loadTodaysAgenda();
        } catch (error) { alert(error.message); }
    }

    async function handleDeleteTask(task) {
        const confirmed = await showConfirmModal("Hapus Tugas", `Anda yakin ingin menghapus "${task.title}"?`);
        if(task.id && confirmed) {
            try {
                const response = await fetch(`${TASKS_API_URL}/${task.id}`, { method: 'DELETE' });
                if (!response.ok) throw new Error('Gagal menghapus tugas');
                taskModal.classList.remove('visible');
                calendar.refetchEvents();
                loadTodaysAgenda();
            } catch (error) { alert(error.message); }
        }
    }
    
    function handleAIOrganizerClick() {
        aiOrganizerBtn.disabled = true;
        aiOrganizerBtn.textContent = 'Mengarahkan...';
        const events = Array.from(sidebarEventsList.querySelectorAll('.agenda-item .agenda-item-title')).map(el => el.textContent.trim());
        const tasks = Array.from(document.querySelectorAll('#task-categories-container .agenda-item .agenda-item-title')).map(el => el.textContent.trim());
        const form = document.createElement('form');
        form.method = 'POST';
        
        // KODE YANG SUDAH DIPERBAIKI: Menggunakan variabel dari window.APP_CONFIG
        form.action = window.APP_CONFIG.routes.ask_ai;

        const eventsInput = document.createElement('input');
        eventsInput.type = 'hidden';
        eventsInput.name = 'events';
        eventsInput.value = JSON.stringify(events);
        form.appendChild(eventsInput);
        const tasksInput = document.createElement('input');
        tasksInput.type = 'hidden';
        tasksInput.name = 'tasks';
        tasksInput.value = JSON.stringify(tasks);
        form.appendChild(tasksInput);
        document.body.appendChild(form);
        form.submit();
    }

    function showConfirmModal(title, message) {
        return new Promise((resolve) => {
            const confirmBtn = document.getElementById('confirmDeleteBtn');
            const cancelBtns = confirmDeleteModal.querySelectorAll('.modal-close-btn, #cancelDeleteBtn');
            confirmDeleteModal.querySelector('#confirmTitle').textContent = title;
            confirmDeleteModal.querySelector('#confirmMessage').textContent = message;
            const confirmHandler = () => cleanup(true);
            const cancelHandler = () => cleanup(false);
            const cleanup = (value) => {
                confirmDeleteModal.classList.remove('visible');
                confirmBtn.removeEventListener('click', confirmHandler);
                cancelBtns.forEach(btn => btn.removeEventListener('click', cancelHandler));
                resolve(value);
            };
            confirmBtn.addEventListener('click', confirmHandler, { once: true });
            cancelBtns.forEach(btn => btn.addEventListener('click', cancelHandler, { once: true }));
            confirmDeleteModal.classList.add('visible');
        });
    }

    function combineDateTime(dateStr, timeStr) {
        if (!dateStr) return null;
        return `${dateStr} ${timeStr || '00:00:00'}`;
    }
    
    // --- 3.5. INISIALISASI AWAL ---
    loadTodaysAgenda();

    // --- INISIALISASI FITUR NOTIFIKASI ---
    requestNotificationPermission(); 
    setInterval(checkAndNotify, 60000); // Cek setiap 60 detik
});