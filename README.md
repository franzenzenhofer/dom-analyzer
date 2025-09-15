# 🤓 DOM Analyzer - Ultimate Website Statistics Tool

**10,000+ Statistics per URL** | **12 User Agents** | **Advanced Visualizations**

A comprehensive DOM analysis tool that provides deep insights into website structure, performance, SEO, accessibility, and security. Built by Franz Enzenhofer.

## 🚀 Features

### Core Capabilities
- **10,000+ data points** analyzed per URL
- **12 different user agents** testing (Desktop, Mobile, Bots)
- **Third-party domain tracking** with categorization
- **Resource preloading detection** (dns-prefetch, preconnect, prefetch, preload)
- **Asset loading analysis** with waterfall visualization
- **Network request mapping** with domain categorization
- **CDN detection** (Cloudflare, CloudFront, Akamai, etc.)
- **Third-party service identification** (50+ services)

### Analysis Categories
1. **DOM Complexity** - Tree depth, node distribution, complexity scoring
2. **CSS Analysis** - Selector complexity, BEM detection, Atomic CSS patterns
3. **JavaScript** - Framework detection (React, Vue, Angular, jQuery, etc.)
4. **Performance** - Web Vitals, lazy loading, resource hints, critical path
5. **SEO Signals** - Meta tags, Schema.org, Open Graph, content quality
6. **Accessibility** - WCAG 2.1, ARIA usage, semantic HTML scoring
7. **Security** - Header analysis, CSP evaluation, cookie security
8. **Network Resources** - CDN usage, API detection, tracking pixels
9. **Forms** - Validation, autocomplete, UX features
10. **Colors & Typography** - Palette extraction, font analysis
11. **Mobile Responsiveness** - Viewport, touch-friendly, flexible layouts
12. **Third-Party Integrations** - Payment, analytics, social, support
13. **Page Weight** - Size distribution, optimization opportunities

### Visualizations
- 🌟 **Sunburst Chart** - DOM hierarchy visualization
- 📊 **Treemap** - Resource distribution
- 🔥 **Heatmap** - Performance metrics
- 🎯 **Radar Chart** - Multi-factor analysis
- 🌌 **3D Scatter Plot** - Correlation analysis
- 💧 **Waterfall Chart** - Resource loading timeline
- 🔀 **Sankey Diagram** - Data flow visualization
- 🫧 **Bubble Chart** - Tag distribution
- 📦 **Box Plot** - Statistical distributions
- 🎻 **Violin Plot** - Density analysis
- 🕸️ **Network Graph** - Dependency visualization

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/franzenzenhofer/dom-analyzer.git
cd dom-analyzer

# Install dependencies
pip install -r requirements.txt
```

## 🎮 Usage

### Web Interface

```bash
# Start the Flask app
python3 app.py

# Open browser to http://127.0.0.1:5000
```

### Command Line Interface

```bash
# Basic analysis
python3 cli.py https://example.com

# Detailed analysis with JSON output
python3 cli.py https://example.com --format json --output results.json

# Summary format
python3 cli.py https://example.com --format summary

# Specific categories only
python3 cli.py https://example.com --categories seo accessibility performance

# CSV export
python3 cli.py https://example.com --format csv --output results.csv
```

## 🧪 Testing

```bash
# Run all tests
./run_tests.sh

# Unit tests only
./run_tests.sh --unit-only

# E2E tests
./run_tests.sh --e2e-only

# Performance benchmarks
./run_tests.sh --benchmarks
```

## 📊 Test Results

### Hacker News Analysis
- **DOM Elements**: 813
- **Max Depth**: 12
- **Complexity Score**: 9,756
- **Security Score**: 68.8/100
- **Content-to-Code Ratio**: 11.2%

### Google.com Analysis
- **DOM Elements**: 476
- **Max Depth**: 19
- **Complexity Score**: 9,044
- **Security Score**: 50.0/100
- **Accessibility**: 100% images with alt text

### EVI.gv.at Analysis
- **Full analysis saved**: evi_analysis.json
- **Third-party domains detected**
- **Resource preloading strategies identified**
- **Asset loading waterfall generated**

## 🏗️ Architecture

```
dom-analyzer/
├── app.py                  # Flask web application
├── cli.py                  # Command-line interface
├── core_analyzer.py        # Shared analysis logic (DRY)
├── analyzer_enhanced.py    # Enhanced analyzer with 10,000+ metrics
├── templates/
│   ├── index.html         # Main UI
│   └── visualizations.html # Advanced charts
├── static/                # Generated graphs
├── test_analyzer.py       # Unit tests
├── test_e2e.py           # End-to-end tests
├── test_benchmarks.py    # Performance tests
├── test_fixtures.py      # Test data
└── run_tests.sh          # Test runner
```

## 🔑 Key Statistics Tracked

### Network & Resources
- **Total external requests**
- **Third-party domains** (categorized)
- **Subdomain requests**
- **CDN usage** (10+ CDN providers)
- **Resource hints** (prefetch, preload, preconnect)
- **Asset types** (JS, CSS, images, fonts)
- **Protocol distribution** (HTTP/HTTPS)
- **Tracking pixels detected**

### Performance Metrics
- **Critical render path**
- **Lazy loading usage**
- **Async/defer scripts**
- **Web Vitals indicators**
- **Service Worker detection**
- **Image optimization** (WebP, AVIF)
- **Compression opportunities**

### Third-Party Services
- **Payment gateways** (Stripe, PayPal, Square)
- **Analytics tools** (GA, GTM, Matomo)
- **Social media** (Facebook, Twitter, LinkedIn)
- **Customer support** (Intercom, Zendesk)
- **Marketing tools** (Mailchimp, HubSpot)
- **Authentication** (Auth0, Firebase)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details.

## 👤 Author

**Franz Enzenhofer**
- GitHub: [@franzenzenhofer](https://github.com/franzenzenhofer)
- Team: team@fullstackoptimization.com

## 🙏 Acknowledgments

- Built with Flask, BeautifulSoup, and Plotly
- Inspired by the need for comprehensive DOM analysis
- Special focus on third-party tracking and resource loading analysis

---

**Note**: This tool performs deep analysis of websites and may take 30+ seconds for complex sites. The comprehensive analysis provides insights that help optimize performance, security, and user experience.