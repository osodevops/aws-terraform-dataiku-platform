

class Cluster:
    dss_client: object
    cluster: object
    cluster_id: str
    region: str
    cluster_type: str
    cluster_config: dict

    def __init__(self, dss_client, cluster_id, cluster_type, cluster_config):
        self.dss_client = dss_client
        self.cluster_id = cluster_id
        self.cluster_type = cluster_type
        self.cluster_config = cluster_config
    
    def create(self):
        self.cluster = self.dss_client.create_cluster(self.cluster_id, self.cluster_type, self.cluster_config)

    def attach(self):
        self.cluster.start()
    
    def exists(self, cluster_id):
        rest = [result for result in self.dss_client.list_clusters() if result['name'] == cluster_id]

        # return true if the cluster with cluster_id exists.
        if not rest:
            return False

        return True

    def attached(self):
        return self.cluster.get_status().get_raw()["state"] == "RUNNING"
