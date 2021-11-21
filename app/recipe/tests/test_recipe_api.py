from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
import recipe
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    #Return a recipe detail url
    return reverse('recipe:recipe-detail', args=[recipe_id])

def sample_ingredient(user, name='Tomato'):
    #Create and return sample ingredient
    return Ingredient.objects.create(user=user, name=name)

def sample_tag(user, name='Main course'):
    #Create and return sample tag
    return Tag.objects.create(user=user, name=name )

def sample_recipe(user, **params):
    #Create and return sample recipe
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 90,
        'price': 5.00
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    #Test unauthenticated recipe API access

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        #Test that authorization is required
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    #Test authenticated recipe API access
    
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@djangoproject.com",
            password='testpass123'
        )
        self.client.force_authenticate(self.user)


    def test_retrieve_recipes(self):
        #Test retrieving a list of recipes
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('id')

        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_recipes_limited_user(self):
        #Test retrieving recipes for user
        user2 = get_user_model().objects.create_user(
            email='test3@djangoproject.com',
            password='testpass1234'
        )

        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        #Test viewing a recipe detail
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

        
    def test_create_basic_recipe(self):
        #Test create basic recipe
        payload = {
            'title': 'Chocolate Cheesecake',
            'time_minutes': 60,
            'price': 20.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))


    def test_create_recipe_with_tags(self):
        #Test creating recipe with tags
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')

        payload = {
            'title': 'Chocolate lime cheesecake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.00
        }

        res = self.client.post(RECIPES_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    
    def test_create_recipe_with_ingredients(self):
        #Test creating recipe with ingredients
        ingredient1 = sample_ingredient(user=self.user, name='Shrimp')
        ingredient2 = sample_ingredient(user=self.user, name='Curry')

        payload = {
            'title': 'Shrimp curr',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 240,
            'price': 90.00
        }

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

