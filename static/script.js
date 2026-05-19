let currentLogoData = null;
let selectedStyle = null;

// Загрузка стилей при старте
async function loadStyles() {
    try {
        const response = await fetch('/styles');
        const data = await response.json();
        renderStyleGrid(data.styles);
    } catch (error) {
        console.error('Error loading styles:', error);
    }
}

function renderStyleGrid(styles) {
    const grid = document.getElementById('style-grid');
    grid.innerHTML = '';

    for (const [key, style] of Object.entries(styles)) {
        const div = document.createElement('div');
        div.className = 'style-option';
        div.dataset.style = key;
        div.innerHTML = `
            <div class="style-name">${style.name}</div>
            <div class="style-desc">${style.description}</div>
        `;
        div.onclick = () => selectStyle(key, div);
        grid.appendChild(div);
    }
}

function selectStyle(styleKey, element) {
    // Remove selected class from all
    document.querySelectorAll('.style-option').forEach(el => {
        el.classList.remove('selected');
    });
    element.classList.add('selected');
    selectedStyle = styleKey;
}

// Генерация логотипа
document.getElementById('generate-btn').addEventListener('click', async () => {
    const businessName = document.getElementById('business-name').value.trim();
    const industry = document.getElementById('industry').value;
    const slogan = document.getElementById('slogan').value.trim();
    const additionalInfo = document.getElementById('additional-info').value.trim();

    if (!businessName) {
        alert('Пожалуйста, введите название компании');
        return;
    }

    if (!selectedStyle) {
        alert('Пожалуйста, выберите стиль логотипа');
        return;
    }

    const loading = document.getElementById('loading');
    loading.classList.remove('hidden');

    const formData = new FormData();
    formData.append('business_name', businessName);
    formData.append('industry', industry);
    formData.append('style', selectedStyle);
    if (slogan) formData.append('slogan', slogan);
    if (additionalInfo) formData.append('additional_info', additionalInfo);

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            displayLogo(data.logo);
            currentLogoData = data.logo;
        } else {
            alert('Ошибка: ' + (data.detail || 'Неизвестная ошибка'));
        }
    } catch (error) {
        alert('Ошибка соединения: ' + error.message);
    } finally {
        loading.classList.add('hidden');
    }
});

function displayLogo(logo) {
    const container = document.getElementById('logo-container');
    container.innerHTML = logo.svg;

    document.getElementById('logo-description').textContent = logo.description;
    document.getElementById('download-btn').disabled = false;
    document.getElementById('refine-btn').disabled = false;
}

// Скачивание логотипа
document.getElementById('download-btn').addEventListener('click', () => {
    if (!currentLogoData) return;

    const svg = currentLogoData.svg;
    const blob = new Blob([svg], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `logo_${currentLogoData.business_name.toLowerCase().replace(/\s+/g, '_')}.svg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});

// Доработка логотипа
document.getElementById('refine-btn').addEventListener('click', () => {
    const refineSection = document.getElementById('refine-section');
    refineSection.classList.toggle('hidden');
});

document.getElementById('submit-refine-btn').addEventListener('click', async () => {
    const feedback = document.getElementById('feedback-input').value.trim();
    if (!feedback) {
        alert('Введите пожелания по доработке');
        return;
    }
})