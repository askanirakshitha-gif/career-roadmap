import inspect
import anthropic
print('anthropic version', getattr(anthropic, '__version__', 'unknown'))
try:
    print('signature', inspect.signature(anthropic.Anthropic))
except Exception as e:
    print('signature error', e)
