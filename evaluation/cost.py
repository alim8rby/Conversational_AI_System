"""Optional token-cost calculation.

No provider price is hard-coded. Cost is only reported when explicit per-token
rates are supplied by the deployment environment.
"""

def estimate_cost(token_usage, input_cost_per_token=None, output_cost_per_token=None):
    if not token_usage:
        return None
    if input_cost_per_token is None or output_cost_per_token is None:
        return None
    prompt = token_usage.get("prompt_tokens")
    completion = token_usage.get("completion_tokens")
    if prompt is None or completion is None:
        return None
    return (
        prompt * input_cost_per_token
        + completion * output_cost_per_token
    )
