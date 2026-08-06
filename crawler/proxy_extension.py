import os
import zipfile

def create_proxy_auth_extension(proxy_string, output_file='proxy_auth_plugin.zip'):
    """
    Tạo một Chrome Extension on-the-fly để truyền Username/Password cho Proxy.
    proxy_string format: "user:pass@host:port" hoặc ":pass@host:port"
    """
    try:
        credentials, endpoint = proxy_string.split('@')
        if ':' in credentials:
            user, pwd = credentials.split(':', 1)
        else:
            user, pwd = "", credentials
            
        host, port = endpoint.split(':')
    except Exception as e:
        print("Lỗi parse proxy string:", e)
        return None
        
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
              },
              bypassList: ["localhost"]
            }
          };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (host, port, user, pwd)

    extension_path = os.path.abspath(output_file)
    with zipfile.ZipFile(extension_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    
    return extension_path
