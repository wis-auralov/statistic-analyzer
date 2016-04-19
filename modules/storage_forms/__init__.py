# -*- coding: utf-8 -*-
"""
Модуль хранения форм и формсетов в базе данных
Для того что бы реализовать сохранение формы в базе нужно:

- добавить в settings.TYPE_REPORT_CHOICES новый чойс с типом отчета

- для исходного класса (вью + форм миксин) унаследоваться от миксин-класса
    StorageFormMixin

- добавить параметры в класс-наследник:
    form - класс формы
    formset - класс формсета (если не указан - не будет сохранен)
    report_type - вид отчета (должен быть один из 1х значений в кортежах
                              settings.TYPE_REPORT_CHOICES)


- добавить в методе "post" после валидации формы :
    необходимо добавить этот код что бы сразу после валидации можно было
    засейвить форму. так как метод может вернуть редирект - позволяем его
    выплюнуть в респонс

    action_triggered, store_result = self.store_form_by_action(
        request, form=form, formset=formset
    )
    if isinstance(store_result, HttpResponse):
        return store_result
    if not action_triggered:
        pass  # здесь код дальнейшей обработки поста

- инклудить в шаблон :
    {% include 'widgets/stored_form_list.html' %} - в общую структуру шаблона
    {% include 'widgets/stored_form_actions.html' %} - внутрь основной формы

- подключить css файлы:
    <link rel="stylesheet" type="text/css"
    href="{% static 'storage_forms/css/storage_style.css' %}"/>

- подключить в админке:
    фильтрацию по типу отчета в модели StoredFormCollection


в результате:
     в контексте шаблонов будут доступны переменные:
     "form" - основная форма,
     "formset" - формсет (если есть) ,
     "stored_forms" - сохраненные формы (для указанного типа отчета)
     "current_stored_form" - текущая выбранная форма, загруженная из базы

     при сохранении в базу будут сыпаться формы с пометкой для какого типа
     отчета они


"""

default_app_config = 'storage_forms.apps.StorageFormsConfig'
