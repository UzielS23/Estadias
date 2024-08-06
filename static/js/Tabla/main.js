$(function() {

  $('.js-check-all').on('click', function() {
    
    if ( $(this).prop('checked') ) {
      $('.control--checkbox input[type="checkbox"]').each(function() {
        $(this).prop('checked', true);
      })
    } else {
      $('.control--checkbox input[type="checkbox"]').each(function() {
        $(this).prop('checked', false);
      })
    }

  });

  $('.js-ios-switch-all').on('click', function() {
    
    if ( $(this).prop('checked') ) {
      $('.ios-switch input[type="checkbox"]').each(function() {
        $(this).prop('checked', true);
        $(this).closest('tr').addClass('active');
      })
    } else {
      $('.ios-switch input[type="checkbox"]').each(function() {
        $(this).prop('checked', false);
        $(this).closest('tr').removeClass('active');
      })
    }

  });

  $('.ios-switch input[type="checkbox"]').on('click', function() {
    if ( $(this).closest('tr').hasClass('active') ) {
      $(this).closest('tr').removeClass('active');
    } else {
      $(this).closest('tr').addClass('active');
    }
  });

    

});

function eliminarProblema(checkbox) {
  if (checkbox.checked) {
      const id = checkbox.getAttribute('data-id');
      fetch(`/delete_problema/${id}`, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          }
      }).then(response => {
          if (response.ok) {
              // Elimina la fila del problema de la tabla
              checkbox.closest('tr').remove();
          } else {
              console.error('Error al eliminar el problema');
          }
      }).catch(error => console.error('Error:', error));
  }
}