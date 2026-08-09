"""H2158 -- report the SHAPE of the configured Anthropic credential, never its value.

The API arm came back 401 with a credential present, which has several distinct causes
that need different fixes and are indistinguishable without looking at the prefix:

  * `sk-ant-api...`  a real Messages API key -> should work; a 401 means revoked,
                     wrong org/workspace, or a stray quote/newline in the file.
  * `sk-ant-oat...`  an OAuth access token -> goes on `Authorization: Bearer` WITH the
                     `anthropic-beta: oauth-2025-04-20` header, NOT on `x-api-key`.
                     The SDK's api_key= path sends x-api-key, hence 401.
  * `sk-ant-sid...`  a session/console cookie value, not an API credential at all.
  * anything else    not an Anthropic credential.

Prints only length, prefix, and whether stray whitespace/quotes survived parsing. The
value itself is never printed, so this is safe to run with output captured in a
transcript.

    python src/pilot/h2158_key_shape.py

Model: authored by Opus 5 (`claude-opus-5`) for handoff H2158.
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

SECRETS_ENV = r'C:\Users\user\.secrets\anthropic.env'
NAMES = ('ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN')

KNOWN = {
    'sk-ant-api': 'Messages API key -- correct type for this arm',
    'sk-ant-oat': 'OAuth ACCESS TOKEN -- needs Authorization: Bearer + the '
                  'anthropic-beta: oauth-2025-04-20 header, NOT x-api-key',
    'sk-ant-ort': 'OAuth REFRESH token -- not directly usable; exchange it first',
    'sk-ant-sid': 'console session id -- not an API credential',
}


def classify(value):
    for prefix, meaning in KNOWN.items():
        if value.startswith(prefix):
            return prefix, meaning
    if value.startswith('sk-ant-'):
        return value[:11], 'unrecognised sk-ant- subtype'
    return value[:4], 'does not look like an Anthropic credential'


def report(source, name, raw):
    value = raw.strip().strip('"').strip("'")
    prefix, meaning = classify(value)
    print('  source      : %s' % source)
    print('  name        : %s' % name)
    print('  length      : %d (after stripping quotes/whitespace)' % len(value))
    print('  raw length  : %d %s' % (len(raw),
                                     '(!! stray whitespace or quotes in the file)'
                                     if len(raw) != len(value) else ''))
    print('  prefix      : %s...' % prefix)
    print('  verdict     : %s' % meaning)
    if any(c in value for c in ' \t\r\n'):
        print('  !! the value contains an INTERNAL space/newline -- likely a wrapped paste')
    print()


def main():
    found = False
    for name in NAMES:
        raw = os.environ.get(name)
        if raw:
            found = True
            report('environment', name, raw)
    if os.path.exists(SECRETS_ENV):
        with open(SECRETS_ENV, encoding='utf-8-sig') as fh:
            for line in fh:
                if line.strip().startswith('#') or '=' not in line:
                    continue
                name, _, raw = line.partition('=')
                if name.strip() in NAMES:
                    found = True
                    report(SECRETS_ENV, name.strip(), raw.rstrip('\n'))
    else:
        print('  %s does not exist' % SECRETS_ENV)
    if not found:
        print('  no Anthropic credential found in the environment or in %s' % SECRETS_ENV)
    return 0


if __name__ == '__main__':
    sys.exit(main())
