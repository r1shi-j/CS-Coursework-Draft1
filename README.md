<h1>Setup</h1>
<h4>The system works best on macOS</h4>
<h2>Prerequisites</h2>
<ul>
  <li>Python 3 must be installed</li>
  <li>Visual studio code must be installed with the python extension (by Microsoft) also installed</li>
</ul>
<span>Follow the guide below to install the required modules into a virtual environment depending on your operating sytem.</span></p>

<h2>For macOS </h2>
<p><code>python3 -m venv venv</code></p>
<p><code>source venv/bin/activate</code></p>
<p><code>pip install -r requirements.txt</code></p>
<p><code>python3 main.py</code></p>

<h2>For Windows ⊞ 🗑 (using PowerShell)</h2>
<p><code>python -m venv venv</code></p>
<p><code>Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process</code></p>
<p><code>.\venv\Scripts\Activate.ps1</code></p>
<p><code>pip install -r requirements.txt</code></p>
<p><code>python main.py</code></p>

<h1>Modules required</h3>
<h4>Modules that should all be preinstalled in macOS and Windows</h4>
<p>
<span><code>sqlite3</code></span>
<span><code>tkinter</code></span>
</p>
<p>
<span><code>datetime</code></span>
<span><code>collections</code></span>
<span><code>typing</code></span>
<span><code>re</code></span>
<span><code>uuid</code></span>
<span><code>hashlib</code></span>
</p>
<p>
<span><code>os</code></span>
<span><code>platform</code></span>
<span><code>traceback</code></span>
<span><code>sys</code></span>
<span><code>argparse</code></span>
<span><code>threading (macOS only)</code></span>
</p>
<h4>Modules required to be installed (additional info can be found in <code>requirements.txt</code>)</h4>
<p>
<span><code>tkcalendar</code></span>
<span><code>matplotlib</code></span>
<span><code>zxcvbn</code></span>
<span><code>LocalAuthentication (macOS only)</code></span>
</p>
<p>Following the steps above will install these modules into your virual environment</p>
