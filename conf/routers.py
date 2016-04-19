# -*- coding: utf-8 -*-

ADDITIONAL_DB = ('raw_statistics', )


class DefaultRouter(object):
    """A router to control all database operations on models in
    the myapp application """

    def db_for_read(self, model, **hints):
        if model._meta.app_label in ADDITIONAL_DB:
            return model._meta.app_label
        return None

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # приложения в ADDITIONAL_DB разнесены по одноименным БД
        if app_label in ADDITIONAL_DB and db != app_label:
            return False
        if db in ADDITIONAL_DB and db != app_label:
            return False
        return None