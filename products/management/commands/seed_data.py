
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import Category, Product, ProductImage


class Command(BaseCommand):

    help = "Create sample categories, products, and product images."

    @transaction.atomic
    def handle(self, *args, **options):

        image_root = (
            Path(settings.BASE_DIR)
            / "products"
            / "seed_images"
        )

        # Parent categories
        parent_categories = [
            {
                "name": "Electronics",
                "slug": "electronics",
            },
            {
                "name": "Skin Care",
                "slug": "skin-care",
            },
        ]

        category_map = {}

        for data in parent_categories:
            category, created = Category.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "is_active": True,
                },
            )

            category_map[data["slug"]] = category

            if created:
                self.stdout.write(f"Category created: {category.name}")

        # Subcategories
        subcategories = [
            ("Laptops", "laptops", "electronics"),
            ("Smartphones", "smartphones", "electronics"),
            ("Audio", "audio", "electronics"),
            ("Accessories", "accessories", "electronics"),
            ("Smart Home", "smart-home", "electronics"),

            ("Cleansers", "cleansers", "skin-care"),
            ("Moisturizers", "moisturizers", "skin-care"),
            ("Serums", "serums", "skin-care"),
            ("Sunscreens", "sunscreens", "skin-care"),
            ("Face Masks", "face-masks", "skin-care"),
        ]

        for name, slug, parent_slug in subcategories:

            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "parent": category_map[parent_slug],
                    "is_active": True,
                },
            )

            category_map[slug] = category

            if created:
                self.stdout.write(f"Subcategory created: {name}")

        # Sample products
        products_data = [
            {
                "name": "MacBook Air M4",
                "category": "laptops",
                "description": "Apple MacBook Air powered by the M4 chip.",
                "price": 150000000,
                "stock": 8,
                "images": [
                    "electronics/laptops/macbook_air_m4.jpg",
                ],
            },
            {
                "name": "Dell XPS 15",
                "category": "laptops",
                "description": "Dell premium performance laptop.",
                "price": 180000000,
                "stock": 5,
                "images": [
                    "electronics/laptops/dell_xps_15.jpg",
                ],
            },
            {
                "name": "iPhone 17 Pro",
                "category": "smartphones",
                "description": "Apple iPhone 17 Pro smartphone.",
                "price": 140000000,
                "stock": 10,
                "images": [
                    "electronics/smartphones/iphone_17_pro_1.jpg",
                    "electronics/smartphones/iphone_17_pro_2.jpg",
                    "electronics/smartphones/iphone_17_pro_3.jpg",
                ],
            },
            {
                "name": "Samsung Galaxy S25",
                "category": "smartphones",
                "description": "Samsung Galaxy S25 smartphone.",
                "price": 95000000,
                "stock": 12,
                "images": [
                    "electronics/smartphones/samsung_s25_1.jpg",
                    "electronics/smartphones/samsung_s25_2.jpg",
                    "electronics/smartphones/samsung_s25_3.jpg",
                ],
            },
            {
                "name": "AirPods Pro",
                "category": "audio",
                "description": "Apple wireless noise-cancelling earbuds.",
                "price": 18000000,
                "stock": 15,
                "images": ["electronics/audio/airpods_pro.jpg"],
            },
            {
                "name": "Sony Wireless Headphones",
                "category": "audio",
                "description": "Sony wireless over-ear headphones.",
                "price": 22000000,
                "stock": 9,
                "images": ["electronics/audio/sony_headphones.jpg"],
            },
            {
                "name": "Logitech Wireless Mouse",
                "category": "accessories",
                "description": "Logitech wireless computer mouse.",
                "price": 3500000,
                "stock": 20,
                "images": ["electronics/accessories/logitech_mouse.jpg"],
            },
            {
                "name": "Mechanical Keyboard",
                "category": "accessories",
                "description": "Mechanical keyboard for everyday use.",
                "price": 6500000,
                "stock": 14,
                "images": ["electronics/accessories/mechanical_keyboard.jpg"],
            },
            {
                "name": "Amazon Echo Dot",
                "category": "smart-home",
                "description": "Smart speaker for a connected home.",
                "price": 7500000,
                "stock": 7,
                "images": ["electronics/smart_home/echo_dot.jpg"],
            },
            {
                "name": "Smart LED Light",
                "category": "smart-home",
                "description": "Smart LED light for home automation.",
                "price": 1800000,
                "stock": 25,
                "images": ["electronics/smart_home/smart_light.jpg"],
            },
            {
                "name": "CeraVe Foaming Cleanser",
                "category": "cleansers",
                "description": "Foaming facial cleanser.",
                "price": 1200000,
                "stock": 18,
                "images": ["skincare/cleansers/cerave_cleanser.jpg"],
            },
            {
                "name": "La Roche-Posay Cleanser",
                "category": "cleansers",
                "description": "Gentle facial cleansing product.",
                "price": 1600000,
                "stock": 12,
                "images": ["skincare/cleansers/la_roche_posay_cleanser.jpg"],
            },
            {
                "name": "Neutrogena Moisturizer",
                "category": "moisturizers",
                "description": "Hydrating daily face moisturizer.",
                "price": 1400000,
                "stock": 16,
                "images": ["skincare/moisturizers/neutrogena_moisturizer.jpg"],
            },
            {
                "name": "Laneige Moisturizer",
                "category": "moisturizers",
                "description": "Daily moisturizing skincare product.",
                "price": 2100000,
                "stock": 10,
                "images": ["skincare/moisturizers/laneige_moisturizer.jpg"],
            },
            {
                "name": "The Ordinary Serum",
                "category": "serums",
                "description": "Hyaluronic acid facial serum.",
                "price": 1700000,
                "stock": 20,
                "images": ["skincare/serums/ordinary_serum.jpg"],
            },
            {
                "name": "Vitamin C Serum",
                "category": "serums",
                "description": "Vitamin C skincare serum.",
                "price": 1900000,
                "stock": 11,
                "images": ["skincare/serums/vitamin_c_serum.jpg"],
            },
            {
                "name": "Bioderma Sunscreen",
                "category": "sunscreens",
                "description": "Daily sunscreen product.",
                "price": 1500000,
                "stock": 15,
                "images": ["skincare/sunscreens/bioderma_sunscreen.jpg"],
            },
            {
                "name": "La Roche-Posay Sunscreen",
                "category": "sunscreens",
                "description": "Facial sunscreen product.",
                "price": 2200000,
                "stock": 9,
                "images": ["skincare/sunscreens/la_roche_posay_sunscreen.jpg"],
            },
            {
                "name": "Mediheal Face Mask",
                "category": "face-masks",
                "description": "Sheet face mask for skincare routines.",
                "price": 450000,
                "stock": 30,
                "images": ["skincare/face_masks/mediheal_mask.jpg"],
            },
            {
                "name": "Innisfree Clay Mask",
                "category": "face-masks",
                "description": "Clay facial mask.",
                "price": 950000,
                "stock": 13,
                "images": ["skincare/face_masks/innisfree_mask.jpg"],
            },
        ]

        created_products = 0
        created_images = 0

        for data in products_data:

            product, created = Product.objects.get_or_create(
                name=data["name"],
                category=category_map[data["category"]],
                defaults={
                    "description": data["description"],
                    "price": data["price"],
                    "stock": data["stock"],
                    "is_active": True,
                },
            )

            if created:
                created_products += 1

            for position, relative_path in enumerate(data["images"]):

                if product.images.filter(sort_order=position).exists():
                    continue

                image_path = image_root / relative_path

                if not image_path.is_file():
                    raise FileNotFoundError(
                        f"Seed image not found: {image_path}"
                    )

                with image_path.open("rb") as image_file:

                    product_image = ProductImage(
                        product=product,
                        alt_text=f"{product.name} image {position + 1}",
                        is_primary=(position == 0),
                        sort_order=position,
                        image=File(
                            image_file,
                            name=image_path.name,
                        ),
                    )

                    # Run model and image validators before saving.
                    product_image.full_clean()
                    product_image.save()

                    created_images += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed completed: {created_products} products and "
                f"{created_images} images created."
            )
        )
