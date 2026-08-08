from flask_tutorial.errors import BusinessRuleError, ResourceNotFoundError
from flask_tutorial.extensions import db
from flask_tutorial.models.customer import Customer
from flask_tutorial.schemas.common import PageResponse


class CustomerService:
    def get_all(self, page: int, page_size: int, search: str | None = None) -> PageResponse[Customer]:
        query = Customer.query
        if search:
            pattern = f"%{search}%"
            query = query.filter(
                db.or_(Customer.first_name.ilike(pattern), Customer.last_name.ilike(pattern))
            )
        query = query.order_by(Customer.id)
        total_count = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return PageResponse(items=items, page=page, page_size=page_size, total_count=total_count)

    def get_by_id(self, customer_id: int) -> Customer:
        customer = db.session.get(Customer, customer_id)
        if customer is None:
            raise ResourceNotFoundError(f"Customer {customer_id} not found")
        return customer

    def create(self, first_name: str, last_name: str, telephone: str, email: str, address: str) -> Customer:
        if self._email_taken(email):
            raise BusinessRuleError(f"Email {email} is already in use")
        customer = Customer(
            first_name=first_name, last_name=last_name, telephone=telephone, email=email, address=address
        )
        db.session.add(customer)
        db.session.commit()
        return customer

    def update(
        self, customer_id: int, first_name: str, last_name: str, telephone: str, email: str, address: str
    ) -> Customer:
        customer = self.get_by_id(customer_id)
        if self._email_taken(email, exclude_id=customer_id):
            raise BusinessRuleError(f"Email {email} is already in use")
        customer.first_name = first_name
        customer.last_name = last_name
        customer.telephone = telephone
        customer.email = email
        customer.address = address
        db.session.commit()
        return customer

    def delete(self, customer_id: int) -> None:
        customer = self.get_by_id(customer_id)
        db.session.delete(customer)
        db.session.commit()

    def _email_taken(self, email: str, exclude_id: int | None = None) -> bool:
        query = Customer.query.filter(Customer.email == email)
        if exclude_id is not None:
            query = query.filter(Customer.id != exclude_id)
        return db.session.query(query.exists()).scalar()
