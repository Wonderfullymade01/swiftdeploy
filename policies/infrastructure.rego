package infrastructure

import future.keywords.if

default allow := false
default deny_reasons := []

allow if {
    count(deny_reasons) == 0
}

deny_reasons := reasons if {
    reasons := [msg |
        input.disk_free_gb < data.thresholds.min_disk_free_gb
        msg := sprintf("Disk free (%.1fGB) is below minimum (%.1fGB)", [input.disk_free_gb, data.thresholds.min_disk_free_gb])
    ]
}

deny_reasons := reasons if {
    reasons := [msg |
        input.cpu_load > data.thresholds.max_cpu_load
        msg := sprintf("CPU load (%.2f) exceeds maximum (%.2f)", [input.cpu_load, data.thresholds.max_cpu_load])
    ]
}

decision := {
    "allow": allow,
    "reasons": deny_reasons
}