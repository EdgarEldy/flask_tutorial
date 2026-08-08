from flask_tutorial.services.order_service import OrderService


def test_compute_total_multiplies_quantity_by_unit_price():
    assert OrderService._compute_total(3, 9.99) == 29.97


def test_compute_total_with_zero_quantity_is_zero():
    assert OrderService._compute_total(0, 9.99) == 0
