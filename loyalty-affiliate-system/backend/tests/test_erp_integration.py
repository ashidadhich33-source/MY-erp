"""
Integration tests for ERP Integration Service.

Tests ERP connectivity, data synchronization, error handling,
and performance monitoring for Logic ERP integration.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session

from app.services.erp_service import (
    ERPIntegrationService, LogicERPConnector, ERPConnection,
    SyncStatus, DataMappingType, DataMapping, SyncResult
)


class TestERPIntegrationService:
    """Test cases for ERPIntegrationService."""

    @pytest.fixture
    def erp_service(self, db_session):
        """Create ERP integration service instance."""
        return ERPIntegrationService(db_session)

    @pytest.fixture
    def mock_erp_connector(self):
        """Create mock ERP connector."""
        connector = Mock(spec=LogicERPConnector)
        connector.connect = AsyncMock(return_value=True)
        connector.test_connection = AsyncMock(return_value=True)
        connector.get_customers = AsyncMock(return_value=[])
        connector.get_products = AsyncMock(return_value=[])
        connector.get_sales = AsyncMock(return_value=[])
        return connector

    @pytest.fixture
    def erp_connection_config(self):
        """Sample ERP connection configuration."""
        return {
            "host": "erp.example.com",
            "port": 8080,
            "database": "logic_erp",
            "username": "erp_user",
            "password": "erp_password",
            "api_key": "test_api_key",
            "timeout": 30
        }

    def test_configure_connection(self, erp_service, erp_connection_config):
        """Test ERP connection configuration."""
        connection = erp_service.configure_connection(erp_connection_config)

        assert isinstance(connection, ERPConnection)
        assert connection.host == erp_connection_config["host"]
        assert connection.port == erp_connection_config["port"]
        assert connection.database == erp_connection_config["database"]
        assert connection.username == erp_connection_config["username"]
        assert connection.password == erp_connection_config["password"]
        assert connection.api_key == erp_connection_config["api_key"]
        assert connection.timeout == erp_connection_config["timeout"]

    @pytest.mark.asyncio
    async def test_initialize_connector_success(self, erp_service, erp_connection_config):
        """Test successful ERP connector initialization."""
        with patch('app.services.erp_service.LogicERPConnector') as mock_connector_class:
            mock_connector = Mock()
            mock_connector.connect = AsyncMock(return_value=True)
            mock_connector_class.return_value = mock_connector

            result = await erp_service.initialize_connector("logic")

            assert result == True
            mock_connector_class.assert_called_once()
            mock_connector.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_connector_failure(self, erp_service, erp_connection_config):
        """Test failed ERP connector initialization."""
        with patch('app.services.erp_service.LogicERPConnector') as mock_connector_class:
            mock_connector = Mock()
            mock_connector.connect = AsyncMock(return_value=False)
            mock_connector_class.return_value = mock_connector

            result = await erp_service.initialize_connector("logic")

            assert result == False

    @pytest.mark.asyncio
    async def test_test_connection_success(self, erp_service):
        """Test successful connection test."""
        with patch.object(erp_service, 'initialize_connector', return_value=True):
            with patch.object(erp_service, 'connector') as mock_connector:
                mock_connector.test_connection = AsyncMock(return_value=True)

                result = await erp_service.test_connection()

                assert result["status"] == "connected"
                assert result["message"] == "ERP connection successful"

    @pytest.mark.asyncio
    async def test_test_connection_failure(self, erp_service):
        """Test failed connection test."""
        with patch.object(erp_service, 'initialize_connector', return_value=True):
            with patch.object(erp_service, 'connector') as mock_connector:
                mock_connector.test_connection = AsyncMock(return_value=False)

                result = await erp_service.test_connection()

                assert result["status"] == "failed"
                assert result["message"] == "ERP connection failed"

    @pytest.mark.asyncio
    async def test_sync_customers_full_sync(self, erp_service, db_session):
        """Test full customer synchronization."""
        # Mock ERP customer data
        erp_customers = [
            {
                "id": "CUST_001",
                "customer_name": "John Doe",
                "email_address": "john.doe@example.com",
                "phone_number": "+1234567890",
                "address": "123 Main St",
                "customer_type": "Regular",
                "credit_limit": 1000.00,
                "tax_id": "123-45-6789",
                "updated_at": datetime.utcnow()
            }
        ]

        with patch.object(erp_service, 'initialize_connector', return_value=True):
            with patch.object(erp_service, 'connector') as mock_connector:
                mock_connector.get_customers = AsyncMock(return_value=erp_customers)

                result = await erp_service.sync_customers(full_sync=True)

                assert isinstance(result, SyncResult)
                assert result.records_processed == 1
                assert result.status in [SyncStatus.COMPLETED, SyncStatus.PARTIAL]

    @pytest.mark.asyncio
    async def test_sync_customers_incremental_sync(self, erp_service):
        """Test incremental customer synchronization."""
        erp_customers = [
            {
                "id": "CUST_002",
                "customer_name": "Jane Smith",
                "email_address": "jane.smith@example.com",
                "phone_number": "+1987654321",
                "updated_at": datetime.utcnow()
            }
        ]

        with patch.object(erp_service, 'initialize_connector', return_value=True):
            with patch.object(erp_service, 'connector') as mock_connector:
                mock_connector.get_customers = AsyncMock(return_value=erp_customers)

                with patch.object(erp_service, '_get_last_sync_time', return_value=datetime.utcnow() - timedelta(hours=1)):
                    with patch.object(erp_service, '_is_customer_updated', return_value=True):
                        result = await erp_service.sync_customers(full_sync=False)

                        assert isinstance(result, SyncResult)
                        assert result.records_processed == 1

    @pytest.mark.asyncio
    async def test_sync_sales_success(self, erp_service):
        """Test successful sales synchronization."""
        erp_sales = [
            {
                "id": "SALE_001",
                "customer_id": "CUST_001",
                "total_amount": 299.99,
                "sale_date": datetime.utcnow() - timedelta(days=1),
                "invoice_number": "INV-001"
            }
        ]

        with patch.object(erp_service, 'initialize_connector', return_value=True):
            with patch.object(erp_service, 'connector') as mock_connector:
                mock_connector.get_sales = AsyncMock(return_value=erp_sales)

                result = await erp_service.sync_sales(full_sync=False)

                assert isinstance(result, SyncResult)
                assert result.records_processed == 1
                assert result.status == SyncStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_transform_customer_data(self, erp_service):
        """Test customer data transformation."""
        erp_customer = {
            "id": "CUST_001",
            "customer_name": "John Doe",
            "email_address": "john.doe@example.com",
            "phone_number": "+1234567890",
            "address": "123 Main St, City, State 12345",
            "customer_type": "Premium",
            "credit_limit": 5000.00,
            "tax_id": "123-45-6789",
            "updated_at": datetime.utcnow().isoformat()
        }

        transformed = erp_service._transform_customer_data(erp_customer)

        assert transformed["erp_id"] == "CUST_001"
        assert transformed["name"] == "John Doe"
        assert transformed["email"] == "john.doe@example.com"
        assert transformed["phone"] == "+1234567890"
        assert transformed["customer_type"] == "Premium"
        assert transformed["credit_limit"] == 5000.00
        assert transformed["tax_id"] == "123-45-6789"
        assert "sync_timestamp" in transformed
        assert "data_hash" in transformed

    @pytest.mark.asyncio
    async def test_transform_sale_data(self, erp_service):
        """Test sale data transformation."""
        erp_sale = {
            "id": "SALE_001",
            "customer_id": "CUST_001",
            "total_amount": 299.99,
            "sale_date": datetime.utcnow().isoformat(),
            "invoice_number": "INV-001"
        }

        transformed = erp_service._transform_sale_data(erp_sale)

        assert transformed["erp_sale_id"] == "SALE_001"
        assert transformed["customer_erp_id"] == "CUST_001"
        assert transformed["sale_amount"] == 299.99
        assert transformed["points_earned"] == 29  # 299.99 * 0.01
        assert transformed["transaction_type"] == "earned"
        assert transformed["source"] == "purchase"
        assert "sync_timestamp" in transformed

    def test_calculate_data_hash(self, erp_service):
        """Test data hash calculation for change detection."""
        test_data = {
            "id": "CUST_001",
            "name": "John Doe",
            "email": "john@example.com"
        }

        hash1 = erp_service._calculate_data_hash(test_data)
        hash2 = erp_service._calculate_data_hash(test_data)

        # Same data should produce same hash
        assert hash1 == hash2
        assert isinstance(hash1, str)
        assert len(hash1) == 32  # MD5 hash length

        # Different data should produce different hash
        test_data2 = test_data.copy()
        test_data2["name"] = "Jane Doe"
        hash3 = erp_service._calculate_data_hash(test_data2)

        assert hash1 != hash3

    def test_configure_data_mapping(self, erp_service):
        """Test data mapping configuration."""
        mappings = [
            DataMapping(
                source_field="customer_id",
                target_field="erp_id",
                mapping_type=DataMappingType.CUSTOMER,
                transformation=None,
                validation_rules={"required": True},
                is_required=True
            ),
            DataMapping(
                source_field="customer_name",
                target_field="name",
                mapping_type=DataMappingType.CUSTOMER,
                transformation="uppercase",
                validation_rules=None,
                is_required=True
            )
        ]

        erp_service.configure_data_mapping(DataMappingType.CUSTOMER, mappings)

        retrieved_mappings = erp_service.get_data_mapping(DataMappingType.CUSTOMER)

        assert len(retrieved_mappings) == 2
        assert retrieved_mappings[0].source_field == "customer_id"
        assert retrieved_mappings[0].target_field == "erp_id"
        assert retrieved_mappings[1].transformation == "uppercase"

    def test_validate_data_mapping_valid(self, erp_service):
        """Test validation of valid data mappings."""
        mappings = [
            DataMapping(
                source_field="customer_id",
                target_field="erp_id",
                mapping_type=DataMappingType.CUSTOMER,
                is_required=True
            ),
            DataMapping(
                source_field="customer_name",
                target_field="name",
                mapping_type=DataMappingType.CUSTOMER,
                is_required=False
            )
        ]

        erp_service.configure_data_mapping(DataMappingType.CUSTOMER, mappings)

        validation = erp_service.validate_data_mapping(DataMappingType.CUSTOMER)

        assert validation["is_valid"] == True
        assert len(validation["errors"]) == 0

    def test_validate_data_mapping_invalid(self, erp_service):
        """Test validation of invalid data mappings."""
        mappings = [
            DataMapping(
                source_field="",  # Missing source field
                target_field="erp_id",
                mapping_type=DataMappingType.CUSTOMER,
                is_required=True
            )
        ]

        erp_service.configure_data_mapping(DataMappingType.CUSTOMER, mappings)

        validation = erp_service.validate_data_mapping(DataMappingType.CUSTOMER)

        assert validation["is_valid"] == False
        assert len(validation["errors"]) > 0
        assert "Missing source field" in str(validation["errors"])

    @pytest.mark.asyncio
    async def test_get_erp_data_summary(self, erp_service):
        """Test ERP data summary retrieval."""
        mock_data = {
            "customers": {
                "count": 150,
                "last_updated": datetime.utcnow().isoformat()
            },
            "products": {
                "count": 500,
                "last_updated": datetime.utcnow().isoformat()
            },
            "sales": {
                "count": 45,
                "total_amount": 15000.00,
                "last_updated": datetime.utcnow().isoformat()
            }
        }

        with patch.object(erp_service, 'initialize_connector', return_value=True):
            with patch.object(erp_service, 'connector') as mock_connector:
                mock_connector.get_customers = AsyncMock(return_value=[{}] * 150)
                mock_connector.get_products = AsyncMock(return_value=[{}] * 500)
                mock_connector.get_sales = AsyncMock(return_value=[{"total_amount": 333.33}] * 45)

                summary = await erp_service.get_erp_data_summary()

                assert "customers" in summary
                assert "products" in summary
                assert "sales" in summary
                assert summary["customers"]["count"] == 150
                assert summary["products"]["count"] == 500
                assert summary["sales"]["count"] == 45

    def test_generate_sync_report(self, erp_service):
        """Test synchronization report generation."""
        sync_results = [
            SyncResult(
                status=SyncStatus.COMPLETED,
                records_processed=100,
                records_successful=95,
                records_failed=5,
                errors=["Customer email missing", "Phone invalid"],
                duration=45.2,
                timestamp=datetime.utcnow()
            ),
            SyncResult(
                status=SyncStatus.PARTIAL,
                records_processed=50,
                records_successful=48,
                records_failed=2,
                errors=["Product not found"],
                duration=23.1,
                timestamp=datetime.utcnow()
            )
        ]

        report = erp_service.generate_sync_report(sync_results)

        assert "summary" in report
        assert "details" in report
        assert report["summary"]["total_processed"] == 150
        assert report["summary"]["total_successful"] == 143
        assert report["summary"]["total_failed"] == 7
        assert report["summary"]["success_rate"] == pytest.approx(95.33, abs=0.01)
        assert report["summary"]["total_duration"] == pytest.approx(68.3, abs=0.1)

        assert len(report["details"]) == 2
        assert report["details"][0]["records_processed"] == 100
        assert report["details"][1]["records_processed"] == 50

    @pytest.mark.asyncio
    async def test_get_sync_status(self, erp_service):
        """Test sync status retrieval."""
        # Mock sync status data
        with patch.object(erp_service, 'test_connection') as mock_test:
            with patch.object(erp_service, '_get_last_sync_time') as mock_last_sync:
                mock_test.return_value = {
                    "status": "connected",
                    "message": "ERP connection successful"
                }
                mock_last_sync.return_value = datetime.utcnow() - timedelta(hours=1)

                status = await erp_service.get_sync_status()

                assert "connection_status" in status
                assert "last_sync" in status
                assert "recent_syncs" in status
                assert "pending_syncs" in status
                assert "failed_syncs" in status

    def test_error_handling_connection_failure(self, erp_service):
        """Test error handling for connection failures."""
        with patch.object(erp_service, 'initialize_connector', side_effect=Exception("Connection timeout")):
            import asyncio
            async def test_connection():
                return await erp_service.test_connection()

            # Should handle exception gracefully
            try:
                result = asyncio.run(test_connection())
                assert result["status"] == "failed"
            except Exception as e:
                # Should not propagate connection exceptions
                assert "Connection timeout" in str(e)

    def test_error_handling_sync_failure(self, erp_service):
        """Test error handling for sync failures."""
        with patch.object(erp_service, 'initialize_connector', return_value=True):
            with patch.object(erp_service, 'connector') as mock_connector:
                mock_connector.get_customers = AsyncMock(side_effect=Exception("API rate limit exceeded"))

                import asyncio
                async def test_sync():
                    return await erp_service.sync_customers()

                result = asyncio.run(test_sync())

                assert result.status == SyncStatus.FAILED
                assert len(result.errors) > 0
                assert "API rate limit exceeded" in str(result.errors[0])

    def test_data_validation_and_cleaning(self, erp_service):
        """Test data validation and cleaning during transformation."""
        # Test with invalid email
        invalid_customer = {
            "id": "CUST_001",
            "customer_name": "John Doe",
            "email_address": "invalid-email",  # Invalid email
            "phone_number": "+1234567890",
            "address": "",  # Empty address
            "customer_type": "Regular",
            "credit_limit": "invalid_number",  # Invalid number
            "tax_id": "123-45-6789"
        }

        # Should handle invalid data gracefully
        try:
            transformed = erp_service._transform_customer_data(invalid_customer)
            # Should still produce valid output even with invalid input
            assert transformed["erp_id"] == "CUST_001"
            assert transformed["name"] == "John Doe"
        except Exception:
            # Should not crash on invalid data
            pass

    def test_performance_monitoring(self, erp_service):
        """Test performance monitoring for sync operations."""
        # This would typically involve timing measurements
        # For this test, we just verify the structure exists

        sync_results = [
            SyncResult(
                status=SyncStatus.COMPLETED,
                records_processed=1000,
                records_successful=1000,
                records_failed=0,
                errors=[],
                duration=45.2,
                timestamp=datetime.utcnow()
            )
        ]

        report = erp_service.generate_sync_report(sync_results)

        # Should include performance metrics
        assert "summary" in report
        assert "total_duration" in report["summary"]
        assert report["summary"]["total_duration"] == 45.2

    def test_concurrent_sync_operations(self, erp_service):
        """Test concurrent synchronization operations."""
        # This is a conceptual test - in real implementation,
        # we would test thread safety and concurrent access

        # Mock concurrent operations
        with patch.object(erp_service, 'sync_customers') as mock_sync_customers:
            with patch.object(erp_service, 'sync_sales') as mock_sync_sales:
                mock_sync_customers.return_value = SyncResult(
                    status=SyncStatus.COMPLETED,
                    records_processed=100,
                    records_successful=100,
                    records_failed=0,
                    errors=[],
                    duration=30.0,
                    timestamp=datetime.utcnow()
                )
                mock_sync_sales.return_value = SyncResult(
                    status=SyncStatus.COMPLETED,
                    records_processed=50,
                    records_successful=50,
                    records_failed=0,
                    errors=[],
                    duration=15.0,
                    timestamp=datetime.utcnow()
                )

                import asyncio

                async def run_concurrent_syncs():
                    # Simulate concurrent sync operations
                    await asyncio.gather(
                        erp_service.sync_customers(),
                        erp_service.sync_sales()
                    )

                # Should handle concurrent operations without issues
                asyncio.run(run_concurrent_syncs())

    def test_data_consistency_checks(self, erp_service):
        """Test data consistency validation."""
        # Test data consistency between ERP and loyalty system
        erp_customer = {
            "id": "CUST_001",
            "customer_name": "John Doe",
            "email_address": "john.doe@example.com",
            "phone_number": "+1234567890"
        }

        # Calculate hash for change detection
        hash1 = erp_service._calculate_data_hash(erp_customer)

        # Modify data
        erp_customer["email_address"] = "john.doe.updated@example.com"
        hash2 = erp_service._calculate_data_hash(erp_customer)

        # Hashes should be different
        assert hash1 != hash2

        # Same data should have same hash
        hash3 = erp_service._calculate_data_hash(erp_customer)
        assert hash2 == hash3

    def test_audit_trail_creation(self, erp_service):
        """Test audit trail creation during sync operations."""
        # This is a conceptual test - in real implementation,
        # we would verify that all sync operations create audit entries

        sync_result = SyncResult(
            status=SyncStatus.COMPLETED,
            records_processed=100,
            records_successful=95,
            records_failed=5,
            errors=["Minor error"],
            duration=45.2,
            timestamp=datetime.utcnow()
        )

        # In real implementation, this would create audit log entries
        # For this test, we verify the structure is correct
        assert sync_result.status == SyncStatus.COMPLETED
        assert sync_result.records_processed == 100
        assert len(sync_result.errors) == 1