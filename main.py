import webview
import os
from bridge import HermitAPI

def start_app():
    api = HermitAPI()
    
    # Path to our HTML
    html_path = os.path.join(os.path.dirname(__file__), 'web', 'index.html')
    
    window = webview.create_window(
        'HermitVault - Secure Password Manager',
        html_path,
        js_api=api,
        width=1200,
        height=850,
        min_size=(1000, 750),
        background_color='#171218'
    )
    
    webview.start(debug=False)

if __name__ == "__main__":
    start_app()
