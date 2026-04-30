const fileInput = document.getElementById("file-input");
const uploadBtn = document.getElementById("upload-btn");
const uploadStatus = document.getElementById("upload-status");

const refreshBtn = document.getElementById("refresh-btn");
const datasetSelect = document.getElementById("dataset-select");
const datasetMeta = document.getElementById("dataset-meta");

const previewBtn = document.getElementById("preview-btn");
const previewOutput = document.getElementById("preview-output");

const sqlInput = document.getElementById("sql-input");
const sqlBtn = document.getElementById("sql-btn");
const sqlOutput = document.getElementById("sql-output");

const questionInput = document.getElementById("question-input");
const insightBtn = document.getElementById("insight-btn");
const insightOutput = document.getElementById("insight-output");

let datasets = [];

function selectedDatasetId() {
    return datasetSelect.value;
}

function renderDatasetSelect() {
    datasetSelect.innerHTML = "";
    if (!datasets.length) {
        const opt = document.createElement("option");
        opt.value = "";
        opt.textContent = "Нет загруженных датасетов";
        datasetSelect.appendChild(opt);
        datasetMeta.textContent = "";
        return;
    }

    datasets.forEach((ds) => {
        const opt = document.createElement("option");
        opt.value = ds.id;
        opt.textContent = `${ds.source_name} (${ds.rows} строк, ${ds.columns} колонок)`;
        datasetSelect.appendChild(opt);
    });
    showSelectedMeta();
}

function showSelectedMeta() {
    const ds = datasets.find((d) => d.id === selectedDatasetId()) || datasets[0];
    if (!ds) {
        datasetMeta.textContent = "";
        return;
    }
    datasetMeta.textContent = `ID: ${ds.id} | Файл: ${ds.source_name} | Размер: ${ds.rows}x${ds.columns}`;
}

async function refreshDatasets() {
    const response = await fetch("/datasets");
    const data = await response.json();
    datasets = data.datasets || [];
    renderDatasetSelect();
}

async function uploadDataset() {
    const file = fileInput.files[0];
    if (!file) {
        uploadStatus.textContent = "Выберите файл перед загрузкой.";
        return;
    }

    uploadBtn.disabled = true;
    uploadStatus.textContent = "Загрузка...";
    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/datasets/upload", {
            method: "POST",
            body: formData
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Ошибка загрузки.");
        }
        uploadStatus.textContent = `Готово: ${data.dataset.source_name}`;
        await refreshDatasets();
    } catch (error) {
        uploadStatus.textContent = error.message;
    } finally {
        uploadBtn.disabled = false;
    }
}

async function previewDataset() {
    const id = selectedDatasetId();
    if (!id) {
        previewOutput.textContent = "Сначала загрузите и выберите датасет.";
        return;
    }

    const response = await fetch(`/datasets/${id}/preview?rows=20`);
    const data = await response.json();
    if (!response.ok) {
        previewOutput.textContent = data.detail || "Ошибка предпросмотра.";
        return;
    }
    previewOutput.textContent = JSON.stringify(data.preview, null, 2);
}

async function runSql() {
    const id = selectedDatasetId();
    if (!id) {
        sqlOutput.textContent = "Сначала выберите датасет.";
        return;
    }

    const formData = new FormData();
    formData.append("sql", sqlInput.value);
    formData.append("limit", "200");

    sqlBtn.disabled = true;
    sqlOutput.textContent = "Выполняю SQL...";
    try {
        const response = await fetch(`/datasets/${id}/sql`, {
            method: "POST",
            body: formData
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Ошибка SQL.");
        }
        sqlOutput.textContent = JSON.stringify(data.result, null, 2);
    } catch (error) {
        sqlOutput.textContent = error.message;
    } finally {
        sqlBtn.disabled = false;
    }
}

async function askInsight() {
    const id = selectedDatasetId();
    if (!id) {
        insightOutput.textContent = "Сначала выберите датасет.";
        return;
    }
    if (!questionInput.value.trim()) {
        insightOutput.textContent = "Введите вопрос для модели.";
        return;
    }

    const formData = new FormData();
    formData.append("question", questionInput.value.trim());

    insightBtn.disabled = true;
    insightOutput.textContent = "Запрашиваю модель...";
    try {
        const response = await fetch(`/datasets/${id}/insight`, {
            method: "POST",
            body: formData
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Ошибка LLM-анализа.");
        }
        insightOutput.textContent = data.answer;
    } catch (error) {
        insightOutput.textContent = error.message;
    } finally {
        insightBtn.disabled = false;
    }
}

uploadBtn.addEventListener("click", uploadDataset);
refreshBtn.addEventListener("click", refreshDatasets);
datasetSelect.addEventListener("change", showSelectedMeta);
previewBtn.addEventListener("click", previewDataset);
sqlBtn.addEventListener("click", runSql);
insightBtn.addEventListener("click", askInsight);

refreshDatasets();
