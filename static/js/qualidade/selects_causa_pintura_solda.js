// Array com as causas
const causas_pintura = ["Faltando Solda", "Olho de Peixe", "Arranhão", "Escorrimento", "Empoeiramento", "Casca de Laranja", "Manchas",
    "Contato", "Amassando", "Camada Baixa", "Corrosão", "Marcação por Água", "Marcação por Óleo", "Tonalidade", "Marca texto industrial", "Respingo de Solda",
    "Marcação de Peça", "Falta de aderência", "Decapante", "Desplacamento", "Água"
];

const causas_solda = ["Faltando Solda", "Porosidade", "Solda não conforme (robô)", "Solda deslocada", "Medida não conforme", "Casca de Laranja", "Solda sem penetração",
    "Excesso de respingo", "Excesso de rebarba", "Excesso de solda", "Mordedura", "Erro de montagem","Outro"
];

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

            const label = document.createElement("label");
            label.textContent = `Causa ${i}`;

            const campoArquivos = criarCampoArquivos(i);
            const campoQuantidade = criarCampoQuantidade(i);

            if (setor === 'Pintura') {
                
                div.className = "col-sm-6 mb-4";

                div.appendChild(label);
                
                var select = criarSelectCausa(i,causas_pintura);
                div.appendChild(select);
                divRow.appendChild(div);
                divRow.appendChild(campoArquivos);

            } else if(setor === 'Estamparia'){

                div.className = "col-sm-4 mb-4";

                div.appendChild(label);

                var select = criarSelectCausa(i,causas_pintura);
                div.appendChild(select);
                divRow.appendChild(div);
                divRow.appendChild(campoQuantidade);
                divRow.appendChild(campoArquivos);

            } else {

                div.className = "col-sm-7 mb-4";

                div.appendChild(label);

                var select = criarSelectCausa(i,causas_solda);
                div.appendChild(select);
                divRow.appendChild(div);
                divRow.appendChild(campoArquivos);

            }

            colunaCausa.appendChild(divRow);
        }
        colunaCausa.querySelectorAll('[id^="foto_inspecao_"]').forEach(inputElement => {
            inputElement.addEventListener("change", function () {
                const files = this.files;
                const label = this.parentNode.querySelector('.custom-file-label'); // Obter a label correspondente
                label.textContent = files.length === 1 ? `${files.length} arquivo` : `${files.length} arquivos`;
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

function criarCampoQuantidade(i) {
    const campoQuantidade = document.createElement('div');
    campoQuantidade.id = `campo_quantidade_${i}`;
    campoQuantidade.className = 'col-sm-3 mb-4';

    const labelQuantidade = document.createElement('label');
    labelQuantidade.textContent = `Quantidade:`;

    const inputFile = document.createElement('input');
    inputFile.type = 'number';
    inputFile.className = 'form-control';
    inputFile.id = `quantidade_causas_${i}`;
    inputFile.name = `quantidade_causas_${i}`;

    campoQuantidade.appendChild(labelQuantidade);

    campoQuantidade.appendChild(inputFile);

    return campoQuantidade;
}


// Função para criar campo de arquivos
function criarCampoArquivos(i) {
    const campoArquivos = document.createElement('div');
    campoArquivos.id = `campo_arquivos_${i}`;
    campoArquivos.className = 'col-sm-6 mb-4';

    const labelArquivos = document.createElement('label');
    labelArquivos.textContent = `Arquivos da causa ${i}:`;

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
    labelInputFile.textContent = 'Arquivos';

    customFileDiv.appendChild(inputFile);
    customFileDiv.appendChild(labelInputFile);

    campoArquivos.appendChild(labelArquivos);
    campoArquivos.appendChild(customFileDiv);

    return campoArquivos;
}

const nConformidades = document.getElementById("n_conformidades");
if (nConformidades) {
    nConformidades.addEventListener("input", () => {
        if(nConformidades.value < 0 || nConformidades === ''){
            $("#coluna_causa").empty()
            return
        }
        adicionarSelects("n_nao_conformidades", "coluna_causa", "Pintura");
    });
}

const nConformidadesReinspecao = document.getElementById("n_conformidades_reinspecao");
if (nConformidadesReinspecao) {
    nConformidadesReinspecao.addEventListener("input", () => {
        if(nConformidadesReinspecao.value < 0 || nConformidadesReinspecao === ''){
            $("#coluna_causa_reinspecao").empty()
            return
        }
        adicionarSelects("n_nao_conformidades_reinspecao", "coluna_causa_reinspecao", "Pintura");
    });
}

const inputConformidadesSolda = document.getElementById("inputConformidadesSolda");
if (inputConformidadesSolda) {
    inputConformidadesSolda.addEventListener("input", () => {
        if(inputConformidadesSolda.value < 0 || inputConformidadesSolda === ''){
            $("#coluna_causa_solda").empty()
            return
        }
        adicionarSelects("inputNaoConformidadesSolda", "coluna_causa_solda", "Solda");
    });
}


const inputReinspecionadasConformidadesSolda = document.getElementById("inputReinspecionadasConformidadesSolda");
if (inputReinspecionadasConformidadesSolda) {
    inputReinspecionadasConformidadesSolda.addEventListener("input", () => {
        if(inputReinspecionadasConformidadesSolda.value < 0 || inputReinspecionadasConformidadesSolda === ''){
            $("#coluna_causa_reinspecao_solda").empty()
            return
        }
        adicionarSelects("inputReinspecionadasNaoConformidadesSolda", "coluna_causa_reinspecao_solda", "Solda");
    });
}

let qtd_conformidade_edicao = document.getElementById("qtd_conformidade_edicao");
let qtd_conformidade_atualizada_edicao = document.getElementById("qtd_conformidade_atualizada_edicao");
let num_causas_edicao = document.getElementById("num_causas_edicao").value

if (qtd_conformidade_atualizada_edicao) {
    qtd_conformidade_atualizada_edicao.addEventListener("input", () => {
        num_causas_edicao = qtd_conformidade_edicao.value - qtd_conformidade_atualizada_edicao.value
        if(qtd_conformidade_atualizada_edicao.value < 0 || qtd_conformidade_atualizada_edicao === ''){
            $("#coluna_causa_edicao_solda").empty()
            return
        }
        $('#num_causas_edicao').val(num_causas_edicao)
        adicionarSelects('num_causas_edicao', "coluna_causa_edicao_solda", "Solda");
    });
}

