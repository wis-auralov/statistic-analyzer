$(document).ready(function() {
    var formset_global_counter = $('#formset-body').children().length;

    $('#formset-body').on('click', 'button[formset-delete-button]', function(){
        var total_forms = $('input[name=form-TOTAL_FORMS]');
        $.each(total_forms, function(index, counter){
            counter.value = parseInt(counter.value) - 1;
        });

        $(this).parent().remove();
    });


    $('#add-form').click(function(){
        var tmpl_markup = $('#formset-empty-form').html();
        var compiled_tmpl = tmpl_markup.replace(/__prefix__/g, formset_global_counter);
        $('div#formset-body').append(compiled_tmpl);

        var total_forms = $('input[name=form-TOTAL_FORMS]');
        $.each(total_forms, function(index, counter){
            counter.value = parseInt(counter.value) + 1;
        });
        formset_global_counter += parseInt(formset_global_counter) + 1;
    });

});