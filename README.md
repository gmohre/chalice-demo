# chalice-demo
Chalice Card Generator
## Features

### Status Endpoint GET
/card

Returns a dictionary containing a status message, a card json url, and an image url

### Card Generator Endpoint POST
/card/<key>

Searches the ScryFall api for a card with the name <key>. Saves the base64-encoded image provided in the raw payload to a static location. Writes to a static JSON file with card data and image location.

### Card Renderer
/custom-cards/Card_Template.html

Renders an custom version of the mtg-card-html template (https://github.com/ronniemon/mtg-card-html). Loads static JSON file containing card data and image location.
