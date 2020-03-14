from django.contrib import admin
from .models import Module, Professor, Rating, ModuleInstance

admin.site.register(Module)

admin.site.register(ModuleInstance)

admin.site.register(Professor)

admin.site.register(Rating)
