// Iniciar produção 

document.getElementById('btnSalvar').addEventListener('click', function () {

    showLoading();

    var peca = document.getElementById('userInput').value;
    var dt_planejada = document.getElementById('inputData').value;
    var qt_planejada = document.getElementById('inputQuantidade').value;
    
    let _data = {
        peca: peca,
        dt_planejada: dt_planejada,
        qt_planejada: qt_planejada,

    };

    if (!inputData || !dt_planejada || !qt_planejada) {
        alert('Preencha todos os campos.');
        hideLoading();
        return;
    };


    fetch('/iniciar-producao-serralheria', {
        method: "POST",
        body: JSON.stringify(_data),
        headers: { "Content-type": "application/json; charset=UTF-8" }
    })
        .then(response => {
            return response.json(); // Retorna a promessa JSON
        })
        .then(json => {
            console.log(json);
            $('#modalPecaFora').modal('hide');
            hideLoading();
        })
        .catch(err => {
            console.log(err);
            hideLoading();
        });

    document.getElementById('userInput').value = '';
    document.getElementById('inputData').value = '';
    document.getElementById('inputQuantidade').value = '';
    

});

// Finalizar produção

// document.getElementById('btnSalvar').addEventListener('click', function () {

//     var peca = document.getElementById('userInput').value;
//     var dt_planejada = document.getElementById('inputData').value;
//     var qt_planejada = document.getElementById('inputQuantidade').value;
    
//     let _data = {
//         peca: peca,
//         dt_planejada: dt_planejada,
//         qt_planejada: qt_planejada,

//     };

//     fetch('/iniciar-producao-serralheria', {
//         method: "POST",
//         body: JSON.stringify(_data),
//         headers: { "Content-type": "application/json; charset=UTF-8" }
//     })
//         .then(response => response.json())
//         .then(json => console.log(json))
//         .catch(err => console.log(err));

// });

