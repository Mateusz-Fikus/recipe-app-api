from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    #Base viewset for user owned recipe attributes
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        #Return objects for the current authenticated user only
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        #Create a new object
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    #Manage tags in the database
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

class IngredeientViewSet(BaseRecipeAttrViewSet):
    #Manage ingredients in the database
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    #Manage recipes in the database
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, qs):
        #Convert a list of string ids to a list of ints for filtering
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        #Retrieve recipes for authenticated users

        #for filtering when passing args in get
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset

        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids) #syntax for foregin key filter

        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        #Return appropriate serializer class
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer

        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        #Upload an image to a recipe
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

        