from src.dss_cluster import Cluster
from tests.mock_api_client import MockDssClient, MockCluster


def test_cluster():
    mock_client = MockDssClient()
    cluster_obj = Cluster(mock_client)
    assert True


def test_create():
    mock_client = MockDssClient()
    cluster_obj = Cluster(mock_client)

    cluster_obj.create("foo_cluster_id", "foo_cluster_type", "foo_config")
    assert MockDssClient.create_cluster.calls == 1
    MockDssClient.create_cluster.calls = 0
    assert type(cluster_obj.cluster).__name__ == "MockCluster"


def test_attach():
    mock_client = MockDssClient()
    cluster_obj = Cluster(mock_client)

    cluster_obj.create("foo_cluster_id", "foo_cluster_type", "foo_config")
    cluster_obj.attach()

    assert MockCluster.start.calls == 1
    MockCluster.start.calls = 0


def test_exists_true():
    mock_client = MockDssClient()
    cluster_obj = Cluster(mock_client)

    assert cluster_obj.exists('cluster_exists')
    assert not cluster_obj.exists('cluster_not_exists')


def test_attached():
    mock_client = MockDssClient()
    cluster_obj = Cluster(mock_client)

    cluster_obj.create("foo_cluster_id", "foo_cluster_type", "foo_config")
    assert not cluster_obj.attached()

    cluster_obj.attach()
    assert cluster_obj.attached()