function openModal(row,columnIndex,df_com_codigos) {

    $("#loading").show();
    $("#infoModalLabel").text(row[0] + ' - ' + columnIndex)
    $("#informacoes_conjuntos").text("Conjuntos Faltantes")

    // Pega os elementos de input pelo ID
    document.getElementById('data_carga').value = formatDate(row[1],'I') || '';
    document.getElementById('carreta_conjunto').value = row[0] || '';

    let filteredDf = df_com_codigos.filter(item => item[0] === row[0] && item[1] === columnIndex && item[2] === row[1] && item[6] > 0);

    $('#formContainerConjunto').empty();

    var url = '/pecas_conjunto?carreta='+ encodeURIComponent(row[0])

    filteredDf.forEach(function(item,index) {
        const html = `
                    <div class="row">
                        <div class="col-sm-4 mb-4">
                            <label for="codigo_conjunto_${index}">Codigo do Conjunto:</label>
                            <input type="text" name="codigo_conjunto_${index}" id="codigo_conjunto_${index}" value="${item[7]}" class="form-control" disabled>
                        </div>
                        <div class="col-sm-4 mb-4">
                            <label for="descricao_conjunto_${index}">Descrição do Conjunto:</label>
                            <input type="text" name="descricao_conjunto_${index}" id="descricao_conjunto_${index}" value="${item[8]}" class="form-control" disabled>
                        </div>
                        <div class="col-sm-4 mb-4">
                            <label for="codigo_conjunto_${index}">Quantidade Faltante:</label>
                            <input type="text" name="codigo_conjunto_${index}" id="codigo_conjunto_${index}" value="${item[6]}" class="form-control" disabled>
                        </div>
                    </div>`;
        url += '&codigo='+ item[7] + '&quantidade=' + item[6]
        $('#formContainerConjunto').append(html);
    })

    var xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.onload = function() {
        $('#formContainerPecas').empty();
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            console.log(response)
            var pecas = response[0];
            var saldo = response[1];
            var count = 0
            pecas.forEach(function (item,index) {
                if((saldo[index][1] - item.quantidade_total) < 0){
                    var inputs =`
                    <div class="row">
                        <div class="col-sm-3 mb-4">
                            <label for="codigo_peca_${index}">Codigo da Peça:</label>
                            <input type="text" name="codigo_peca_${index}" id="codigo_peca_${index}" value="${item.codigo}" class="form-control" disabled>
                        </div>
                        <div class="col-sm-7 mb-4">
                            <label for="descricao_peca_${index}">Descrição da Peça:</label>
                            <input type="text" name="descricao_peca_${index}" id="descricao_peca_${index}" value="${item.descricao}" class="form-control" disabled>
                        </div>
                        <div class="col-sm-2 mb-4">
                            <label for="qtd_faltante_peca_${index}">Faltante:</label>
                            <input type="text" name="qtd_faltante_peca_${index}" id="qtd_faltante_peca_${index}" value="${saldo[index][1] - item.quantidade_total}" class="form-control" disabled>
                        </div>
                    </div>`;
                    count += 1
                    console.log(count)
                } else {
                    var inputs = ''
                }

                $('#formContainerPecas').append(inputs);
            })

            if(count == 0) {

                var inputs = `
                <div class="row">
                    <div class="d-flex flex-row justify-content-center m-auto">
                        <h5>Todas as peças necessárias estão disponíveis no estoque</h5>
                    </div>
                </div>`

                $('#formContainerPecas').append(inputs);
            }

            $("#loading").hide();
            $("#infoModal").modal('show')
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
}
