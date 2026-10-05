export const hotIngredients={
  "cayenne": {
    "name": "Fresh stemmed red cayenne peppers",
    "role": "Pepper"
  },
  "redChili": {
    "name": "Fresh stemmed red chilies",
    "role": "Pepper"
  },
  "jalapeno": {
    "name": "Fresh stemmed jalapeños",
    "role": "Pepper"
  },
  "habanero": {
    "name": "Fresh stemmed habaneros",
    "role": "Pepper"
  },
  "scotch": {
    "name": "Fresh stemmed Scotch bonnets",
    "role": "Pepper"
  },
  "arbol": {
    "name": "Rehydrated, drained árbol chilies",
    "role": "Pepper"
  },
  "ancho": {
    "name": "Rehydrated, drained ancho chilies",
    "role": "Pepper"
  },
  "piquin": {
    "name": "Rehydrated, drained piquín chilies",
    "role": "Pepper"
  },
  "chipotle": {
    "name": "Canned chipotles in adobo",
    "role": "Pepper",
    "allergens": "Check prepared ingredient label"
  },
  "bell": {
    "name": "Roasted red bell pepper, peeled",
    "role": "Base"
  },
  "tomato": {
    "name": "Cooked tomato",
    "role": "Base"
  },
  "tomatillo": {
    "name": "Cooked tomatillos",
    "role": "Base"
  },
  "carrot": {
    "name": "Cooked carrot",
    "role": "Base"
  },
  "guava": {
    "name": "Seedless guava pulp",
    "role": "Fruit"
  },
  "pineapple": {
    "name": "Grilled pineapple flesh",
    "role": "Fruit"
  },
  "mango": {
    "name": "Ripe mango flesh",
    "role": "Fruit"
  },
  "vinegar": {
    "name": "White vinegar",
    "role": "Acid"
  },
  "lime": {
    "name": "Lime juice",
    "role": "Acid"
  },
  "lemon": {
    "name": "Lemon juice",
    "role": "Acid"
  },
  "water": {
    "name": "Water",
    "role": "Liquid"
  },
  "oil": {
    "name": "Olive oil",
    "role": "Oil"
  },
  "neutralOil": {
    "name": "Neutral oil",
    "role": "Oil"
  },
  "garlic": {
    "name": "Peeled fresh garlic",
    "role": "Aromatic"
  },
  "onion": {
    "name": "Chopped onion",
    "role": "Aromatic"
  },
  "cilantro": {
    "name": "Fresh cilantro, washed",
    "role": "Herb"
  },
  "parsley": {
    "name": "Fresh parsley, washed",
    "role": "Herb"
  },
  "sugar": {
    "name": "White sugar",
    "role": "Sweet"
  },
  "salt": {
    "name": "Fine salt",
    "role": "Seasoning"
  },
  "cumin": {
    "name": "Ground cumin",
    "role": "Spice"
  },
  "coriander": {
    "name": "Ground coriander",
    "role": "Spice"
  },
  "caraway": {
    "name": "Ground caraway",
    "role": "Spice"
  },
  "cardamom": {
    "name": "Ground cardamom",
    "role": "Spice"
  },
  "mayo": {
    "name": "Prepared mayonnaise",
    "role": "Base",
    "allergens": "Egg; check label"
  },
  "mustard": {
    "name": "Prepared yellow mustard",
    "role": "Base",
    "allergens": "Mustard; check label"
  },
  "birdEye": {
    "name": "Stemmed African bird’s-eye chilies",
    "role": "Pepper"
  }
};
export const hotSauces=[
  {
    "id": "thai-sriracha",
    "name": "Thai Sriracha",
    "region": "Thailand",
    "family": "Garlic",
    "heat": "Medium",
    "photoId": "red",
    "source": "https://hot-thai-kitchen.com/sriracha-hot-sauce/",
    "description": "A smooth chili-garlic sauce with sweet and sour balance, documented by Thai cook Pailin Chongchitnant.",
    "recipe": {
      "redChili": 46,
      "vinegar": 25,
      "water": 14,
      "garlic": 8,
      "sugar": 6,
      "salt": 1
    },
    "method": "Chop the prepared ingredients. Blend, then simmer gently in a covered pan, stirring until the fresh peppers and garlic soften. Cool before tasting; use a ventilated kitchen and avoid breathing chili steam. This is a fresh cooked adaptation, not an aged or fermented sauce.",
    "provenance": "Regional style",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Grilled chicken",
      "Seafood",
      "Eggs"
    ]
  },
  {
    "id": "arbol-salsa",
    "name": "Chile de Árbol Salsa",
    "region": "Mexico",
    "family": "Salsa",
    "heat": "Hot",
    "photoId": "roasted",
    "source": "https://www.mexicoinmykitchen.com/chile-de-arbol-salsa-recipe/",
    "description": "Cooked tomato and tomatillo soften the sharp flavor of dried árbol chilies.",
    "recipe": {
      "arbol": 14,
      "tomato": 36,
      "tomatillo": 26,
      "onion": 10,
      "water": 10,
      "garlic": 3,
      "salt": 1
    },
    "method": "Weigh the cooked or rehydrated ingredients after draining. Blend with the remaining ingredients. Cool any warm ingredients promptly, then refrigerate in a clean container.",
    "provenance": "Regional style",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Beef tacos",
      "Pork",
      "Grilled mushrooms"
    ]
  },
  {
    "id": "salsa-verde",
    "name": "Salsa Verde",
    "region": "Mexico",
    "family": "Salsa",
    "heat": "Medium",
    "photoId": "verde",
    "source": "https://www.mexicoinmykitchen.com/salsa-verde-recipe/",
    "description": "Tomatillo and green chili make a tangy cooked salsa. Cilantro is optional across household versions.",
    "recipe": {
      "tomatillo": 60,
      "jalapeno": 17,
      "onion": 10,
      "cilantro": 6,
      "water": 4,
      "garlic": 2,
      "salt": 1
    },
    "method": "Weigh the cooked or rehydrated ingredients after draining. Blend with the remaining ingredients. Cool any warm ingredients promptly, then refrigerate in a clean container.",
    "provenance": "Regional style",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Chicken",
      "Pork",
      "Corn"
    ]
  },
  {
    "id": "caribbean-pepper",
    "name": "Caribbean Pepper Sauce",
    "region": "Trinidad & Caribbean",
    "family": "Fresh pepper",
    "heat": "Very hot",
    "photoId": "orange",
    "source": "https://caribbeanpot.com/traditional-caribbean-pepper-sauce/",
    "description": "Scotch bonnet, garlic and fresh herbs in a coarse pepper sauce, documented by Chris De La Rosa.",
    "recipe": {
      "scotch": 58,
      "vinegar": 25,
      "cilantro": 7,
      "garlic": 6,
      "lime": 3,
      "salt": 1
    },
    "method": "Wash and prepare the fresh ingredients. Pulse with the remaining ingredients to your preferred texture. Transfer to a clean container and refrigerate promptly. Taste a cooled spoonful before adjusting.",
    "provenance": "Regional style",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Grilled fish",
      "Chicken",
      "Rice dishes"
    ]
  },
  {
    "id": "harissa",
    "name": "Harissa",
    "region": "Tunisia / North Africa",
    "family": "Paste",
    "heat": "Hot",
    "photoId": "harissa",
    "source": "https://www.themediterraneandish.com/harissa-recipe/",
    "description": "A dried-chili paste with garlic and warm spices. The linked home version includes roasted peppers; local and household versions differ.",
    "recipe": {
      "ancho": 30,
      "bell": 34,
      "oil": 12,
      "lemon": 10,
      "garlic": 7,
      "cumin": 2,
      "coriander": 2,
      "caraway": 2,
      "salt": 1
    },
    "method": "Weigh the cooked or rehydrated ingredients after draining. Blend with the remaining ingredients. Cool any warm ingredients promptly, then refrigerate in a clean container.",
    "provenance": "Regional style",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Lamb",
      "Chicken",
      "Cauliflower"
    ]
  },
  {
    "id": "zhoug",
    "name": "Zhoug",
    "region": "Yemeni tradition · Jerusalem adaptation",
    "family": "Herb",
    "heat": "Hot",
    "photoId": "herb",
    "source": "https://ottolenghi.co.uk/pages/recipes/crispy-chicken-carlin-peas-zhoug",
    "description": "Chili and fresh herbs with aromatic spices. This reference is Ottolenghi and Tamimi’s Jerusalem-style adaptation.",
    "recipe": {
      "cilantro": 35,
      "parsley": 12,
      "jalapeno": 25,
      "oil": 15,
      "water": 6,
      "garlic": 4,
      "cumin": 1,
      "cardamom": 1,
      "salt": 1
    },
    "method": "Wash and prepare the fresh ingredients. Pulse with the remaining ingredients to your preferred texture. Transfer to a clean container and refrigerate promptly. Taste a cooled spoonful before adjusting.",
    "provenance": "Regional style",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Chicken",
      "Lamb",
      "Flatbread"
    ]
  },
  {
    "id": "aji-criollo",
    "name": "Ají Criollo",
    "region": "Ecuador",
    "family": "Fresh pepper",
    "heat": "Hot",
    "photoId": "herb",
    "source": "https://www.laylita.com/recetas/aji-criollo/",
    "description": "Fresh chilies, cilantro, garlic, onion and citrus make a bright Ecuadorian table condiment.",
    "recipe": {
      "redChili": 28,
      "cilantro": 15,
      "water": 28,
      "onion": 12,
      "lime": 10,
      "garlic": 6,
      "salt": 1
    },
    "method": "Wash and prepare the fresh ingredients. Pulse with the remaining ingredients to your preferred texture. Transfer to a clean container and refrigerate promptly. Taste a cooled spoonful before adjusting.",
    "provenance": "Regional style",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Grilled beef",
      "Potatoes",
      "Empanadas"
    ]
  },
  {
    "id": "smoked-chipotle",
    "name": "Smoked Chipotle",
    "region": "Mexican chili · US bottle style",
    "family": "Smoky",
    "heat": "Medium",
    "photoId": "chipotle",
    "source": "https://www.tabasco.com/hot-sauces/",
    "description": "Chipotle brings the smoke of dried, smoked jalapeños. Prepared adobo adds its own seasoning.",
    "recipe": {
      "chipotle": 45,
      "vinegar": 26,
      "water": 22,
      "sugar": 5,
      "garlic": 2
    },
    "method": "Weigh the cooked or rehydrated ingredients after draining. Blend with the remaining ingredients. Cool any warm ingredients promptly, then refrigerate in a clean container.",
    "provenance": "Commercial reference",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Pork",
      "Beef",
      "Beans"
    ]
  },
  {
    "id": "aged-red",
    "name": "Louisiana Aged Red",
    "region": "Louisiana · USA",
    "family": "Vinegar",
    "heat": "Medium",
    "photoId": "red",
    "source": "https://www.tabasco.com/products/hot-sauces/original-red-sauce/",
    "description": "The commercial reference uses aged red peppers, vinegar and salt. Aging contributes flavor beyond fresh chili heat.",
    "recipe": {
      "cayenne": 40,
      "vinegar": 53,
      "water": 5,
      "salt": 2
    },
    "method": "Chop the prepared ingredients. Blend, then simmer gently in a covered pan, stirring until the fresh peppers and garlic soften. Cool before tasting; use a ventilated kitchen and avoid breathing chili steam. This is a fresh cooked adaptation, not an aged or fermented sauce.",
    "provenance": "Commercial reference",
    "note": "TABASCO Original Red ages its peppers up to three years. The maker below is a fresh alternative and cannot reproduce that aging.",
    "pairs": [
      "Grilled meats",
      "Vegetables"
    ]
  },
  {
    "id": "cayenne-vinegar",
    "name": "Cayenne Vinegar",
    "region": "Louisiana-style · USA",
    "family": "Vinegar",
    "heat": "Medium",
    "photoId": "red",
    "source": "https://www.franksredhot.com/en-ca/products/franks-redhot-original-cayenne-pepper-sauce",
    "description": "A cayenne-led vinegar sauce with garlic; a familiar base for wing sauces.",
    "recipe": {
      "cayenne": 37,
      "vinegar": 43,
      "water": 15,
      "garlic": 3,
      "salt": 2
    },
    "method": "Chop the prepared ingredients. Blend, then simmer gently in a covered pan, stirring until the fresh peppers and garlic soften. Cool before tasting; use a ventilated kitchen and avoid breathing chili steam. This is a fresh cooked adaptation, not an aged or fermented sauce.",
    "provenance": "Commercial reference",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Grilled meats",
      "Vegetables"
    ]
  },
  {
    "id": "green-jalapeno",
    "name": "Green Jalapeño",
    "region": "Louisiana-style · USA",
    "family": "Vinegar",
    "heat": "Mild",
    "photoId": "verde",
    "source": "https://www.tabasco.com/hot-sauces/",
    "description": "A green jalapeño profile, brighter and less smoky than chipotle.",
    "recipe": {
      "jalapeno": 45,
      "vinegar": 35,
      "water": 16,
      "salt": 2,
      "garlic": 2
    },
    "method": "Chop the prepared ingredients. Blend, then simmer gently in a covered pan, stirring until the fresh peppers and garlic soften. Cool before tasting; use a ventilated kitchen and avoid breathing chili steam. This is a fresh cooked adaptation, not an aged or fermented sauce.",
    "provenance": "Commercial reference",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Grilled meats",
      "Vegetables"
    ]
  },
  {
    "id": "garlic-pepper",
    "name": "Garlic Pepper",
    "region": "Louisiana-style · USA",
    "family": "Garlic",
    "heat": "Mild",
    "photoId": "garlic",
    "source": "https://www.tabasco.com/hot-sauces/",
    "description": "A garlic-forward pepper sauce; this fresh blend interprets the commercial flavor family.",
    "recipe": {
      "redChili": 36,
      "vinegar": 34,
      "water": 18,
      "garlic": 10,
      "salt": 2
    },
    "method": "Chop the prepared ingredients. Blend, then simmer gently in a covered pan, stirring until the fresh peppers and garlic soften. Cool before tasting; use a ventilated kitchen and avoid breathing chili steam. This is a fresh cooked adaptation, not an aged or fermented sauce.",
    "provenance": "Commercial reference",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Grilled meats",
      "Vegetables"
    ]
  },
  {
    "id": "habanero-fruit",
    "name": "Habanero Fruit",
    "region": "Caribbean-inspired · US bottle style",
    "family": "Fruit",
    "heat": "Very hot",
    "photoId": "orange",
    "source": "https://www.tabasco.com/hot-sauces/",
    "description": "Habanero heat alongside tropical fruit. Fruit changes the flavor and body; it does not provide a reliable heat rating.",
    "recipe": {
      "habanero": 20,
      "mango": 28,
      "vinegar": 28,
      "water": 18,
      "garlic": 3,
      "sugar": 2,
      "salt": 1
    },
    "method": "Chop the prepared ingredients. Blend, then simmer gently in a covered pan, stirring until the fresh peppers and garlic soften. Cool before tasting; use a ventilated kitchen and avoid breathing chili steam. This is a fresh cooked adaptation, not an aged or fermented sauce.",
    "provenance": "Commercial reference",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Grilled meats",
      "Vegetables"
    ]
  },
  {
    "id": "arbol-piquin",
    "name": "Árbol & Piquín",
    "region": "Mexico",
    "family": "Dried chili",
    "heat": "Hot",
    "photoId": "roasted",
    "source": "https://www.cholula.com/en-us/",
    "description": "A bottled style featuring árbol and piquín chilies with spices. This is not a copy of Cholula’s proprietary formula.",
    "recipe": {
      "arbol": 28,
      "piquin": 8,
      "vinegar": 32,
      "water": 26,
      "garlic": 4,
      "salt": 2
    },
    "method": "Weigh the cooked or rehydrated ingredients after draining. Blend with the remaining ingredients. Cool any warm ingredients promptly, then refrigerate in a clean container.",
    "provenance": "Commercial reference",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Grilled meats",
      "Vegetables"
    ]
  },
  {
    "id": "habanero-oil",
    "name": "Habanero Oil Salsa",
    "region": "Chetumal · Mexico",
    "family": "Emulsion",
    "heat": "Very hot",
    "photoId": "orange",
    "source": "https://www.mexicoinmykitchen.com/creamy-habanero-salsa/",
    "description": "An oil-emulsified habanero salsa with a silky texture; creamy does not necessarily mean dairy.",
    "recipe": {
      "habanero": 28,
      "neutralOil": 38,
      "water": 25,
      "garlic": 7,
      "salt": 2
    },
    "method": "Use softened, cooled peppers and garlic. Blend with water and salt, then gradually blend in oil to emulsify. Refrigerate promptly; this is not oil-preserved storage.",
    "provenance": "Regional style",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Steak",
      "Fish",
      "Chicken"
    ]
  },
  {
    "id": "ancho-arbol",
    "name": "Ancho–Árbol Salsa",
    "region": "Mexico",
    "family": "Dried chili",
    "heat": "Hot",
    "photoId": "chipotle",
    "source": "https://www.mexicoinmykitchen.com/ancho-arbol-chile-pepper-salsa/",
    "description": "Ancho contributes depth and dried-fruit character; árbol provides sharper heat.",
    "recipe": {
      "ancho": 35,
      "arbol": 10,
      "water": 35,
      "tomato": 12,
      "onion": 4,
      "garlic": 3,
      "salt": 1
    },
    "method": "Weigh the cooked or rehydrated ingredients after draining. Blend with the remaining ingredients. Cool any warm ingredients promptly, then refrigerate in a clean container.",
    "provenance": "Regional style",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Grilled meats",
      "Vegetables"
    ]
  },
  {
    "id": "habanero-tomatillo",
    "name": "Habanero Tomatillo",
    "region": "Mexico",
    "family": "Salsa",
    "heat": "Very hot",
    "photoId": "verde",
    "source": "https://www.mexicoinmykitchen.com/habanero-tomatillo-salsa-recipe/",
    "description": "Cooked tomatillos with habanero: tartness and a fragrant, assertive chili finish.",
    "recipe": {
      "tomatillo": 65,
      "habanero": 12,
      "onion": 12,
      "water": 7,
      "garlic": 3,
      "salt": 1
    },
    "method": "Weigh the cooked or rehydrated ingredients after draining. Blend with the remaining ingredients. Cool any warm ingredients promptly, then refrigerate in a clean container.",
    "provenance": "Regional style",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Grilled meats",
      "Vegetables"
    ]
  },
  {
    "id": "sambal-oelek",
    "name": "Sambal Oelek",
    "region": "Indonesian style",
    "family": "Paste",
    "heat": "Hot",
    "photoId": "sambal",
    "source": "https://usa.lkk.com/en/industrial/products/sambal-oelek",
    "description": "A coarse chili paste. This commercial reference is useful for texture and ingredient context, not a universal sambal recipe.",
    "recipe": {
      "redChili": 73,
      "vinegar": 15,
      "water": 9,
      "salt": 3
    },
    "method": "Wash and prepare the fresh ingredients. Pulse with the remaining ingredients to your preferred texture. Transfer to a clean container and refrigerate promptly. Taste a cooled spoonful before adjusting.",
    "provenance": "Commercial reference",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Grilled meats",
      "Vegetables"
    ]
  },
  {
    "id": "peri-peri",
    "name": "PERi-PERi",
    "region": "Southern African / Portuguese influence",
    "family": "Citrus",
    "heat": "Hot",
    "photoId": "red",
    "source": "https://www.nandos.co.uk/UK/cook/medium-peri-peri-sauce",
    "description": "A chili, citrus and garlic profile. Nando’s Medium is the commercial reference; heat levels differ among products.",
    "recipe": {
      "lemon": 20,
      "vinegar": 16,
      "oil": 12,
      "water": 8,
      "garlic": 6,
      "salt": 2,
      "birdEye": 36
    },
    "method": "Chop the prepared ingredients. Blend, then simmer gently in a covered pan, stirring until the fresh peppers and garlic soften. Cool before tasting; use a ventilated kitchen and avoid breathing chili steam. This is a fresh cooked adaptation, not an aged or fermented sauce.",
    "provenance": "Commercial reference",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Grilled meats",
      "Vegetables"
    ]
  },
  {
    "id": "guava-pepper",
    "name": "Guava Peppersauce",
    "region": "Caribbean · chef variation",
    "family": "Fruit",
    "heat": "Hot",
    "photoId": "orange",
    "source": "https://caribbeanpot.com/insanely-good-guava-peppersauce-hot-sauce/",
    "description": "Guava pulp rounds out Scotch bonnet heat. A documented fruit-sauce variation, rather than one island’s universal recipe.",
    "recipe": {
      "guava": 48,
      "scotch": 18,
      "vinegar": 20,
      "water": 8,
      "garlic": 3,
      "lime": 2,
      "salt": 1
    },
    "method": "Chop the prepared ingredients. Blend, then simmer gently in a covered pan, stirring until the fresh peppers and garlic soften. Cool before tasting; use a ventilated kitchen and avoid breathing chili steam. This is a fresh cooked adaptation, not an aged or fermented sauce.",
    "provenance": "Chef variation",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Grilled meats",
      "Vegetables"
    ]
  },
  {
    "id": "pineapple-pepper",
    "name": "Grilled Pineapple Peppersauce",
    "region": "Caribbean · chef variation",
    "family": "Fruit",
    "heat": "Hot",
    "photoId": "orange",
    "source": "https://caribbeanpot.com/grilled-caribbean-pineapple-peppersauce/",
    "description": "Grilled pineapple adds roasted sweetness to a Scotch bonnet sauce.",
    "recipe": {
      "pineapple": 48,
      "scotch": 17,
      "vinegar": 20,
      "water": 9,
      "garlic": 3,
      "lime": 2,
      "salt": 1
    },
    "method": "Chop the prepared ingredients. Blend, then simmer gently in a covered pan, stirring until the fresh peppers and garlic soften. Cool before tasting; use a ventilated kitchen and avoid breathing chili steam. This is a fresh cooked adaptation, not an aged or fermented sauce.",
    "provenance": "Chef variation",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Grilled meats",
      "Vegetables"
    ]
  },
  {
    "id": "aji-verde",
    "name": "Ají Verde",
    "region": "Peruvian-style · chef adaptation",
    "family": "Creamy",
    "heat": "Medium",
    "photoId": "creamy",
    "source": "https://www.seriouseats.com/peruvian-style-grilled-chicken-with-green-sauce-recipe",
    "description": "A creamy green condiment for grilled chicken. The linked version uses jalapeño, cilantro and mayonnaise; it is a chef’s adaptation.",
    "recipe": {
      "jalapeno": 20,
      "cilantro": 20,
      "mayo": 35,
      "lime": 12,
      "water": 8,
      "garlic": 4,
      "salt": 1
    },
    "method": "Wash and prepare the fresh ingredients. Pulse with the remaining ingredients to your preferred texture. Transfer to a clean container and refrigerate promptly. Taste a cooled spoonful before adjusting.",
    "provenance": "Chef variation",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Grilled chicken",
      "Potatoes",
      "Vegetables"
    ]
  },
  {
    "id": "chili-garlic",
    "name": "Fresh Chili Garlic",
    "region": "Thai-inspired · OmaPit",
    "family": "Garlic",
    "heat": "Hot",
    "photoId": "garlic",
    "source": "https://hot-thai-kitchen.com/sriracha-hot-sauce/",
    "description": "A coarser, less sweet home variation on the chili-garlic profile. It is an OmaPit blend, not a named regional standard.",
    "recipe": {
      "redChili": 56,
      "garlic": 12,
      "vinegar": 20,
      "water": 9,
      "sugar": 2,
      "salt": 1
    },
    "method": "Chop the prepared ingredients. Blend, then simmer gently in a covered pan, stirring until the fresh peppers and garlic soften. Cool before tasting; use a ventilated kitchen and avoid breathing chili steam. This is a fresh cooked adaptation, not an aged or fermented sauce.",
    "provenance": "Original variation",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Grilled meats",
      "Vegetables"
    ]
  },
  {
    "id": "mustard-bonnet",
    "name": "Mustard Scotch Bonnet",
    "region": "Caribbean-inspired · OmaPit",
    "family": "Mustard",
    "heat": "Very hot",
    "photoId": "mustard",
    "source": "https://caribbeanpot.com/traditional-caribbean-pepper-sauce/",
    "description": "A mustard-forward variation on Scotch bonnet pepper sauce. This entry is an original blend, not a claimed authentic Bajan formula.",
    "recipe": {
      "scotch": 28,
      "mustard": 28,
      "vinegar": 24,
      "water": 13,
      "garlic": 4,
      "onion": 2,
      "salt": 1
    },
    "method": "Chop the prepared ingredients. Blend, then simmer gently in a covered pan, stirring until the fresh peppers and garlic soften. Cool before tasting; use a ventilated kitchen and avoid breathing chili steam. This is a fresh cooked adaptation, not an aged or fermented sauce.",
    "provenance": "Original variation",
    "note": "Regional recipes vary. This maker is an original home interpretation, not the source recipe.",
    "pairs": [
      "Grilled meats",
      "Vegetables"
    ]
  }
];
