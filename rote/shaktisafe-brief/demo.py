"""Offline synthetic demo. No live conditions or real warnings are represented."""
import copy
import tempfile
from pathlib import Path
from shaktisafe import compose, source, markdown, write
from test_shaktisafe import ctx, payload, CLOCK

def main() -> None:
    """Write three explicitly synthetic demonstration reports."""
    context = ctx()
    results = [source(n, context, lambda _, n=n: payload(n), CLOCK) for n in ('weather', 'air', 'alerts')]
    destination = Path('demo-output')
    destination.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as state:
        first = compose(context, results, state, CLOCK)
        changed = copy.deepcopy(results)
        changed[0]['data']['metrics']['temperature_2m']['max'] = 16
        changed[1]['data']['metrics']['pm2_5']['max'] = 20
        second = compose(context, changed, state, CLOCK)
        failed = copy.deepcopy(changed)
        failed[0] = {k: v for k, v in failed[0].items() if k != 'data'}
        failed[0].update(status='unavailable', reason='Synthetic timeout for demonstration')
        third = compose(context, failed, state, CLOCK)
    for name, report in [('01-baseline', first), ('02-changed', second), ('03-source-failure', third)]:
        report['mode'] = 'SYNTHETIC DEMO — NOT LIVE CONDITIONS'
        write(destination / (name + '.json'), report)
        (destination / (name + '.md')).write_text(markdown(report), encoding="utf-8")
    print(markdown(second))
    print('Three labeled demonstrations saved in demo-output/')


if __name__ == "__main__":
    main()
