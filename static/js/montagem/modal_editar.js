function modalEditar(data_carga,data_planejada,codigo,descricao,qtd_planejada,id) {

    $("#editar_data_carga_montagem").val(data_carga)
    $("#editar_data_planejada_montagem").val(data_planejada)
    $("#editar_codigo_montagem").val(codigo)
    $("#editar_descricao_montagem").val(descricao)
    $("#editar_quantidade_planejada_montagem").val(qtd_planejada)
    $("#editar_id_planejada_montagem").val(id)

}

$("#submitEditar").on('click', function() {
    showLoading();
    const nova_quantidade_planejada = parseInt($("#editar_quantidade_planejada_montagem").val());
    const id_planejada_montagem = $("#editar_id_planejada_montagem").val();

    // Verificar se a quantidade é um número válido e maior ou igual a zero
    if (isNaN(nova_quantidade_planejada) || nova_quantidade_planejada < 0) {
        alert("Quantidade Planejada está vazia ou menor que zero");
        hideLoading();
        return;
    }

    $.ajax({
        url: '/editar-montagem',
        type: 'POST',  // Método POST
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({
            'id_planejada_montagem': id_planejada_montagem,
            'nova_quantidade_planejada': nova_quantidade_planejada
        }),  // Enviando um objeto JSON
        success: function(response) {
            alert('Quantidade planejada alterada para ' + nova_quantidade_planejada);
            location.reload()
        },
        error: function(xhr, status, error) {
            alert('Ocorreu um erro: ' + xhr.responseText || error);
            hideLoading();
        }
    });
});