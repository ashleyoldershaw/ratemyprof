from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# professor class, used for modules and ratings
class Professor(models.Model):
    id = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return "{} - {}".format(self.id, self.name)


# module class, used for ratings
class Module(models.Model):
    code = models.CharField(max_length=4, primary_key=True)
    title = models.CharField(max_length=200)

    def __str__(self):
        return "{} - {}".format(self.code, self.title)


class ModuleInstance(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    prof = models.ManyToManyField(Professor)
    semester = models.CharField(max_length=1)
    year = models.CharField(max_length=4)

    def __str__(self):
        return "{} ({} S{})".format(self.module, self.year, self.semester)


# rating class
class Rating(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    moduleInstance = models.ForeignKey(ModuleInstance, on_delete=models.CASCADE)
    prof = models.ForeignKey(Professor, on_delete=models.CASCADE)
    rating = models.IntegerField (
        validators=[
            MaxValueValidator(5),
            MinValueValidator(0)
        ]
    )

    def __str__(self):
        return "{} {}: {}".format(self.prof.id , self.module, self.rating)
