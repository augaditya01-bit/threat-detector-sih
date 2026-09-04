"""
STEP 1: Generate a synthetic network-traffic dataset.

Why this file exists:
Real datasets like CICIDS2017 need a manual download-request form,
which takes time to get approved. This script creates a FAKE but
realistically-shaped dataset with the same idea (flow features +
a label), so you can build and test your entire pipeline TODAY.

Once your real CICIDS2017 CSV arrives, you just point the other
scripts at that file instead -- the code doesn't change.

Run this file first. It creates: data/traffic.csv
"""

import numpy as np
import pandas as pd

np.random.seed(42)

def make_benign(n):
    """Normal traffic: moderate, fairly random packet behavior."""
    return pd.DataFrame({
        "flow_duration": np.random.normal(500, 150, n).clip(1, None),
        "total_fwd_packets": np.random.poisson(15, n),
        "total_bwd_packets": np.random.poisson(15, n),
        "flow_bytes_per_sec": np.random.normal(2000, 500, n).clip(1, None),
        "flow_packets_per_sec": np.random.normal(20, 5, n).clip(1, None),
        "syn_flag_count": np.random.poisson(1, n),
        "src_ip_entropy": np.random.normal(3.0, 0.5, n).clip(0, None),
        "avg_iat": np.random.normal(200, 50, n).clip(1, None),        # avg time between packets (ms)
        "iat_std": np.random.normal(80, 20, n).clip(1, None),         # jitter/burstiness
        "label": "BENIGN",
    })

def make_syn_flood(n):
    """SYN flood: huge number of SYNs, very high packet rate, short duration."""
    return pd.DataFrame({
        "flow_duration": np.random.normal(20, 10, n).clip(1, None),
        "total_fwd_packets": np.random.poisson(500, n),
        "total_bwd_packets": np.random.poisson(2, n),
        "flow_bytes_per_sec": np.random.normal(500, 100, n).clip(1, None),
        "flow_packets_per_sec": np.random.normal(4000, 800, n).clip(1, None),
        "syn_flag_count": np.random.poisson(400, n),
        "src_ip_entropy": np.random.normal(7.5, 0.5, n).clip(0, None),  # many spoofed random sources
        "avg_iat": np.random.normal(2, 1, n).clip(0.1, None),
        "iat_std": np.random.normal(1, 0.5, n).clip(0.1, None),
        "label": "SYN_FLOOD",
    })

def make_udp_amplification(n):
    """UDP amplification: massive bytes/sec, few large response packets."""
    return pd.DataFrame({
        "flow_duration": np.random.normal(100, 40, n).clip(1, None),
        "total_fwd_packets": np.random.poisson(10, n),
        "total_bwd_packets": np.random.poisson(300, n),
        "flow_bytes_per_sec": np.random.normal(50000, 8000, n).clip(1, None),
        "flow_packets_per_sec": np.random.normal(1500, 300, n).clip(1, None),
        "syn_flag_count": np.random.poisson(0, n),
        "src_ip_entropy": np.random.normal(6.5, 0.5, n).clip(0, None),
        "avg_iat": np.random.normal(5, 2, n).clip(0.1, None),
        "iat_std": np.random.normal(3, 1, n).clip(0.1, None),
        "label": "UDP_AMPLIFICATION",
    })

def make_botnet_beacon(n):
    """Botnet C2: very regular timing (low jitter), small periodic packets."""
    return pd.DataFrame({
        "flow_duration": np.random.normal(3600, 200, n).clip(1, None),  # long-lived connection
        "total_fwd_packets": np.random.poisson(60, n),
        "total_bwd_packets": np.random.poisson(60, n),
        "flow_bytes_per_sec": np.random.normal(150, 30, n).clip(1, None),  # small, quiet traffic
        "flow_packets_per_sec": np.random.normal(1, 0.3, n).clip(0.1, None),
        "syn_flag_count": np.random.poisson(1, n),
        "src_ip_entropy": np.random.normal(1.0, 0.3, n).clip(0, None),   # talks to ~same address
        "avg_iat": np.random.normal(60000, 500, n).clip(1, None),        # checks in every ~60s, VERY regular
        "iat_std": np.random.normal(50, 10, n).clip(1, None),            # low jitter = the giveaway
        "label": "BOTNET_C2",
    })

def main():
    n_benign = 6000
    n_attack_each = 700

    df = pd.concat([
        make_benign(n_benign),
        make_syn_flood(n_attack_each),
        make_udp_amplification(n_attack_each),
        make_botnet_beacon(n_attack_each),
    ], ignore_index=True)

    # shuffle rows so attacks aren't grouped together (more realistic "stream" order)
    df = df.sample(frac=1, random_state=1).reset_index(drop=True)

    # simulate a timestamp column, spaced out to look like a live capture
    df["timestamp"] = pd.date_range("2026-09-04 09:00:00", periods=len(df), freq="200ms")

    df.to_csv("data/traffic.csv", index=False)
    print(f"Created data/traffic.csv with {len(df)} rows")
    print(df["label"].value_counts())

if __name__ == "__main__":
    main()