# common IAM roles
Various access dependencies can exist within Dataiku
This module defines security groups that can be assigned to nodes.

To allow access to a specific load-balancer:
- Create an SG using this module via the `security_group_target_names` parameter, and note the name given in the terraform output.
  - All SGs will be created as `<name>-access`
- Provide the name to the target node via `lb_allow_security_groups`. This will allow all connections from that security group in to the load balancer on the given HTTPS port.
- Provide the name to any source nodes via `additional_security_groups`. This will assign the new group to any instances launched via the Autoscaling Group.

For example, if the Design node needs access to the Automation node via the load-balancer, we would do the following:
- Within this wrapper, set `security_group_target_names` to `["automation"]` and execute Terraform. This will create an SG named `automation-access`.
- Within the `pre-prod/dss/automation` wrapper, set `lb_allow_security_groups` to `["automation-access"]`
- Within `pre-prod/dss/design`, set `additional_security_groups` to `["automation-access"]`
