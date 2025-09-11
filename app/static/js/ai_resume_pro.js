// GANTI SEMUA ISI FILE app/static/js/ai_resume_pro.js DENGAN INI

document.addEventListener('DOMContentLoaded', () => {
    // Referensi Elemen
    const uploadInput = document.getElementById('pdf-upload-input');
    const uploadBox = document.getElementById('upload-box');
    const reviewContainer = document.getElementById('review-container');
    const loadingSpinner = document.getElementById('loading-spinner');
    const downloadBtn = document.getElementById('download-btn');
    const deleteBtn = document.getElementById('delete-btn');
    const savedResumesList = document.getElementById('saved-resumes-list');
    
    // Referensi elemen template CV
    const resumeOutputEl = document.getElementById('resume-output');

    let currentResumeId = null;
    const apiEndpoint = '/api/ai/review-resume-pdf';

    const showState = (state) => {
        uploadBox.style.display = 'none';
        reviewContainer.style.display = 'none';
        loadingSpinner.style.display = 'none';
        switch (state) {
            case 'upload':
                uploadBox.style.display = 'flex';
                downloadBtn.style.display = 'none';
                deleteBtn.style.display = 'none';
                currentResumeId = null;
                document.querySelectorAll('.resume-item.active').forEach(el => el.classList.remove('active'));
                break;
            case 'loading':
                loadingSpinner.style.display = 'flex';
                break;
            case 'review':
                reviewContainer.style.display = 'block'; // Diubah dari grid ke block
                downloadBtn.style.display = 'inline-flex';
                deleteBtn.style.display = 'inline-flex';
                break;
        }
    };
    
    // FUNGSI BARU UNTUK MENGISI TEMPLATE CV
    const populateResumeTemplate = (data) => {
        try {
            const resumeData = JSON.parse(data);

            document.getElementById('resume-full-name').textContent = resumeData.personal_data?.full_name || '';
            document.getElementById('resume-professional-title').textContent = resumeData.personal_data?.professional_title || '';
            document.getElementById('profile-summary-content').textContent = resumeData.profile_summary || '';

            const pd = resumeData.personal_data;
            document.getElementById('personal-data-content').innerHTML = `
                <p><strong>Tempat/Tgl Lahir</strong>${pd?.dob_place || '-'}</p>
                <p><strong>Jenis Kelamin</strong>${pd?.gender || '-'}</p>
                <p><strong>Agama</strong>${pd?.religion || '-'}</p>
                <p><strong>Kewarganegaraan</strong>${pd?.nationality || '-'}</p>
            `;

            const contact = resumeData.contact;
            document.getElementById('contact-content').innerHTML = `
                <p><strong>Telepon</strong>${contact?.phone || '-'}</p>
                <p><strong>Email</strong>${contact?.email || '-'}</p>
                <p><strong>Alamat</strong>${contact?.address || '-'}</p>
            `;

            const skillsContent = document.getElementById('skills-content');
            skillsContent.innerHTML = '';
            resumeData.skills?.forEach(skill => {
                skillsContent.innerHTML += `<span class="skill-item">${skill}</span> `;
            });

            const workExpContent = document.getElementById('work-experience-content');
            workExpContent.innerHTML = '';
            resumeData.work_experience?.forEach(job => {
                workExpContent.innerHTML += `
                    <div class="work-item">
                        <h4>${job.job_title}</h4>
                        <div class="company">${job.company_name}</div>
                        <div class="date">${job.date_range}</div>
                        <ul>
                            ${job.responsibilities.map(r => `<li>${r}</li>`).join('')}
                        </ul>
                    </div>
                `;
            });

            const educationContent = document.getElementById('education-content');
            educationContent.innerHTML = '';
            resumeData.education?.forEach(edu => {
                educationContent.innerHTML += `
                    <div class="education-item">
                        <h4>${edu.institution}</h4>
                        <div class="degree">${edu.degree}</div>
                        <div class="date">${edu.date_range}</div>
                        <p>${edu.description || ''}</p>
                    </div>
                `;
            });
            // Lanjutkan untuk social media, dll.

        } catch (error) {
            console.error("Gagal parsing JSON dari AI:", error);
            alert("Maaf, AI memberikan format yang tidak terduga. Coba unggah lagi.");
            showState('upload');
        }
    };
    
    const displayResumeData = (data, isNewUpload = false) => {
        currentResumeId = data.resume_id;
        const resumeDataJson = isNewUpload ? data.resume_data_json : data.feedback;
        populateResumeTemplate(resumeDataJson);
        showState('review');

        document.querySelectorAll('.resume-item').forEach(el => {
            el.classList.toggle('active', el.dataset.id == currentResumeId);
        });
    };

    const processFile = async (file) => {
        showState('loading');
        const formData = new FormData();
        formData.append('resume_pdf', file);
        try {
            const response = await fetch(apiEndpoint, { method: 'POST', body: formData });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Terjadi kesalahan.');
            displayResumeData(data, true);
            addResumeToSidebar(data);
        } catch (error) {
            alert(`Error: ${error.message}`);
            showState('upload');
        }
    };

    const addResumeToSidebar = (data) => {
        const existingItem = document.querySelector(`.resume-item[data-id='${data.resume_id}']`);
        if (existingItem) return;

        savedResumesList.querySelector('.empty-list-text')?.remove();
        const newItem = document.createElement('a');
        newItem.href = "#";
        newItem.className = 'resume-item active';
        newItem.dataset.id = data.resume_id;
        newItem.innerHTML = `<span class="filename">${data.filename}</span><span class="timestamp">${data.created_at}</span>`;
        savedResumesList.prepend(newItem);
        newItem.addEventListener('click', (e) => { e.preventDefault(); fetchAndDisplayResume(data.resume_id); });
    };
    
    const fetchAndDisplayResume = async (resumeId) => {
        showState('loading');
        try {
            const response = await fetch(`/api/resumes/${resumeId}`);
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Gagal memuat resume.');
            displayResumeData(data, false);
        } catch (error) {
            alert(error.message);
            showState('upload');
        }
    };

    uploadInput.addEventListener('change', () => { if (uploadInput.files.length > 0) processFile(uploadInput.files[0]); });
    uploadBox.addEventListener('dragover', (e) => e.preventDefault());
    uploadBox.addEventListener('drop', (e) => { e.preventDefault(); if (e.dataTransfer.files.length > 0) processFile(e.dataTransfer.files[0]); });
    
    downloadBtn.addEventListener('click', () => {
        const { jsPDF } = window.jspdf;
        const resumeEl = document.getElementById('resume-output');
        const filename = document.querySelector(`.resume-item[data-id='${currentResumeId}'] .filename`)?.textContent || 'resume.pdf';
        
        downloadBtn.textContent = 'Mempersiapkan PDF...';
        
        html2canvas(resumeEl, { scale: 2, useCORS: true }).then(canvas => {
            const imgData = canvas.toDataURL('image/png');
            const pdf = new jsPDF('p', 'mm', 'a4');
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
            
            pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
            pdf.save(`Farmile - ${filename}`);
            downloadBtn.textContent = 'Unduh Hasil';
        });
    });

    deleteBtn.addEventListener('click', async () => {
        if (!currentResumeId || !confirm('Anda yakin ingin menghapus resume ini?')) return;
        try {
            const response = await fetch(`/api/resumes/${currentResumeId}`, { method: 'DELETE' });
            if (!response.ok) throw new Error('Gagal menghapus.');
            document.querySelector(`.resume-item[data-id='${currentResumeId}']`)?.remove();
            showState('upload');
        } catch (error) { alert(error.message); }
    });

    document.querySelectorAll('.resume-item').forEach(item => {
        item.addEventListener('click', (e) => { e.preventDefault(); fetchAndDisplayResume(item.dataset.id); });
    });

    showState('upload');
});