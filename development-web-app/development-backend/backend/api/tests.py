"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import os

import django
import numpy as np

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.backend.settings')

# Initialize Django
django.setup()

from unittest.mock import Mock, patch
from factory import Factory, Faker, SubFactory
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from api.services.user_service import UserService
from api.services.user_privilege_service import UserPrivilegeService
from api.services.sku_order_quantity_prediction_service import SkuOrderQuantityPredictionService
from api.services.sku_metric_service import SkuMetricService
from api.services.ml_model_service import MLModelService
from api.services.inventory_optimization_service import InventoryOptimizationService
from api.services.distribution_optimization_service import DistributionOptimizationService
from api.services.user_erp_api_service import UserErpApiService
from api.models.login_user import LoginUser
from api.models.sku_metric import SkuMetric
from api.models.dtos.user_dto import UserDto
from api.models.ml_model import MLModel
from api.models.user_erp_api import UserErpApi
from api.models.inventory_optimization import InventoryOptimization
from api.models.sku_order_quantity_prediction import SkuOrderQuantityPrediction
from api.models.distribution_optimization import DistributionOptimization
from api.models.serializers.page_criteria_serializers import PageParams, SkuOrderQuantityPredictionCriteria, \
    InventoryOptimizationCriteria, DistributionOptimizationCriteria
from api.utils.enums import UserPrivileges
from api.utils.enums import Role
from api.utils.custom_exceptions import CustomLoggerException
from api.utils.constant_messages import USER_EMAIL_NOT_FOUND, USER_ID_NOT_FOUND
from api.utils.dto_converters import user_dto_to_login_user
from api.utils.constant_messages import INVALID_CREDENTIALS


# Factories for creating mock objects
class LoginUserFactory(Factory):
    class Meta:
        model = LoginUser

    id = Faker('random_int', min=1, max=1000)
    email = Faker('email')
    password = Faker('password')
    role = Role.USER.value


class UserDtoFactory(Factory):
    class Meta:
        model = UserDto

    id = Faker('random_int', min=1, max=1000)
    email = Faker('email')
    role = Role.USER.value
    is_active = True
    updated_at = None
    created_at = Faker('date_time_this_year')
    login_at = None
    privilege_names = ["USER_PRIVILEGE"]


class SkuMetricFactory(Factory):
    class Meta:
        model = SkuMetric

    sku_number = Faker('random_int', min=1, max=1000)
    is_weekend = Faker('pybool')
    is_holiday = Faker('pybool')
    mean_temperature = Faker('pyfloat', left_digits=2, right_digits=2, positive=True)
    rain = Faker('pybool')
    average_competition_price_external = Faker('pyfloat', left_digits=2, right_digits=2, positive=True)
    review_sentiment_score = Faker('pyfloat', left_digits=1, right_digits=2)
    review_sentiment_timestamp = Faker('date_time_this_year')
    trend_value = Faker('random_int', min=0, max=100)
    sku_order_record_id = Faker('random_int', min=1, max=1000)
    user = SubFactory(LoginUserFactory)


class SkuOrderQuantityPredictionFactory(Factory):
    class Meta:
        model = SkuOrderQuantityPrediction

    model_name = Faker('word')
    sku_number = Faker('random_int', min=1, max=1000)
    week_number = Faker('random_int', min=1, max=52)
    year_of_the_week = Faker('random_int', min=2022, max=2025)
    predicted_value = Faker('pyfloat', left_digits=1, right_digits=2, positive=True)
    mae = Faker('pyfloat', left_digits=1, right_digits=2, positive=True)
    mape = Faker('pyfloat', left_digits=1, right_digits=2, positive=True)
    sku_order_record = SubFactory(SkuMetricFactory)
    user = SubFactory(LoginUserFactory)


class MLModelFactory(Factory):
    class Meta:
        model = MLModel

    model_type = Faker('word')
    model_name = Faker('word')
    model_file = b"dummy model binary content"
    mape = Faker('pyfloat', left_digits=1, right_digits=2, positive=True)
    mae = Faker('pyfloat', left_digits=1, right_digits=2, positive=True)
    model_features = Faker('sentence')
    user = SubFactory(LoginUserFactory)


class InventoryOptimizationFactory(Factory):
    class Meta:
        model = InventoryOptimization

    sku_number = Faker('random_int', min=1, max=1000)
    order_quantity_q = Faker('pyfloat', left_digits=2, right_digits=2, positive=True)
    reorder_point_r = Faker('pyfloat', left_digits=2, right_digits=2, positive=True)
    holding_cost = Faker('pyfloat', left_digits=2, right_digits=2, positive=True)
    setup_transportation_cost = Faker('pyfloat', left_digits=2, right_digits=2, positive=True)
    stockout_cost = Faker('pyfloat', left_digits=2, right_digits=2, positive=True)
    total_cost = Faker('pyfloat', left_digits=3, right_digits=2, positive=True)
    order_frequency = Faker('pyfloat', left_digits=2, right_digits=2, positive=True)
    cycle_time = Faker('pyfloat', left_digits=2, right_digits=2, positive=True)
    is_custom = Faker('pybool')
    inventory_record_id = Faker('random_int', min=1, max=1000)
    user = SubFactory(LoginUserFactory)


class DistributionOptimizationFactory(Factory):
    class Meta:
        model = DistributionOptimization

    total_cost = Faker('pyfloat', left_digits=2, right_digits=2, positive=True)
    vehicle_id = Faker('random_int', min=1, max=1000)
    start_location_name = Faker('word')
    destination_location_name = Faker('word')
    units = Faker('random_int', min=1, max=100)
    # For the foreign key 'user', we'll simulate with an integer (assuming repository handles the conversion)
    user_id = Faker('random_int', min=1, max=1000)


class UserErpApiFactory(Factory):
    class Meta:
        model = UserErpApi

    id = Faker('random_int', min=1, max=1000)
    client_name = Faker('company')
    login_token_url = Faker('url')
    sku_order_url = Faker('url')
    inventory_params_url = Faker('url')
    distribution_routing_url = Faker('url')
    sku_order_latest_url = Faker('url')
    inventory_params_latest_url = Faker('url')
    token_username = Faker('user_name')
    token_password = Faker('password', length=12)
    user = SubFactory(LoginUserFactory)


# Unit Tests for UserService
class UserServiceTest(TestCase):
    def setUp(self):
        # Arrange
        self.user_repository = Mock()
        self.user_service = UserService(self.user_repository)

    def test_create_user_success(self):
        """
        Test creating a user successfully.
        """
        # Arrange
        user = LoginUserFactory(role=Role.ADMIN.value)
        self.user_repository.add_user.return_value = user

        # Act
        created_user = self.user_service.create_user(user)

        # Assert
        self.assertEqual(created_user.role, Role.ADMIN.value)
        self.assertEqual(created_user.email, user.email)
        self.user_repository.add_user.assert_called_once_with(user)

    def test_create_user_invalid_role(self):
        """
        Test creating a user with an invalid role raises a CustomLoggerException.
        """
        # Arrange
        user = LoginUserFactory(role="INVALID_ROLE")

        # Act & Assert
        with self.assertRaises(CustomLoggerException) as cm:
            self.user_service.create_user(user)
        self.assertIn(f"Invalid role: {user.role}", str(cm.exception))
        self.user_repository.add_user.assert_not_called()

    @patch('api.services.user_service.authenticate')
    def test_change_password_success(self, mock_auth):
        """
        Test changing a user's password successfully when the old password is correct.
        """
        # Arrange
        user = LoginUserFactory()
        old_password = "old_correct_password"
        new_password = "new_secure_password"

        # Make authenticate(...) return 'user' => means old password is valid
        mock_auth.return_value = user

        # Simulate a successful password change in the repository
        updated_user = LoginUserFactory(email=user.email, password=user.password)
        self.user_repository.change_user_password_by_email.return_value = updated_user

        # Act
        self.user_service.change_password(
            user_with_old_password=LoginUser(email=user.email, password=old_password),
            new_password=new_password
        )

        # Assert
        # 1) authenticate was called with the old password
        mock_auth.assert_called_once_with(email=user.email, password=old_password)
        # 2) repository was called to set the new password
        self.user_repository.change_user_password_by_email.assert_called_once_with(user.email, new_password)

    @patch('api.services.user_service.authenticate')
    def test_change_password_user_not_found(self, mock_auth):
        """
        Test changing a password when the user does not exist in the repository
        (simulate repository returning None).
        """
        # Arrange
        user = LoginUserFactory()
        old_password = "old_correct_password"
        new_password = "new_secure_password"

        # old password is correct => authenticate returns 'user'
        mock_auth.return_value = user

        # The repository indicates the user wasn't actually found/updated => None
        self.user_repository.change_user_password_by_email.return_value = None

        # Act & Assert
        with self.assertRaises(ValueError) as cm:
            self.user_service.change_password(
                user_with_old_password=LoginUser(email=user.email, password=old_password),
                new_password=new_password
            )
        self.assertIn(USER_EMAIL_NOT_FOUND.format(email=user.email), str(cm.exception))

        # Check calls
        mock_auth.assert_called_once_with(email=user.email, password=old_password)
        self.user_repository.change_user_password_by_email.assert_called_once_with(user.email, new_password)

    def test_update_user_success(self):
        """
        Test updating a user's information successfully.
        """
        # Arrange
        user_dto = UserDtoFactory()
        mock_user = user_dto_to_login_user(user_dto)
        self.user_repository.modify_user.return_value = mock_user

        # Act
        updated_user = self.user_service.update_user(mock_user)

        # Assert
        self.assertEqual(updated_user.email, user_dto.email)
        self.assertEqual(updated_user.role, user_dto.role)
        self.user_repository.modify_user.assert_called_once_with(mock_user)

    def test_update_user_failure(self):
        """
        Test updating a user with an invalid ID raises ValueError.
        """
        # Arrange
        user_dto = UserDtoFactory()
        user = user_dto_to_login_user(user_dto)
        # Simulate repository returning None to indicate user not found
        self.user_repository.modify_user.return_value = None

        # Act & Assert
        with self.assertRaises(ValueError) as cm:
            self.user_service.update_user(user)
        self.assertIn(USER_ID_NOT_FOUND.format(id=user.id), str(cm.exception))
        self.user_repository.modify_user.assert_called_once_with(user)

    def test_get_all_users_success(self):
        """Test retrieving all users with the role 'USER' successfully."""
        # Create mock users
        user1 = LoginUserFactory(role=Role.USER.value)
        user2 = LoginUserFactory(role=Role.USER.value)
        self.user_repository.find_all_users.return_value = [user1, user2]

        # Call the service method
        users = self.user_service.get_all_users()

        # Assert the results
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0].role, Role.USER.value)
        self.assertEqual(users[1].role, Role.USER.value)
        self.user_repository.find_all_users.assert_called_once()

    def test_get_all_users_empty(self):
        """Test retrieving users when no users with role 'USER' exist."""
        self.user_repository.find_all_users.return_value = []

        # Call the service method
        users = self.user_service.get_all_users()

        # Assert the results
        self.assertEqual(len(users), 0)
        self.user_repository.find_all_users.assert_called_once()

    def test_authenticate_user_inactive_or_invalid_credentials(self):
        """
        Test authenticate_user raises CustomLoggerException if user is inactive or invalid credentials.
        """
        # Arrange
        inactive_user = LoginUserFactory(is_active=False)
        # Patch the 'authenticate' function to return the inactive user
        with patch('api.services.user_service.authenticate', return_value=inactive_user):
            # Act & Assert
            with self.assertRaises(CustomLoggerException) as cm:
                self.user_service.authenticate_user(inactive_user)
            self.assertIn(INVALID_CREDENTIALS, str(cm.exception))
            self.user_repository.update_login_timestamp_by_email.assert_not_called()


# Unit Tests for UserPrivilegeService
class UserPrivilegeServiceTest(TestCase):
    def setUp(self):
        # Arrange
        self.user_privilege_repository = Mock()
        self.user_privilege_service = UserPrivilegeService(self.user_privilege_repository)
        self.admin_user = LoginUserFactory(role=Role.ADMIN.value)
        self.normal_user = LoginUserFactory(role=Role.USER.value)

    def test_assign_privileges_to_user_success(self):
        """
        Test assigning valid privileges to a user successfully.
        """
        # Arrange
        privileges = [UserPrivileges.ADMIN_PRIVILEGE.value, UserPrivileges.ROUTING.value]
        self.user_privilege_repository.assign_user_privileges.return_value = privileges

        # Act
        self.user_privilege_service.assign_privileges_to_user(self.admin_user, privileges)

        # Assert
        self.user_privilege_repository.assign_user_privileges.assert_called_once_with(self.admin_user, privileges)

    def test_assign_privileges_to_user_invalid_privilege(self):
        """
        Test assigning an invalid privilege raises a CustomLoggerException.
        """
        # Arrange
        privileges = ["INVALID_PRIVILEGE"]

        # Act & Assert
        with self.assertRaises(CustomLoggerException) as cm:
            self.user_privilege_service.assign_privileges_to_user(self.admin_user, privileges)

        self.assertIn("Privilege 'INVALID_PRIVILEGE' is not included in UserPrivilege enum list, not added.",
                      str(cm.exception))
        self.user_privilege_repository.assign_user_privileges.assert_not_called()

    def test_assign_admin_privilege_to_non_admin_user(self):
        """
        Test assigning admin privilege to a non-admin user raises a CustomLoggerException.
        """
        # Arrange
        privileges = [UserPrivileges.ADMIN_PRIVILEGE.value]

        # Act & Assert
        with self.assertRaises(CustomLoggerException) as cm:
            self.user_privilege_service.assign_privileges_to_user(self.normal_user, privileges)

        self.assertIn("Cannot assign admin privileges to a non-admin user.", str(cm.exception))
        self.user_privilege_repository.assign_user_privileges.assert_not_called()

    def test_get_privileges_for_user_success(self):
        """
        Test retrieving privileges for a user.
        """
        # Arrange
        privileges = [UserPrivileges.ROUTING.value, UserPrivileges.DEMAND_FORECASTING.value]
        self.user_privilege_repository.find_user_privileges_by_user_id.return_value = privileges

        # Act
        retrieved_privileges = self.user_privilege_service.get_privileges_for_user(self.normal_user)

        # Assert
        self.assertEqual(retrieved_privileges, privileges)
        self.user_privilege_repository.find_user_privileges_by_user_id.assert_called_once_with(self.normal_user.id)

    def test_update_privileges_for_user_success(self):
        """
        Test updating privileges for a user with valid new privileges.
        The repository method 'update_user_privileges' should return the final list.
        """
        # Arrange
        new_privileges = [UserPrivileges.ROUTING.value, UserPrivileges.DEMAND_FORECASTING.value]
        final_enabled = [UserPrivileges.ROUTING.value, UserPrivileges.DEMAND_FORECASTING.value]
        self.user_privilege_repository.update_user_privileges.return_value = final_enabled

        # Act
        result = self.user_privilege_service.update_privileges_for_user(self.normal_user, new_privileges)

        # Assert
        self.assertEqual(result, final_enabled)
        self.user_privilege_repository.update_user_privileges.assert_called_once_with(
            self.normal_user, new_privileges
        )

    def test_update_privileges_for_user_invalid_privilege(self):
        """
        Test updating privileges with an invalid privilege raises a CustomLoggerException.
        """
        # Arrange
        new_privileges = ["INVALID_PRIVILEGE"]

        # Act & Assert
        with self.assertRaises(CustomLoggerException) as cm:
            self.user_privilege_service.update_privileges_for_user(self.admin_user, new_privileges)
        self.assertIn("Privilege 'INVALID_PRIVILEGE' is not included in UserPrivilege enum list, not added.",
                      str(cm.exception))
        self.user_privilege_repository.update_user_privileges.assert_not_called()

    def test_update_privileges_for_user_assign_admin_privilege_to_non_admin(self):
        """
        Test updating privileges to include 'admin-privilege' for a non-admin user
        raises CustomLoggerException. The repository method should NOT be called.
        """
        # Arrange
        new_privileges = [UserPrivileges.ADMIN_PRIVILEGE.value]

        # Act & Assert
        with self.assertRaises(CustomLoggerException) as cm:
            self.user_privilege_service.update_privileges_for_user(self.normal_user, new_privileges)
        self.assertIn("Cannot assign admin privileges to a non-admin user.", str(cm.exception))
        self.user_privilege_repository.update_user_privileges.assert_not_called()


# Unit Tests for SkuOrderQuantityPredictionService
class SkuOrderQuantityPredictionServiceTest(TestCase):
    def setUp(self):
        """
        Setup the test case with a mocked repository and service instance.
        """
        # Arrange
        self.repository = Mock()
        self.service = SkuOrderQuantityPredictionService(self.repository)

    def test_get_all_predictions_success(self):
        """
        Test retrieving all SKU order quantity predictions that match the given criteria.
        """
        # Arrange: Create PageParams and Criteria instances using DRF serializer 'data' argument.
        page_params = PageParams(data={"page": 1, "page_size": 10})
        page_params.is_valid(raise_exception=True)
        criteria = SkuOrderQuantityPredictionCriteria(
            data={"model_name": "TestModel", "user_id": 123, "sku_number": 456}
        )
        criteria.is_valid(raise_exception=True)
        prediction_instance = SkuOrderQuantityPredictionFactory.build()
        predictions_list = [prediction_instance]
        self.repository.find_all_sku_order_quantity_predictions.return_value = predictions_list
        # Act
        result = self.service.get_all_predictions(page_params, criteria)
        # Assert
        self.assertEqual(result, predictions_list)
        self.repository.find_all_sku_order_quantity_predictions.assert_called_once_with(page_params, criteria)

    def test_create_sku_order_quantity_prediction(self):
        """
        Test that a new SKU order quantity prediction is stored correctly.
        """
        # Arrange
        prediction_instance = SkuOrderQuantityPredictionFactory.build()
        # Act
        self.service.create_sku_order_quantity_prediction(prediction_instance)
        # Assert
        self.repository.store_sku_order_quantity_prediction.assert_called_once_with(prediction_instance)

    def test_get_sku_order_quantity_prediction_by_record_id_success(self):
        """
        Test successfully retrieving a prediction by its record ID.
        """
        # Arrange
        record_id = 101
        prediction_instance = SkuOrderQuantityPredictionFactory.build()
        self.repository.find_sku_order_quantity_prediction_by_record_id.return_value = prediction_instance
        # Act
        result = self.service.get_sku_order_quantity_prediction_by_record_id(record_id)
        # Assert
        self.assertEqual(result, prediction_instance)
        self.repository.find_sku_order_quantity_prediction_by_record_id.assert_called_once_with(record_id)

    def test_get_sku_order_quantity_prediction_by_record_id_not_found(self):
        """
        Test that retrieving a prediction by a non-existent record ID raises ObjectDoesNotExist.
        """
        # Arrange
        record_id = 202
        self.repository.find_sku_order_quantity_prediction_by_record_id.side_effect = ObjectDoesNotExist
        # Act & Assert
        with self.assertRaises(ObjectDoesNotExist) as context:
            self.service.get_sku_order_quantity_prediction_by_record_id(record_id)
        self.assertIn(f"No SkuOrderQuantityPrediction found for sku_order_record_id={record_id}.",
                      str(context.exception))
        self.repository.find_sku_order_quantity_prediction_by_record_id.assert_called_once_with(record_id)

    def test_calculate_demand_parameters_no_predictions(self):
        """
        Test that when no predictions exist for a given SKU number, the service returns (None, None).
        """
        # Arrange
        sku_number = 789
        self.repository.find_sku_order_quantity_prediction_by_sku_number.return_value = []
        # Act
        result = self.service.calculate_demand_parameters(sku_number)
        # Assert
        self.assertEqual(result, (None, None))
        self.repository.find_sku_order_quantity_prediction_by_sku_number.assert_called_once_with(sku_number)

    def test_calculate_demand_parameters_with_valid_predictions(self):
        """
        Test computing demand parameters (lambda and sigma) when predictions exist.
        """
        # Arrange
        sku_number = 321
        predictions = [
            SkuOrderQuantityPredictionFactory.build(predicted_value=2.0),
            SkuOrderQuantityPredictionFactory.build(predicted_value=4.0),
            SkuOrderQuantityPredictionFactory.build(predicted_value=6.0)
        ]
        self.repository.find_sku_order_quantity_prediction_by_sku_number.return_value = predictions
        expected_lambda = np.mean([2.0, 4.0, 6.0])
        expected_sigma = np.std([2.0, 4.0, 6.0])
        # Act
        result = self.service.calculate_demand_parameters(sku_number)
        # Assert
        self.assertAlmostEqual(result[0], expected_lambda)
        self.assertAlmostEqual(result[1], expected_sigma)
        self.repository.find_sku_order_quantity_prediction_by_sku_number.assert_called_once_with(sku_number)

    def test_calculate_demand_parameters_with_zero_predictions(self):
        """
        Test that if all predictions are zero, the service defaults to (1.0, 1.0).
        """
        # Arrange
        sku_number = 654
        predictions = [
            SkuOrderQuantityPredictionFactory.build(predicted_value=0.0),
            SkuOrderQuantityPredictionFactory.build(predicted_value=0.0)
        ]
        self.repository.find_sku_order_quantity_prediction_by_sku_number.return_value = predictions
        # Act
        result = self.service.calculate_demand_parameters(sku_number)
        # Assert
        self.assertEqual(result, (1.0, 1.0))
        self.repository.find_sku_order_quantity_prediction_by_sku_number.assert_called_once_with(sku_number)


# Unit Tests for SkuMetricService
class SkuMetricServiceTest(TestCase):
    def setUp(self):
        # Arrange: Initialize the mocked repository and the service instance.
        self.repository = Mock()
        self.service = SkuMetricService(self.repository)

    def test_get_all_sku_order_record_ids_by_sku_number_success(self):
        """
        Test that get_all_sku_order_record_ids_by_sku_number returns a list of record IDs when available.
        """
        # Arrange
        sku_number = 123
        record_ids = [101, 102, 103]
        self.repository.find_all_sku_order_record_ids_by_sku_number.return_value = record_ids
        # Act
        result = self.service.get_all_sku_order_record_ids_by_sku_number(sku_number)
        # Assert
        self.assertEqual(result, record_ids)
        self.repository.find_all_sku_order_record_ids_by_sku_number.assert_called_once_with(sku_number)

    def test_get_all_sku_order_record_ids_by_sku_number_empty(self):
        """
        Test that get_all_sku_order_record_ids_by_sku_number returns an empty list when no record IDs are found.
        """
        # Arrange
        sku_number = 456
        self.repository.find_all_sku_order_record_ids_by_sku_number.return_value = []
        # Act
        result = self.service.get_all_sku_order_record_ids_by_sku_number(sku_number)
        # Assert
        self.assertEqual(result, [])
        self.repository.find_all_sku_order_record_ids_by_sku_number.assert_called_once_with(sku_number)

    def test_get_by_sku_order_record_id_found(self):
        """
        Test that get_by_sku_order_record_id returns a SkuMetric instance when found.
        """
        # Arrange
        sku_order_record_id = 789
        sku_metric_instance = SkuMetricFactory.build()
        self.repository.find_by_sku_order_record_id.return_value = sku_metric_instance
        # Act
        result = self.service.get_by_sku_order_record_id(sku_order_record_id)
        # Assert
        self.assertEqual(result, sku_metric_instance)
        self.repository.find_by_sku_order_record_id.assert_called_once_with(sku_order_record_id)

    def test_get_by_sku_order_record_id_not_found(self):
        """
        Test that get_by_sku_order_record_id returns None when no SkuMetric is found.
        """
        # Arrange
        sku_order_record_id = 890
        self.repository.find_by_sku_order_record_id.return_value = None
        # Act
        result = self.service.get_by_sku_order_record_id(sku_order_record_id)
        # Assert
        self.assertIsNone(result)
        self.repository.find_by_sku_order_record_id.assert_called_once_with(sku_order_record_id)


class MLModelServiceTest(TestCase):
    def setUp(self):
        # Arrange
        self.repository = Mock()
        self.service = MLModelService(self.repository)

    def test_get_trained_model_success(self):
        # Arrange
        user_id = 123
        model_type = "TestModel"
        ml_model_instance = MLModelFactory.build(user_id=user_id, model_type=model_type)
        self.repository.find_model_file_by_user_and_name.return_value = ml_model_instance
        # Act
        result = self.service.get_trained_model(user_id, model_type)
        # Assert
        self.assertEqual(result, ml_model_instance)
        self.repository.find_model_file_by_user_and_name.assert_called_once_with(user_id, model_type)

    def test_get_trained_model_not_found(self):
        # Arrange
        user_id = 456
        model_type = "NonExistentModel"
        self.repository.find_model_file_by_user_and_name.return_value = None
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.service.get_trained_model(user_id, model_type)
        self.assertIn("ML model not found in DB.", str(context.exception))
        self.repository.find_model_file_by_user_and_name.assert_called_once_with(user_id, model_type)


# Unit Tests for InventoryOptimizationService
class InventoryOptimizationServiceTest(TestCase):
    def setUp(self):
        # Arrange
        self.repository = Mock()
        self.service = InventoryOptimizationService(self.repository)

    def test_get_all_optimizations_success(self):
        # Arrange
        page_params = PageParams(data={"page": 1, "page_size": 10})
        page_params.is_valid(raise_exception=True)
        criteria = InventoryOptimizationCriteria(data={"user_id": 123, "inventory_record_id": 456})
        criteria.is_valid(raise_exception=True)
        optimization_instance = InventoryOptimizationFactory.build()
        optimizations_list = [optimization_instance]
        self.repository.find_all_inventory_optimizations.return_value = optimizations_list
        # Act
        result = self.service.get_all_optimizations(page_params, criteria)
        # Assert
        self.assertEqual(result, optimizations_list)
        self.repository.find_all_inventory_optimizations.assert_called_once_with(page_params, criteria)

    def test_create_inventory_optimization(self):
        # Arrange
        optimization_instance = InventoryOptimizationFactory.build()
        self.repository.store_inventory_optimization.return_value = optimization_instance
        # Act
        result = self.service.create_inventory_optimization(optimization_instance)
        # Assert
        self.assertEqual(result, optimization_instance)
        self.repository.store_inventory_optimization.assert_called_once_with(optimization_instance)


# Unit Tests for DistributionOptimizationService
class DistributionOptimizationServiceTest(TestCase):
    def setUp(self):
        # Arrange
        self.repository = Mock()
        self.service = DistributionOptimizationService(self.repository)

    def test_get_all_distribution_optimizations_success(self):
        # Arrange
        page_params = PageParams(data={"page": 1, "page_size": 10})
        page_params.is_valid(raise_exception=True)
        criteria = DistributionOptimizationCriteria(data={"user_id": 123, "vehicle_id": 456})
        criteria.is_valid(raise_exception=True)
        optimization_instance = DistributionOptimizationFactory.build()
        optimizations_list = [optimization_instance]
        self.repository.find_all_distribution_optimizations.return_value = optimizations_list
        # Act
        result = self.service.get_all_distribution_optimizations(page_params, criteria)
        # Assert
        self.assertEqual(result, optimizations_list)
        self.repository.find_all_distribution_optimizations.assert_called_once_with(page_params, criteria)

    def test_create_distribution_optimization(self):
        # Arrange
        optimization_instance = DistributionOptimizationFactory.build()
        self.repository.store_distribution_optimization.return_value = optimization_instance
        # Act
        result = self.service.create_distribution_optimization(optimization_instance)
        # Assert
        self.assertEqual(result, optimization_instance)
        self.repository.store_distribution_optimization.assert_called_once_with(optimization_instance)


# Unit Tests for UserErpApiService
class UserErpApiServiceTest(TestCase):
    def setUp(self):
        """
        Set up the test environment by mocking the repository and initializing the service.
        """
        # Mock repository
        self.user_erp_api_repository = Mock()
        self.user_erp_api_service = UserErpApiService(self.user_erp_api_repository)

    def test_get_user_erp_api_success(self):
        """
        Test retrieving an existing ERP API record successfully.
        """
        # Arrange
        user = LoginUserFactory()
        expected_record = UserErpApiFactory(user=user)
        self.user_erp_api_repository.find_user_erp_api_by_user_id.return_value = expected_record
        # Act
        result = self.user_erp_api_service.get_user_erp_api(user.id)
        # Assert
        self.assertEqual(result, expected_record)
        self.user_erp_api_repository.find_user_erp_api_by_user_id.assert_called_once_with(user.id)

    def test_get_user_erp_api_not_found(self):
        """
        Test retrieving an ERP API record for a non-existent user raises an exception.
        """
        # Arrange
        user_id = 9999  # Non-existent user
        self.user_erp_api_repository.find_user_erp_api_by_user_id.return_value = None
        # Act & Assert
        with self.assertRaises(CustomLoggerException) as e:
            self.user_erp_api_service.get_user_erp_api(user_id)
        self.assertIn(f"No ERP API record found for user_id={user_id}", str(e.exception))
        self.user_erp_api_repository.find_user_erp_api_by_user_id.assert_called_once_with(user_id)

    def test_create_or_update_user_erp_api_create_success(self):
        """
        Test creating a new ERP API record successfully.
        """
        # Arrange
        user = LoginUserFactory()
        new_record = UserErpApiFactory(user=user)
        self.user_erp_api_repository.store_or_update_user_erp_api_record.return_value = new_record
        # Act
        result = self.user_erp_api_service.create_or_update_user_erp_api(new_record)
        # Assert
        self.assertEqual(result, new_record)
        self.user_erp_api_repository.store_or_update_user_erp_api_record.assert_called_once_with(new_record)

    def test_create_or_update_user_erp_api_update_success(self):
        """
        Test updating an existing ERP API record successfully.
        """
        # Arrange
        user = LoginUserFactory()
        updated_record = UserErpApiFactory(user=user, client_name="Updated Client")
        self.user_erp_api_repository.store_or_update_user_erp_api_record.return_value = updated_record
        # Act
        result = self.user_erp_api_service.create_or_update_user_erp_api(updated_record)
        # Assert
        self.assertEqual(result.client_name, "Updated Client")
        self.user_erp_api_repository.store_or_update_user_erp_api_record.assert_called_once_with(updated_record)
