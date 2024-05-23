// Array com as causas
const causas = ["Faltando Solda", "Olho de Peixe", "Arranhão", "Escorrimento", "Empoeiramento", "Casca de Laranja", "Manchas",
    "Contato", "Amassando", "Camada Baixa", "Corrosão", "Marcação por Água", "Marcação por Óleo", "Tonalidade", "Marca texto industrial", "Respingo de Solda",
    "Marcação de Peça", "Falta de aderência", "Decapante", "Desplacamento", "Água"
];

const causas_solda = ["Faltando Solda", "Porosidade", "Solda não conforme (robô)", "Solda deslocada", "Medida não conforme", "Casca de Laranja", "Solda sem penetração",
    "Excesso de respingo", "Excesso de rebarba", "Excesso de solda", "Mordedura", "Erro de montagem","Outro"];

// Função para adicionar select de causas
function adicionarSelects(n_nao_conformidades, coluna_causa, setor) {
    const nConformidades = document.getElementById(n_nao_conformidades).value;
    const colunaCausa = document.getElementById(coluna_causa);

    colunaCausa.innerHTML = "";

    const divRow = document.createElement('div');
    divRow.className = 'row';

    if (nConformidades > 0) {
        colunaCausa.style.display = 'block';
        for (let i = 1; i <= nConformidades; i++) {
            const div = document.createElement("div");
            div.className = "col-sm-6 mb-4";

            const label = document.createElement("label");
            label.textContent = `Causa ${i}`;

            if (setor === 'Pintura') {
                var select = criarSelectCausa(i,causas);
            } else {
                var select = criarSelectCausa(i,causas_solda);
            }

            const campoArquivos = criarCampoArquivos(i);

            div.appendChild(label);
            div.appendChild(select);
            divRow.appendChild(div);
            divRow.appendChild(campoArquivos);
            colunaCausa.appendChild(divRow);
        }
        colunaCausa.querySelectorAll('[id^="foto_inspecao_"]').forEach(inputElement => {
            inputElement.addEventListener("change", function () {
                const files = this.files;
                const label = this.parentNode.querySelector('.custom-file-label'); // Obter a label correspondente
                label.textContent = files.length === 1 ? `Possui ${files.length} arquivo` : `Possui ${files.length} arquivos`;
            });
        });
    } else {
        colunaCausa.style.display = 'none';
    }
}

// Função para criar select de causa
function criarSelectCausa(i,causas) {
    const select = document.createElement("select");
    select.name = `causa_reinspecao_${i}`;
    select.id = `causa_reinspecao_${i}`;
    select.className = "form-control";

    const optionHidden = document.createElement("option");
    optionHidden.value = "";
    optionHidden.selected = true;
    optionHidden.hidden = true;
    select.appendChild(optionHidden);

    causas.forEach(causa => {
        const option = document.createElement("option");
        option.value = causa;
        option.textContent = causa;
        select.appendChild(option);
    });

    return select;
}

// Função para criar campo de arquivos
function criarCampoArquivos(i) {
    const campoArquivos = document.createElement('div');
    campoArquivos.id = `campo_arquivos_${i}`;
    campoArquivos.className = 'col-sm-6 mb-4';

    const labelArquivos = document.createElement('label');
    labelArquivos.textContent = `Escolha os arquivos da causa ${i}:`;

    const customFileDiv = document.createElement('div');
    customFileDiv.className = 'custom-file';

    const inputFile = document.createElement('input');
    inputFile.type = 'file';
    inputFile.className = 'custom-file-input';
    inputFile.id = `foto_inspecao_${i}`;
    inputFile.name = `foto_inspecao_${i}`;
    inputFile.accept = 'image/*';
    inputFile.multiple = true;

    const labelInputFile = document.createElement('label');
    labelInputFile.className = 'custom-file-label';
    labelInputFile.htmlFor = `foto_inspecao_${i}`;
    labelInputFile.textContent = 'Escolha os arquivos';

    customFileDiv.appendChild(inputFile);
    customFileDiv.appendChild(labelInputFile);

    campoArquivos.appendChild(labelArquivos);
    campoArquivos.appendChild(customFileDiv);

    return campoArquivos;
}

const nConformidades = document.getElementById("n_conformidades");
if (nConformidades) {
    nConformidades.addEventListener("input", () => {
        adicionarSelects("n_nao_conformidades", "coluna_causa", "Pintura");
    });
}

const nConformidadesReinspecao = document.getElementById("n_conformidades_reinspecao");
if (nConformidadesReinspecao) {
    nConformidadesReinspecao.addEventListener("input", () => {
        adicionarSelects("n_nao_conformidades_reinspecao", "coluna_causa_reinspecao", "Pintura");
    });
}

const inputConformidadesSolda = document.getElementById("inputConformidadesSolda");
if (inputConformidadesSolda) {
    inputConformidadesSolda.addEventListener("input", () => {
        adicionarSelects("inputNaoConformidadesSolda", "coluna_causa_solda", "Solda");
    });
}

const inputReinspecionadasConformidadesSolda = document.getElementById("inputReinspecionadasConformidadesSolda");
if (inputReinspecionadasConformidadesSolda) {
    inputReinspecionadasConformidadesSolda.addEventListener("input", () => {
        adicionarSelects("inputReinspecionadasNaoConformidadesSolda", "coluna_causa_reinspecao_solda", "Solda");
    });
}

