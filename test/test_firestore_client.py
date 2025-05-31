from src.firestore_client import FirestoreClient
from unittest.mock import patch, MagicMock

def test_firestore_client_init_sets_db():
    with patch("src.firestore_client.firestore.Client") as MockClient:
        mock_instance = MockClient.return_value
        client = FirestoreClient("testcoll")
        assert client.db == mock_instance

def test_get_document_calls_collection_document():
    with patch("src.firestore_client.firestore.Client") as MockClient:
        mock_db = MockClient.return_value
        mock_collection = MagicMock()
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value.exists = True
        mock_doc_ref.get.return_value.to_dict.return_value = {"id": "1"}
        mock_collection.document.return_value = mock_doc_ref
        mock_db.collection.return_value = mock_collection

        client = FirestoreClient("testcoll")
        doc = client.get_document("1")
        assert doc == {"id": "1"}
        mock_db.collection.assert_called_with("testcoll")
        mock_collection.document.assert_called_with("1")

def test_add_document_calls_collection_add():
    with patch("src.firestore_client.firestore.Client") as MockClient:
        mock_db = MockClient.return_value
        mock_collection = MagicMock()
        mock_collection.add.return_value = (MagicMock(id="123"), None)
        mock_db.collection.return_value = mock_collection

        client = FirestoreClient("testcoll")
        doc_id = client.add_document({"foo": "bar"})
        assert doc_id == "123"
        mock_db.collection.assert_called_with("testcoll")
        mock_collection.add.assert_called_with({"foo": "bar"})
