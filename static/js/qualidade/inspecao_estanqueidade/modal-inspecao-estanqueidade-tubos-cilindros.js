function modalTubos(id,data,codigo,qtd_apontada) {

    $('#id_tubo').val(id)

    $('#data_tubo').val(formatarDataModal(data));

    $('#produto_tubo_estanqueidade').val(codigo);
    $('#qtd_inspecionada_tubo_estanqueidade').val(qtd_apontada);

    // Exibir o modal
    $('#estanqueidadeTubosModal').modal('show');
}

function modalReteste(id, descricao, data, ficha,quantidade_reinspecao, tubos) {

    $('#reteste_descricao').text("Campo para realizar o reteste referente a inspeção do " + descricao + " do dia " + formatarDataBrComHora(data,0))

    $('#reteste_status_estanqueidade').val('')
    $("#nao_conformidade_tubos").empty();

    $("#tipo_inspecao_estanqueidade").val(tubos);

    $("#motivo_ficha_retrabalho_estanqueidade").css("display","none");
    $("#causasContainerEstanqueidade").css("display","none");
    $("#add_remove_cause").css("display","none");
    $('#quantidade_tubo_estanqueidade-0').val('')
    $('#inputGroupFile_tubo-0').val('')
    $('#causasTuboEstanqueidade').val('')
    $('#motivo_reteste_estanqueidade').val('')

    $('#ficha_reteste_estanqueidade').val(ficha)
    $('#qnt_reinspecao').val(quantidade_reinspecao)
    $("#id_reteste").val(id)

    $('#modalReteste').modal('show');
}

function modalCilindros(id,data,codigo,qtd_apontada) {

    
    $('#id_cilindro').val(id)

    $('#data_cilindro').val(formatarDataModal(data));

    $('#produtoEstanqueidade_cilindro').val(codigo);
    $('#qtd_inspecionada_cilindro').val(qtd_apontada);

    // Exibir o modal
    $('#cilindrosModal').modal('show');
}

function formatarDataModal(data) {
    let date = new Date(data);

    // Obtém o dia, mês e ano
    let dia = String(date.getDate()).padStart(2, '0');
    let mes = String(date.getMonth() + 1).padStart(2, '0'); // getMonth() retorna de 0 a 11
    let ano = date.getFullYear();

    // Formata a data como dd/mm/YYYY
    return `${dia}/${mes}/${ano}`;
}

function modalHistoricoEstanqueidade(idinspecao,inspecao) {

    $("#loading").show();
        
    $.ajax({
        url: '/modal-historico-estanqueidade',
        type: 'POST',  // Alterado para POST
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({ 'id': idinspecao ,'tipo_inspecao':inspecao}),  // Enviando um objeto JSON
        success: function(response) {
            $("#loading").hide();
            cardHistoricoTubosCilindros(response);
        },
        error: function(error) {
            $("#loading").hide();
            alert('Ocorreu um erro ');
            console.log(error);
        }
    });
}

function cardHistoricoTubosCilindros(response) {

    $("#modalTimeline .modal-header h5").text("Possui " + response.dados_historico.length + " inspeções")

    $('#listaHistorico').empty();

    $('#modalTimeline').modal('show');

    for (var i = 0; i < response.dados_historico.length; i++) {

        var item = response.dados_historico[i];

        // Criar elemento da lista e definir atributos de dados
        var listItem = $('<a>', {
            class: 'list-group-item list-group-item-action modal-edit',
            'aria-current': 'true',
            'data-index': i, // Armazenar o índice do item como um atributo de dados
            'data-item': JSON.stringify(item) // Armazenar todo o item como um atributo de dados
        });

        listItem.css('cursor','pointer');
        

        var content = `
            <div class="d-flex w-100 justify-content-between">
                <h6 class="mb-4">${item.descricao}</h6>
                <div class="d-flex flex-column align-items-end" style="min-width:160px">
                    <small>Inspetor: ${item.inspetor}</small>
                    <small>Qnt. inspecionada: ${item.quantidade_inspecionada}</small>
                    <small>Não conformidade: ${item.nao_conformidade}</small>
                    <small>Exec.: ${i}</small>
                </div>
            </div>
            <p class="mb-1" style="font-size: small;"><strong>Data Inspeção:</strong> ${formatarDataBrComHora(item.data_execucao,3)}</p>
        `;
        
        listItem.html(content);
        
        $('#listaHistorico').append(listItem);
    }

    $(".modal-edit").on('click', function () {
        // Recuperar os dados do item clicado
        const itemData = JSON.parse($(this).attr('data-item'));
        // Verificar se há causa e foto associadas
        if (itemData.causas) {
            // Esconder o modal atual
            $("#modalTimeline").modal('hide');
    
            // Configurar o modal de causas
            modalVisualizarCausaEstanqueidadeTubosCilindros(itemData); // Passa os dados do item para o modal
        } else {
            alert("Não possui nenhuma causa ou foto associada.");
        }
    });
}

function modalVisualizarCausaEstanqueidadeTubosCilindros(items) {
    // Configurar o título do modal

    $("#visualizacaoCausasModal .modal-body").empty();

    let content = "";

    if (items.nao_conformidade > 0) {
        $("#visualizacaoCausasModal .modal-header h5").text("Detalhes da Causa");
        items.causas.forEach(item => {
            content += `<div class="card mb-3">`;

            // Adicionar a linha da imagem somente se item.foto_da_causa existir
            if (item.foto_da_causa) {
                content += `<img src="${item.foto_da_causa}" alt="Foto da Causa" style="width:100%; height:400px;">`;
            }
            content += `<div class="card-body">
                                <div class="d-flex justify-content-between">
                                <div>
                                    <h5 class="card-title">${item.causa}</h5>
                                    <p><strong>Motivo:</strong> ${item.motivo}</p>
                                    <p><strong>Quantidade:</strong> ${item.quantidade}</p>
                                    <p class="card-text"><strong>Ficha: </strong><a href="${item.ficha}" target="_blank">${item.ficha}</a></p>
                                </div>
                                <p class="card-text" style="text-align:end"><small class="text-body-secondary">${formatarDataBrComHora(items.data_execucao,3)}</small></p>
                            </div>
                        </div>
                    </div>
                `;
            });
    } else {
        $("#visualizacaoCausasModal .modal-header h5").text("Link da Ficha");
        content = `<div class="card mb-3">
                        <div class="card-body">
                            <div class="d-flex justify-content-between">
                            <div>
                                <p class="card-text"><strong>Ficha: </strong><a href="${items.causas[0].ficha}" target="_blank">${items.causas[0].ficha}</a></p>
                            </div>
                            <p class="card-text" style="text-align:end"><small class="text-body-secondary">${formatarDataBrComHora(items.data_execucao,3)}</small></p>
                        </div>
                    </div>
                </div>
            `;
    }

    $("#visualizacaoCausasModal .modal-body").html(content);

    // Exibir o modal
    $("#visualizacaoCausasModal").modal('show');
}