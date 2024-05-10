function getResumo() {

    $("#loading").show();
    
    var dataInicial = document.getElementById('dataReuniaoInicial').value;
    var dataFinal = document.getElementById('dataReuniaoFinal').value;

    var url = '/resumos-geral?datainicio='+ encodeURIComponent(dataInicial) +'&datafim='+ encodeURIComponent(dataFinal);

    var xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.onload = function() {
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            var data = response.data;
            var colunas = response.colunas;
            var df_com_codigos = response.df_com_codigos;
            // Manipular os dados recebidos da API aqui
            buildTable(data,colunas,df_com_codigos)
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
        document.getElementById('filtro_faltando_pecas').checked = false
        getResumo();
    })
})

function buildTable(jsonData,colunas,df_com_codigos) {
    const thead = document.querySelector('#dataTableReuniao thead tr');
    const tbody = document.querySelector('#tbodyConjuntoReuniao');
    const campoTable = document.getElementById('campoTable');

    campoTable.style.display = 'block';
    thead.innerHTML = '';
    tbody.innerHTML = '';

    populateTableHeader(thead, colunas);
    populateTableBody(tbody, jsonData, colunas, df_com_codigos);
}

function populateTableHeader(thead, columnNames) {
    columnNames.forEach(name => {
        const th = document.createElement('th');
        th.textContent = name;
        if(name === 'Quantidade de Carretas'){
            th.style.display = 'none';
        }
        th.style.minWidth = '100px'
        thead.appendChild(th);
    });
}

function populateTableBody(tbody, jsonData, columnNames,df_com_codigos) {
    jsonData.forEach(row => {
        const tr = document.createElement('tr');
        row.forEach((cell, index) => {
            const td = document.createElement('td');
            td.setAttribute('data-title', columnNames[index]);
            let cellContent = cell;
            if (typeof cell === 'string' && (cell.includes('P:') || cell.includes('M:'))) {
                cellContent = cell.replace('M:', '<br>M:').replace('P:', '<br>P:');
            }
            if (cellContent) {
                td.innerHTML = cellContent || "0";
                if (cellContent === row[1]) {
                    td.innerHTML = formatDate(cellContent,'T')
                } 
                if (typeof cell === 'string' && cell.includes('FP -')) {
                    td.classList.add('fp-highlight');
                    td.addEventListener('click', function() {
                        openModal(row, columnNames[index],df_com_codigos);
                    });
                }
            }
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

function formatDate(dataString,parameter) {
    var data = new Date(dataString);
    // Ajustar para o fuso horário local
    data.setMinutes(data.getMinutes() - data.getTimezoneOffset());
    data.setDate(data.getDate() + 1); // Adicionar um dia à data
    var dia = ("0" + data.getDate()).slice(-2);
    var mes = ("0" + (data.getMonth() + 1)).slice(-2);
    var ano = data.getFullYear();
    if(parameter == 'I'){
        return ano + '-' + mes + '-' + dia;
    } else {
        return dia + '/' + mes + '/' + ano;
    }
}