
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
    
    // Exibir o modal
    $('#inspecaoModal').modal('show');

}

$('#n_conformidades').on('input',function() {

    let n_conformidades_value = parseInt($('#n_conformidades').val(), 10);
    let qtd_produzida_value = parseInt($('#qtd_produzida').val(), 10);

    $('#n_nao_conformidades').val(qtd_produzida_value - n_conformidades_value);

    if(n_conformidades_value >= qtd_produzida_value || n_conformidades_value < 0 || n_conformidades_value === '') {
        $("#causa_reinspecao").prop('disabled', true);
        $("#causa_reinspecao").val('');
        $('#n_nao_conformidades').val('');
    } else {
        $("#causa_reinspecao").prop('disabled', false);
    }
})

// Envio das informações para o Backend da Inspecao
$('#envio_inspecao').on('click',function(){

    $("#loading").show();

    $('#envio_inspecao').prop('disabled',true);

    let n_conformidades_value = $('#n_conformidades').val();
    let inspetor = $('#inspetor').val();
    let qtd_produzida_value = $('#qtd_produzida').val();
    let causa_reinspecao =  $("#causa_reinspecao").val();

    if(n_conformidades_value === "" || inspetor === null || n_conformidades_value < 0 || n_conformidades_value > qtd_produzida_value){
        alert("Preencha todos os campos corretamente")
        $('#envio_inspecao').prop('disabled',false);
        $("#loading").hide();
        return
    } else if(n_conformidades_value >= 0 && n_conformidades_value < qtd_produzida_value && causa_reinspecao === null){
        alert("Preencha todos os campos corretamente")
        $('#envio_inspecao').prop('disabled',false);
        $("#loading").hide();
        return
    }

    let id_inspecao =  $('#inspecaoModalLabel').text();
    let data_inspecao = $('#data_inspecao').val();
    let n_nao_conformidades = $('#n_nao_conformidades').val();
    let reinspecao = false;

    $.ajax({
        url: '/inspecao',
        type: 'POST',  // Alterado para POST
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({ 'id_inspecao': id_inspecao ,'data_inspecao':data_inspecao,'n_conformidades_value':n_conformidades_value,
        'n_nao_conformidades':n_nao_conformidades,'causa_reinspecao':causa_reinspecao,'inspetor':inspetor,'qtd_produzida':qtd_produzida_value,'reinspecao':reinspecao}),  // Enviando um objeto JSON
        success: function(response) {
            window.location.reload();
            console.log(response)
            $("#loading").hide();
        },
        error: function(error) {
            console.log(error);
            $('#envio_inspecao').prop('disabled',false);
            $("#loading").hide();
        }
    });
})

// Exibindo modal de Reinspecao

function modalReinspecao(id, data, peca, cor,n_nao_conformidades,inspetor) {

    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);

    // Configurar o conteúdo do modal com os parâmetros recebidos
    $('#reinspecaoModalLabel').text(id);
    $('#data_inspecao_anterior').val(data);
    $('#peca_reinspecionada').val(peca);
    $('#cor_reinspecionada').val(cor);
    $('#data_nova_inspecao').val(today.toLocaleDateString());
    $('#n_conformidades_reinspecao').val('');
    $('#inspetor_reinspecao').val(inspetor);
    $("#causa_nova_reinspecao").val('');
    $("#n_nao_conformidades_reinspecao").val('');
    $('#qtd_produzida_reinspecao').val(n_nao_conformidades);

    // Exibir o modal
    $('#reinspecaoModal').modal('show');

}

// Verificação do Input de Reinspecao

$('#n_conformidades_reinspecao').on('input',function() {

    let n_conformidades_value = parseInt($('#n_conformidades_reinspecao').val(), 10);
    let qtd_produzida_value = parseInt($('#qtd_produzida_reinspecao').val(), 10);

    $('#n_nao_conformidades_reinspecao').val(qtd_produzida_value - n_conformidades_value);

    if(n_conformidades_value >= qtd_produzida_value || n_conformidades_value < 0 || n_conformidades_value === '') {
        $("#causa_nova_reinspecao").prop('disabled', true);
        $("#causa_nova_reinspecao").val('');
        $('#n_nao_conformidades_reinspecao').val('');
    } else {
        $("#causa_nova_reinspecao").prop('disabled', false);
    }
})

// Envio das informações para o Backend da Reinspecao

$('#envio_reinspecao').on('click',function() {

    $('#envio_reinspecao').prop('disabled',true);

    $("#loading").show();

    let n_conformidades_value = $('#n_conformidades_reinspecao').val();
    let inspetor = $('#inspetor_reinspecao').val();
    let qtd_produzida_value = $('#qtd_produzida_reinspecao').val();
    let causa_reinspecao =  $("#causa_nova_reinspecao").val();

    if(n_conformidades_value === "" || inspetor === null || n_conformidades_value < 0 || n_conformidades_value > qtd_produzida_value){
        alert("Preencha todos os campos corretamente")
        $('#envio_reinspecao').prop('disabled',false);
        $("#loading").hide();
        return
    } else if(n_conformidades_value >= 0 && n_conformidades_value < qtd_produzida_value && causa_reinspecao === null){
        alert("Preencha todos os campos corretamente")
        console.log("else if")
        $('#envio_reinspecao').prop('disabled',false);
        $("#loading").hide();
        return
    }

    let id_inspecao =  $('#reinspecaoModalLabel').text();
    let data_inspecao = $('#data_nova_inspecao').val();
    let n_nao_conformidades = $('#n_nao_conformidades_reinspecao').val();
    let reinspecao = true;

    $.ajax({
        url: '/inspecao',
        type: 'POST',  // Alterado para POST
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({ 'id_inspecao': id_inspecao ,'data_inspecao':data_inspecao,'n_conformidades_value':n_conformidades_value,
        'n_nao_conformidades':n_nao_conformidades,'causa_reinspecao':causa_reinspecao,'inspetor':inspetor,'qtd_produzida':qtd_produzida_value,'reinspecao':reinspecao}),  // Enviando um objeto JSON
        success: function(response) {
            window.location.reload();
            console.log(response)
            $("#loading").hide();
        },
        error: function(error) {
            console.log(error);
            $('#envio_reinspecao').prop('disabled',false);
            $("#loading").hide();
        }
    });
})

// tooltip da tabela de A inspecionar 
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})

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