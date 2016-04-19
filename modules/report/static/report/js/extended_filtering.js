$(document).ready(function() {
    var FILTERS_CHOICES_API = '/report/api/get_filter_choices/'
    var CLIENT_FILTER_FIELDS = []

    // запоминаем все дополнительные множественные фильтры (их порядок будет
    // определять последовательность обновлений при запросах)

    $('select.client_filter_fields[multiple="multiple"]').each(
        function(ind, el){
            CLIENT_FILTER_FIELDS.push($(el).attr('name'));
        }
    )
    var applyFilterChoices = function(selectGroupsChoices, selectNamesForUpdate){
        $.each(selectNamesForUpdate,function(index, selectName){
            console.log(selectName);
            var selectObject = $('select.client_filter_fields[multiple="multiple"][name="'+selectName+'"]')[0];
            $(selectObject).empty();
            if (selectGroupsChoices[selectName].length > 0){
                $(selectObject).show();
                $.each(selectGroupsChoices[selectName],function(ind, selectChoice){
                    selectObject.options[ind] = new Option(selectChoice[0], selectChoice[1]);
                })
            }
            else{ $(selectObject).hide(); }
        })
    }

    var extraFilterChanged = function(selectObjectName, selectValuesList){
        // Если установлено selectValuesList то значение добавляется в
        // запрашиваемые данные на сервер
        var indexOfSelectObject = CLIENT_FILTER_FIELDS.indexOf(selectObjectName)
        if (indexOfSelectObject == CLIENT_FILTER_FIELDS.length - 1) return;
        resObj = {}
        for(var i=0; i<=indexOfSelectObject; i++){
            console.log(i);
            var selectName = CLIENT_FILTER_FIELDS[i];
            var selectObject = $('select.client_filter_fields[multiple="multiple"][name="'+selectName+'"]')[0];
            resObj[selectName] = $(selectObject).val()
        }
        var selectNamesForUpdate = []
        for(var i=indexOfSelectObject+1; i< CLIENT_FILTER_FIELDS.length; i++){
            selectNamesForUpdate.push(CLIENT_FILTER_FIELDS[i])
        }
        if (selectValuesList){
            resObj[selectObjectName] = selectValuesList
        }

        $.ajax({
            type: 'post',
            url: FILTERS_CHOICES_API,
            data: JSON.stringify(resObj),
            contentType: "application/json; charset=utf-8",
            traditional: true,
            success: function (data) {
                console.log(data);
                applyFilterChoices(data.data, selectNamesForUpdate)
            }
        });
    }


    var bindChangeFilteredDealers = function(){
        $($('select[name="dealer"]')[0]).bind("DOMSubtreeModified",
            function() {
                if (! dealerSelectProcessed){
                    setTimeout(function(){
                        var selectedDealerIds = [];
                        $('select[name="dealer"] option').each(
                            function(){ selectedDealerIds.push($(this).val()) }
                        )
                        dealerSelectProcessed = false;
                        extraFilterChanged('dealer', selectedDealerIds)
                    }, 300);
                    dealerSelectProcessed = true;
                }
            }
        )
    }

    //  при инициализаци страницы смотрим какие мультиплчойсы пустые и скрываем их:
    $('select.client_filter_fields[multiple="multiple"]').each(
        function(index, item){
            if (item.length == 0) $(item).hide();
        }
    )
    //  вешаем обработчик на изменение каждого мультипл чойса
    $('select.client_filter_fields[multiple="multiple"]').change(
        function(){
            extraFilterChanged($(this).attr('name'))
        }
    )
    // вешаем обработчик на джанговский горизонтал-фильтр (отложенно, что бы
    // прямо при загрузке просто проинициализировалось то, что мы передали с
    // формой
    var dealerSelectProcessed = false;
    setTimeout(bindChangeFilteredDealers, 300)
});