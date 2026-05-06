package canary

default allow := false
default deny_reasons := []

deny_reasons := reasons if {
    reasons := [msg |
        checks := [
            [input.error_rate > data.thresholds.max_error_rate,
             sprintf("Error rate (%.2f%%) exceeds maximum (1.00%%)", [input.error_rate * 100])],
            [input.p99_latency_ms > data.thresholds.max_p99_latency_ms,
             sprintf("P99 latency (%.0fms) exceeds maximum (500ms)", [input.p99_latency_ms])]
        ]
        check := checks[_]
        check[0] == true
        msg := check[1]
    ]
}

allow if {
    count(deny_reasons) == 0
}

decision := {
    "allow": allow,
    "reasons": deny_reasons
}