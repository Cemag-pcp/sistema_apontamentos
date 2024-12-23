function modalTanque() {

    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);

    $('#data_estanqueidade_tanque').val(today.toLocaleDateString());

    // Exibir o modal
    $('#estanqueidadeTanqueModal').modal('show');
}

function modalTanqueReinspecao(id_inspecao,id,codigo, descricao, inspetor) {
    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);

    $('#data_estanqueidade_tanque_reinspecao').val(today.toLocaleDateString());
    $('#id_estanqueidade_tanque_reinspecao').val(id_inspecao);
    $('#produto-estanqueidade-tanque-reinspecao').val(codigo + " - " + descricao);
    $('#inspetores_estanqueidade_tanque_reinspecao').val(inspetor);

    // Construindo os parâmetros para a URL
    const idInspecao = encodeURIComponent(id); // Ajustar conforme a lógica
    const url = `/detalhes-estanqueindade-tanque?id=${idInspecao}`;

    $.ajax({
        url: url,
        type: 'GET',  // Utilizando GET
        dataType: 'json',
        success: function(response) {
            // Exibir o modal
            console.log(response)
            // Ocultar todas as divs inicialmente e desabilitar todos os requireds
            disabledAllTypesReinspecao()

            // Iterar sobre os dados recebidos
            response.data.forEach(item => {
                const tipoTeste = item.tipo_teste;
                const nao_conformidade = item.nao_conformidade ? "Sim" : "Não";

                // Usar switch para determinar a div a ser exibida
                if (tipoTeste === "Corpo do tanque parte inferior") {
                    $('#col-parteInferior-reinspecao').show();
                    $("#col-parteInferior-reinspecao input, #col-parteInferior-reinspecao select").val("");
                    if(!item.nao_conformidade) {

                        $("#flag-parte-inferior-tanque-reinspecao").val(false)
                        $("#pressao-inicial-parte-inferior-reinspecao").val(item.pressao_inicial)
                        $("#pressao-final-parte-inferior-reinspecao").val(item.pressao_final)
                        $("#duracao-parte-inferior-reinspecao").val(item.hora_execucao)
                        $("#vazamento-parte-inferior-reinspecao").val(nao_conformidade)

                        $("#col-parteInferior-reinspecao input, #col-parteInferior-reinspecao select").prop("disabled", true);
                        $("#buttonParteInferior-reinspecao").css("text-decoration", "none");
                        $("#buttonParteInferior-reinspecao").css("background-color", "#d5ffd5");
                        $("#buttonParteInferior-reinspecao h6")
                            .removeClass("text-primary")
                            .addClass("text-success");

                        // Alterar ícones (remover fa-plus e adicionar fa-check)
                        $("#buttonParteInferior-reinspecao i")
                            .removeClass("fa-plus")
                            .addClass("fa-check")
                            .addClass("text-success")
                    } else {
                        $("#col-parteInferior-reinspecao input, #col-parteInferior-reinspecao select").prop("required", true);
                        $("#duracao-parte-inferior-reinspecao").val("00:00:00")
                        $("#flag-parte-inferior-tanque-reinspecao").val(true)
                    }
                } else if (tipoTeste === "Corpo do tanque + longarinas") {
                    $('#col-corpoLongarina-reinspecao').show();
                    $("#col-corpoLongarina-reinspecao input, #col-corpoLongarina-reinspecao select").val("");
                    if(!item.nao_conformidade) {

                        $("#flag-longarina-tanque-reinspecao").val(false)
                        $("#pressao-inicial-longarina-reinspecao").val(item.pressao_inicial)
                        $("#pressao-final-longarina-reinspecao").val(item.pressao_final)
                        $("#duracao-longarina-reinspecao").val(item.hora_execucao)
                        $("#vazamento-longarina-reinspecao").val(nao_conformidade)

                        $("#col-corpoLongarina-reinspecao input, #col-corpoLongarina-reinspecao select").prop("disabled", true);
                        $("#buttonCorpoLongarina-reinspecao").css("text-decoration", "none");
                        $("#buttonCorpoLongarina-reinspecao").css("background-color", "#d5ffd5");
                        $("#buttonCorpoLongarina-reinspecao h6")
                            .removeClass("text-primary")
                            .addClass("text-success");

                        // Alterar ícones (remover fa-plus e adicionar fa-check)
                        $("#buttonCorpoLongarina-reinspecao i")
                            .removeClass("fa-plus")
                            .addClass("fa-check")
                            .addClass("text-success")
                    } else {
                        $("#col-corpoLongarina-reinspecao input, #col-corpoLongarina-reinspecao select").prop("required", true);
                        $("#duracao-longarina-reinspecao").val("00:00:00")
                        $("#flag-longarina-tanque-reinspecao").val(true)
                    }
                } else if (tipoTeste === "Corpo do tanque") {
                    $('#col-corpoTanque-reinspecao').show();
                    $("#col-corpoTanque-reinspecao input, #col-corpoTanque-reinspecao select").val("");
                    if(!item.nao_conformidade) {

                        $("#flag-corpo-tanque-reinspecao").val(false)
                        $("#pressao-inicial-corpo-tanque-reinspecao").val(item.pressao_inicial)
                        $("#pressao-final-corpo-tanque-reinspecao").val(item.pressao_final)
                        $("#duracao-corpo-tanque-reinspecao").val(item.hora_execucao)
                        $("#vazamento-corpo-tanque-reinspecao").val(nao_conformidade)

                        $("#col-corpoTanque-reinspecao input, #col-corpoTanque-reinspecao select").prop("disabled", true);
                        $("#buttonCorpoTanque-reinspecao").css("text-decoration", "none");
                        $("#buttonCorpoTanque-reinspecao").css("background-color", "#d5ffd5");
                        $("#buttonCorpoTanque-reinspecao h6")
                            .removeClass("text-primary")
                            .addClass("text-success");

                        // Alterar ícones (remover fa-plus e adicionar fa-check)
                        $("#buttonCorpoTanque-reinspecao i")
                            .removeClass("fa-plus")
                            .addClass("fa-check")
                            .addClass("text-success")
                        
                    } else {
                        $("#col-corpoTanque-reinspecao input, #col-corpoTanque-reinspecao select").prop("required", true);
                        $("#duracao-corpo-tanque-reinspecao").val("00:00:00")
                        $("#flag-corpo-tanque-reinspecao").val(true)
                    }
                } else if (tipoTeste === "Corpo do tanque + chassi") {
                    $('#col-corpoChassi-reinspecao').show();
                    $("#col-corpoChassi-reinspecao input, #col-corpoChassi-reinspecao select").val("");
                    if(!item.nao_conformidade) {

                        $("#flag-corpo-chassi-reinspecao").val(false)
                        $("#pressao-inicial-corpo-chassi-reinspecao").val(item.pressao_inicial)
                        $("#pressao-final-corpo-chassi-reinspecao").val(item.pressao_final)
                        $("#duracao-corpo-chassi-reinspecao").val(item.hora_execucao)
                        $("#vazamento-corpo-chassi-reinspecao").val(nao_conformidade)

                        $("#col-corpoChassi-reinspecao input, #col-corpoChassi-reinspecao select").prop("disabled", true);
                        $("#buttonCorpoChassi-reinspecao").css("text-decoration", "none");
                        $("#buttonCorpoChassi-reinspecao").css("background-color", "#d5ffd5");
                        $("#buttonCorpoChassi-reinspecao h6")
                            .removeClass("text-primary")
                            .addClass("text-success");

                        // Alterar ícones (remover fa-plus e adicionar fa-check)
                        $("#buttonCorpoChassi-reinspecao i")
                            .removeClass("fa-plus")
                            .addClass("fa-check")
                            .addClass("text-success")
                    } else {
                        $("#col-corpoChassi-reinspecao input, #col-corpoChassi-reinspecao select").prop("required", true);
                        $("#duracao-corpo-chassi-reinspecao").val("00:00:00")
                        $("#flag-corpo-chassi-reinspecao").val(true)
                    }
                }
            });

            // Exibir o modal
            $('#estanqueidadeTanqueReinspecaoModal').modal('show');
        },
        error: function(error) {
            alert('Ocorreu um erro');
            console.log(error);
        }
    });
}

function modalHistoricoEstanqueidadeTanque(idinspecao,inspecao) {

    $("#loading").show();
        
    $.ajax({
        url: '/modal-historico-estanqueidade-tanque',
        type: 'POST',  // Alterado para POST
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({ 'id': idinspecao ,'tipo_inspecao':inspecao}),  // Enviando um objeto JSON
        success: function(response) {
            $("#loading").hide();
            cardHistoricoTanque(response);
        },
        error: function(error) {
            $("#loading").hide();
            alert('Ocorreu um erro ');
            console.log(error);
        }
    });
}

function cardHistoricoTanque(response) {
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
        
        
        var naoConformidade = item.detalhes_pressao.some(detalhe => detalhe.nao_conformidade);
        var naoConformidadeTexto = naoConformidade ? "Sim" : "Não";

        var content = `
            <div class="d-flex w-100 justify-content-between">
                <h6 class="mb-4">${item.codigo + " - " + item.descricao}</h6>
                <div class="d-flex flex-column align-items-end" style="min-width:160px">
                    <small>Inspetor: ${item.inspetor}</small>
                    <small>Vazamento: ${naoConformidadeTexto}</small>
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
        console.log(itemData)
        // Verificar se há causa e foto associadas
        if (itemData.detalhes_pressao) {
            // Esconder o modal atual
            $("#modalTimeline").modal('hide');
    
            // Configurar o modal de causas
            modalVisualizarCausaEstanqueidadeTanque(itemData); // Passa os dados do item para o modal
        } else {
            Swal.fire({
                icon: "error",
                title: "Erro....",
                text: "Os dados da inspeção estão incompletos.",
            });
        }
    });
}

function modalVisualizarCausaEstanqueidadeTanque(items) {
    // Configurar o título do modal

    $("#visualizacaoCausasModal .modal-body").empty();

    let content = "";

    $("#visualizacaoCausasModal .modal-header h5").text("Detalhes da inspeção");

    items.detalhes_pressao.forEach(item => {
        content += `<div class="card mb-3">`;

        content += `<div class="card-body">
                        <div>
                            <div class="d-flex justify-content-between">
                                <h5 class="card-title">${item.tipo_teste}</h5>
                                <p>
                                    <strong>Vazamento:</strong>
                                    ${item.nao_conformidade ? 'Sim' : 'Não'}
                                </p>
                            </div>
                            <p><strong>Pressao Inicial:</strong> ${item.pressao_inicial}</p>
                            <p><strong>Quantidade:</strong> ${item.pressao_final}</p>
                            <p class="card-text"><strong>Duração do teste: </strong>${item.hora_execucao}</p>
                        </div>
                    </div>
            `;
    });

    $("#visualizacaoCausasModal .modal-body").html(content);

    // Exibir o modal
    $("#visualizacaoCausasModal").modal('show');
}