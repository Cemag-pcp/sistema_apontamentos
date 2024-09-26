function modalInspecao(id, data, peca, cor,qtd_produzida) {

    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);

    // Configurar o conteúdo do modal com os parâmetros recebidos
    $('#inspecaoModalLabel').text(id);
    $('#data_finalizada').val(data);
    $('#peca_inspecionada').val(peca);
    $('#cor_inspecionada').val(cor);
    $('#qtd_produzida').val(qtd_produzida);
    $('#data_inspecao').val(today.toLocaleDateString());
    $('#n_conformidades').val('');
    $('#inspetor').val('');
    $("#causa_reinspecao").val('');
    $('#n_nao_conformidades').val('');
    $('#causasPintura-0').val('');
    $('#quantidade_causas_pintura-0').val('');
    
    // Exibir o modal
    $('#inspecaoModal').modal('show');

    $("#coluna_causa").html('')
}

function modalReinspecao(id,data,peca,cor,n_nao_conformidades,inspetor) {

    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);

    const dataHoraCompleta = new Date(data);

    let dataFormatada = dataHoraCompleta.toISOString().split('T')[0];

    // Configurar o conteúdo do modal com os parâmetros recebidos
    $('#reinspecaoModalLabel').text(id);
    $('#data_inspecao_anterior').val(dataFormatada);
    $('#peca_reinspecionada').val(peca);
    $('#cor_reinspecionada').val(cor);
    $('#data_nova_inspecao').val(today.toLocaleDateString());
    $('#n_conformidades_reinspecao').val('');
    $('#inspetor_reinspecao').val(inspetor);
    $("#causa_nova_reinspecao").val('');
    $("#n_nao_conformidades_reinspecao").val('');
    $('#qtd_produzida_reinspecao').val(n_nao_conformidades);
    $('#causasPinturaR-0').val('');
    $('#quantidade_causas_pinturaR-0').val('');

    // Exibir o modal
    $('#reinspecaoModal').modal('show');

    $("#coluna_causa_reinspecao").html('')

}

function modalTimeline(idinspecao,setor) {

    $("#loading").show();
        
    $.ajax({
        url: '/modal-historico',
        type: 'POST',  // Alterado para POST
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({ 'idinspecao': idinspecao ,'setor':setor}),  // Enviando um objeto JSON
        success: function(response) {

            setorCards(response)
        },
        error: function(error) {
            $("#loading").hide();
            alert('Ocorreu um erro ');
            console.log(error);
        }
    });
}

function setorCards(response) {

    var historico = response[0]
    var foto_causa = response[1]

    console.log(historico)
    console.log(foto_causa)

    var qt_apontada = historico[0][12]

    $("#modalTimeline .modal-header h5").text("Possui " + historico.length + " inspeções")

    $('#listaHistorico').empty();

    $('#modalTimeline').modal('show');

    $("#loading").hide();

    var qtd_disponivel_inspecao = historico[0][12]
    var setor = historico[0][4]

    var qtd_na_reinspecao = 0

    if(setor === 'Pintura') {

        for (var i = 0; i < historico.length; i++) {

            var item = historico[i];

            qtd_na_reinspecao += item[2]

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
                    <h6 class="mb-1">${item[9]}</h6>
                    <div class="d-flex flex-column align-items-end">
                        <small>Conformidade : ${item[2]}</small>
                        <small>Não Conformidade: ${qtd_disponivel_inspecao - item[2]}</small>
                        <small>Inspetor : ${item[3]}</small>
                        <small>Exec.:  ${item[5]}</small>
                    </div>
                </div>
                <p class="mb-1" style="font-size: small;"><strong>Data Inspeção:</strong> ${formatarDataBrComHora(item[1],3)}</p>
            `;
            
            listItem.html(content);
            
            $('#listaHistorico').append(listItem);

            qtd_disponivel_inspecao = qtd_disponivel_inspecao - item[2]
        }

        $("#modalTimeline .modal-footer #modal-footer-quantidade-produzida").text("Total do conj. inspecionados : " + qt_apontada)

        $("#modalTimeline .modal-footer #modal-footer-quantidade-reinspecao").text("Quantidade p/ reinspecionar : " + (qt_apontada - qtd_na_reinspecao))

        $(".modal-edit").on('click', function() {
            var dataItemString = $(this).data('item');
            var concatenatedPhotos = concatPhotosByCriteria(foto_causa, dataItemString[5]);
            if (Object.keys(concatenatedPhotos).length !== 0) {
                $("#modalTimeline").modal('hide')
                modalVisualizarCausas(concatenatedPhotos);
            } else {
                alert("Não possui nenhuma não conformidade")
            }
        }); 

    } else if(setor === 'Solda - Cilindro' || setor === 'Solda - Tubo') {

        for (var i = 0; i < historico.length; i++) {

            var item = historico[i];

            qtd_na_reinspecao += item[2]

            // Criar elemento da lista e definir atributos de dados
            var listItem = $('<a>', {
                class: 'list-group-item list-group-item-action modal-edit',
                'aria-current': 'true',
                'data-index': i, // Armazenar o índice do item como um atributo de dados
                'data-item': JSON.stringify(item) // Armazenar todo o item como um atributo de dados
            });

            listItem.css('cursor','pointer');
            
            if(i == 0) {
                var content = `
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-4">${item[9]}</h6>
                    <div class="d-flex flex-column align-items-end">
                        <small style="width:170px">Inspetor: ${item[3]}</small>
                        <small style="width:170px">Quantidade inspecionada: ${item[12]}</small>
                        <small>Exec.: ${item[5]}</small>
                    </div>
                </div>
                <p class="mb-1" style="font-size: small;"><strong>Data Inspeção:</strong> ${formatarDataBrComHora(item[1],3)}</p>
            `;
            } else {
                function verificarConformidade(valor) {
                    if (valor === true) {
                        return "Conforme";
                    } else if (valor === false) {
                        return "Não Conforme";
                    } else {
                        return "";
                    }
                }

                var content = `
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-4" style="color:red">RETESTE</h6>
                    <div class="d-flex flex-column align-items-end">
                        <small style="width:150px">Reteste 1: ${verificarConformidade(item[2])}</small>
                        <small style="width:150px">Reteste 2: ${verificarConformidade(item[7])}</small>
                        <small style="width:150px">Reteste 3: ${verificarConformidade(item[8])}</small>
                        <small>Exec.: ${item[5]}</small>
                    </div>
                </div>
                <p class="mb-1" style="font-size: small;"><strong>Motivo:</strong> ${item[11]}</p>
                <p class="mb-1" style="font-size: small;"><strong>Data Inspeção:</strong> ${formatarDataBrComHora(item[1],3)}</p>
            `
            }
            
            listItem.html(content);
            
            $('#listaHistorico').append(listItem);
        }

        $(".modal-edit").on('click', function() {
            var dataItemString = $(this).data('item');
            var concatenatedPhotos = concatPhotosByCriteria(foto_causa, dataItemString[5]);
            if (Object.keys(concatenatedPhotos).length !== 0) {
                $("#modalTimeline").modal('hide')
                modalVisualizarCausas(concatenatedPhotos);
            } else {
                alert("Não possui nenhuma não conformidade ou é reteste")
            }
        }); 
           
    } else if (setor === 'Solda') {
        for (var i = 0; i < historico.length; i++) {

            var item = historico[i];

            qtd_na_reinspecao += item[2]

            // Criar elemento da lista e definir atributos de dados
            var listItem = $('<a>', {
                class: 'list-group-item modal-edit no-more-hover',
                'aria-current': 'true',
                'data-index': i, // Armazenar o índice do item como um atributo de dados
            });

            listItem.css('text-decoration','none');
            listItem.css('color','#6e707e');
            
            var content = `
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">${item[9]}</h6>
                    <div class="d-flex flex-column align-items-end text-right">
                        <div class="dropdown">
                            <a href="#" class="dropdown-toggle" data-toggle="dropdown">Opções</a>
                            <div class="dropdown-menu drop">
                                <a class="dropdown-item option1" data-item='${JSON.stringify(item)}' style='cursor:pointer'>Visualizar causas da não conformidade</a>
                                <a class="dropdown-item option2" data-item='${JSON.stringify(item)}' style='cursor:pointer'>Editar as conformidades</a>
                            </div>
                        </div>
                        <small>Conformidade : ${item[2]}</small>
                        <small>Não Conformidade : ${item[10]}</small>
                        <small>Inspetor : ${item[3]}</small>
                        <small>Exec.:  ${item[5]}</small>
                    </div>
                </div>
                <p class="mb-1" style="font-size: small;"><strong>Data Inspeção:</strong> ${formatarDataBrComHora(item[1],3)}</p>
            `;
            
            listItem.html(content);
            
            $('#listaHistorico').append(listItem);

        }

        $("#modalTimeline .modal-footer #modal-footer-quantidade-produzida").text("Total do conj. inspecionados : " + qt_apontada)

        $("#modalTimeline .modal-footer #modal-footer-quantidade-reinspecao").text("Qtd. p/ reinspecionar : " + (qt_apontada - qtd_na_reinspecao))

        $(".option1").on('click', function() {
            var dataItemString = $(this).data('item');
            var concatenatedPhotos = concatPhotosByCriteria(foto_causa, dataItemString[5]);
            if (Object.keys(concatenatedPhotos).length !== 0) {
                $("#modalTimeline").modal('hide')
                modalVisualizarCausas(concatenatedPhotos);
            } else {
                alert("Não possui nenhuma não conformidade")
            }
        }); 
        $(".option2").on('click', function() {
            var dataItemString = $(this).data('item');
            if(dataItemString[2] != 0){
                $("#modalTimeline").modal('hide')
                modalEditarConformidade(dataItemString[0],dataItemString[2],dataItemString[5],dataItemString[9],dataItemString[10])
            } else {
                alert("Número de Conformidade é igual a 0")
            }
        }); 
            
    } else {
        var foto_ficha = response[2]
        console.log(foto_ficha)

        var medidasHTML = '';
        for (var i = 0; i < foto_ficha.length; i++) {
            // Medidas HTML para um único conjunto de medidas
            var medidas = '';

            if (foto_ficha[i][4] !== null) medidas += `<small>Medida A: ${foto_ficha[i][4]}</small><br>`;
            if (foto_ficha[i][5] !== null) medidas += `<small>Medida B: ${foto_ficha[i][5]}</small><br>`;
            if (foto_ficha[i][6] !== null) medidas += `<small>Medida C: ${foto_ficha[i][6]}</small><br>`;
            if (foto_ficha[i][7] !== null) medidas += `<small>Medida D: ${foto_ficha[i][7]}</small><br>`;

            // Adiciona um espaçamento entre os conjuntos de medidas
            if (medidas) {
                medidasHTML += `${medidas}<br>`;
            }
        }

        for (var i = 0; i < historico.length; i++) {

            var item = historico[i];

            qtd_na_reinspecao += item[2]

            // Criar elemento da lista e definir atributos de dados
            var listItem = $('<a>', {
                class: 'list-group-item modal-edit no-more-hover',
                'aria-current': 'true',
                'data-index': i, // Armazenar o índice do item como um atributo de dados
            });

            listItem.css('text-decoration','none');
            listItem.css('color','#6e707e');
            
            if(i == 0){
                var content = `
                <div class="row">
                    <div class="col-sm-7">
                        <h6 class="mb-1">${item[9]}</h6>
                        ${medidasHTML}
                    </div>
                    <div class="col-sm-5">
                        <div class="d-flex flex-column align-items-end text-right">
                            <div class="dropdown">
                                <a href="#" class="dropdown-toggle" data-toggle="dropdown">Opções</a>
                                <div class="dropdown-menu drop">
                                    <a class="dropdown-item option1" data-item='${JSON.stringify(item)}' style='cursor:pointer'>Visualizar causas da não conformidade</a>
                                </div>
                            </div>
                            <small>Conformidade : ${item[2]}</small>
                            <small>Não Conformidade : ${item[10]}</small>
                            <small>Inspetor : ${item[3]}</small>
                            <small>Exec.:  ${item[5]}</small>
                        </div>
                    </div>
                </div>
                <p class="mb-1" style="font-size: small;"><strong>Data Inspeção:</strong> ${formatarDataBrComHora(item[1],3)}</p>
            `;
            } else if (i == 1){
                var content = `
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">${item[9]}</h6>
                    <div class="d-flex flex-column align-items-end text-right">
                        <div class="dropdown">
                            <a href="#" class="dropdown-toggle" data-toggle="dropdown">Opções</a>
                            <div class="dropdown-menu drop">
                                <a class="dropdown-item option1" data-item='${JSON.stringify(item)}' style='cursor:pointer'>Visualizar causas da não conformidade</a>
                                <a class="dropdown-item option2" data-item='${JSON.stringify(item)}' style='cursor:pointer'>Visualizar fichas da Inspeção</a>
                            </div>
                        </div>
                        <small>Conformidade : ${item[2]}</small>
                        <small>Não Conformidade : ${item[10]}</small>
                        <small>Inspetor : ${item[3]}</small>
                        <small>Exec.:  ${item[5]}</small>
                        <small style="width:250px">Contém a Ficha de Inspeção 100% <i class="fa-solid fa-circle-check" style="color: #63E6BE;"></i></small>
                    </div>
                </div>
                <p class="mb-1" style="font-size: small;"><strong>Data Inspeção:</strong> ${formatarDataBrComHora(item[1],3)}</p>
            `;
            } else {
                var content = `
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">${item[9]}</h6>
                    <div class="d-flex flex-column align-items-end text-right">
                        <div class="dropdown">
                            <a href="#" class="dropdown-toggle" data-toggle="dropdown">Opções</a>
                            <div class="dropdown-menu drop">
                                <a class="dropdown-item option1" data-item='${JSON.stringify(item)}' style='cursor:pointer'>Visualizar causas da não conformidade</a>
                            </div>
                        </div>
                        <small>Conformidade : ${item[2]}</small>
                        <small>Não Conformidade : ${item[10]}</small>
                        <small>Inspetor : ${item[3]}</small>
                        <small>Exec.:  ${item[5]}</small>
                    </div>
                </div>
                <p class="mb-1" style="font-size: small;"><strong>Data Inspeção:</strong> ${formatarDataBrComHora(item[1],3)}</p>
            `;
            }

            listItem.html(content);
            
            $('#listaHistorico').append(listItem);

        }

        $(".option1").on('click', function() {
            var dataItemString = $(this).data('item');
            var concatenatedPhotos = concatPhotosByCriteria(foto_causa, dataItemString[5]);
            if (Object.keys(concatenatedPhotos).length !== 0) {
                $("#modalTimeline").modal('hide')
                modalVisualizarCausas(concatenatedPhotos);
            } else {
                alert("Não possui nenhuma não conformidade")
            }
        }); 
        $(".option2").on('click', function() {
            var dataItemString = $(this).data('item');
            var concatenatedPhotos = concatTokensByCriteria(foto_ficha, dataItemString[5]);
            if (Object.keys(concatenatedPhotos).length !== 0) {
                $("#modalTimeline").modal('hide')
                modalVisualizarCausas(concatenatedPhotos);
            } else {
                alert("Não possui nenhuma não conformidade")
            }
        }); 
    }
}

function modalVisualizarCausas(concatenatedPhotos) {
    // Limpar qualquer conteúdo anterior do modal
    $('#visualizacaoCausasModal .modal-body').empty();

    console.log(concatenatedPhotos)

    $("#visualizacaoCausasModalLabel").text("Contém " + Object.keys(concatenatedPhotos).length + " não conformidades");

    // Iterar sobre as chaves e valores do objeto concatenatedPhotos
    for (var key in concatenatedPhotos) {
        if (concatenatedPhotos.hasOwnProperty(key)) {
            // Separar as imagens com base no delimitador ';'
            var photos = concatenatedPhotos[key].split(';').filter(function(photo) {
                return photo.trim() !== ''; // Retorna verdadeiro se a foto não estiver vazia
            });
            // Iterar sobre as imagens e criar elementos de imagem correspondentes
            for (var i = 0; i < photos.length; i++) {
                var photoUrl = photos[i];

                // Criar o elemento de cartão (card)
                var card = $('<div>', {
                    class: 'card mb-3'
                });

                if (photoUrl != "null"){
                    // Criar o elemento de imagem do cartão
                    var image = $('<img>', {
                        class: 'card-img-top top-card-causas',
                        src: photoUrl,
                        alt: 'Imagem'
                    });

                    card.append(image);
                }
                
                // Criar o elemento do corpo do cartão
                var cardBody = $('<div>', {
                    class: 'card-body'
                });

                // Criar o parágrafo com o texto do cartão
                var cardText = $('<h5>', {
                    class: 'card-title',
                    text: key
                });

                // Adicionar a imagem e o texto ao corpo do cartão
                cardBody.append(cardText);

                // Adicionar o corpo do cartão ao cartão
                card.append(cardBody);

                // Adicionar o cartão ao modal
                $('#visualizacaoCausasModal .modal-body').append(card);
            }
        }
    }

    // Exibir o modal
    $('#visualizacaoCausasModal').modal('show');
}

function modalEditarConformidade(id,n_conformidade,num_execução,descricao,nao_conformidades) {

    $('#qtd_conformidade_edicao').val(n_conformidade)
    
    $('#qtd_conformidade_atualizada_edicao').val('')

    $('#id_edicao').val(id)

    $('#num_execucao_edicao').val(num_execução)

    $('#nao_conformidades_edicao').val(nao_conformidades)

    $('#descricao_peca_edicao').val(descricao)
    
    $("#num_causas_edicao").val("")
    $("#qtd_conformidade_atualizada_edicao").val("")
    $("#causasSoldaE-0").val("")
    $("#quantidade_causas_soldaE-0").val("")

    $('#editarConformidadesModal').modal('show');
}

function changeTab(tabName) {
    // Ocultar todas as tabelas
    var tables = document.querySelectorAll('.card-body');
    tables.forEach(function(table) {
        table.style.display = 'none';
    });

    // Mostrar a tabela correspondente à aba clicada
    document.getElementById(tabName + 'Table').style.display = 'block';

    // Remover a classe "active" de todas as abas
    var tabs = document.querySelectorAll('.nav-link');
    tabs.forEach(function(tab) {
        tab.classList.remove('active');
    });

    // Adicionar a classe "active" à aba clicada
    var clickedTab = document.querySelector('[onclick="changeTab(\'' + tabName + '\')"]');
    clickedTab.classList.add('active');
}

function formatarDataBrComHora(dataString,sum) {
    // Cria um objeto Date a partir da string
    var data = new Date(dataString);

    data.setDate(data.getDate());

    // Obtém os componentes da data
    var dia = data.getDate().toString().padStart(2, '0');
    var mes = (data.getMonth() + 1).toString().padStart(2, '0');
    var ano = data.getFullYear();
    var hora = (data.getHours() + sum).toString().padStart(2, '0');
    var minuto = data.getMinutes().toString().padStart(2, '0');
    var segundo = data.getSeconds().toString().padStart(2, '0');

    var formatoDesejado = `${dia}/${mes}/${ano} ${hora}:${minuto}:${segundo}`;

    return formatoDesejado;
}

function concatPhotosByCriteria(foto_causa, execucaoDesejada) {
    var concatenatedPhotos = {};

    // Itera sobre o array foto_causa
    for (var i = 0; i < foto_causa.length; i++) {
        var key = foto_causa[i][2]
        var execucao = foto_causa[i][3]; // Número da execução

        // Verifica se a execução corresponde à execução desejada
        if (execucao === execucaoDesejada) {
            // Se a chave ainda não existir no objeto concatenatedPhotos, inicializa como uma string vazia
            if (!concatenatedPhotos[key]) {
                concatenatedPhotos[key] = '';
            }

            // Concatena o valor da primeira posição do subarray à string correspondente à chave
            concatenatedPhotos[key] += foto_causa[i][1];
        }
    }

    return concatenatedPhotos;
}

function concatTokensByCriteria(ficha, execucaoDesejada) {
    var concatenatedPhotos = {};

    // Itera sobre o array foto_causa
    for (var i = 0; i < ficha.length; i++) {
        if(ficha[i][2] == true){
            var key = "Ficha de Inspeção 100%";  // A chave é o valor da terceira posição do subarray
        } else {
            var key = "Ficha de Inspeção de Produção";  // A chave é o valor da terceira posição do subarray
        }
        
        var execucao = ficha[i][3]; // Número da execução

        // Verifica se a execução corresponde à execução desejada
        if (execucao === execucaoDesejada) {
            // Se a chave ainda não existir no objeto concatenatedPhotos, inicializa como uma string vazia
            if (!concatenatedPhotos[key]) {
                concatenatedPhotos[key] = '';
            }

            // Concatena o valor da primeira posição do subarray à string correspondente à chave
            concatenatedPhotos[key] += ficha[i][1];
        }
    }

    return concatenatedPhotos;
}

$('#n_conformidades').on('input',function() {

    let n_conformidades_value = parseInt($('#n_conformidades').val(), 10);
    let qtd_produzida_value = parseInt($('#qtd_produzida').val(), 10);
    let containerCausas = $("#selectContainerInspecao");
    
    $('#n_nao_conformidades').val(qtd_produzida_value - n_conformidades_value);

    if(n_conformidades_value >= qtd_produzida_value || n_conformidades_value < 0 || n_conformidades_value === '') {
        $("#causa_reinspecao").prop('disabled', true);
        $("#causa_reinspecao").val('');
        containerCausas.css('display','none')
        $('#n_nao_conformidades').val(0);
        $('#causasPintura-0').val('');
        $('#quantidade_causas_pintura-0').val('');
    } else {
        $("#causa_reinspecao").prop('disabled', false);
        containerCausas.css('display','flex')
    }
})

$('#envio_inspecao').on('click', function () {

    let inputConformidadesSolda = parseInt($('#n_conformidades').val());
    let inputNaoConformidadesSolda = parseInt($('#n_nao_conformidades').val());
    let inputConjunto = $('#peca_inspecionada').val();
    let inspetor = $("#inspetor").val();
    let qtd_produzida_value = parseInt($("#qtd_produzida").val());
    let tipos_causas_estamparia = $("#tipos_causas_pintura").val();
    let qtd_causas = 0

    
    if (inputConformidadesSolda === "" || inspetor === null || inputConformidadesSolda > qtd_produzida_value || inputConformidadesSolda < 0) {
        alert('Verifique se o campo de conformidades ou inspetor estão com valores corretos');
        return; // Interrompe a execução
    }

    for (let i = 0; i < tipos_causas_estamparia; i++) {
        qtd_causas += parseInt($("#quantidade_causas_pintura-" + i).val())
    }

    if((qtd_causas != inputNaoConformidadesSolda) && inputNaoConformidadesSolda != 0){
        alert('Verifique se a soma dos campos de "Quantidade" está igual ao valor de "Total de NÃO conformidades"');
        $("#loading").hide();
        return; // Interrompe a execução
    }

    $("#confirmarConformidades").val(inputConformidadesSolda);
    $("#confirmarNaoConformidades").val(inputNaoConformidadesSolda);
    
    $('#modalConfirmacaoPintura #p_confirmar_inspecao_pintura').text("Deseja confirmar as informações preenchidas referente a inspeção do conjunto " + inputConjunto);

    $("#btnEnviarPinturaReinspecao").css("display","none")
    $("#btnEnviarPintura").css("display","block")

    $('#inspecaoModal').modal('hide');

    $('#modalConfirmacaoPintura').modal('show');
})

$('#btnEnviarPintura').on('click', function () {

    $("#loading").show();

    $('#btnEnviarPintura').prop('disabled',true);

    var formData = new FormData();

    let id_inspecao = $('#inspecaoModalLabel').text();
    let data_inspecao = $('#data_inspecao').val();
    let n_conformidades = parseInt($('#n_conformidades').val());
    let n_nao_conformidades = parseInt($('#n_nao_conformidades').val());
    let list_causas = [];
    let list_quantidade = [];
    let inspetor = $("#inspetor").val();
    let qtd_produzida_value = parseInt($('#qtd_produzida').val());
    let tipos_causas_estamparia = $("#tipos_causas_pintura").val()
    let reinspecao = 'False';

    for (let i = 0; i < tipos_causas_estamparia; i++) {
        let causas = $("#causasPintura-" + i).val();
        let quantidade = $("#quantidade_causas_pintura-" + i).val();
        let inputId = '#inputGroupFile_pintura-' + i;
        let files = $(inputId)[0].files;
        for (let file of files) {
            formData.append('foto_inspecao_' + i + '[]', file);
        }
        list_causas.push(causas)
        list_quantidade.push(quantidade)
    }

    formData.append('id_inspecao', id_inspecao);
    formData.append('data_inspecao', data_inspecao);
    formData.append('n_conformidades', n_conformidades);
    formData.append('n_nao_conformidades', n_nao_conformidades);
    formData.append('list_causas', JSON.stringify(list_causas));
    formData.append('list_quantidade', JSON.stringify(list_quantidade));
    formData.append('inspetor', inspetor);
    formData.append('tipos_causas_pintura', tipos_causas_estamparia);
    formData.append('qtd_produzida', qtd_produzida_value);
    formData.append('reinspecao', reinspecao);

    $.ajax({
        url: '/inspecao',
        type: 'POST',
        data: formData,
        processData: false, // Não processe os dados
        contentType: false, // Não defina o tipo de conteúdo
        success: function (response) {
            location.reload();
        },
        error: function (error) {
            console.log(error);
            $('#btnEnviarPintura').prop('disabled', false);
            $("#loading").hide();
        }
    });
});

$('#envio_reinspecao').on('click', function () {
    let inputConformidadesSolda = parseInt($('#n_conformidades_reinspecao').val());
    let inputNaoConformidadesSolda = parseInt($('#n_nao_conformidades_reinspecao').val());
    let inputConjunto = $('#peca_reinspecionada').val();
    let inspetor = $("#inspetor_reinspecao").val();
    let qtd_produzida_value = parseInt($('#qtd_produzida_reinspecao').val());
    let tipos_causas_estamparia = $("#tipos_causas_pintura_reinspecao").val();
    let qtd_causas = 0

    if (inputConformidadesSolda === "" || inspetor === null || inputConformidadesSolda > qtd_produzida_value || inputConformidadesSolda < 0) {
        alert('Verifique se o campo de conformidades ou inspetor estão com valores corretos');
        return; // Interrompe a execução
    }

    for (let i = 0; i < tipos_causas_estamparia; i++) {
        qtd_causas += parseInt($("#quantidade_causas_pinturaR-" + i).val())
    }

    if((qtd_causas != inputNaoConformidadesSolda) && inputNaoConformidadesSolda != 0){
        alert('Verifique se a soma dos campos de "Quantidade" está igual ao valor de "Total de NÃO conformidades"');
        $("#loading").hide();
        return; // Interrompe a execução
    }

    $("#confirmarConformidades").val(inputConformidadesSolda);
    $("#confirmarNaoConformidades").val(inputNaoConformidadesSolda);
    
    $('#modalConfirmacaoPintura #p_confirmar_inspecao_pintura').text("Deseja confirmar as informações preenchidas referente a inspeção do conjunto " + inputConjunto);

    $("#btnEnviarPinturaReinspecao").css("display","block")
    $("#btnEnviarPintura").css("display","none")

    $('#reinspecaoModal').modal('hide');
    
    $('#modalConfirmacaoPintura').modal('show');
})

$('#btnEnviarPinturaReinspecao').on('click',function() {

    $('#btnEnviarPinturaReinspecao').prop('disabled',true);

    $("#loading").show();

    var formData = new FormData();

    let id_inspecao = $('#reinspecaoModalLabel').text();
    let data_inspecao = $('#data_nova_inspecao').val();
    let n_conformidades = parseInt($('#n_conformidades_reinspecao').val());
    let n_nao_conformidades = parseInt($('#n_nao_conformidades_reinspecao').val());
    let list_causas = [];
    let list_quantidade = [];
    let inspetor = $("#inspetor_reinspecao").val();
    let qtd_produzida_value = parseInt($('#qtd_produzida_reinspecao').val());
    let tipos_causas_estamparia = $("#tipos_causas_pintura_reinspecao").val()
    let reinspecao = true;

    for (let i = 0; i < tipos_causas_estamparia; i++) {
        let causas = $("#causasPinturaR-" + i).val();
        let quantidade = $("#quantidade_causas_pinturaR-" + i).val();
        let inputId = '#inputGroupFile_pinturaR-' + i;
        let files = $(inputId)[0].files;
        for (let file of files) {
            formData.append('foto_inspecao_' + i + '[]', file);
        }
        list_causas.push(causas)
        list_quantidade.push(quantidade)
    }

    if (n_conformidades === "" || inspetor === null || n_conformidades > qtd_produzida_value || n_conformidades < 0) {
        alert('Verifique se o campo de conformidades ou inspetor estão com valores corretos');
        $('#btnEnviarPinturaReinspecao').prop('disabled',false);
        $("#loading").hide();
        return; // Interrompe a execução
    }

    formData.append('id_inspecao', id_inspecao);
    formData.append('data_inspecao', data_inspecao);
    formData.append('n_conformidades', n_conformidades);
    formData.append('n_nao_conformidades', n_nao_conformidades);
    formData.append('list_causas', JSON.stringify(list_causas));
    formData.append('list_quantidade', JSON.stringify(list_quantidade));
    formData.append('inspetor', inspetor);
    formData.append('tipos_causas_pintura', tipos_causas_estamparia);
    formData.append('qtd_produzida', qtd_produzida_value);
    formData.append('reinspecao', reinspecao);

    $.ajax({
        url: '/inspecao',
        type: 'POST',
        data: formData,
        processData: false, // Não processe os dados
        contentType: false, // Não defina o tipo de conteúdo
        success: function (response) {
            location.reload();
        },
        error: function (error) {
            console.log(error);
            $('#btnEnviarPinturaReinspecao').prop('disabled', false);
            $("#loading").hide();
        }
    });
})

$('#n_conformidades_reinspecao').on('input',function() {

    let n_conformidades_value = parseInt($('#n_conformidades_reinspecao').val(), 10);
    let qtd_produzida_value = parseInt($('#qtd_produzida_reinspecao').val(), 10);
    let containerCausas = $("#selectContainerReinspecao");

    $('#n_nao_conformidades_reinspecao').val(qtd_produzida_value - n_conformidades_value);

    if(n_conformidades_value >= qtd_produzida_value || n_conformidades_value < 0 || n_conformidades_value === '') {
        $("#causa_nova_reinspecao").prop('disabled', true);
        $("#causa_nova_reinspecao").val('');
        containerCausas.css('display','none')
        $('#n_nao_conformidades_reinspecao').val(0);
        $('#causasPinturaR-0').val('');
        $('#quantidade_causas_pinturaR-0').val('');
    } else {
        $("#causa_nova_reinspecao").prop('disabled', false);
        containerCausas.css('display','flex')
    }
})

$('#atualizarConformidades').on('click', function(){

    $("#loading").show();

    var formData = new FormData();

    let id_edicao = $("#id_edicao").val();
    let list_causas = [];
    let list_quantidade = [];
    let qtd_conformidade_antiga = parseInt($("#qtd_conformidade_edicao").val());
    let conformidade_atualizada = $("#qtd_conformidade_atualizada_edicao");
    let num_execucao = $("#num_execucao_edicao").val();
    let nao_conformidades = $("#nao_conformidades_edicao").val();
    let num_causas_edicao = $("#num_causas_edicao").val();
    let tipos_causas_solda = $('#tipos_causas_solda_edicao').val();
    let qtd_causas = 0

    if(parseInt(conformidade_atualizada.val()) >= qtd_conformidade_antiga || parseInt(conformidade_atualizada.val()) < 0 || parseInt(conformidade_atualizada.val()) === ''){
        alert("Valor inválido")
        conformidade_atualizada.val('')
        $("#loading").hide();
        return
    }

    conformidade_atualizada = $("#qtd_conformidade_atualizada_edicao").val();

    for (var i = 0; i < tipos_causas_solda; i++) {
        qtd_causas += parseInt($("#quantidade_causas_soldaE-" + i).val())
        let causas = $("#causasSoldaE-" + i).val();
        let quantidade = $("#quantidade_causas_soldaE-" + i).val();
        let inputId = '#inputGroupFile_soldaE-' + i;
        let files = $(inputId)[0].files;
        for (let file of files) {
            formData.append('foto_inspecao_' + i + '[]', file);
        }
        list_causas.push(causas)
        list_quantidade.push(quantidade)
    }

    if((qtd_causas != num_causas_edicao) && num_causas_edicao != 0){
        alert('Verifique se a soma dos campos de "Quantidade" está igual ao valor de "Total de NÃO conformidades"');
        $("#loading").hide();
        return; // Interrompe a execução
    }

    formData.append('id_edicao', id_edicao);
    formData.append('qtd_conformidade_antiga', qtd_conformidade_antiga);
    formData.append('conformidade_atualizada', conformidade_atualizada);
    formData.append('nao_conformidades', nao_conformidades);
    formData.append('nao_conformidades', nao_conformidades);
    formData.append('num_execucao', num_execucao);
    formData.append('list_causas', JSON.stringify(list_causas));
    formData.append('list_quantidade', JSON.stringify(list_quantidade));
    formData.append('tipos_causas_solda', tipos_causas_solda);

    $.ajax({
        url: '/atualizar-conformidade',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false, 
        success: function(response) {
            location.reload()
        },
        error: function(error) {
            $("#loading").hide();
            alert('Ocorreu um erro ');
            console.log(error);
        }
    });
    
})

// Envio das informações para o Backend da Reinspecao


// tooltip da tabela de A inspecionar 
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})

