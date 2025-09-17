document.addEventListener('DOMContentLoaded', () => {
    const reflectionModal = document.getElementById('reflectionModal');
    if (reflectionModal) {
        const reflectionForm = document.getElementById('reflectionForm');
        const reflectionText = document.getElementById('reflectionText');
        const reflectionUserProjectId = document.getElementById('reflectionUserProjectId');

        document.querySelectorAll('.open-reflection-modal').forEach(button => {
            button.addEventListener('click', () => {
                const userProjectId = button.dataset.userprojectid;
                const currentReflection = button.dataset.reflection;

                reflectionUserProjectId.value = userProjectId;
                reflectionText.value = currentReflection;

                reflectionModal.classList.add('visible');
            });
        });

        reflectionModal.addEventListener('click', (e) => {
            if (e.target === reflectionModal || e.target.closest('.modal-close-btn')) {
                reflectionModal.classList.remove('visible');
            }
        });

        reflectionForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const userProjectId = reflectionUserProjectId.value;
            const text = reflectionText.value;
            const submitButton = reflectionForm.querySelector('button[type="submit"]');

            submitButton.disabled = true;
            submitButton.textContent = 'Menyimpan...';

            try {
                const response = await fetch(`/api/user-project/${userProjectId}/reflection`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ reflection: text })
                });
                if (!response.ok) throw new Error('Gagal menyimpan refleksi.');

                const buttonToUpdate = document.querySelector(`.open-reflection-modal[data-userprojectid='${userProjectId}']`);
                if(buttonToUpdate) {
                    buttonToUpdate.dataset.reflection = text;
                }

                reflectionModal.classList.remove('visible');
                alert('Refleksi berhasil disimpan!');
            } catch (error) {
                alert(error.message);
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = 'Simpan Refleksi';
            }
        });
    }
});