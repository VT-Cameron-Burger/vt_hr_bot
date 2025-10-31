#!/usr/bin/env python3
"""Aggregate OpenAI usage logs and produce daily totals + cost estimates.

Reads JSON-lines from `openai_usage.log` (one JSON object per line) and
produces a human-readable summary of tokens used per day and per model.

By default the script prints per-day totals and an overall summary. You
can optionally provide model cost rates with --rate to estimate USD cost
(e.g. --rate gpt-3.5-turbo=0.002 means $0.002 per 1k tokens).

Usage:
  python scripts/aggregate_openai_usage.py [--log FILE] [--rate MODEL=RATE] [--since YYYY-MM-DD] [--until YYYY-MM-DD]

Examples:
  python scripts/aggregate_openai_usage.py
  python scripts/aggregate_openai_usage.py --rate gpt-3.5-turbo=0.002 --rate gpt-4=0.03

Notes:
- The script is conservative: it expects each log line to be a JSON object
  with at least {"timestamp":..., "model":..., "usage": {"prompt_tokens":.., "completion_tokens":.., "total_tokens":..}}
- If usage fields are missing, that line is skipped.
"""

import argparse
import os
import json
from collections import defaultdict, Counter
from datetime import datetime, timezone

DEFAULT_LOG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'openai_usage.log')

# Default rate per 1k tokens (USD) — these are conservative placeholders.
# Prefer passing explicit --rate MODEL=RATE pairs for accuracy.
DEFAULT_RATES = {
    'gpt-3.5-turbo': 0.002,  # USD per 1k tokens (example)
    'gpt-4': 0.03,
    'gpt-4o-mini': 0.01,
}


def parse_args():
    p = argparse.ArgumentParser(description='Aggregate OpenAI usage log and estimate costs')
    p.add_argument('--log', default=DEFAULT_LOG, help='Path to openai_usage.log (JSON lines)')
    p.add_argument('--rate', action='append', default=[], help='Model rate as MODEL=USD_PER_1K, can be used multiple times')
    p.add_argument('--since', help='Start date (inclusive) YYYY-MM-DD')
    p.add_argument('--until', help='End date (inclusive) YYYY-MM-DD')
    p.add_argument('--json', action='store_true', help='Output machine-readable JSON summary')
    return p.parse_args()


def load_rates(rate_args):
    rates = dict(DEFAULT_RATES)
    for r in rate_args:
        if '=' in r:
            model, val = r.split('=', 1)
            try:
                rates[model.strip()] = float(val)
            except Exception:
                print(f"Warning: invalid rate value for {r}; skipping")
        else:
            print(f"Warning: rate format MODEL=RATE expected, got: {r}; skipping")
    return rates


def parse_line(line):
    try:
        obj = json.loads(line)
        # timestamp -> date
        ts = obj.get('timestamp') or obj.get('time')
        if not ts:
            return None
        # normalize timestamp to date string YYYY-MM-DD
        try:
            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        except Exception:
            try:
                # try parsing as float epoch
                dt = datetime.fromtimestamp(float(ts), tz=timezone.utc)
            except Exception:
                return None
        date = dt.date().isoformat()
        model = obj.get('model') or obj.get('openai_model') or 'unknown'
        usage = obj.get('usage') or {}
        prompt_tokens = int(usage.get('prompt_tokens') or 0)
        completion_tokens = int(usage.get('completion_tokens') or 0)
        total_tokens = int(usage.get('total_tokens') or (prompt_tokens + completion_tokens))
        return {
            'date': date,
            'model': model,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens,
        }
    except Exception:
        return None


def aggregate(logfile, since=None, until=None):
    if not os.path.exists(logfile):
        print(f"No log file found at {logfile}")
        return None

    per_day = defaultdict(lambda: Counter())
    per_model = defaultdict(lambda: Counter())
    entries = 0

    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = parse_line(line)
            if not obj:
                continue
            date = obj['date']
            if since and date < since:
                continue
            if until and date > until:
                continue
            model = obj['model']
            per_day[date]['prompt_tokens'] += obj['prompt_tokens']
            per_day[date]['completion_tokens'] += obj['completion_tokens']
            per_day[date]['total_tokens'] += obj['total_tokens']

            per_model[model]['prompt_tokens'] += obj['prompt_tokens']
            per_model[model]['completion_tokens'] += obj['completion_tokens']
            per_model[model]['total_tokens'] += obj['total_tokens']

            entries += 1

    return {
        'entries': entries,
        'per_day': {d: dict(per_day[d]) for d in sorted(per_day.keys())},
        'per_model': {m: dict(per_model[m]) for m in sorted(per_model.keys())},
    }


def estimate_costs(aggregate_data, rates):
    # rates are per 1k tokens
    per_model_costs = {}
    total_cost = 0.0
    for model, vals in aggregate_data['per_model'].items():
        total_tokens = vals.get('total_tokens', 0)
        rate = rates.get(model, None)
        if rate is None:
            per_model_costs[model] = {'total_tokens': total_tokens, 'estimated_usd': None}
        else:
            cost = (total_tokens / 1000.0) * float(rate)
            per_model_costs[model] = {'total_tokens': total_tokens, 'estimated_usd': round(cost, 6)}
            total_cost += cost

    # per-day cost using model-agnostic average (naive): apply no model split
    per_day_costs = {}
    for day, vals in aggregate_data['per_day'].items():
        day_total = vals.get('total_tokens', 0)
        # estimate using a weighted average of rates by model share isn't trivial here without model breakdown per day
        # so we leave per-day cost None unless only one model present in per_model
        per_day_costs[day] = {'total_tokens': day_total, 'estimated_usd': None}

    return {
        'per_model_costs': per_model_costs,
        'per_day_costs': per_day_costs,
        'total_estimated_usd': round(total_cost, 6)
    }


def main():
    args = parse_args()
    rates = load_rates(args.rate)

    agg = aggregate(args.log, since=args.since, until=args.until)
    if agg is None:
        return

    cost = estimate_costs(agg, rates)

    if args.json:
        out = {'aggregate': agg, 'cost': cost, 'rates_used': rates}
        print(json.dumps(out, indent=2))
        return

    print('\nOpenAI Usage Summary')
    print('Entries:', agg['entries'])
    print('\nPer-model totals:')
    for model, vals in agg['per_model'].items():
        print(f"  {model}: prompt={vals.get('prompt_tokens',0)} completion={vals.get('completion_tokens',0)} total={vals.get('total_tokens',0)}")
        est = cost['per_model_costs'].get(model, {})
        if est.get('estimated_usd') is not None:
            print(f"     estimated cost: ${est['estimated_usd']}")
        else:
            print(f"     estimated cost: (no rate for model; pass --rate {model}=0.002 to set)")

    print('\nPer-day totals:')
    for day, vals in agg['per_day'].items():
        print(f"  {day}: total_tokens={vals.get('total_tokens',0)} (prompt={vals.get('prompt_tokens',0)}, completion={vals.get('completion_tokens',0)})")

    print('\nTotal estimated cost across models:', f"${cost['total_estimated_usd']}")
    print('\nRates used:')
    for m, r in rates.items():
        print(f"  {m}: ${r} per 1k tokens")


if __name__ == '__main__':
    main()
