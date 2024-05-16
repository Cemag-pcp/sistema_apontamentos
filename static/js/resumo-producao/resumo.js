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
            if(response == 'Verifique se contém carga para esses dias'){
                buildTable('','','','')
                alert(response)
                $("#loading").hide();
                return
            } else if(response ==='Pintura' || response === 'Montagem'){
                buildTable('','','','')
                alert("Não possui dados de " + response +" nesse intervalo de data")
                $("#loading").hide();
                return
            }

            var data = response.data;
            var colunas = response.colunas;
            var df_com_codigos = response.df_com_codigos;
            var base_final = response.base_final;
            var carretas_dentro_da_base = response.carretas_dentro_da_base;
            
            console.log(base_final)

            $('#bodyCarretasCadastradasReuniao').empty();
            // Manipular os dados recebidos da API aqui
            carretCadastradas('#bodyCarretasCadastradasReuniao',carretas_dentro_da_base);
            baixar_resumo(dataInicial,dataFinal)
            buildTable(data,colunas,df_com_codigos,base_final)
            $("#loading").hide();
        } else {
            console.error('Erro ao chamar a API:', response);
            $("#loading").hide();
        }
    };
    xhr.onerror = function() {
        console.error('Erro ao chamar a API.');
        $("#loading").hide();
    };
    xhr.send();
};

document.addEventListener('DOMContentLoaded',function() {
    var botaoFiltrar = document.getElementById('filtrar_datas');
    botaoFiltrar.addEventListener('click',function () {
        // document.getElementById('filtro_faltando_pecas').checked = false
        getResumo();
    })
})

function buildTable(jsonData,colunas,df_com_codigos,base_final) {
    const thead = document.querySelector('#dataTableReuniao thead tr');
    const tbody = document.querySelector('#tbodyConjuntoReuniao');
    const tbodyBaseFinal = document.querySelector('#tbodyBaseFinal');
    const campoTable = document.getElementById('campoTable');

    campoTable.style.display = 'block';
    thead.innerHTML = '';
    tbody.innerHTML = '';
    tbodyBaseFinal.innerHTML = '';
    
    if(colunas !== '') {
        populateTableHeader(thead, colunas);
        populateTableBodyReuniao(tbody, jsonData, colunas, df_com_codigos);
    } if(base_final !== ''){
        populateTableBodyBaseFinal(tbodyBaseFinal,base_final)
    }
}

function populateTableHeader(thead, columnNames) {
    columnNames.forEach(name => {
        const th = document.createElement('th');
        th.textContent = name;
        if(name === 'Quantidade de Carretas') {
            th.style.display = 'none';
        }
        th.style.minWidth = '100px'
        thead.appendChild(th);
    });
}

function populateTableBodyBaseFinal(tbody,base_final) {

    base_final.forEach(function(item) {
        // Cria uma nova linha da tabela
        var newRow = document.createElement("tr");
    
        // Define o HTML das células da linha com os dados correspondentes
        newRow.innerHTML = `
            <td data-title='Data da Carga'>${formatDate(item["data_carga"],'T')}</td>
            <td data-title='Processo'>${item["processo"]}</td>
            <td data-title='Código do Conjunto'>${item["codigo_conjunto"]}</td>
            <td data-title='Descrição do Conjunto'>${item["peca"]}</td>
            <td data-title='Código da Peça'>${item["codigo"]}</td>
            <td data-title='Descrição da Peça'>${item["descricao"]}</td>
            <td data-title='Quantidade Atualizada'>${item["qt_atualizada"]}</td>
        `;
    
        // Adiciona a nova linha ao corpo da tabela
        tbody.appendChild(newRow);
    });
}

function populateTableBodyReuniao(tbody, jsonData, columnNames,df_com_codigos) {
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