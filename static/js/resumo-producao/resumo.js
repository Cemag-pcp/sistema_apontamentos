function getResumo() {

    $("#loading").show();
    
    var dataInicial = document.getElementById('dataReuniaoInicial').value;
    var dataFinal = document.getElementById('dataReuniaoFinal').value;

    var url = '/resumos-geral?datainicio='+ encodeURIComponent(dataInicial) +'&datafim='+ encodeURIComponent(dataFinal);

    var xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.onload = function() {
        if (xhr.status === 200) {
            var data = JSON.parse(xhr.responseText);
            // Manipular os dados recebidos da API aqui
            buildTable(data)
            $("#loading").hide();
        } else {
            console.error('Erro ao chamar a API:', xhr.statusText);
            $("#loading").hide();
        }
    };
    xhr.onerror = function() {
        console.error('Erro ao chamar a API.');
        $("#loading").hide();
    };
    xhr.send();
};

document.addEventListener('DOMContentLoaded',function(){
    var botaoFiltrar = document.getElementById('filtrar_datas');
    botaoFiltrar.addEventListener('click',function () {
        getResumo();
    })
})

function buildTable(jsonData) {
    const thead = document.querySelector('#dataTableReuniao thead tr');
    const tbody = document.querySelector('#tbodyConjuntoReuniao');
    const campoTable = document.getElementById('campoTable');

    campoTable.style.display = 'block';
    thead.innerHTML = '';
    tbody.innerHTML = '';

    const maxColumns = getMaxColumns(jsonData);
    const baseColumnNames = getBaseColumnNames(maxColumns);
    populateTableHeader(thead, baseColumnNames);
    populateTableBody(tbody, jsonData, baseColumnNames);
}

function getMaxColumns(jsonData) {
    return jsonData.data.reduce((max, row) => Math.max(max, row.length), 0);
}

function getBaseColumnNames(maxColumns) {
    const columnNames = ["Produto", "Data", "Código do Conjunto", "Descrição", "Código da Pintura", "Quantidade", "Chassi", "Conj. Intermed", "Eixo Completo", "Fueiro","Icamento",
"Lateral","Plat.Tranque","Cacamba"];
    columnNames.length = maxColumns; // Ajusta o tamanho do array de cabeçalhos para o máximo encontrado
    return columnNames;
}

function populateTableHeader(thead, columnNames) {
    columnNames.forEach(name => {
        const th = document.createElement('th');
        th.textContent = name;
        thead.appendChild(th);
    });
}

function populateTableBody(tbody, jsonData, columnNames) {
    jsonData.data.forEach(row => {
        const tr = document.createElement('tr');
        row.forEach((cell, index) => {
            const td = document.createElement('td');
            if (cell || columnNames[index] === "Quantidade") {
                td.textContent = cell || "0";
                if (typeof cell === 'string' && cell.includes('FP -')) {
                    td.classList.add('fp-highlight');
                    td.addEventListener('click', function() {
                        openModal(row);
                    });
                }
            } else {
                td.textContent = row[index] || "";
            }
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

function formatDate(dataString) {
    var data = new Date(dataString);
    // Ajustar para o fuso horário local
    data.setMinutes(data.getMinutes() - data.getTimezoneOffset());
    data.setDate(data.getDate() + 1); // Adicionar um dia à data
    var dia = ("0" + data.getDate()).slice(-2);
    var mes = ("0" + (data.getMonth() + 1)).slice(-2);
    var ano = data.getFullYear();
    return ano + '-' + mes + '-' + dia;
}

function openModal(row) {
    // Pega os elementos de input pelo ID
    console.log(row[1])
    console.log(formatDate(row[1]))

    document.getElementById('data_carga').value = formatDate(row[1]) || '';
    document.getElementById('codigo_conjunto').value = row[2];
    document.getElementById('carreta_conjunto').value = row[0] || '';
    document.getElementById('quantidade_conjunto').value = row[5] || '0'; // Coluna 'Quantidade' preenchida com '0' se vazia
    
    // Mostra o modal
    $('#infoModal').modal('show');
}


