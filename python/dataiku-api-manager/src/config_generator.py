class ConfigGenerator:
    # Class to generate all config that is plugged directly into DSS

    def __init__(self):
        pass

    @staticmethod
    def containerized_execution(base_image: str, namespace: str, cluster_id: str, registry_host: str):
        return [{
            'allowedGroups': [],
            'baseImage': f"{registry_host}/{base_image}",
            'baseImageType': 'EXEC',
            'createNamespace': True,
            'dockerNetwork': 'host',
            'dockerResources': [],
            'dockerTLSVerify': False,
            'ensureNamespaceCompliance': False,
            'hostPathVolumes': [],
            'isFinal': False,
            'kubernetesNamespace': namespace,
            'kubernetesResources': {'cpuLimit': -1.0,
                                    'cpuRequest': -1.0,
                                    'customLimits': [],
                                    'customRequests': [],
                                    'memLimitMB': -1,
                                    'memRequestMB': -1},
            'name': cluster_id,
            'prePushMode': 'ECR',
            'properties': [],
            'repositoryURL': registry_host,
            'type': 'KUBERNETES',
            'usableBy': 'ALL'
        }]

    @staticmethod
    def cluster(region, cluster_id):
        return {
            "config": {
                "connectionInfo": {
                    "mode": "INLINE",
                    "inlinedConfig": {
                        "region": region,
                    },
                    "inlinedPluginConfig": {}
                },
                "clusterId": cluster_id
            }
        }

    @staticmethod
    def cgroups(cgroup_limits):
        return {
            "enabled": True,
            "hierarchiesMountPoint": "/sys/fs/cgroup",
            "mlKernels": {
                "targets": [
                    {
                        "cgroupPathTemplate": "memory/DSS/${user}/MLKernels"
                    }
                ]
            },
            "pythonRRecipes": {
                "targets": [
                    {
                        "cgroupPathTemplate": "memory/DSS/${user}/pythonRRecip"
                    }
                ]
            },
            "pythonRSparkRecipes": {
                "targets": [
                    {
                        "cgroupPathTemplate": "memory/DSS/${user}/pythonRSparkRecipes"
                    }
                ]
            },
            "jupyterKernels": {
                "targets": [
                    {
                        "cgroupPathTemplate": "memory/DSS/${user}/jupyterKernels"
                    }
                ]
            },
            "mlRecipes": {
                "targets": [
                    {
                        "cgroupPathTemplate": "memory/DSS/${user}/MLRecipes"
                    }
                ]
            },
            "pythonMacros": {
                "targets": [
                    {
                        "cgroupPathTemplate": "memory/DSS/${user}/pythonMacros"
                    }
                ]
            },
            "rmarkdownBuilders": {
                "targets": [
                    {
                        "cgroupPathTemplate": "memory/DSS/${user}/markdownBuilders"
                    }
                ]
            },
            "webappDevBackends": {
                "targets": [
                    {
                        "cgroupPathTemplate": "memory/DSS/${user}/webappDevBackends"
                    }
                ]
            },
            "eda": {
                "targets": [
                    {
                        "cgroupPathTemplate": "memory/DSS/${user}/eda"
                    }
                ]
            },
            "cgroups": [
                {
                    "cgroupPathTemplate": "memory/DSS",
                    "limits": cgroup_limits
                }
            ]
        }

    @staticmethod
    def api_infrastructure(namespace, registry_host, image_prefix, base_image):
        return {
        "prePushMode": "ECR",
        "k8sNamespace": namespace,
        "registryHost": registry_host,
        "imagesNamePrefix": image_prefix,
        "baseImageTag": f"{registry_host}/{base_image}",
        "defaultServiceExposition": {
            "type": "arbitrary_yaml",
            "params": {
                "yaml": """
apiVersion: v1
kind: Service
metadata:
  name: dku-${apiDeployerDeploymentId} # __exposed_service_id__
  namespace: dataiku
  labels:
${labels}
  annotations:
${annotations}

spec:
  selector:
${selector}
  type: NodePort
  ports:
  - port: ${deployment:port}
    targetPort: ${exposedPort}
    protocol: TCP
---

---
apiVersion: projectcontour.io/v1
kind: HTTPProxy
metadata:
  name:  dku-${apiDeployerDeploymentId} # __exposed_ingress_id__
  namespace: dataiku
  annotations:
    external-dns.alpha.kubernetes.io/hostname: ${deployment:hostname}.test.osodevops.io
    kubernetes.io/ingress.class: contour
spec:
  virtualhost:
    fqdn: ${deployment:hostname}.test.osodevops.io
  routes:
    - conditions:
        - prefix: /
      services:
        - name: dku-${apiDeployerDeploymentId}
          port: ${deployment:port}
"""
            }
        }
    }

    @staticmethod
    def project_infrastructure(dns_name, api_key, trust_certs):
        return {
            "automationNodeUrl": f"https://{dns_name}",
            "adminApiKey": api_key,
            "trustAllSSLCertificates": trust_certs
            }

    @staticmethod
    def saml(enabled, saml_idp_metadata, entity_id, acs_url):
        if enabled:
            return {
                'enabled': True,
                'protocol': "SAML",
                'remappingRules': [],
                'samlIDPMetadata': saml_idp_metadata,
                'samlSPParams': {
                    'entityId': entity_id,
                    'acsURL': acs_url,
                    'signRequests': False
                },
                'samlLoginAttribute': "NameID",
                'openIDParams': {
                    'scope': "openid email",
                    'claimKeyIdentifier': "email",
                    'useGlobalProxy': True,
                    'tokenEndpointAuthMethod': "CLIENT_SECRET_BASIC"
                    },
                'spnegoMode': "PREAUTH_KEYTAB",
                'spnegoStripRealm': True
            }
        else:
            return {
                'enabled': False,
            }
