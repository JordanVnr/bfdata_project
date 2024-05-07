import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_recipe_links(url):
    """
    Extracts URLs of recipes from a webpage containing multiple recipe links.

    Args:
        url (str): The URL of a webpage containing links to recipes.

    Returns:
        list: A list of URLs (strings) pointing to individual recipe pages.
    """

    # Send a GET request to retrieve the HTML content of the page
    response = requests.get(url)

    # Create a BeautifulSoup object from the HTML content
    soup = BeautifulSoup(response.text, "html5lib")

    # List to store the extracted links
    links = []

    # Find all <a> tags with the class "recipe-card-link"
    recipe_links = soup.find_all('a', class_='recipe-card-link')

    # Iterate through the found tags and extract the href attribute
    for link in recipe_links:
        href = link.get('href')  # Get the value of the href attribute
        links.append(href)

    return links

def recipe_type(url):
    """
    Determines the type of recipe based on the provided URL.

    Args:
        url (str): The URL of a webpage containing top-rated recipes.

    Returns:
        str: The type of recipe ('entree', 'plat', or 'dessert') based on the URL.
    """

    if url == "https://www.marmiton.org/recettes/top-internautes-entree.aspx": return "entree"
    if url == "https://www.marmiton.org/recettes/top-internautes-plat-principal.aspx": return "plat"
    if url == "https://www.marmiton.org/recettes/top-internautes-dessert.aspx": return "dessert"


def scrape_recipe_data(url):
    """
    Extracts information about a recipe from a given URL.

    Args:
        url (str): The URL of the recipe page to be scraped.

    Returns:
        tuple: A tuple containing various details of the recipe, including:
            - recipe_name (str): The name of the recipe.
            - recipe_rate (str): The rating of the recipe.
            - recipe_comments (str): The number of comments/reviews for the recipe.
            - recipe_difficulty (str): The difficulty level of the recipe.
            - recipe_timer (str): The preparation time of the recipe.
            - ingredients_dict (dict): A dictionary containing ingredients and their quantities.
    """

    # Send a GET request to retrieve the HTML content of the recipe URL
    response = requests.get(url)

    # Create a BeautifulSoup object from the HTML content
    soup = BeautifulSoup(response.text, "html5lib")
    
    # Find the recipe title in the <h1> tag
    recipe_name = soup.find('h1').text.strip()  
    
    # Find the recipe rating in the <span> tag with class "recipe-header__rating-text"
    recipe_rate = soup.find('span',class_="recipe-header__rating-text").text.strip()     
    
    # Find the recipe comments in the <a> tag with href "#topReviewsTitle"
    comments_tag = soup.find('i', class_='icon icon-icon_comment')
    recipe_comments = comments_tag.find_next('a', href="#topReviewsTitle").text.strip()     
    

    # Find the recipe difficulty level in the <i> tag with class "icon-difficulty"
    difficulty_tag = soup.find('i', class_='icon icon-difficulty')     
    recipe_difficulty = difficulty_tag.find_next('span').text.strip()

    # Find the recipe difficulty level in the <i> tag with class "icon-timer1"
    timer_tag = soup.find('i', class_='icon icon-timer1')     
    recipe_timer = timer_tag.find_next('span').text.strip()

    # Extract ingredients and their quantities into a dictionary
    ingredients_dict = {}
    ingredient_tags = soup.find_all('div', class_='card-ingredient', attrs={'data-name': True})
    for tag in ingredient_tags:
        ingredient_name = tag['data-name']
        quantity_tag = tag.find_next('span', class_='count')
        ingredient_quantity = quantity_tag.text.strip()
        ingredients_dict[ingredient_name] = ingredient_quantity

    return recipe_name, recipe_rate, recipe_comments, recipe_difficulty, recipe_timer, ingredients_dict

def scrape_recipes_info(urls,recipe_type):
    """
    Extracts information about recipes from a list of URLs, categorized by a specified recipe type.

    Args:
        urls (list): A list of URLs pointing to recipe pages.
        recipe_type (str): The type/category of the recipes (e.g., 'entree', 'plat', 'dessert').

    Returns:
        pd.DataFrame: A DataFrame containing detailed information about each recipe,
                      categorized by the specified recipe type.
    """

    # List to store recipe info (name, rating, difficulty, comments, ingredients, URL)
    recipes_info = []

    # Iterate through each recipe URL in the list
    for url in urls:
        recipe_name, recipe_rating, recipe_comments, recipe_difficulty, recipe_timer, ingredients_dict = scrape_recipe_data(url)

        # Add recipe info to the list
        recipes_info.append({
            'Recipe Type': recipe_type,
            'Recipe Name': recipe_name,
            'Rating': recipe_rating,
            'Comments': recipe_comments.split()[0],
            'Difficulty': recipe_difficulty,
            'Timer': recipe_timer,
            'Ingredients': ingredients_dict,
            'URL': url    
            })    
    # Transfome list to a DataFrame
    recipes_dataframe = pd.DataFrame(recipes_info)

    return recipes_dataframe

def append_dataframes(*dataframes):
    """
    Concatenates an arbitrary number of DataFrames together.

    Args:
        *dataframes: Variable-length argument list of DataFrames to concatenate.

    Returns:
        pd.DataFrame: Concatenated DataFrame containing all rows from input DataFrames.
    """
    # Concatenate all DataFrames together using pd.concat()
    concatenated_df = pd.concat(dataframes, ignore_index=True)
    
    return concatenated_df
    
def create_database():
    """
    Creates a database by scraping recipe information from specified URLs and categorizing them by type.

    Returns:
        pd.DataFrame: A DataFrame containing combined recipe information for entrees, main dishes (plats), and desserts.
    """

    # URLs for different recipe types
    url_entree = "https://www.marmiton.org/recettes/top-internautes-entree.aspx"
    url_plat = "https://www.marmiton.org/recettes/top-internautes-plat-principal.aspx"
    url_dessert = "https://www.marmiton.org/recettes/top-internautes-dessert.aspx"

    # Scrape recipe information and categorize by type
    df_entree = scrape_recipes_info(scrape_recipe_links(url_entree),recipe_type(url_entree))
    df_plat = scrape_recipes_info(scrape_recipe_links(url_plat),recipe_type(url_plat))
    df_dessert = scrape_recipes_info(scrape_recipe_links(url_dessert),recipe_type(url_dessert))

    # Combine DataFrames for different recipe types
    df_final = append_dataframes(df_entree,df_plat,df_dessert)

    return df_final

create_database().to_csv("DataFrame Marmiton.csv")