import pytest

from flask_tutorial.errors import BusinessRuleError
from flask_tutorial.services.auth_service import AuthService


@pytest.fixture
def fake_email_service(mocker):
    return mocker.Mock()


@pytest.fixture
def service(fake_email_service):
    return AuthService(email_service=fake_email_service)


def test_register_raises_business_rule_error_on_duplicate_email(service, mocker):
    mocker.patch.object(AuthService, "_email_registered", return_value=True)

    with pytest.raises(BusinessRuleError):
        service.register("Ada", "Lovelace", "ada@example.com", "supersecret123")


def test_register_calls_email_service_with_a_confirmation_link(app, service, fake_email_service, mocker):
    mocker.patch.object(AuthService, "_email_registered", return_value=False)
    mocker.patch("flask_tutorial.services.auth_service.Role.query")
    mocker.patch("flask_tutorial.services.auth_service.db.session")

    with app.app_context():
        service.register("Ada", "Lovelace", "ada@example.com", "supersecret123")

    fake_email_service.send.assert_called_once()
    to, subject, html_body = fake_email_service.send.call_args[0]
    assert to == "ada@example.com"
    assert "confirm" in subject.lower()
    assert "token=" in html_body


def test_login_raises_when_account_is_not_enabled_before_checking_the_password(service, mocker):
    user = mocker.Mock(enabled=False, account_locked=False)
    mocker.patch.object(AuthService, "_find_user_by_email", return_value=user)
    check_password = mocker.patch("flask_tutorial.services.auth_service.check_password_hash")

    with pytest.raises(BusinessRuleError):
        service.login("ada@example.com", "wrong-or-right-does-not-matter")

    check_password.assert_not_called()


def test_login_raises_when_account_is_locked_before_checking_the_password(service, mocker):
    user = mocker.Mock(enabled=True, account_locked=True)
    mocker.patch.object(AuthService, "_find_user_by_email", return_value=user)
    check_password = mocker.patch("flask_tutorial.services.auth_service.check_password_hash")

    with pytest.raises(BusinessRuleError):
        service.login("ada@example.com", "wrong-or-right-does-not-matter")

    check_password.assert_not_called()


def test_forgot_password_does_not_raise_when_the_account_does_not_exist(service, mocker):
    mocker.patch.object(AuthService, "_find_user_by_email", return_value=None)
    issue_email = mocker.patch.object(AuthService, "_issue_password_reset_email")

    service.forgot_password("nobody@example.com")

    issue_email.assert_not_called()


def test_forgot_password_issues_a_reset_email_when_the_account_exists(service, mocker):
    user = mocker.Mock()
    mocker.patch.object(AuthService, "_find_user_by_email", return_value=user)
    issue_email = mocker.patch.object(AuthService, "_issue_password_reset_email")

    service.forgot_password("ada@example.com")

    issue_email.assert_called_once_with(user)
