import requests
from unittest.mock import Mock, patch

# Reproduce the issue
session = requests.Session()
session.headers['Accept-Encoding'] = None

# Mock the actual send method to capture the request
captured_request = None
def mock_send(prepped, *args, **kwargs):
    global captured_request
    captured_request = prepped
    resp = Mock()
    resp.status_code = 200
    resp.headers = {}
    resp.text = ''
    resp.cookies = {}
    return resp

with patch.object(requests.Session, 'send', side_effect=mock_send):
    session.get('https://example.com')

print("Headers sent when session header is None:")
for k, v in captured_request.headers.items():
    if k.lower() == 'accept-encoding':
        print(f"  {k}: {repr(v)}")
        print(f"  ❌ Bug confirmed: 'None' string is sent instead of omitting the header")

# Now test the expected behavior when passing None in method call
session = requests.Session()
session.headers['Accept-Encoding'] = 'gzip, deflate'

with patch.object(requests.Session, 'send', side_effect=mock_send):
    session.get('https://example.com', headers={'Accept-Encoding': None})

print("\nHeaders sent when passing None in method call:")
if 'Accept-Encoding' not in captured_request.headers:
    print("  ✅ Correct: Accept-Encoding header is omitted")
else:
    print(f"  {k}: {repr(v)}")

# Show the fix
print("\nThe fix:")
print("We need to modify requests to filter out None values from session headers when preparing the request, same as it does for per-request headers.")
print("The change would be in requests.sessions.Session.merge_environment_settings or in the prepare_request method, to remove any headers with value None.")
