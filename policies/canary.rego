package canary

default allow := false
default deny_reasons := []

deny_reasons := reasons if {
    reasons := [msg |
        checks := [
            [input.error_rate > data.thresholds.max_error_rate,
             sprintf("Error rate exceeds maximum of 1.00%% (current: %.2f%%)", [input.error_rate * 100])],
            [input.p99_latency_ms > data.thresholds.max_p99_latency_ms,
             sprintf("P99 latency exceeds maximum of 500ms (current: %.0fms)", [input.p99_latency_ms])]
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