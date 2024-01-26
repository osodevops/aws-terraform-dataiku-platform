variable "copy_tags" {
  description = "Deterime if the snapshot tags should be copied"
  type        = bool
  default     = true
}

variable "enable_policy" {
  description = "Whether to enable the policy"
  type        = bool
  default     = true
}

variable "resource_type" {
  description = "resource type can be VOLUME or INSTANCE."
  type        = string
  default     = ""
}

variable "retain_snapshot_count" {
  description = "The number of snapshots for DLM to retain"
  type        = number
  default     = 7
}

variable "schedule_name" {
  description = "The name of the lifecycle policy."
  type        = string
}

variable "snapshot_interval" {
  description = "The create rule interval."
  type        = number
  default     = 24
}

variable "snapshot_time" {
  description = "When should the snapshot policy be evaluated"
  type        = string
  default     = "23:45"
}

variable "target_instance_tag" {
  description = "Map of tags to value that select instances for snapshot"
  type = map(string)
  default = {
    DssSnapshot = "true"
  }
}
