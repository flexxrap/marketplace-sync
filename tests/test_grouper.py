from grouper import group_products

_PRODUCTS = [
    {"brand": "Lenovo", "category": "Ноутбуки", "sale_price_rub": 50000, "rating": 4.8},
    {"brand": "Lenovo", "category": "Ноутбуки", "sale_price_rub": 60000, "rating": 4.5},
    {"brand": "ASUS",   "category": "Ноутбуки", "sale_price_rub": 45000, "rating": 4.2},
    {"brand": "Lenovo", "category": "Планшеты", "sale_price_rub": 30000, "rating": 4.0},
]


def _find(groups, category, brand):
    return next(g for g in groups if g["category"] == category and g["brand"] == brand)


def test_correct_number_of_groups():
    groups = group_products(_PRODUCTS)
    assert len(groups) == 3  # Lenovo/Ноутбуки, ASUS/Ноутбуки, Lenovo/Планшеты


def test_price_aggregates():
    groups = group_products(_PRODUCTS)
    g = _find(groups, "Ноутбуки", "Lenovo")
    assert g["count"] == 2
    assert g["min_price_rub"] == 50000
    assert g["max_price_rub"] == 60000
    assert g["avg_price_rub"] == 55000.0


def test_rating_aggregate():
    groups = group_products(_PRODUCTS)
    g = _find(groups, "Ноутбуки", "Lenovo")
    assert g["avg_rating"] == round((4.8 + 4.5) / 2, 2)


def test_sorted_by_count_descending():
    groups = group_products(_PRODUCTS)
    counts = [g["count"] for g in groups]
    assert counts == sorted(counts, reverse=True)


def test_single_item_group():
    groups = group_products(_PRODUCTS)
    g = _find(groups, "Ноутбуки", "ASUS")
    assert g["count"] == 1
    assert g["min_price_rub"] == g["max_price_rub"] == g["avg_price_rub"] == 45000


def test_empty_input():
    assert group_products([]) == []
