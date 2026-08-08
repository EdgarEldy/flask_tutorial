from flask_tutorial.errors import ResourceNotFoundError
from flask_tutorial.extensions import db
from flask_tutorial.models.category import Category
from flask_tutorial.schemas.common import PageResponse


class CategoryService:
    def get_all(self, page: int, page_size: int) -> PageResponse[Category]:
        query = Category.query.order_by(Category.id)
        total_count = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return PageResponse(items=items, page=page, page_size=page_size, total_count=total_count)

    def get_by_id(self, category_id: int) -> Category:
        category = db.session.get(Category, category_id)
        if category is None:
            raise ResourceNotFoundError(f"Category {category_id} not found")
        return category

    def create(self, category_name: str) -> Category:
        category = Category(category_name=category_name)
        db.session.add(category)
        db.session.commit()
        return category

    def update(self, category_id: int, category_name: str) -> Category:
        category = self.get_by_id(category_id)
        category.category_name = category_name
        db.session.commit()
        return category

    def delete(self, category_id: int) -> None:
        category = self.get_by_id(category_id)
        db.session.delete(category)
        db.session.commit()
