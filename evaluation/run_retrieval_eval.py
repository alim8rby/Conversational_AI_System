"""Deterministic retrieval metric evaluator."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BENCHMARK_PATH=ROOT/"evaluation"/"retrieval_benchmark_v1.json"
def precision_at_k(retrieved,relevant,k):
    top=retrieved[:k]
    return sum(x in relevant for x in top)/len(top) if top else 0.0
def recall_at_k(retrieved,relevant,k):
    return sum(x in relevant for x in retrieved[:k])/len(relevant) if relevant else 0.0
def reciprocal_rank(retrieved,relevant):
    for rank,item in enumerate(retrieved,1):
        if item in relevant:return 1.0/rank
    return 0.0
def evaluate_case(case,k=3):
    retrieved=case["retrieved_memory_ids"]; relevant=set(case["relevant_memory_ids"])
    return {"case_id":case["case_id"],"precision_at_k":precision_at_k(retrieved,relevant,k),"recall_at_k":recall_at_k(retrieved,relevant,k),"mrr":reciprocal_rank(retrieved,relevant)}
def main():
    benchmark=json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))
    cases=[evaluate_case(c) for c in benchmark["cases"]]
    metrics={"precision_at_3":sum(c["precision_at_k"] for c in cases)/len(cases),"recall_at_3":sum(c["recall_at_k"] for c in cases)/len(cases),"mrr":sum(c["mrr"] for c in cases)/len(cases)}
    print(json.dumps({"benchmark_version":benchmark["benchmark_version"],"metrics":metrics,"cases":cases},indent=2))
if __name__=="__main__":main()
