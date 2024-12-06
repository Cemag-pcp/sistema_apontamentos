function modalTubos() {

    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);


    $('#data_tubo').val(today.toLocaleDateString());
   
    // Exibir o modal
    $('#estanqueidadeTubosModal').modal('show');
}

function modalCilindros() {

    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);

    $('#data_cilindro').val(today.toLocaleDateString());

    // Exibir o modal
    $('#estanqueidadeCilindrosModal').modal('show');
}

function modalTanque() {

    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);

    $('#data_tanque').val(today.toLocaleDateString());

    // Exibir o modal
    $('#estanqueidadeTanqueModal').modal('show');
}

