import decimal

from django.contrib.auth import logout, authenticate
from django.contrib.auth.models import User
from django.db.models import Avg
from rest_framework import authentication, permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.status import HTTP_400_BAD_REQUEST

from rest_framework.views import APIView
from .models import Professor, Rating, ModuleInstance


@api_view(['POST'])
def register(request):
    """
    Register a new user
    """
    if request.data['username'] and request.data['email'] and request.data['password']:
        User.objects.create_user(request.data['username'], request.data['email'], request.data['password'])
        return Response("User added!")
    else:
        return Response("Not enough data provided! Need username, email and password", status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_user(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if not user:
        return Response("User not found")

    token, _ = Token.objects.get_or_create(user=user)

    return Response(token.key)


@api_view(['GET'])
def logout_user(request):
    """
    log out a user
    """
    logout(request)
    return Response("Logged out!")


@api_view(['GET'])
def list_modules(request):
    """
    View a list of all the modules and the lecturers teaching them
    """
    modules = ModuleInstance.objects.all()
    if modules:
        base_string = "{:5} {:30} {:5} {:9} {}\n"
        module_table = base_string.format("Code", "Module", "Year", "Semester", "Taught by")
        for module in modules:
            module_table += "-----------------------------------------------------------------------\n"
            module_table += base_string.format(
                module.module.code, module.module.title, module.year, module.semester, module.prof.all()[0])
            if len(module.prof.all()) > 1:
                for i in range(1, len(module.prof.all())):
                    module_table += base_string.format("", "", "", "", module.prof.all()[i])
        return Response(module_table, content_type="text/plain")
    else:
        return Response("No modules found!", content_type="text/plain")


@api_view(['GET'])
def view_ratings(request):
    """
    view a list of all the lecturers and their ratings
    """
    profs = Professor.objects.all()
    if profs:
        prof_table = ""
        for prof in profs:
            prof_ratings = Rating.objects.all().filter(prof=prof.id)
            if prof_ratings:
                average_rating = prof_ratings.aggregate(ave=Avg('rating'))['ave']
                average_rating = int(decimal.Decimal(average_rating)
                                     .quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))

                prof_table += "{} has a rating of {}\n".format(prof.name, "*" * average_rating)
            else:
                prof_table += "{} has no ratings!\n".format(prof.name, prof.id)

        return Response(prof_table)
    else:
        return Response("No lecturers exist!")


@api_view(['GET'])
def average_rating_per_module(request):
    """
    view the rating of a lecturer in an individual module
    """
    params = request.query_params
    ratings = Rating.objects.all().filter(prof=params['prof'], module=params['module'])
    if ratings:
        average_rating = ratings.aggregate(ave=Avg('rating'))['ave']
        average_rating = int(decimal.Decimal(average_rating)
                             .quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return Response("The rating for {} on module {} is {}".format(
            ratings[0].prof, ratings[0].module, "*" * average_rating))

    else:
        return Response("No ratings exist for this prof on this module!")


class RateProf(APIView):
    """
    Class to rate users

    * Requires token authentication.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        rate a lecturer in a specific module
        """
        params = request.query_params

        # look for the module mentioned, if it's there log the rating, if not then return
        mod = ModuleInstance.objects.all().filter(module=params["module"], prof=params["prof"],
                                                  semester=params["semester"], year=params["year"])
        if mod:
            rating = Rating(prof=Professor.objects.all().filter(id=params['prof'])[0],
                            moduleInstance=mod[0], rating=int(params["rating"]), module=mod[0].module)
            rating.save()

            return Response("Thanks for rating!")
        else:
            return Response("Invalid input! There was no module at that time taught by that lecturer. Try again")
