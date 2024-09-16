function showLoading() {
    $('#loading').show();
}

function hideLoading() {
    $('#loading').hide();
}

function addOneDay(dateString) {
    const date = new Date(dateString);  // Converte a string para o objeto Date
    date.setDate(date.getDate() + 1);   // Adiciona 1 dia à data atual
    return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function formatCellText(text) {
    // Remove espaços extras e formata a string
    return text
        .replace(/(\w+ \d+\.\d+) - (\d+) - (.*)/g, '$1 - $2')  // Formata o padrão específico
        .replace(/(Já consumido - \d+ ).*/, '$1')           // Remove o que vem após o segundo ' - ' para "Já consumido"
        .replace(/(Em estoque - \d+\.\d+ - \d+).*/, '$1');
}

function updateSearch(dataInicial,dataFinal) {
    const tbody = document.querySelector('#dataTableConsulta tbody');
    const thead = document.querySelector('#dataTableConsulta thead');
    tbody.innerHTML = '';

    // Obtenha o filtro atual
    const recursoFiltro = document.getElementById('recursoFiltro').value.toLowerCase();

    // Filtra e ordena os dados
    const filteredData = window.receivedData.filter(item => 
        item[1].toLowerCase().includes(recursoFiltro)
    );

    // Ordena por data (assumindo que a data está na primeira posição do item)
    filteredData.sort((a, b) => new Date(a[0]) - new Date(b[0]));

    const ths = thead.querySelectorAll('th');
    // Itera sobre os dados recebidos e adiciona linhas à tabela
    filteredData.forEach((item) => {
        const tr = document.createElement('tr');
        
        item.forEach((cell, index) => {
            const td = document.createElement('td');
            td.style.minWidth = '130px';

            if (ths[index]) {
                td.setAttribute('data-title', ths[index].textContent.trim());
            }
            if (index === 0) {
                td.textContent = addOneDay(cell);
            } else if (index === 3) {
                td.style.display = 'none';
                td.textContent = cell;
            } else if (index < 3) {
                td.textContent = cell;
            } else {
                // td.setAttribute('title', "M: \n"+ cell + "\nP: ");
                td.setAttribute('title', cell);
                cell = String(cell)

                cell = formatCellText(cell);

                console.log(cell)
                if (cell.includes('Já consumido')) {
                    // Expressão regular para capturar todas as ocorrências de "Já consumido" com quantidade e código
                    cell = cell.replace(/Já consumido\s(\d+\.\d+)\s-\s(\d{6})/g, function(_, quantity, code) {
                        return `<br><a href="#" data-toggle="modal" data-target="#modalPecas" data-code="${code}" data-quantity="${quantity}">
                                    <i class="fas fa-check-circle" style="color:green"></i> ${code} - ${quantity}
                                </a> OK`;
                    });
                }
                if (cell.includes('Em estoque')) {
                    // Expressão regular para capturar todas as ocorrências de "Em estoque" com quantidade e código
                    cell = cell.replace(/Em estoque\s-\s(\d+\.\d+)\s-\s(\d{6})/g, function(_, quantity, code) {
                        return `<br><a href="#" data-toggle="modal" data-target="#modalPecas" data-code="${code}" data-quantity="${quantity}">
                                    <i class="fas fa-box" style="color:orange"></i> ${code} - ${quantity}
                                </a>`;
                    });
                }
                if (cell.includes('Falta')) {
                    // Expressão regular para capturar todas as ocorrências de "Falta" com quantidade e código
                    cell = cell.replace(/Falta\s(\d+\.\d+)\s-\s(\d{6})/g, function(_, quantity, code) {
                        return `<br><a href="#" data-toggle="modal" data-target="#modalPecas" data-code="${code}" data-quantity="${quantity}">
                                    <i class="fas fa-exclamation-triangle" style="color:red"></i> ${code} - ${quantity}
                                </a>`;
                    });
                }
    
                // Define o conteúdo HTML da célula
                // td.innerHTML ="M:"+ cell + "<br>P: ";
                td.innerHTML = cell;
            }
    
            tr.appendChild(td);
        });
        // Adiciona a coluna com o botão "Consumir" se a quarta coluna não estiver vazia
        const tdButton = document.createElement('td');
        if (item[3] !== '' && item[3] !== null) { // Verifica se a quarta coluna não está vazia
            const button = document.createElement('button');
            button.textContent = 'Consumir';
            button.className = 'btn btn-primary';
            button.onclick = function() {
                handleConsumir(item);
            };
            tdButton.appendChild(button);
        }
        tr.appendChild(tdButton);

        tbody.appendChild(tr);
    });
    const consumirTudoButton = document.getElementById('consumir_tudo');

    if (filteredData.length > 0) {
        consumirTudoButton.style.display = 'block';

        const itensSelecionados = filteredData.map(item => ({
            carreta: item[1],
            numeroSerie: item[3]
        }));

        consumirTudoButton.onclick = function() {
            handleConsumirTudo(itensSelecionados,dataInicial,dataFinal);
        };
    } else {
        consumirTudoButton.style.display = 'none';
    }
}
