function dataConsumo(dataString) {
    const data = new Date(dataString);
    const dia = data.getUTCDate().toString().padStart(2, '0'); // Dia com dois dígitos
    const mes = (data.getUTCMonth() + 1).toString().padStart(2, '0'); // Mês com dois dígitos (Janeiro é 0, por isso o +1)
    const ano = data.getUTCFullYear();
    return `${dia}/${mes}/${ano}`;
}

// Função para lidar com a lógica do botão "Consumir"
function handleConsumir(item) {
    const confirmed = confirm(`Você deseja consumir o item com número de série: ${item[1]}?`);
    if (confirmed) {
        showLoading();
        fetch('/consumir-item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id_carreta: item[3],carreta: item[1] })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Resposta do servidor:', data.message);
            hideLoading();
            filtrarDatasPorCarretas();
        })
        .catch(error => {
            console.error('Erro:', error);
            hideLoading();
        });
    } else {
        // Lógica para quando o usuário cancelar
        console.log('Consumir cancelado para:', item[3]);
    }
}

// Função para lidar com a lógica do botão "Consumir"
function handleConsumirTudo(itens,dataInicial,dataFinal) {
    let confirmed;
    if(dataInicial===dataFinal) {
        confirmed = confirm(`Você deseja consumir tudo da data ${dataConsumo(dataInicial)}?`);
        if (confirmed) {
            showLoading();
            fetch('/consumir-tudo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({itens})
            })
            .then(response => response.json())
            .then(data => {
                console.log('Resposta do servidor:', data.message);
                hideLoading();
                filtrarDatasPorCarretas();
            })
            .catch(error => {
                console.error('Erro:', error);
                hideLoading();
            });
        } else {
            // Lógica para quando o usuário cancelar
            console.log('Consumir cancelado para:', dataConsumo(dataInicial));
        }
    } else {
        confirmed = confirm(`Você deseja consumir tudo entre as data: ${dataConsumo(dataInicial)} e ${dataConsumo(dataFinal)}?`);
        
        if (confirmed) {
            showLoading();
            fetch('/consumir-tudo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({itens})
            })
            .then(response => response.json())
            .then(data => {
                console.log('Resposta do servidor:', data.message);
                hideLoading();
                filtrarDatasPorCarretas();
            })
            .catch(error => {
                console.error('Erro:', error);
                hideLoading();
            });
        } else {
            // Lógica para quando o usuário cancelar
            console.log(`Consumir cancelado para: ${dataConsumo(dataInicial)} e ${dataConsumo(dataFinal)}`)
        }
        
    }
}