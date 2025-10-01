import pandas as pd
import pytest
from tablefaker.tablefaker import TableFaker

def test_zipf_top10_share_exceeds_uniform(tmp_path):
    """Zipf distribution should concentrate more selections in top keys than uniform."""
    cfg = "tests/test_yaml_configs/distributions.yaml"
    tf = TableFaker()
    dfs = tf.to_pandas(cfg)
    uni = dfs["orders_uniform"]["customer_id"].value_counts(normalize=True).sort_values(ascending=False)
    zipf = dfs["orders_zipf"]["customer_id"].value_counts(normalize=True).sort_values(ascending=False)

    top10_uni = uni.head(10).sum()
    top10_zipf = zipf.head(10).sum()

    assert top10_zipf > top10_uni, "Zipf top-10 share should be greater than uniform top-10 share"

def test_weighted_parent_correlates_with_weights(tmp_path):
    """Weighted_parent should favor parents with higher weight values (rating 5 > 4 > 3)."""
    cfg = "tests/test_yaml_configs/distributions.yaml"
    tf = TableFaker()
    dfs = tf.to_pandas(cfg)
    customers = dfs["customers"].set_index("customer_id")
    orders_w = dfs["orders_weighted"]

    counts = orders_w["customer_id"].value_counts()
    # map customer_id -> rating
    rating_counts = {}
    for cid, cnt in counts.items():
        rating = customers.loc[cid, "rating"]
        rating_counts.setdefault(rating, []).append(cnt)

    # compute average selections per customer for each rating
    avg_by_rating = {r: (sum(vals)/len(vals)) for r, vals in rating_counts.items()}

    # Expect higher rating -> higher average selection given weights {"5":3,"4":2,"3":1}
    assert avg_by_rating.get(5, 0) >= avg_by_rating.get(4, 0)
    assert avg_by_rating.get(4, 0) >= avg_by_rating.get(3, 0)

def test_distributions_are_deterministic_with_seed(tmp_path):
    """With a fixed seed in the YAML the distributions should be deterministic across runs."""
    cfg = "tests/test_yaml_configs/distributions.yaml"
    tf1 = TableFaker()
    dfs1 = tf1.to_pandas(cfg)
    tf2 = TableFaker()
    dfs2 = tf2.to_pandas(cfg)

    for tbl in ["orders_uniform", "orders_zipf", "orders_weighted"]:
        csv1 = dfs1[tbl].to_csv(index=False)
        csv2 = dfs2[tbl].to_csv(index=False)
        assert csv1 == csv2