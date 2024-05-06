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
            // Manipular os dados recebidos da API aqui
            buildTable(data,colunas)
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

function buildTable(jsonData,colunas) {
    const thead = document.querySelector('#dataTableReuniao thead tr');
    const tbody = document.querySelector('#tbodyConjuntoReuniao');
    const campoTable = document.getElementById('campoTable');

    campoTable.style.display = 'block';
    thead.innerHTML = '';
    tbody.innerHTML = '';

    populateTableHeader(thead, colunas);
    populateTableBody(tbody, jsonData, colunas);
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

function populateTableBody(tbody, jsonData, columnNames) {
    jsonData.forEach(row => {
        console.log(row)
        const tr = document.createElement('tr');
        row.forEach((cell, index) => {
            const td = document.createElement('td');
            td.setAttribute('data-title', columnNames[index]);
            let cellContent = cell;
            if (typeof cell === 'string' && (cell.includes('P:') || cell.includes('S:'))) {
                // Substitui 'P:' por '<br>P:' para adicionar quebra de linha no HTML
                cellContent = cell.replace('S:', '<br>S:').replace('P:', '<br>P:');
            }

            // Verifica se a célula precisa de formatação especial para zero
            if (cellContent || columnNames[index] === "Quantidade Faltante") {
                td.innerHTML = cellContent || "0";
                if (cellContent === row[1]) {
                    td.innerHTML = formatDate(cellContent,'T')
                } 
                if (typeof cell === 'string' && cell.includes('FP -')) {
                    td.classList.add('fp-highlight');
                    td.addEventListener('click', function() {
                        openModal(row);
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

function openModal(row) {

    $("#loading").show();
    $("#infoModalLabel").text(row[3])
    $("#informacoes_pecas").text("Informações das peças ref. o conjunto - " + row[3])
    // Pega os elementos de input pelo ID
    document.getElementById('data_carga').value = formatDate(row[1],'I') || '';
    document.getElementById('codigo_conjunto').value = row[2];
    document.getElementById('carreta_conjunto').value = row[0] || '';
    document.getElementById('quantidade_conjunto').value = row[5] || '0'; // Coluna 'Quantidade' preenchida com '0' se vazia
    document.getElementById('qtd_carreta').value = row[6] || '0';
    
    $.ajax({
        url: '/pecas_conjunto',
        type: 'POST',  // Alterado para POST
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({'codigo_conjunto': row[2] ,'carreta_conjunto':row[0]}),  // Enviando um objeto JSON
        success: function(response) {
            console.log(response);
            
            $('#formContainer').empty();

            response.forEach(function(item,index) {
                const html = `
                    <div class="row">
                        <div class="col-sm-6 mb-4">
                            <label for="codigo_conjunto_${index}">Codigo da Peça:</label>
                            <input type="text" name="codigo_conjunto_${index}" id="codigo_conjunto_${index}" value="${item[0]}" class="form-control" disabled>
                        </div>
                        <div class="col-sm-6 mb-4">
                            <label for="descricao_conjunto_${index}">Descrição da Peça:</label>
                            <input type="text" name="descricao_conjunto_${index}" id="descricao_conjunto_${index}" value="${item[1]}" class="form-control" disabled>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-sm-6 mb-4">
                            <label for="materia_prima_${index}">Matéria Prima:</label>
                            <input type="text" name="materia_prima_${index}" id="materia_prima_${index}" value="${item[2]}" class="form-control" disabled>
                        </div>
                        <div class="col-sm-6 mb-4">
                            <label for="qt_pecas_${index}">Quantidade de Peças:</label>
                            <input type="text" name="qt_pecas_${index}" id="qt_pecas_${index}" value="${item[3] * row[5]}" class="form-control" disabled>
                        </div>
                    </div>
                    <hr>`;
                $('#formContainer').append(html);
            })
            
            $("#loading").hide();
            $('#infoModal').modal('show');
        },
        error: function(error) {
            console.log(error);
            $("#loading").hide();
        }
    });
}
