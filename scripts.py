
import os
import django
from django.contrib.auth import get_user_model

# Set the Django settings module (replace 'your_project.settings' with your actual settings module)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

# Initialize Django
django.setup()

import csv
import uuid
from django.contrib.auth.models import User  # Adjust if using a custom user model
from products.models import Product  # Replace 'myapp' with your actual app name

# Load sellers (assuming 'seller1' and 'seller2' exist in the database)
sellers = list(get_user_model().objects.filter(username__in=["seller3", "seller4"]))

with open("GROCERY_MOCK_DATA.csv", newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for index, row in enumerate(reader):
        seller = sellers[index % 2]  # Alternate between seller1 and seller2
        price = float(row['price'].replace('$', ''))  # Convert price to float
        description = row['description'] if row['description'] else "description"

        Product.objects.create(
            id=uuid.uuid4(),
            name=row['name'],
            description=description,
            price=price,
            stock=int(row['stock']),
            discount_percentage=float(row['discount_percentage']),
            sold_by=seller,
            category='GI'
        )
